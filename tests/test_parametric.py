import unittest,itertools,random
from fractions import Fraction as Q
from perfectjet.exact import rank
from perfectjet.parametric import (var,const,add,sub,mul,clean,evaluate,groebner,reduce,is_unit_ideal,nonempty,
                                   saturate,rational_points,dimension,divide,rank_cells,classify,drop_locus,
                                   polynomial_matrix,sextic_family,partner_surface)
from perfectjet.loci import partner_loci
from perfectjet.transvectants import gate_matrix

x,y=var(0,2),var(1,2)
one=const(1,2)


def P(*terms):
    out={}
    for c,e in terms:out=add(out,{e:Q(c)})
    return out


class GroebnerTests(unittest.TestCase):
    def test_reduced_basis_is_canonical(self):
        gens=[sub(mul(x,x),y),sub(mul(x,y),one),sub(mul(y,y),x)]
        bases={tuple(tuple(sorted(g.items())) for g in groebner(list(p))) for p in itertools.permutations(gens)}
        self.assertEqual(len(bases),1)
        g=groebner(gens)
        for p in gens:self.assertEqual(reduce(p,g),{})

    def test_membership_and_unit_ideal(self):
        g=groebner([sub(mul(x,x),one),sub(y,x)])
        self.assertEqual(reduce(sub(mul(y,y),one),g),{})
        self.assertNotEqual(reduce(sub(y,one),g),{})
        self.assertTrue(is_unit_ideal(groebner([x,sub(x,one)])))

    def test_nonempty_and_saturation(self):
        self.assertFalse(nonempty([mul(x,y)],[x,y],2))
        self.assertTrue(nonempty([mul(x,y)],[x],2))
        sat=saturate([mul(x,y)],[x],2);self.assertEqual(sat,[y])
        self.assertEqual(dimension(sat,2),1);self.assertEqual(dimension([x,y],2),0)
        self.assertEqual(dimension([],2),2)

    def test_rational_points(self):
        pts=rational_points([sub(mul(x,x),one),sub(y,x)],2)
        self.assertEqual(pts,[(Q(-1),Q(-1)),(Q(1),Q(1))])
        self.assertEqual(rational_points([sub(mul(x,x),const(2,2)),y],2),[])

    def test_exact_division(self):
        p=sub(mul(x,x),mul(y,y));self.assertEqual(divide(p,sub(x,y)),add(x,y))
        self.assertIsNone(divide(add(mul(x,x),one),x))


def rand_poly(rng,deg=1):
    return clean({e:Q(rng.randint(-2,2)) for e in itertools.product(range(deg+1),repeat=2) if sum(e)<=deg})


class CellTests(unittest.TestCase):
    def test_cells_partition_grid_with_correct_rank(self):
        rng=random.Random(71)
        for _ in range(25):
            m,n=rng.randint(1,3),rng.randint(1,3)
            a=[[rand_poly(rng,rng.randint(0,1)) for _ in range(n)] for _ in range(m)]
            cells=rank_cells(a,2)
            for pt in itertools.product(range(-3,4),repeat=2):
                direct=rank([[evaluate(p,pt) for p in row] for row in a])
                self.assertEqual(classify(cells,pt),direct)

    def test_planted_curve_and_point(self):
        # diag(x*y-1, x-2, 1): rank 3 generically, 2 on two curves, 1 at their two meets.
        a=[[sub(mul(x,y),one),{},{}],[{},sub(x,const(2,2)),{}],[{},{},one]]
        r=drop_locus(a,2,["x","y"])
        self.assertEqual(r["generic_rank"],3)
        ranks=sorted(c["rank"] for c in r["drop_cells"]);self.assertIn(1,ranks)
        pt=[c for c in r["drop_cells"] if c["rank"]==1][0]
        self.assertEqual(pt["rational_points"],[(Q(2),Q(1,2))])

    def test_matrix_interpolation(self):
        a=polynomial_matrix(lambda s,t:[[s*t+1,s-t],[t*t,Q(3)]],2,2)
        self.assertEqual(a[0][0],add(mul(x,y),one));self.assertEqual(a[1][0],mul(y,y))


class PartnerSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rows={r["degree"]:r for r in partner_surface(range(3,6))}

    def test_slice_recovers_one_parameter_loci(self):
        one_param={r["degree"]:r for r in partner_loci(range(3,6))}
        for n,row in self.rows.items():
            on_slice={pt[0] for c in row["drop_cells"] for pt in c.get("rational_points",[]) if pt[1]==0}
            self.assertEqual(on_slice,{p["t"] for p in one_param[n]["correction_points"]})

    def test_reported_points_replay(self):
        found=set()
        for n,row in self.rows.items():
            for c in row["drop_cells"]:
                for pt in c.get("rational_points",[]):
                    f=sextic_family(*pt)
                    self.assertEqual(rank(gate_matrix(f,n,3)+gate_matrix(f,n,5)),c["rank"])
                    found.add((n,pt))
        for item in ((3,(Q(0),Q(15))),(4,(Q(0),Q(-5))),(5,(Q(16),Q(-9))),(5,(Q(-16),Q(-9))),(5,(Q(40,7),Q(0)))):
            self.assertIn(item,found)

    def test_degree_three_curve(self):
        curve=[c for c in self.rows[3]["drop_cells"] if c["dimension"]==1]
        self.assertEqual(len(curve),1);self.assertEqual(curve[0]["rank"],3)

    def test_exceptional_factorizations(self):
        from perfectjet.parametric import exceptional_factorizations
        self.assertTrue(all(r["factorization_verified"] for r in exceptional_factorizations()))

    def test_grid_classification(self):
        for n in (3,5):
            gates=polynomial_matrix(lambda a,b:gate_matrix(sextic_family(a,b),n,3)+gate_matrix(sextic_family(a,b),n,5),2,1)
            cells=rank_cells(gates,2)
            for pt in itertools.product(range(-3,4),repeat=2):
                f=sextic_family(*pt)
                self.assertEqual(classify(cells,pt),rank(gate_matrix(f,n,3)+gate_matrix(f,n,5)))


if __name__=='__main__':unittest.main()
