import unittest,itertools,random
from fractions import Fraction as Q
from perfectjet.exact import rank,nullspace,target_recovery,observable_space,hankel
from perfectjet.polynomial import Poly,feature_closure
from perfectjet.transvectants import transvectant,c3_family,partner_dimensions
from perfectjet.rings import QuotientRing,cyclotomic,core_field_receipt
from perfectjet.collision import CyclotomicCollision,kappa,valuation_rbf,divisor_rank_polynomial
from perfectjet.populations import SelectionPopulation,weighted_quotient_replay,histogram_partition
from perfectjet.semantics import PartialMachine
from perfectjet.dynamics import energy_balance,reduction_defect,contraction_error,certified_best
from perfectjet.jets import iterate_defect,riccati_residual
from perfectjet.psg import flip_root


class ExactLinearTests(unittest.TestCase):
    def test_nullspace_annihilation(self):
        for a in ([[1,2,3],[2,4,6]],[[1,0,1],[0,1,2]],[[0,0,0]]):
            ns=nullspace(a)
            self.assertEqual(len(ns)+rank(a),3)
            for v in ns:self.assertTrue(all(sum(x*y for x,y in zip(row,v))==0 for row in a))

    def test_target_witness_and_repair(self):
        r=target_recovery([[1,1]],[[1,-1]])
        self.assertFalse(r['recoverable']);self.assertNotEqual(r['target_response'],[0])
        self.assertTrue(target_recovery([[1,1],[1,-1]],[[1,-1]])['recoverable'])

    def test_observable_closure(self):
        self.assertEqual(len(observable_space([[1,1],[0,1]],[[1,0]])),2)
        self.assertEqual(len(observable_space([[1,0],[0,2]],[[1,0]])),1)

    def test_hankel_sequence_ranks(self):
        fib=[0,1]
        for _ in range(12):fib.append(fib[-1]+fib[-2])
        self.assertEqual(rank(hankel(fib,5,5)),2)
        self.assertEqual(rank(hankel([2**n for n in range(12)],5,5)),1)


class AlgebraTests(unittest.TestCase):
    def test_feature_exact_evolution(self):
        x=Poly.variable(0,1)
        r=feature_closure([Poly.constant(1,1),x],[2*x+1])
        self.assertTrue(r['closed']);self.assertEqual(r['transition'],[[1,0],[1,2]])
        for initial in range(-3,4):
            state=initial
            for _ in range(6):state=2*state+1
            self.assertEqual(state,2**6*initial+2**6-1)

    def test_unclosed_and_repaired_features(self):
        x,y=Poly.variable(0),Poly.variable(1)
        self.assertFalse(feature_closure([x],[x*x,y])['closed'])
        self.assertTrue(feature_closure([x,y,y*y],[x+y*y,y])['closed'])

    def test_molecular_parameter_identity(self):
        x,y=Poly.variable(0),Poly.variable(1)
        # Degree <=2 in lambda: three exact evaluations establish both gate identities.
        for lam in (Q(0),Q(1),Q(-3,2),Q(40,7)):
            f,h,g=c3_family(lam)
            self.assertEqual(transvectant(f,g,3),0);self.assertEqual(transvectant(f,g,5),0)
            self.assertNotEqual(transvectant(f,g,1),0)
            self.assertEqual(transvectant(f,h,3),72*(7*lam-40)*(x**4*y+x*y**4))
            self.assertEqual(transvectant(f,h,5),0)

    def test_quantum_cubic_obstruction(self):
        x,y=Poly.variable(0),Poly.variable(1)
        self.assertEqual(transvectant(x**3,y**3,3),36)
        self.assertEqual(transvectant(x**2,y**2,3),0)

    def test_exceptional_factor(self):
        x,y=Poly.variable(0),Poly.variable(1);f,h,g=c3_family(Q(40,7))
        self.assertEqual(g,(x**3-y**3)*h)

    def test_trivial_vs_active(self):
        f,_,_=c3_family(1)
        self.assertEqual(partner_dimensions(f,6),{'degree':6,'kernel_dimension':1,'active_dimension':0})
        self.assertEqual(partner_dimensions(f,5)['active_dimension'],0)
        self.assertEqual(partner_dimensions(c3_family(Q(40,7))[0],5)['active_dimension'],1)

    def test_archived_squarefree_pair(self):
        x,y=Poly.variable(0),Poly.variable(1)
        g=-x*y*(x-y)*(x*x-x*y+y*y)
        f=Q(1,2)*(2*x**6-6*x**5*y+5*x**4*y*y+5*x*x*y**4-6*x*y**5+2*y**6)
        self.assertEqual(transvectant(f,g,3),0);self.assertEqual(transvectant(f,g,5),0)
        self.assertNotEqual(transvectant(f,g,1),0)

    def test_field_replay(self):
        r=core_field_receipt()
        for key in ('alpha_polynomial_zero','plastic_polynomial_zero','hessian_identity_zero','vertex_identity_zero'):
            self.assertTrue(r[key])

    def test_quotient_inverse_and_nonunit(self):
        r=QuotientRing([-1,5,-4,1]);u=r.generator
        for z in (u,u-1,u*u+2):self.assertEqual(z*z.inverse(),1)
        with self.assertRaises(ZeroDivisionError):r.zero.inverse()
        s=QuotientRing([-1,0,1])
        with self.assertRaises(ZeroDivisionError):(s.generator-1).inverse()


