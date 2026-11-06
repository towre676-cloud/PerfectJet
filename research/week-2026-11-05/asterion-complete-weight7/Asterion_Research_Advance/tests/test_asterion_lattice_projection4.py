"""Compare four-current output projections with original full mode evaluation."""
from fractions import Fraction as Q
import unittest
from perfectjet.asterion_primitives import JetAlgebra, LatticeE8VOA, THETA
from perfectjet.asterion_lattice_projection4 import ProjectedLatticeE8VOA4


class FourCurrentProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.j=JetAlgebra(); cls.full=LatticeE8VOA(cls.j)
        cls.projected=ProjectedLatticeE8VOA4(cls.j)

    def check_word(self,word):
        expected={k:z for k,z in self.full.word(word).items()
                  if all(i in self.projected.support for _,i in k[1])}
        actual={k:Q(z,self.projected.SCALE**len(word))
                for k,z in self.projected._projected_word(word)}
        self.assertEqual(actual,expected)

    def test_four_roots_modes_through_weight_seven(self):
        j=self.j; u=j.algebra.root_index[THETA]; v=j.opposite[u]
        a=j.simple[0]; b=j.opposite[a]
        for indices in ((u,v,u,v),(u,a,v,b),(a,b,u,v)):
            for modes in ((1,1,1,1),(1,1,1,4),(1,1,2,3),(1,2,2,2)):
                with self.subTest(indices=indices,modes=modes):
                    self.check_word(tuple(zip(modes,indices)))

    def test_mixed_cartan_root_commutators(self):
        j=self.j;u=j.algebra.root_index[THETA];v=j.opposite[u]
        for word in (((1,u),(2,3),(1,v),(3,0)),
                     ((1,u),(1,v),(2,j.simple[1]),(3,1)),
                     ((2,0),(1,u),(1,v),(3,1))):
            self.check_word(word)

    def test_nonzero_charge_and_cache_reuse(self):
        j=self.j; roots=list(j.algebra.root_index)
        a=THETA
        b=next(b for b in roots if tuple(x+y for x,y in zip(a,b)) in j.algebra.root_index)
        c=tuple(-x-y for x,y in zip(a,b))
        for quartet in ((a,b,c,a),(b,a,c,b),(c,b,a,c)):
            indices=[j.algebra.root_index[r] for r in quartet]
            for modes in ((1,1,1,1),(1,1,2,3)):
                self.check_word(tuple(zip(modes,indices)))

    def test_symmetric_lift_matches_full_output_projection(self):
        j=self.j;u=j.algebra.root_index[THETA];v=j.opposite[u]
        for mono in (((u,0),(v,0),(u,0),(v,3)),
                     ((u,0),(v,1),(0,0),(1,2))):
            p={tuple(sorted(mono)):Q(3,7)}
            expected={k:z for k,z in self.full.symmetric_lift(p).items()
                      if all(i in self.projected.support for _,i in k[1])}
            self.assertEqual(self.projected.symmetric_lift(p),expected)

    def test_output_supports_and_weight_bound(self):
        j=self.j;u=j.algebra.root_index[THETA];v=j.opposite[u]
        word=((1,u),(1,v),(1,u),(4,v))
        for support in ((0,),(1,3),(0,1,2)):
            projected=ProjectedLatticeE8VOA4(j,support=support)
            expected={k:z for k,z in self.full.word(word).items()
                      if all(i in support for _,i in k[1])}
            actual={k:Q(z,projected.SCALE**4) for k,z in projected._projected_word(word)}
            self.assertEqual(actual,expected)
        bounded=ProjectedLatticeE8VOA4(j,maximum_weight=2)
        with self.assertRaises(ValueError):bounded._projected_word(word)

if __name__=='__main__':unittest.main()
