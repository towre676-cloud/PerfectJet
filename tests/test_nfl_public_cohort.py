import unittest
import numpy as np
import pandas as pd
from perfectjet.applications.nfl_scouting.public_cohort import (
    PublicCohort, build_cohort, height_inches, source_features, run_public_benchmark)

class PublicCohortTests(unittest.TestCase):
    def frames(self):
        combine=pd.DataFrame([
            {'pfr_id':'a','season':2020,'pos':'DE','ht':'6-3','wt':250,'forty':4.6,'bench':20,'vertical':35,'broad_jump':120,'cone':7.1,'shuttle':4.2,'draft_ovr':1},
            {'pfr_id':'b','season':2020,'pos':'DT','ht':'6-2','wt':300,'forty':5.0,'bench':30,'vertical':30,'broad_jump':110,'cone':7.5,'shuttle':4.6,'draft_ovr':2},
            {'pfr_id':'c','season':2026,'pos':'DE','ht':'6-4','wt':260,'forty':4.7,'bench':25,'vertical':32,'broad_jump':115,'cone':7.3,'shuttle':4.4,'draft_ovr':3}])
        players=pd.DataFrame({'pfr_id':['a','b','c'],'gsis_id':['ga','gb','gc']})
        stats=pd.DataFrame({'player_id':['ga','gc'],'season':[2020,2026],'season_type':['REG','REG'],'def_sacks':[0,15],'def_qb_hits':[0,30]})
        snaps=pd.DataFrame({'pfr_player_id':['a','a'],'pfr_game_id':['game1','game2'],'team':['A','A'],'season':[2020,2020],'game_type':['REG','REG'],'defense_snaps':[0,10]})
        return combine,players,stats,snaps

    def test_unknown_outcomes_are_not_silent_zeros(self):
        c=build_cohort(*self.frames());a=c.frame.set_index('pfr_id')
        self.assertEqual(a.loc['a','rookie_sacks'],0)
        self.assertTrue(np.isnan(a.loc['b','rookie_sacks']))
        self.assertTrue(np.isnan(a.loc['b','rookie_defense_snaps']))
        self.assertEqual(a.loc['a','rookie_defense_snaps'],10)

    def test_incomplete_season_is_excluded(self):
        c=build_cohort(*self.frames());self.assertNotIn(2026,c.frame.season.tolist())

    def test_duplicate_source_identity_is_excluded(self):
        c,p,s,n=self.frames();c=pd.concat([c,c.iloc[:1]],ignore_index=True)
        r=build_cohort(c,p,s,n)
        self.assertNotIn('a',r.frame.pfr_id.tolist())
        self.assertEqual(r.audit['ambiguous_combine_ids_excluded'],['a'])

    def test_duplicate_outcomes_and_snaps_rejected(self):
        c,p,s,n=self.frames()
        with self.assertRaisesRegex(ValueError,'duplicate GSIS'):build_cohort(c,p,pd.concat([s,s.iloc[:1]]),n)
        with self.assertRaisesRegex(ValueError,'duplicate player/game'):build_cohort(c,p,s,pd.concat([n,n.iloc[:1]]))

    def test_no_name_matching_for_unknown_id(self):
        c,p,s,n=self.frames();p.loc[0,'pfr_id']='different';p['display_name']=['a','b','c']
        r=build_cohort(c,p,s,n).frame.set_index('pfr_id')
        self.assertTrue(np.isnan(r.loc['a','rookie_sacks']))

    def test_pressure_total_not_added_to_team_splits(self):
        c,p,s,n=self.frames()
        pr=pd.DataFrame({'pfr_id':['a','a','a'],'season':[2020]*3,'player':['A']*3,'tm':['2TM','A','B'],'prss':[10,3,7],'g':[16,5,11],'sk':[2,1,1]})
        r=build_cohort(c,p,s,n,pr).frame.set_index('pfr_id')
        self.assertEqual(r.loc['a','rookie_pressures'],10)
        self.assertEqual(r.loc['a','rookie_pressures_per_100_defense_snaps'],100)

    def test_ambiguous_pressure_name_identity_is_not_guessed(self):
        c,p,s,n=self.frames()
        pr=pd.DataFrame({'pfr_id':['a','b'],'season':[2020]*2,'player':['Same name']*2,'tm':['A']*2,'prss':[10,10],'g':[16,16],'sk':[2,2]})
        r=build_cohort(c,p,s,n,pr)
        self.assertTrue(r.frame.rookie_pressures.isna().all())
        self.assertEqual(r.audit['ambiguous_pressure_player_seasons_excluded'],2)

    def test_predictors_exclude_draft_and_future_nfl_fields(self):
        c=build_cohort(*self.frames()).frame
        c['future_nfl_position']='EDGE';c['career_av']=999
        f=source_features(c,mechanical=True)
        self.assertFalse(any('draft' in str(k) or 'rookie' in str(k) or 'career' in str(k) for k in f))
        self.assertAlmostEqual(f.a40_proxy.iloc[0],80/4.6**2)
        self.assertEqual(height_inches('6-3'),75)
        self.assertTrue(np.isnan(height_inches('unknown')))

    def test_temporal_tuning_uses_only_past_classes(self):
        rng=np.random.default_rng(42);rows=[]
        for year in range(2005,2014):
            for j in range(8):
                x=float(rng.normal());rows.append(dict(pfr_id=f'{year}-{j}',season=year,combine_position='DE',height_inches=75,wt=250,forty=4.6+.1*x,bench=20,vertical=35,broad_jump=120,cone=7.1,shuttle=4.2,rookie_sacks=max(0,5-2*x+rng.normal())))
        r=run_public_benchmark(PublicCohort(pd.DataFrame(rows),{},[]),targets=('rookie_sacks',),test_min_year=2010,minimum_train=16,minimum_test=4,alphas=(1,10),bootstrap_draws=10)
        for fold in r['targets']['rookie_sacks']['folds']:
            for years in fold['inner_years'].values():self.assertTrue(all(y<fold['year'] for y in years))
        self.assertFalse(r['new_sensor_information'])
        self.assertEqual(r['targets']['rookie_sacks']['evaluated_players'],32)

    def test_current_test_outcomes_cannot_change_its_predictions(self):
        rng=np.random.default_rng(71);rows=[]
        for year in range(2005,2011):
            for j in range(6):
                x=float(rng.normal());rows.append(dict(pfr_id=f'{year}-{j}',season=year,combine_position='DE',height_inches=75,wt=250,forty=4.6+.1*x,bench=20,vertical=35,broad_jump=120,cone=7.1,shuttle=4.2,rookie_sacks=max(0,5-2*x+rng.normal())))
        f=pd.DataFrame(rows)
        kw=dict(targets=('rookie_sacks',),test_min_year=2010,minimum_train=12,minimum_test=4,alphas=(1,10),bootstrap_draws=2)
        r1=run_public_benchmark(PublicCohort(f,{},[]),**kw)
        changed=f.copy();changed.loc[changed.season==2010,'rookie_sacks']=10000
        r2=run_public_benchmark(PublicCohort(changed,{},[]),**kw)
        for a,b in zip(r1['targets']['rookie_sacks']['predictions'],r2['targets']['rookie_sacks']['predictions']):
            self.assertEqual(a['mechanical'],b['mechanical'])
            self.assertEqual(a['baseline'],b['baseline'])

if __name__=='__main__':unittest.main()
