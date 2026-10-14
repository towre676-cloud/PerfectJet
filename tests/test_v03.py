import unittest,itertools,random
from fractions import Fraction as Q
from perfectjet.exact import rank,matmul
from perfectjet.lattice import hermite_form,same_lattice,integer_solve,smith_form,invariant_factors
from perfectjet.realization import LinearRepresentation,realize,held_out
from perfectjet.loci import (trim,pmul,padd,pdivmod,pgcd,squarefree,evaluate,interpolate,monic,
                             generic_rank,rank_locus,rational_roots,polynomial_matrix,partner_loci)
from perfectjet.transvectants import partner_dimensions,c3_family
from perfectjet.sieve import (adaptive_sieve,allowed_residues,hits,sieved_hits,exclusion_witness,
                              integer_root,poly_value)


def unimodular(rng,n):
    w=[[int(i==j) for j in range(n)] for i in range(n)]
    for _ in range(3*n):
        i,j=rng.sample(range(n),2) if n>1 else (0,0)
        if i!=j:
            k=rng.randint(-2,2);w[i]=[x+k*y for x,y in zip(w[i],w[j])]
    return w


class HermiteTests(unittest.TestCase):
    def test_shape_and_transform(self):
        rng=random.Random(31)
        for _ in range(60):
            m,n=rng.randint(1,4),rng.randint(1,4);a=[[rng.randint(-6,6) for _ in range(n)] for _ in range(m)]
            u,h,piv=hermite_form(a)
            self.assertEqual(matmul(u,a),[[Q(x) for x in r] for r in h])
            self.assertEqual(len(piv),rank(a))
            for r,c in enumerate(piv):
                self.assertGreater(h[r][c],0)
                self.assertTrue(all(h[i][c]==0 for i in range(r+1,m)))
                self.assertTrue(all(0<=h[i][c]<h[r][c] for i in range(r)))
                self.assertTrue(all(h[r][j]==0 for j in range(c)))
            self.assertTrue(all(not any(h[i]) for i in range(len(piv),m)))

    def test_uniqueness_under_unimodular_mixing(self):
        rng=random.Random(37)
        for _ in range(40):
            m,n=rng.randint(1,4),rng.randint(1,4);a=[[rng.randint(-5,5) for _ in range(n)] for _ in range(m)]
            w=unimodular(rng,m)
            self.assertEqual(hermite_form(a)[1],hermite_form([[int(x) for x in r] for r in matmul(w,a)])[1])

    def test_lattice_equality_matches_membership(self):
        rng=random.Random(41)
        for _ in range(40):
            a=[[rng.randint(-3,3) for _ in range(3)] for _ in range(2)]
            b=[[rng.randint(-3,3) for _ in range(3)] for _ in range(2)]
            contains=lambda big,small:all(integer_solve([list(c) for c in zip(*big)],r)['solvable'] for r in small)
            self.assertEqual(same_lattice(a,b),contains(a,b) and contains(b,a))
        self.assertTrue(same_lattice([[2,0],[0,1]],[[2,1],[0,1]]))
        self.assertFalse(same_lattice([[2,0],[0,1]],[[1,0],[0,1]]))

    def test_square_determinant(self):
        rng=random.Random(43)
        for _ in range(30):
            a=[[rng.randint(-4,4) for _ in range(3)] for _ in range(3)]
            h=hermite_form(a)[1];prod=1
            for i in range(3):prod*=h[i][i]
            f=invariant_factors(a);fp=1
            for x in f:fp*=x
            if len(f)==3:self.assertEqual(prod,fp)  # both equal |det A|
            else:self.assertTrue(any(h[i][i]==0 for i in range(3)) or len(hermite_form(a)[2])<3)


class MultiOutputTests(unittest.TestCase):
    def test_shared_state_is_smaller_than_separate_models(self):
        # Two outputs reading one three-state system; each alone may need fewer states.
        rng=random.Random(47);r=lambda:Q(rng.randint(-3,3),rng.randint(1,2))
        acts=[[[r() for _ in range(3)] for _ in range(3)] for _ in range(2)]
        alpha=[r() for _ in range(3)];beta=[[r(),r()] for _ in range(3)]
        sys=LinearRepresentation(alpha,acts,beta)
        model,info=realize(sys,2,3,outputs=2)
        self.assertEqual(info['rank'],3);self.assertIsNone(held_out(model,sys,2,6))
        for j in range(2):
            single,sinfo=realize(lambda w,j=j:sys(w)[j],2,3)
            self.assertLessEqual(sinfo['rank'],info['rank'])

    def test_stacked_rank_exceeds_each_output(self):
        f=lambda w:(Q(len(w)),Q(2)**len(w))
        model,info=realize(f,1,4,outputs=2)
        self.assertEqual(info['rank'],3)
        self.assertEqual(realize(lambda w:f(w)[0],1,4)[1]['rank'],2)
        self.assertEqual(realize(lambda w:f(w)[1],1,4)[1]['rank'],1)
        self.assertIsNone(held_out(model,f,1,20))

    def test_zero_vector(self):
        model,info=realize(lambda w:(0,0),2,1,outputs=2)
        self.assertEqual(info['rank'],0);self.assertEqual(model((1,0)),(0,0))


def all_minor_gcd(a,r):
    g=[]
    for rows in itertools.combinations(range(len(a)),r):
        for cols in itertools.combinations(range(len(a[0])),r):
            d=max(len(a[i][j]) for i in rows for j in cols)*r
            xs=list(range(d+1))
            def det(x):
                m=[[evaluate(a[i][j],Q(x)) for j in cols] for i in rows]
                from perfectjet.loci import _det
                return _det(m)
            g=pgcd(g,interpolate(xs,[det(x) for x in xs])) if g else monic(interpolate(xs,[det(x) for x in xs]))
    return g


