import unittest,sys
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from run_movement_transfer import model_predict,PHYS,bank

class Transfer(unittest.TestCase):
    def rows(self):
        rng=np.random.default_rng(410);x=pd.DataFrame({c:rng.normal(size=20) for c in PHYS});x['nfl_id']=np.arange(20);x['nfl_position']='DE';x['target']=np.clip(.1+x[PHYS[0]]*.01,0,1);x['movement__test__x']=rng.normal(size=20);return x
    def test_complete_baseline_fallback(self):
        x=self.rows();tr,te=x.iloc[:15],x.iloc[15:]
        a=model_predict(tr,te,[],10,0);b=model_predict(tr,te,['movement__test__x'],10,0)
        np.testing.assert_array_equal(a,b);self.assertTrue(any(k==0 for a,k in bank()))
    def test_athlete_overlap_rejected(self):
        x=self.rows()
        with self.assertRaises(ValueError):model_predict(x.iloc[:15],x.iloc[14:],[],10,0)
    def test_other_test_players_cannot_change_prediction(self):
        x=self.rows();tr,te=x.iloc[:15],x.iloc[15:].copy();a=model_predict(tr,te,['movement__test__x'],10,2)
        te.iloc[1:,te.columns.get_loc('movement__test__x')]=1e12;b=model_predict(tr,te,['movement__test__x'],10,2)
        self.assertAlmostEqual(a[0],b[0],places=10)

if __name__=='__main__':unittest.main()
