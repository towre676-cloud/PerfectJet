"""Independent integer Bareiss ranks and retained covariant coordinate checks."""
from fractions import Fraction as Q
from math import lcm
from pathlib import Path
import json

def bareiss_rank(rows):
    matrix=[]
    for row in rows:
        row=list(map(Q,row));scale=lcm(*(v.denominator for v in row))
        matrix.append([int(v*scale) for v in row])
    if not matrix:return 0
    rank=0;previous=1;n=len(matrix[0])
    for col in range(n):
        found=next((i for i in range(rank,len(matrix)) if matrix[i][col]),None)
        if found is None:continue
        matrix[rank],matrix[found]=matrix[found],matrix[rank]
        pivot=matrix[rank][col]
        for i in range(rank+1,len(matrix)):
            coefficient=matrix[i][col]
            for j in range(col+1,n):
                numerator=matrix[i][j]*pivot-coefficient*matrix[rank][j]
                assert numerator%previous==0
                matrix[i][j]=numerator//previous
            matrix[i][col]=0
        previous=pivot;rank+=1
        if rank==len(matrix):break
    return rank

def decode(columns):return [{(s,i):Q(z) for s,i,z in v} for v in columns]
def dense(columns):
    keys=sorted(set().union(*columns))
    return [[v.get(k,0) for v in columns] for k in keys]
def combination(c,columns):
    out={}
    for z,v in zip(map(Q,c),columns):
        for k,w in v.items():out[k]=out.get(k,0)+z*w
    return {k:v for k,v in out.items() if v}

def run():
    result={}
    for sector,n,pairn,idealrank in [('adjoint',11,7,9),('3875',15,9,13)]:
        r=json.loads(Path(f'quartic_{sector}_ideal_receipt.json').read_text())
        if sector=='adjoint':
            source=decode(r['ambient_evaluation_columns']);pair=decode(r['pair_covariant_evaluation_columns'])
            projected=decode(r['pair_projected_evaluation_columns'])
        else:
            source=decode(r['source_evaluation_columns']);pair=decode(r['pair_evaluation_columns'])
            projected=decode(r['pair_projected_evaluation_columns'])
        ideal=decode(r['ideal_evaluation_columns'])
        assert bareiss_rank(dense(source))==n
        assert bareiss_rank(dense(pair))==pairn
        assert bareiss_rank(r['ideal_coordinate_matrix'])==idealrank
        assert bareiss_rank(dense(ideal))==idealrank
        for row,v in zip(r['pair_projector'],projected):
            assert combination(row,pair)=={k:z for k,z in v.items() if z}
        for row,v in zip(r['ideal_coordinate_matrix'],ideal):
            assert combination(row,source)=={k:z for k,z in v.items() if z}
        products=json.loads(Path(f'quartic_{sector}_products_receipt.json').read_text())
        assert bareiss_rank(r['ideal_coordinate_matrix']+products['product_coordinate_vectors'])==n
        result[sector]={'source_rank':n,'ideal_rank':idealrank,'arc_multiplicity':n-idealrank,
                        'products_exhaust_arc':True,'integer_replay_passed':True}
    s=json.loads(Path('quartic_singlet_ideal_receipt.json').read_text())
    assert bareiss_rank(s['ideal_coordinate_matrix'])==4
    assert bareiss_rank(s['ideal_coordinate_matrix']+[['0','-8','8','-4','0']])==5
    result['singlet']={'source_rank':5,'ideal_rank':4,'arc_multiplicity':1,
                       'D_F0_exhausts_arc':True,'integer_replay_passed':True}
    Path('quartic_independent_rank_verification.json').write_text(json.dumps({'passed':True,'sectors':result},indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':run()
