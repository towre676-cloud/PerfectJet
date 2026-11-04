"""Output projection must equal projecting the FULL established evaluator."""
from fractions import Fraction as Q
import unittest
from perfectjet.asterion_primitives import JetAlgebra, LatticeE8VOA, THETA, ZERO
from perfectjet.asterion_lattice_projection import ProjectedLatticeE8VOA


class ProjectionTests(unittest.TestCase):
    def test_outer_projection_keeps_intermediate_oscillators(self):
        j=JetAlgebra(); full=LatticeE8VOA(j); projected=ProjectedLatticeE8VOA(j)
        u=j.algebra.root_index[THETA]; v=j.opposite[u]
        samples=[((u,0),(v,0)), ((u,0),(v,1),(3,0)),
                 ((u,0),(v,3),(2,1)), ((0,0),(1,2),(0,2)),
                 ((u,1),(v,1),(4,2))]
        for mono in samples:
            polynomial={tuple(sorted(mono)):Q(3,7)}
            expected={k:z for k,z in full.symmetric_lift(polynomial).items()
                      if all(i in projected.support for _,i in k[1])}
            self.assertEqual(projected.symmetric_lift(polynomial),expected)
        full.clear_cache(); projected.clear_cache()

    def test_three_root_generating_function_against_original_modes(self):
        j=JetAlgebra(); full=LatticeE8VOA(j); projected=ProjectedLatticeE8VOA(j)
        roots=list(j.algebra.root_index)
        a=THETA
        b=next(b for b in roots if tuple(x+y for x,y in zip(a,b)) in j.algebra.root_index)
        c=tuple(-x-y for x,y in zip(a,b))
        triples=[(a,b,c),(a,tuple(-x for x in a),a),(b,a,c)]
        for triple in triples:
            indices=[j.algebra.root_index[r] for r in triple]
            for modes in ((1,1,5),(1,2,4),(1,3,3),(2,2,3)):
                word=tuple(zip(modes,indices))
                expected={k:z for k,z in full.word(word).items()
                          if all(i in projected.support for _,i in k[1])}
                actual={k:Q(z,projected.SCALE**3) for k,z in projected._three_root_word(word)}
                self.assertEqual(actual,expected)

    def test_root_product_cache_across_distinct_full_lattice_weights(self):
        j=JetAlgebra();full=LatticeE8VOA(j);projected=ProjectedLatticeE8VOA(j)
        roots=list(j.algebra.root_index)
        for a in roots[::9]:
            i=j.algebra.root_index[a];op=j.opposite[i]
            for last in (i,j.simple[0]):
                word=((1,i),(1,op),(1,last))
                expected={k:z for k,z in full.word(word).items()
                          if all(q in projected.support for _,q in k[1])}
                actual={k:Q(z,projected.SCALE**3) for k,z in projected._projected_word(word)}
                self.assertEqual(actual,expected)

    def test_support_validation(self):
        for support in ((),(-1,),(8,)):
            with self.assertRaises(ValueError):
                ProjectedLatticeE8VOA(support=support)


if __name__=='__main__':
    unittest.main()
