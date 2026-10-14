import unittest,tempfile,random
from dataclasses import replace
from perfectjet.applications.nfl_scouting.synthetic import generate,export_csv,_trajectory
from perfectjet.applications.nfl_scouting.events import extract,extract_all,review_sample,trapezoid_weights
from perfectjet.applications.nfl_scouting.schema import (Attempt,Athlete,load_directory,audit_joins,
                                                         admissible_measurements,DEFAULT_MAPPING)
from perfectjet.applications.nfl_scouting.readouts import DemandFrame,PooledModel,group,split_half
from perfectjet.applications.nfl_scouting.outcomes import build_targets,leakage_check
from perfectjet.applications.nfl_scouting.validate import (run_validation,fixed_prediction_interval,Featurizer,
                                                           resample_dataset,decision_eval)
from perfectjet.applications.nfl_scouting.linalg import pearson,ridge,solve
from perfectjet.applications.nfl_scouting.pipeline import run


class EventTests(unittest.TestCase):
    def test_planted_turn_is_detected_with_its_angle(self):
        rng=random.Random(0)
        for angle in (45,90,135,170):
            frames=_trajectory(rng,5.0,angle,0.3,0.0)
            ev=extract(Attempt("A","A-1","L-drill",frames,"2024-02-28"))
            self.assertEqual(len(ev),1)
            self.assertLess(abs(ev[0].turn_angle-angle),12)
            self.assertLess(abs(ev[0].entry_speed-5.0),0.6)

    def test_faster_recovery_has_larger_eta(self):
        rng=random.Random(1)
        etas=[extract(Attempt("A",f"A-{k}","L-drill",_trajectory(rng,5.0,90,tau,0.0),"2024-02-28"))[0].eta
              for k,tau in enumerate((0.2,0.35,0.6))]
        self.assertGreater(etas[0],etas[1]);self.assertGreater(etas[1],etas[2])

    def test_branches_and_lineage(self):
        ds=generate(n_athletes=6,seed=2);e=extract_all(ds.attempts)[0]
        self.assertEqual(len(e.eta_branches),6);self.assertGreaterEqual(e.sensitivity,0)
        self.assertEqual(e.lineage.attempt_id,e.attempt_id);self.assertIn("nfl-events",e.lineage.extraction_version)

    def test_trapezoid_weights_integrate_constants(self):
        self.assertAlmostEqual(sum(trapezoid_weights([0,0.1,0.2,0.3,0.4,0.5])),0.5)

    def test_review_sheet_is_stratified_and_blinded(self):
        ds=generate(n_athletes=20,seed=3);sheet=review_sample(extract_all(ds.attempts))
        self.assertTrue(any(r["difficult_example"] for r in sheet))
        self.assertTrue(all("target" not in r and "outcome" not in r for r in sheet))
        self.assertEqual(len({r["drill"] for r in sheet}),3)


class ContractTests(unittest.TestCase):
    def test_late_measurements_are_rejected(self):
        a=Athlete("A","DE",2024,{"forty":4.7,"weight":260},{"forty":"2024-03-01","weight":"2024-06-01"})
        use,rej=admissible_measurements(a,"2024-04-20",["forty","weight"])
        self.assertEqual(use,{"forty":4.7});self.assertEqual(rej,["weight"])

    def test_csv_round_trip_and_manifest(self):
        ds=generate(n_athletes=9,seed=4)
        with tempfile.TemporaryDirectory() as d:
            export_csv(ds,d);back=load_directory(d)
            self.assertEqual(set(back.athletes),set(ds.athletes));self.assertEqual(len(back.attempts),len(ds.attempts))
            self.assertEqual(len(back.plays),len(ds.plays));self.assertEqual(len(back.manifest),3)
            self.assertTrue(all(len(v["sha256"])==64 for v in back.manifest.values()))

    def test_audit_finds_chronology_errors(self):
        ds=generate(n_athletes=9,seed=5)
        p=ds.plays[0];bad=replace(p,season=ds.athletes[p.athlete_id].draft_year-1)
        ds.plays.append(bad);self.assertEqual(audit_joins(ds)["n_plays_before_draft"],1)


