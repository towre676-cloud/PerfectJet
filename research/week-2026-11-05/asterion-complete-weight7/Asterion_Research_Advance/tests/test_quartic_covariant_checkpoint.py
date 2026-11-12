"""Independent ranks, exact coupling identities, and source-character gates."""
import json
from pathlib import Path
from fractions import Fraction as Q
import random
import unittest
from quartic_adjoint_ideal import J,add,scale,bracket,form,covariants,samples
from quartic_3875_ideal import covariants as rcov,triple,flatten,probe_functional,probes,sym
from verify_quartic_small_matrices import bareiss_rank,decode,dense,combination
from perfectjet.asterion_primitives import _f_q,decode_polynomial,load_certificates

ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text())
def peval(poly,jets):
    values={(i,r):form({i:1},v) for r,v in enumerate(jets) for i in range(248)}
    out=Q(0)
    for monomial,c in poly.items():
        z=c
        for variable in monomial:z*=values[variable]
        out+=z
    return out

class CovariantCheckpointTests(unittest.TestCase):
    def test_character_counts_exhaust_both_complete_covariant_spaces(self):
        r=read('quartic_schur_receipt.json')['Schur_components']
        def m(p,d):return sum(x['multiplicity'] for x in r[p]['irreducibles'] if x['dimension']==d)
        for d,n,pn in ((248,11,7),(3875,15,9)):
            self.assertEqual(3*m('4',d)+4*m('31',d)+m('22',d)+m('211',d),n)
            self.assertEqual(m('4',d)+2*m('31',d)+m('22',d)+m('211',d),pn)

    def test_integer_ranks_and_all_coordinate_identities(self):
        for sector,n,pn,rank in (('adjoint',11,7,9),('3875',15,9,13)):
            r=read(f'quartic_{sector}_ideal_receipt.json')
            source=decode(r['ambient_evaluation_columns' if sector=='adjoint' else 'source_evaluation_columns'])
            pairs=decode(r['pair_covariant_evaluation_columns' if sector=='adjoint' else 'pair_evaluation_columns'])
            images=decode(r['ideal_evaluation_columns'])
            self.assertEqual(bareiss_rank(dense(source)),n)
            self.assertEqual(bareiss_rank(dense(pairs)),pn)
            self.assertEqual(bareiss_rank(r['ideal_coordinate_matrix']),rank)
            self.assertEqual(bareiss_rank(dense(images)),rank)
            for c,v in zip(r['ideal_coordinate_matrix'],images):
                self.assertEqual(combination(c,source),{k:z for k,z in v.items() if z})

    def test_products_exhaust_each_arc_quotient(self):
        for sector,n in (('adjoint',11),('3875',15)):
            ideal=read(f'quartic_{sector}_ideal_receipt.json')['ideal_coordinate_matrix']
            products=read(f'quartic_{sector}_products_receipt.json')['product_coordinate_vectors']
            self.assertEqual(bareiss_rank(ideal+products),n)
        s=read('quartic_singlet_ideal_receipt.json')
        self.assertEqual(bareiss_rank(s['ideal_coordinate_matrix']),4)
        self.assertEqual(bareiss_rank(s['ideal_coordinate_matrix']+[['0','-8','8','-4','0']]),5)

    def test_actual_FQ_and_P248_coordinate_free_formulas(self):
        rng=random.Random(4242)
        densepoints=tuple({i:rng.choice((-2,-1,1,2)) for i in range(248)} for _ in range(3))
        x,y,z=densepoints
        module,fq=_f_q(J)
        quadratic=module.highest_quadratic_3875()
        xy=bracket(x,y)
        qpolar=sum(c*(form({i:1},x)*form({j:1},xy)+form({j:1},x)*form({i:1},xy))/2
                   for (i,j),c in quadratic.items())
        actual=peval(fq,(x,y))
        self.assertNotEqual(actual,0)
        self.assertEqual(actual,2*qpolar)
        p=decode_polynomial(load_certificates()['sectors']['w5-248']['representatives'][0]['symbol'])
        pv=add(add(scale(x,20*form(x,z)),x,-21*form(y,y)),y,-12*form(x,y))
        value=peval(p,densepoints)
        self.assertNotEqual(value,0)
        self.assertEqual(value,form({247:1},pv))

    def test_adjoint_product_vector_formulas(self):
        for x,y,z,w in samples(3):
            pv=add(add(scale(x,20*form(x,z)),x,-21*form(y,y)),y,-12*form(x,y))
            self.assertEqual(bracket(y,pv),add(scale(covariants(x,y,z)[2],-20),bracket(y,x),-21*form(y,y)))
            a=covariants(x,y,z)
            lhs=add(add(scale(x,2*form(bracket(x,y),z)),bracket(x,y),2*form(x,z)),
                    bracket(x,bracket(bracket(x,y),z)))
            lhs=add(lhs,bracket(bracket(x,y),bracket(x,z)))
            rhs=add(add(add(scale(a[3],2),a[2],2),a[4]),a[6],-1)
            self.assertEqual(lhs,rhs)

    def test_3875_product_vector_formulas(self):
        for x,y,z,w in samples(3):
            p=add(add(scale(x,20*form(x,z)),x,-21*form(y,y)),y,-12*form(x,y))
            dp=add(add(add(add(scale(y,-4*form(x,z)),y,-33*form(y,y)),x,-64*form(y,z)),x,60*form(x,w)),z,-24*form(x,y))
            basis=(*triple(x,w),*rcov(x,y,z),*triple(y,x))
            records=read('quartic_3875_products_receipt.json')['product_coordinate_vectors']
            for coefficients,target in zip(records,(sym(y,p),sym(x,dp))):
                actual={}
                for c,t in zip(coefficients,basis):actual=add(actual,t,Q(c))
                self.assertEqual(actual,target)

    def test_changed_ideal_coordinate_is_rejected(self):
        r=read('quartic_adjoint_ideal_receipt.json')
        source=decode(r['ambient_evaluation_columns']);image=decode(r['ideal_evaluation_columns'])[0]
        bad=list(map(Q,r['ideal_coordinate_matrix'][0]));bad[0]+=1
        self.assertNotEqual(combination(bad,source),{k:z for k,z in image.items() if z})

    def test_all_full_null_dependencies_replayed(self):
        self.assertTrue(read('weight4_3875_source_replay.json')['passed'])
        r=read('weight5_adjoint_source_replay.json')
        self.assertTrue(r['source_replay']['passed'])
        self.assertTrue(r['source_replay']['lattice_replayed'])
        self.assertEqual(r['quartic_product']['F0_equals_c_Y_modulo_ideal'],'91/155')
        self.assertTrue(read('weight6_quartic_source_replay.json')['passed'])

if __name__=='__main__':unittest.main()
