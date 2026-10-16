from fractions import Fraction as Q
import unittest

from perfectjet.categorical import (
    cyclic_cocycle_phase, cyclic_invariant, extension_cochain_phase,
    extension_coboundary_phase, cyclic_repair, rank_one_projector,
    sector_reach, generated_algebra_dimension, receipt,
)


class CyclicRepairTests(unittest.TestCase):
    def test_source_obstruction_is_real(self):
        self.assertEqual(cyclic_invariant(5,2),Q(2,5))
        self.assertEqual(cyclic_invariant(5,0),0)
        self.assertEqual(cyclic_invariant(5,5),0)
        # The zero cochain cannot repair this nonzero source phase.
        self.assertNotEqual(cyclic_cocycle_phase(5,1,1,4,1),0)

    def test_cocycle_identity_independently(self):
        for n in range(2,5):
            for k in range(n):
                w=lambda a,b,c:cyclic_cocycle_phase(n,k,a,b,c)
                for a in range(n):
                    for b in range(n):
                        for c in range(n):
                            for d in range(n):
                                self.assertEqual((w(b,c,d)-w(a+b,c,d)+w(a,b+c,d)
                                                  -w(a,b,c+d)+w(a,b,c)) % 1,0)

    def test_explicit_cochain_repairs_every_triple(self):
        for n in range(2,5):
            for k in range(n):
                row=cyclic_repair(n,k)
                self.assertTrue(row['verified'])
                self.assertEqual(row['triples_checked'],n**6)
                for a,b,c in ((1,n-1,1),(n+1,n*n-1,1),(n*n-1,n*n-1,n*n-1)):
                    self.assertEqual(extension_coboundary_phase(n,k,a,b,c),
                                     cyclic_cocycle_phase(n,k,a,b,c))

    def test_group_periodicity_and_no_hidden_large_replay(self):
        self.assertEqual(extension_cochain_phase(3,1,1,4),
                         extension_cochain_phase(3,1,10,13))
        with self.assertRaises(ValueError):
            cyclic_repair(20,1,max_triples=100)
        with self.assertRaises(ValueError):
            cyclic_cocycle_phase(0,1,0,0,0)


class SectorReachTests(unittest.TestCase):
    def test_prediction_matches_independent_full_algebra_closure(self):
        for vector,dimension,full in [([1,0,0,0,0,0],14,False),
                                      ([1,1,1,0,0,0],18,False),
                                      ([1,1,1,1,1,1],36,True)]:
            row=sector_reach([1,2,3],rank_one_projector(vector),verify_algebra=True,
                             max_dimension=6)
            self.assertEqual(row['generated_algebra_dimension'],dimension)
            self.assertEqual(row['replayed_algebra_dimension'],dimension)
            self.assertTrue(row['algebra_dimension_matches'])
            self.assertEqual(row['full_matrix_algebra'],full)

    def test_static_block_projector_adds_nothing(self):
        p=[[Q(i==j and i<2) for j in range(4)] for i in range(4)]
        row=sector_reach([2,2],p)
        self.assertEqual(row['sector_edges'],[])
        self.assertEqual(row['generated_algebra_dimension'],8)

    def test_nonprojectors_and_nonsymmetric_matrices_rejected(self):
        for p in ([[1,1],[0,0]],[[1,1],[1,1]]):
            with self.assertRaises(ValueError):
                sector_reach([1,1],p)
        with self.assertRaises(ValueError):
            rank_one_projector([0,0])
        with self.assertRaises(ValueError):
            generated_algebra_dimension([2],[[1,0],[0,1]],max_products=1)

    def test_receipt_is_json_serializable(self):
        import json
        self.assertIn('cyclic_repairs',json.loads(json.dumps(receipt())))


if __name__=='__main__':
    unittest.main()
