"""Run from repository root with PYTHONPATH=src python examples/walkthrough.py."""
from fractions import Fraction as Q
from perfectjet.populations import SelectionPopulation
from perfectjet.exact import target_recovery
from perfectjet.transvectants import c3_family,partner_dimensions
from perfectjet.collision import CyclotomicCollision

p=SelectionPopulation([(2,1),(1,2),(2,2)],(3,3),[4,3,5])
print('Feasible population:',p.count(),'optimum:',p.optimum())
for rank in range(p.count()):print('Address',rank,'selection',p.unrank(rank))
print('Hidden target:',target_recovery([[1,1]],[[1,-1]]))
print('Repaired target:',target_recovery([[1,1],[1,-1]],[[1,-1]]))
for parameter in [1,Q(40,7)]:
    print('Quintic active dimension at',parameter,partner_dimensions(c3_family(parameter)[0],5))
print('Collision coefficient at10^100:',CyclotomicCollision(7).coefficient(10**100).record())
