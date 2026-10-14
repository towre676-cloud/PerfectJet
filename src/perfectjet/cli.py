"""Reproduce the retained calculations and inspect the equation atlas."""
import argparse,json
from fractions import Fraction
from pathlib import Path
from . import __version__


def encode(value):
    if isinstance(value,Fraction):return str(value)
    raise TypeError(type(value).__name__)


def report():
    from .transvectants import molecular_receipt
    from .rings import core_field_receipt
    from .collision import collision_receipt
    from .psg import flip_root
    from .exact import target_recovery,observable_space
    from .populations import SelectionPopulation
    from .semantics import PartialMachine
    from .polynomial import Poly,feature_closure
    from .dynamics import energy_balance
    from .jets import iterate_defect
    p=SelectionPopulation([(2,1),(1,2),(2,2),(0,1)],(3,3),[4,3,5,0])
    machine=PartialMachine([0,0,1,1],[(2,),(3,),(2,),(3,)])
    reduced,mapping,blocks=machine.quotient()
    x=Poly.variable(0,1)
    return {"version":__version__,"molecular":molecular_receipt(),"core_field":core_field_receipt(),
            "collision":collision_receipt(),"PSG":flip_root(),
            "observability":{"hidden":target_recovery([[1,1]],[[1,-1]]),
                             "repaired":target_recovery([[1,1],[1,-1]],[[1,-1]]),
                             "observable_rows":observable_space([[1,0],[0,2]],[[1,0]])},
            "selection":{"count":p.count(),"optimum":p.optimum(),
                         "rank_unrank_replay":all(p.rank(p.unrank(i))==i for i in range(p.count()))},
            "SOE":{"blocks":blocks,"mapping":mapping,"reduced_states":len(reduced.observations)},
            "features":{"closed":feature_closure([Poly.constant(1,1),x],[2*x+1]),
                        "unclosed":feature_closure([x],[x*x])},
            "energy":energy_balance([[-1,0],[0,-2]],[[1,0],[0,1]],[1,1],[1,0]),
            "flip_defect":iterate_defect([0,-1,1,2],5),
            "limitations":"No imported upstream solver or Lean theorem is claimed by this release."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=["report","psg","partners","collision","core-field","atlas"])
    parser.add_argument("--output",type=Path)
    parser.add_argument("--conductor",type=int,default=7)
    parser.add_argument("--index",type=int,default=10**100)
    args=parser.parse_args()
    if args.command=="report":out=report()
    elif args.command=="psg":
        from .psg import flip_root
        out=flip_root()
    elif args.command=="partners":
        from .transvectants import census
        out=census()
    elif args.command=="collision":
        from .collision import CyclotomicCollision
        c=CyclotomicCollision(args.conductor)
        out={"conductor":args.conductor,"index":str(args.index),"coefficient":c.coefficient(args.index).record()}
    elif args.command=="core-field":
        from .rings import core_field_receipt
        out=core_field_receipt()
    else:
        root=Path(__file__).resolve().parents[2]
        atlas=root/"data"/"equations.json"
        if not atlas.exists():parser.error("atlas data is available in the repository checkout")
        out=json.loads(atlas.read_text())
    content=json.dumps(out,indent=2,default=encode)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(content)
    else:print(content,end="")


if __name__=="__main__":main()