class ReadoutTests(unittest.TestCase):
    def test_readout_tracks_latent_ability(self):
        ds=generate(n_athletes=60,seed=6);g=group(extract_all(ds.attempts))
        m=PooledModel(DemandFrame(sum(g.values(),[])),g);lat=ds.manifest["synthetic"]["latent"];ids=sorted(g)
        self.assertGreater(pearson([m.intercept_readout(g[i])["theta"] for i in ids],[lat[i] for i in ids]),0.6)

    def test_pooling_reliance_falls_with_more_attempts(self):
        ds=generate(n_athletes=40,seed=7);g=group(extract_all(ds.attempts));m=PooledModel(DemandFrame(sum(g.values(),[])),g)
        a=max(g,key=lambda k:len(g[k]))
        self.assertLess(m.readout(g[a])["pooling_reliance"],m.readout(g[a][:1])["pooling_reliance"])
        self.assertEqual(m.readout([])["pooling_reliance"],1.0)

    def test_single_demand_is_not_identified(self):
        ds=generate(n_athletes=30,seed=8);ev=extract_all(ds.attempts);fr=DemandFrame(ev)
        one=[e for e in ev if e.drill=="L-drill"][:1]
        self.assertFalse(fr.support(one)["identified"])

    def test_linalg(self):
        self.assertEqual([round(v,9) for v in solve([[2,1],[1,3]],[3,5])],[0.8,1.4])
        b=ridge([[1,0],[1,1],[1,2]],[1,3,5],0.0);self.assertAlmostEqual(b[1],2.0,6)


class ValidationTests(unittest.TestCase):
    def test_leakage_check(self):
        ds=generate(n_athletes=40,seed=9)
        tr=[a for a,v in ds.athletes.items() if v.draft_year<2024];te=[a for a,v in ds.athletes.items() if v.draft_year==2024]
        self.assertEqual(leakage_check(ds.plays,tr,te),{"training_targets_unchanged":True,"context_model_unchanged":True})

    def test_test_outcomes_do_not_move_training_predictions(self):
        ds=generate(n_athletes=60,seed=10);ev=extract_all(ds.attempts)
        r1=run_validation(ds,ev)
        moved=replace(ds,plays=[replace(p,outcome=p.outcome+5) if ds.athletes[p.athlete_id].draft_year==2024 else p for p in ds.plays])
        r2=run_validation(moved,ev)
        f1=[f for f in r1["folds"] if f["year"]==2024][0];f2=[f for f in r2["folds"] if f["year"]==2024][0]
        for name in ("baseline","movement"):
            for a,b in zip(f1[name]["pred"],f2[name]["pred"]):self.assertAlmostEqual(a,b,12)

    def test_planted_signal_is_found_and_null_is_not(self):
        ev=lambda ds:extract_all(ds.attempts)
        planted=generate(n_athletes=120,seed=11,signal=1.0)
        r=run_validation(planted,ev(planted));self.assertGreater(fixed_prediction_interval(r["folds"])["lo"],0)
        null=generate(n_athletes=120,seed=11,signal=0.0)
        r=run_validation(null,ev(null));ci=fixed_prediction_interval(r["folds"])
        self.assertLess(ci["lo"],0.0)

    def test_featurizer_never_reads_plays(self):
        import inspect,ast,textwrap
        tree=ast.parse(textwrap.dedent(inspect.getsource(Featurizer)))
        names={n.attr for n in ast.walk(tree) if isinstance(n,ast.Attribute)}|{n.id for n in ast.walk(tree) if isinstance(n,ast.Name)}
        self.assertFalse({"plays","Play","outcome","context"}&names)

    def test_cluster_bootstrap_keeps_athletes_whole(self):
        ds=generate(n_athletes=12,seed=12);b=resample_dataset(ds,random.Random(0))
        self.assertEqual(len(b.athletes),12)
        for a in b.athletes:
            base=a.split("#")[0]
            self.assertEqual(len([x for x in b.attempts if x.athlete_id==a]),len([x for x in ds.attempts if x.athlete_id==base]))

    def test_pipeline_outputs(self):
        ds=generate(n_athletes=60,seed=13,signal=0.5)
        with tempfile.TemporaryDirectory() as d:
            res=run(ds,d,{"seed":1,"bootstrap":0,"readout":"intercept"})
            import os
            for name in ("results.json","cards.json","report.md","review_sheet.csv","fig_demand_support.svg",
                         "fig_predictive_comparison.svg","fig_event_trace.svg"):
                self.assertTrue(os.path.exists(os.path.join(d,name)),name)
            self.assertTrue(res["synthetic"]);
            with open(os.path.join(d,"report.md")) as fh:self.assertIn("SYNTHETIC",fh.read())


if __name__=="__main__":unittest.main()
