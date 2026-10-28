"""Append collision/Pell equations while preserving every earlier record."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'docs/chapters/39_collision_pell_and_analytic_boundaries.md'
ROWS = [
('parity collision local factor','L2(x)=(1+2x-x^2)/(1-x^2)^2','exact_checked','Formal series, or |x|<1; signed exponent-pair weights.'),
('Pell factorization','1+2x-x^2=(1+(1+sqrt(2))*x)*(1+(1-sqrt(2))*x)','exact_checked','Exact quadratic-field identity; not an empirical fit.'),
('positive collision coefficient','A(p^k)=1 if k even, k+1 if k odd','derived','Regroup signed pair series only in its absolute-convergence region Re(s)>1.'),
('ordinary cardinality descendant','A(n)=tau(product(p^v_p(n),v_p(n) odd))','derived','An alternative positive population; individual signed terms remain signed.'),
('Pell-Lucas logarithmic coefficient','[x^n]x*L2_prime/L2=(-1)^(n+1)*P_n+4*1_(2|n)','exact_checked','P0=P1=2; P_n=2P_(n-1)+P_(n-2); n>=1.'),
('formal integer Euler exponents','b_n=(1/n)*sum_(d|n)mu(d)*c_(n/d)','derived','Formal local identity; no assertion of convergence of an infinite zeta product in Re(s)>0.'),
('finite zeta extraction','L(x)=product_(n<=M)(1-x^n)^(-b_n)*R_M(x); R_M=1+O(x^(M+1))','exact_checked','Residual rational factor retained; sufficiently small primes may require separate factors.'),
('non-unit primitive numerator roots','N_L has roots inside and outside |x|=1 for every L>1','derived','c0=1,c1=2,cD=zeta,c(D-1)=2*zeta^2 contradict self-inversiveness; primitive zeta, D=2L-2.'),
('integer Galois norm','P_L(x)=product_(a in units mod L)N_(L,zeta^a)(x) in Z[x]','exact_checked','Full prime-local Galois norm; differs from trace, character average and an individual complex product.'),
('all-conductor norm boundary','NormEuler_L has natural boundary Re(s)=0 iff L>1','derived','Meromorphic continuation Re(s)>0 by classical Estermann; L1=zeta(s)^2. No individual-phase conclusion.'),
('local character projection','C_L(x)=sum_(r,s<L,L|rs)x^(r+s)','exact_checked','1/L times all characters locally; Euler product imposes divisibility separately at each prime.'),
('projection degree and leading term','deg C_L=2L-min_(d|L)(d+L/d); leading=1 for square L,2 otherwise','derived','Exact degree proof, not numerical root classification.'),
('projection gcd sum and derivative','C_L(1)=sum_(r<L)gcd(r,L); C_L_prime(1)=L*(C_L(1)-L)','exact_checked','All positive integer conductors; gcd(0,L)=L.'),
('exceptional projection classification','C_L has all unit-modulus roots iff L in {1,4}','derived','Square-conductor reciprocity plus gcd-sum inequality; classical Estermann supplies analytic consequence.'),
('exceptional conductor four','ProjectionEuler_4(s)=zeta(s)^2*zeta(4s)/zeta(2s)','exact_checked','Prime-local 4|v_p(m)v_p(n) for every p; differs from 4|kappa(m,n).'),
('two-term collision counting asymptotic','sum_(n<=X)A(n)=C*X*log(X)+C*(2*gamma-1+D)*X+O_epsilon(X^(1/2+epsilon))','derived','C=product_p(1-2/(p+1)^2); D=sum_p 4p*log(p)/((p+1)*(p^2+2p-1)); elementary convolution proof.'),
('certified leading constant','C_P*(1-2/(P+1)) <= C <= C_P','exact_checked','Finite exact prime product, integer P>=2; JSON rounding is outward. Not a finite-X asymptotic error bar.'),
('positive residue block populations','C_(L,c)(dL+r)=d*G_(r,c)+B_(r,c)','exact_checked','Actual exponent splits; count/rank/unrank at remote exponent without enumerating all splits.'),
('global residue factor-pair convolution','hist_(mn=N,kappa mod L)=cyclic_convolution_p hist_(a+b=v_p(N),ab mod L)','exact_checked','Supplied distinct primes verified within declared work budget; original integer outputs have separate bit guard.'),
('Pell unit binary transport','(1+sqrt(2))^n=u_n+v_n*sqrt(2); u_n^2-2v_n^2=(-1)^n','exact_checked','Exact or modular binary powering; remote modular values are not the complete integers.'),
]


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',',':')).encode()


def build(check=False):
    source = json.loads((ROOT/'data/equations.json').read_text())
    prefix = [row for row in source['equations'] if not row['id'].startswith('PJ-C')]
    if len(prefix) != 724:
        raise ValueError('expected the unchanged 724-record research prefix')
    rows = [dict(id=f'PJ-C{i:03d}',domain='collision-pell',title=title,equation=equation,
                 status=status,assumptions=assumptions,source=SOURCE+'; src/perfectjet/collision_zeta.py; research/collision_pell/README.md')
            for i,(title,equation,status,assumptions) in enumerate(ROWS,1)]
    source['equations'] = prefix+rows
    extension = {'schema':'perfectjet/collision-equations/1',
                 'preserved_prefix':{'equation_count':len(prefix),'sha256_of_canonical_records':hashlib.sha256(canonical(prefix)).hexdigest()},
                 'equations':rows}
    ranking = json.loads((ROOT/'data/equation_power.json').read_text())
    for row in rows:
        ranking['assignments'][row['id']] = 15
        ranking['callable_labs'][row['id']] = ['collision']
    expected = {'data/equations.json':source,'src/perfectjet/resources/equations.json':source,
                'data/equation_power.json':ranking,'src/perfectjet/resources/equation_power.json':ranking,
                'data/collision_equations.json':extension}
    atlas = ['# Equation atlas','','Status describes evidence in this repository. Exact checking is not Lean verification.','',
             '| ID | Domain | Title | Equation | Status | Assumptions and limits |',
             '|---|---|---|---|---|---|']
    for row in source['equations']:
        atlas.append('| '+' | '.join(str(row[k]).replace('|','\\|').replace('\n',' ') for k in ('id','domain','title','equation','status','assumptions'))+' |')
    chapter = (ROOT/SOURCE).read_text()
    marker = '\n\n<!-- collision-pell-chapter -->\n\n'
    record_index = '\n\n## Collision equation index\n\n| ID | Result |\n|---|---|\n'
    record_index += ''.join('| '+row['id']+' | '+row['title']+' |\n' for row in rows)
    master = (ROOT/'docs/MONOGRAPH.md').read_text().split(marker)[0]+marker+chapter+record_index
    strings = {'docs/EQUATION_ATLAS.md':'\n'.join(atlas)+'\n','docs/MONOGRAPH.md':master}
    for path,value in expected.items():
        strings[path] = json.dumps(value,indent=2,ensure_ascii=False)+'\n'
    for path,content in strings.items():
        if check:
            if (ROOT/path).read_text() != content:
                raise ValueError('stale generated collision resource: '+path)
        else:
            (ROOT/path).write_text(content,encoding='utf-8')
    print(json.dumps({'equations':len(source['equations']),'new_records':len(rows),'earlier_records_preserved':len(prefix),'mode':'check' if check else 'build'}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    build(parser.parse_args().check)
