import unittest
import numpy as np,pandas as pd
import phase_correction as C,repo_predict as R
class PhaseCorrectionTests(unittest.TestCase):
    def test_zero_residual_recovers_baseline(self):
        rng=np.random.default_rng(4);d=pd.DataFrame(rng.normal(size=(24,len(R.PHYS))),columns=R.PHYS);d['nfl_id']=np.arange(24)
        for i in range(5):d['source_'+str(i)]=rng.normal(size=24)
        cols=['source_'+str(i) for i in range(5)];p=C.correction(d.iloc[:18],d.iloc[18:],np.zeros(18),cols)
        np.testing.assert_array_equal(p,np.zeros(6))
        p=C.correction(d.iloc[:18],d.iloc[18:],np.zeros(18),cols,scaled=True)
        np.testing.assert_array_equal(p,np.zeros(6))
    def test_original_player_overlap_rejected(self):
        d=pd.DataFrame({'nfl_id':[1]})
        with self.assertRaises(ValueError):C.conventional_bag(d,d,0,1)
        with self.assertRaises(ValueError):C.correction(d,d,np.zeros(1),['x'])
if __name__=='__main__':unittest.main()
