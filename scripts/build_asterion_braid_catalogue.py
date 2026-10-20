"""Append half-braid statements without changing the698-record prefix."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROWS=[
('flat three-point lift','A+B+C=-60I; [A,B+C]=[B,A+C]=[C,A+B]=0','exact_checked','Actual E8 residues; h=1/34. Flat permutation-equivariant descent gives a linear B3 representation.'),
('tensor exchange parities','P12|channels=diag(1,-1,1,-1,1)','exact_checked','Channel order1,248,3875,30380,27000; actual invariant tensor permutations, not arbitrary square-root choices.'),
('based half-braid reconstruction','R1=sum_i mu_i P_i(U); R2=X R1 X','derived','Simple pure spectrum; positive counterclockwise exchanges at ordered base(0,1/2,1); canonical local logarithms.'),
('exact half-braid spectrum','mu=(zeta^2,zeta,zeta^14,-1,-zeta^9)','exact_checked','zeta=exp(2pi i/17); squared spectrum agrees with existing U,V channel by channel.'),
('linear braid and squares','R1 R2 R1=R2 R1 R2; R1^2=U; R2^2=V','derived','Exact flat equivariant KZ descent; exact cyclotomic braid model and rigorous same-chart consistency replay. Residual enclosure alone is not an equality proof.'),
('central full twist','(R1 R2)^3=zeta^4 I','exact_checked','Central rotation integrates h(A+B+C); independently verified in the Tuba-Wenzl model overQ(zeta17).'),
('half-braid orders and determinants','ord(Ri)=po(Ri)=34; det(Ri)=zeta^9','derived','Displayed five distinct signed half phases, with the tensor-permutation lift fixed.'),
('Tuba-Wenzl class','gamma=zeta^12; gamma^5=det R1; gamma^6=zeta^4','exact_checked','Five-dimensional simple B3 module; all20 Proposition2.8 polynomials are nonzero; uniqueness is Theorem2.9.'),
('cyclotomic integral realization','rho(B3) is conjugate to a subgroup of GL5(Z[zeta17])','derived','Retained ordered triangular matrices have integral cyclotomic coefficients and unit determinant; exact chart conjugator is not computed.'),
('linear modular normalization','Ti=zeta^5 Ri; (T1 T2)^3=(T1 T2 T1)^2=I; det Ti=1','exact_checked','Common character twist changes pure squares tozeta^10U,zeta^10V; original normalization is kept distinct.'),
('triangle-group quotient','normalized image is a quotient of Delta(2,3,34)','derived','s=T1T2T1,t=T1T2; s^2=t^3=(t^-1s)^34=1. Faithfulness and the full normal kernel remain open.'),
('pure-loop spectral recovery from half-braids','Spec(Ri^2)=(zeta^4,zeta^2,zeta^11,1,zeta)','exact_checked','Exact field arithmetic in the independent algebraic model; identification with analytic operators is up to simultaneous conjugacy, using KZ descent and classification.'),
]

def write(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

def main():
    source=json.loads((ROOT/'data/equations.json').read_text())
    prefix=[r for r in source['equations'] if not r['id'].startswith('PJ-HB')]
    if len(prefix)!=698:
        raise ValueError('expected unchanged698-record prefix')
    records=[{'id':f'PJ-HB{i:03d}','domain':'asterion-half-braid','title':title,
        'equation':equation,'status':status,'assumptions':assumptions,
        'source':'docs/ASTERION_HALF_BRAID.md; src/perfectjet/kz_half_braid.py; results/asterion-half-braid/manifest.json'}
        for i,(title,equation,status,assumptions) in enumerate(ROWS,1)]
    digest=hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    write(ROOT/'data/asterion_braid_equations.json',{'schema':'perfectjet/asterion-half-braid-equations/1',
        'preserved_prefix':{'equation_count':698,'sha256_of_canonical_records':digest},'equations':records})
    source['equations']=prefix+records
    for rel in ('data/equations.json','src/perfectjet/resources/equations.json'):
        write(ROOT/rel,source)
    ranking=json.loads((ROOT/'data/equation_power.json').read_text())
    for r in records:
        ranking['assignments'][r['id']]=26
        ranking['callable_labs'][r['id']]=[]
    for rel in ('data/equation_power.json','src/perfectjet/resources/equation_power.json'):
        write(ROOT/rel,ranking)
    atlas=['# Equation atlas','','Status describes evidence in this repository. Exact checking is not Lean verification.','',
        '| ID | Domain | Title | Equation | Status | Assumptions and limits |',
        '|---|---|---|---|---|---|']
    for r in source['equations']:
        atlas.append('| '+' | '.join(str(r[k]).replace('|','\\|').replace('\n',' ') for k in ('id','domain','title','equation','status','assumptions'))+' |')
    (ROOT/'docs/EQUATION_ATLAS.md').write_text('\n'.join(atlas)+'\n')
    print(json.dumps({'equations':len(source['equations']),'new_records':len(records),'preserved_prefix_sha256':digest}))

if __name__=='__main__':
    main()