class LociTests(unittest.TestCase):
    def test_polynomial_arithmetic(self):
        a,b=[Q(1),Q(2),Q(3)],[Q(-1),Q(1)]
        q,r=pdivmod(pmul(a,b),b);self.assertEqual(q,a);self.assertEqual(r,[])
        self.assertEqual(pgcd(pmul(a,b),pmul(b,b)),monic(b))
        self.assertEqual(squarefree(pmul(pmul(b,b),a)),monic(pmul(b,a)))
        xs=[0,1,2,5];p=[Q(3),Q(-1),Q(0),Q(2,3)]
        self.assertEqual(interpolate(xs,[evaluate(p,x) for x in xs]),p)
        self.assertEqual(rational_roots(pmul([Q(-40),Q(7)],[Q(2),Q(0),Q(1)])),[Q(40,7)])

    def test_planted_locus(self):
        rng=random.Random(53)
        for _ in range(12):
            a_,b_=Q(rng.randint(-5,5)),Q(rng.randint(-5,5),rng.randint(1,4))
            diag=[[-a_,Q(1)],pmul([-b_,Q(1)],[Q(-2),Q(0),Q(1)]),[Q(1)],[]]
            p,qm=unimodular(rng,4),unimodular(rng,4)
            a=[[trim([]) for _ in range(4)] for _ in range(4)]
            for i in range(4):
                for j in range(4):
                    for k in range(4):a[i][j]=padd(a[i][j],pmul([Q(p[i][k]*qm[k][j])],diag[k]))
            r=rank_locus(a);self.assertEqual(r['generic_rank'],3)
            self.assertEqual(r['locus'],monic(squarefree(pmul(pmul([-a_,Q(1)],[-b_,Q(1)]),[Q(-2),Q(0),Q(1)]))))
            self.assertEqual({x['t'] for x in r['rational_points']},{a_,b_})
            self.assertEqual(r['locus'],squarefree(all_minor_gcd(a,3)))

    def test_random_against_all_minors(self):
        rng=random.Random(59)
        for _ in range(15):
            m,n=rng.randint(2,3),rng.randint(2,3)
            a=[[trim([Q(rng.randint(-2,2)) for _ in range(rng.randint(1,3))]) for _ in range(n)] for _ in range(m)]
            r=rank_locus(a)
            if r['generic_rank']==0:continue
            self.assertEqual(r['locus'],squarefree(all_minor_gcd(a,r['generic_rank'])))
            for x in range(-6,7):
                low=rank([[evaluate(p,Q(x)) for p in row] for row in a])<r['generic_rank']
                self.assertEqual(low,evaluate(r['locus'],Q(x))==0)

    def test_partner_family_rediscovers_40_over_7(self):
        rows={r['degree']:r for r in partner_loci(range(3,7))}
        self.assertEqual(rows[5]['correction_locus'],[Q(-1600,49),Q(0),Q(1)])
        self.assertEqual([p['t'] for p in rows[5]['correction_points']],[Q(-40,7),Q(40,7)])
        self.assertEqual([p['t'] for p in rows[3]['correction_points']],[Q(-20),Q(0),Q(20)])
        for n,row in rows.items():
            for p in row['correction_points']:
                d=partner_dimensions(c3_family(p['t'])[0],n)
                self.assertEqual(d['kernel_dimension'],n+1-p['rank'])
            for t in (Q(1),Q(3,2)):
                d=partner_dimensions(c3_family(t)[0],n)
                self.assertEqual(d['active_dimension'],row['generic_active_dimension'])


class SieveTests(unittest.TestCase):
    def test_integer_root(self):
        for d in (2,3,5):
            for m in range(-30,31):
                v=m**d
                if v<0 and d%2==0:continue
                self.assertEqual(integer_root(v,d),m if d%2 else abs(m))
                if v>1:self.assertIsNone(integer_root(v+1,d))
        self.assertEqual(integer_root(10**200,2),10**100)

    def test_soundness_and_exact_count(self):
        rng=random.Random(61)
        for _ in range(12):
            coeffs=[rng.randint(-9,9) for _ in range(rng.randint(2,4))];coeffs[-1]=coeffs[-1] or 1
            d=rng.choice((2,3))
            s=adaptive_sieve(coeffs,d,range(2,24),max_modulus=5000)
            truth=hits(coeffs,d,600);found,tested=sieved_hits(coeffs,d,600,s)
            self.assertEqual(found,truth);self.assertLessEqual(tested,600)
            for n,_ in truth:self.assertIsNone(exclusion_witness(coeffs,d,n,[x['modulus'] for x in s['steps']]))

    def test_order_independence(self):
        coeffs,d=[3,0,0,1],2;mods=[4,3,5,7,8,9]
        sets=[]
        for perm in itertools.permutations(mods[:4]):
            sets.append(frozenset(n for n in range(1,500) if exclusion_witness(coeffs,d,n,perm) is None))
        self.assertEqual(len(set(sets)),1)

    def test_identity_excludes_nothing(self):
        s=adaptive_sieve([1,2,1],2,range(2,30))
        self.assertEqual(s['density'],1);self.assertEqual(s['steps'],[])

    def test_density_strictly_decreases(self):
        s=adaptive_sieve([-7,0,2],2,range(2,30))
        ds=[x['density_after'] for x in s['steps']]
        self.assertTrue(all(a>b for a,b in zip(ds,ds[1:])))
        self.assertEqual(s['density'],ds[-1])


if __name__=='__main__':unittest.main()
