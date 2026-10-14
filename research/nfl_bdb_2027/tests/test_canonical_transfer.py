import unittest
import numpy as np,pandas as pd
import canonical_transfer as C
class CanonicalTests(unittest.TestCase):
    def rows(self):
        rng=np.random.default_rng(410);x=pd.DataFrame({c:rng.normal(size=20) for c in C.V.PHYS});x['nfl_id']=np.arange(20);x['combine_position']='DE';x['target']=np.clip(.1+x[C.V.PHYS[0]]*.01,0,1);x['source']=rng.normal(size=20);return x
    def test_baseline_fallback_exact(self):
        x=self.rows();a=C.predict(x.iloc[:15],x.iloc[15:],[],10,0);b=C.predict(x.iloc[:15],x.iloc[15:],['source'],10,0);np.testing.assert_array_equal(a,b)
    def test_player_overlap(self):
        x=self.rows()
        with self.assertRaises(ValueError):C.predict(x.iloc[:15],x.iloc[14:],['source'],10,2)
    def test_test_cohort_does_not_fit_transform(self):
        x=self.rows();te=x.iloc[15:].copy();a=C.predict(x.iloc[:15],te,['source'],10,2);te.loc[te.index[1:],'source']=1e12;b=C.predict(x.iloc[:15],te,['source'],10,2);self.assertAlmostEqual(a[0],b[0],places=10)
if __name__=='__main__':unittest.main()
