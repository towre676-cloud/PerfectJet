"""Artificial integration fixtures; these are not evidence about athletes."""
import copy,json,unittest
from dataclasses import replace
import numpy as np
from perfectjet.applications.nfl_scouting import rolling as R,rolling_reliability as M,repeat_controls as C
from perfectjet.applications.nfl_scouting.schema import Athlete,Attempt,Frame,Play,Dataset


def fixture():
    athletes={};attempts=[];plays=[]
    for i in range(24):
        aid=f'ARTIFICIAL-{i:03}';year=2023 if i<18 else 2024
        x=(i%9-4)/5
        measures={'forty':4.7+.05*x,'weight':240.+5*x,'height':74.+x}
        athletes[aid]=Athlete(aid,'DE' if i%2 else 'DT',year,measures,{k:f'{year}-03-01' for k in measures})
        for j in range(2):
            acc=3.6+x+.04*j
            frames=[Frame(t/10,1.1*t/10+acc*(t/10)**2/2,.005*j*(t/10)**2) for t in range(32)]
            attempts.append(Attempt(aid,f'{aid}-TRY{j}','FORTY_YARD_DASH',frames,f'{year}-03-01'))
        for k in range(6):
            depth=.2+.05*k
            plays.append(Play(aid,year,f'{aid}-PLAY{k}',.8-.04*x+.15*depth+.001*(k%2),
                {'snap_depth':depth,'snap_width':float(k%2),'down':float(k%3+1),
                 'yards_to_go':float(k+2),'lined_up_position':athletes[aid].position}))
    ds=Dataset(athletes,attempts,plays,{'test_only':True},{'minimum_plays':3},synthetic=True)
    tr=sorted(a for a,v in athletes.items() if v.draft_year==2023)
    te=sorted(a for a,v in athletes.items() if v.draft_year==2024)
    return ds,tr,te

class RollingIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds,cls.tr,cls.te=fixture();cls.w,_=R.source_windows(cls.ds)
        cls.frames=R.feature_frames(cls.ds,sorted(cls.ds.athletes),cls.w)
        cls.reference=R.nested_fold(cls.ds,cls.frames,cls.tr,cls.te,2024,alphas=(100.,))

    def test_entire_held_nfl_cannot_change_model_or_tuning(self):
        changed=copy.deepcopy(self.ds)
        changed.plays=[replace(p,outcome=p.outcome+400,context={**p.context,'snap_depth':900})
            if p.athlete_id in self.te else p for p in changed.plays]
        result=R.nested_fold(changed,self.frames,self.tr,self.te,2024,alphas=(100.,))
        for key in ('conventional','tracking','kinematics','jets','history','strong_control'):
            np.testing.assert_allclose(result[key],self.reference[key],atol=0,rtol=0)
        self.assertEqual(result['selected'],self.reference['selected'])
        self.assertEqual(result['inner_mse'],self.reference['inner_mse'])
        self.assertNotEqual(result['y'],self.reference['y'])

    def test_reliability_calibration_ignores_held_nfl(self):
        groups=M.vector_groups(self.w);base=self.frames['conventional']
        one=M.nested_fold(self.ds,base,groups,self.tr,self.te,2024)
        changed=copy.deepcopy(self.ds)
        changed.plays=[replace(p,outcome=p.outcome-50) if p.athlete_id in self.te else p for p in changed.plays]
        two=M.nested_fold(changed,base,groups,self.tr,self.te,2024)
        for k in ('conventional','raw','reliable'):
            np.testing.assert_array_equal(one[k],two[k])
        self.assertEqual(one['selected'],two['selected'])
        self.assertEqual(one['source_calibration'],two['source_calibration'])

    def test_public_allowlist_drops_restricted_predictions(self):
        r={'schema':'test','status':'artificial','include_ngs':True,'source_drills':[],
            'target':{'name':'test'},'comparisons':{},'model_fits':20,'source_features':{},
            'prediction_rule':'test','folds':[self.reference],'private_secret':'never publish'}
        public=R.public_result(r);encoded=json.dumps(public)
        for aid in self.ds.athletes:self.assertNotIn(aid,encoded)
        self.assertNotIn('private_secret',encoded);self.assertNotIn('"y"',encoded)

    def test_repeat_control_has_no_nfl_dependency(self):
        groups=M.vector_groups(self.w);original=lambda a:a
        a=C._fold(groups,self.tr,self.te,original,141014)
        changed=copy.deepcopy(self.ds);changed.plays=[]
        w,_=R.source_windows(changed)
        b=C._fold(M.vector_groups(w),self.tr,self.te,original,141014)
        self.assertEqual(a,b)

    def test_repeat_control_original_player_isolation(self):
        groups=M.vector_groups(self.w)
        original=lambda aid:self.tr[0] if aid==self.te[0] else aid
        with self.assertRaises(ValueError):C._fold(groups,self.tr,self.te,original,141014)

    def test_covariance_basis_is_physical_not_fold_eigenbasis(self):
        from perfectjet.reliable_modes import ReliableModes
        groups=M.vector_groups(self.w);model=ReliableModes.fit(groups,training_groups=self.tr)
        out=M._frames(self.frames['conventional'],self.te,groups,model)
        for aid in self.te:
            expected=model.posterior(groups[aid])[0]-model.mean
            np.testing.assert_allclose(out['reliable'].loc[aid,[f'area_posterior_{k}' for k in range(3)]].astype(float),expected)

if __name__=='__main__':unittest.main()