class CollisionTests(unittest.TestCase):
    def test_cyclotomic_primitive_roots(self):
        for n in range(1,21):
            r=QuotientRing(cyclotomic(n));z=r.generator
            self.assertEqual(z**n,1)
            for d in range(1,n):
                if n%d==0:self.assertNotEqual(z**d,1)

    def test_affine_periodic_coefficients(self):
        for L in range(2,13):
            c=CyclotomicCollision(L)
            for n in range(5*L):
                self.assertEqual(c.coefficient(n),c.direct(n))
                self.assertEqual(c.coefficient(n+2*L)-2*c.coefficient(n+L)+c.coefficient(n),0)

    def test_numerator_series_convolution(self):
        for L in range(2,10):
            c=CyclotomicCollision(L);num=c.numerator()
            for n in range(4*L):
                expected=c.ring.zero
                for j in range(n//L+1):
                    k=n-j*L
                    if k<len(num):expected+=(j+1)*num[k]
                self.assertEqual(expected,c.coefficient(n))
            self.assertEqual(sum(num,c.ring.zero),L)
            self.assertEqual(num[0],1);self.assertEqual(num[-1],c.zeta)

    def test_large_index_recurrence(self):
        c=CyclotomicCollision(7);n=10**100
        self.assertEqual(c.coefficient(n+7)-c.coefficient(n),c.gauss[n%7])

    def test_coprimality_and_bilinearity(self):
        from math import gcd
        for m in range(1,40):
            for n in range(1,40):self.assertEqual(kappa(m,n)==0,gcd(m,n)==1)
        self.assertEqual(kappa(72,108),12)
        self.assertEqual(kappa(12*7,18),kappa(12,18)+kappa(7,18))

    def test_divisor_population(self):
        self.assertEqual(sum(divisor_rank_polynomial(12))*sum(divisor_rank_polynomial(18))-sum(divisor_rank_polynomial(216)),20)

    def test_rbf_geometry(self):
        self.assertEqual(valuation_rbf(12,12),1)
        self.assertEqual(valuation_rbf(12,18),valuation_rbf(18,12))
        self.assertLess(valuation_rbf(12,18),1)


class PopulationTests(unittest.TestCase):
    def test_exhaustive_counts_ranks_and_ties(self):
        rng=random.Random(421)
        for _ in range(15):
            costs=[(rng.randrange(4),rng.randrange(4)) for _ in range(7)]
            caps=(rng.randrange(8),rng.randrange(8));profits=[rng.randrange(-2,6) for _ in costs]
            p=SelectionPopulation(costs,caps,profits)
            feasible=[bits for bits in itertools.product((0,1),repeat=7)
                      if all(sum(b*c[j] for b,c in zip(bits,costs))<=caps[j] for j in range(2))]
            self.assertEqual(p.count(),len(feasible))
            for i,b in enumerate(feasible):self.assertEqual(p.rank(b),i);self.assertEqual(p.unrank(i),b)
            scores=[sum(b*v for b,v in zip(bits,profits)) for bits in feasible]
            self.assertEqual(p.optimum(),{'value':max(scores),'tie_count':scores.count(max(scores))})

    def test_zero_cost_multiplicity(self):
        p=SelectionPopulation([(0,),(0,),(0,)],(0,),[0,0,0])
        self.assertEqual(p.count(),8);self.assertEqual(p.optimum()['tie_count'],8)

    def test_conditional_counts(self):
        p=SelectionPopulation([(2,),(3,),(1,)],(3,))
        self.assertEqual(p.count(),p.conditional_count([0])+p.conditional_count([1]))
        self.assertEqual(p.conditional_count([1,1]),0)

    def test_weighted_aggregation(self):
        self.assertTrue(weighted_quotient_replay([[1,2],[0,1]],[[1,0],[0,1]],[[1,2],[0,1]]))
        self.assertFalse(weighted_quotient_replay([[1,0],[0,2]],[[1,1]],[[1]]))
        self.assertTrue(weighted_quotient_replay([[1,0],[0,1]],[[1,1]],[[1]]))

    def test_histogram(self):
        self.assertEqual(histogram_partition({(1,0):2,(0,1):3},[Q(1,2),Q(1,3)]),2)


class SemanticsDynamicsTests(unittest.TestCase):
    def test_partial_definedness_witness(self):
        m=PartialMachine([0,0],[(None,),(1,)])
        w=m.distinguish(0,1);self.assertEqual(w,(0,));self.assertNotEqual(m.behavior(0,w),m.behavior(1,w))

    def test_quotient_future_equivalence(self):
        m=PartialMachine([0,0,1,1],[(2,),(3,),(2,),(3,)])
        r,q,blocks=m.quotient();self.assertEqual(blocks,[[0,1],[2,3]])
        for s in range(4):
            for length in range(6):self.assertEqual(m.behavior(s,(0,)*length),r.behavior(q[s],(0,)*length))

    def test_energy_source_sign(self):
        r=energy_balance([[-2]],[[3]],[2],[1])
        self.assertEqual(r['energy'],6);self.assertEqual(r['energy_derivative'],-18)
        self.assertEqual(r['lambda'],4);self.assertEqual(r['zeta'],1);self.assertEqual(r['rho'],Q(3,4))

    def test_energy_zero_dial_and_invalid_mass(self):
        self.assertIsNone(energy_balance([[0]],[[1]],[1])['rho'])
        with self.assertRaises(ValueError):energy_balance([[-1]],[[0]],[1])

    def test_defect_recursion(self):
        R,S=reduction_defect([[1,1],[0,2]],[[0],[1]],[[1],[0]],[[1]],[[0]])
        self.assertEqual(R,[[0],[0]]);self.assertEqual(S,[[0],[1]])
        self.assertEqual(contraction_error(Q(1,2),1,[1,1,1]),Q(15,8))

    def test_decision_margins(self):
        self.assertEqual(certified_best([10,6],[1,1]),0)
        self.assertIsNone(certified_best([10,9],[1,1]))

    def test_flip_obstruction(self):
        for a,b in ((0,1),(1,2),(Q(1,2),Q(-1,4))):
            d=iterate_defect([0,-1,a,b],3)
            self.assertEqual(d[:3],[0,0,0]);self.assertEqual(d[3],-2*(b+a*a))

    def test_riccati_rejection(self):
        # I=1/(1-t) solves I'=I^2.
        self.assertEqual(riccati_residual([1]*8,0,0,1),[0]*7)
        self.assertNotEqual(riccati_residual([1]*7+[2],0,0,1)[-1],0)

    def test_psg_corrected_reduction(self):
        r=flip_root();self.assertAlmostEqual(r['alpha'],.7418045150878947,places=14)
        self.assertLess(abs(r['fixed_residual']),1e-14);self.assertLess(abs(r['F']),1e-14)
        self.assertAlmostEqual(r['multiplier'],-1,places=14)


if __name__=='__main__':unittest.main()
