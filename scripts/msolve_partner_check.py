"""Characteristic-0 emptiness of a slice partner locus with Singular (system) and msolve (solver).

Singular forms the exact rational projected determinants det(P L_N S) and the Rabinowitsch
polynomial 1 - z r(1+p+q+r); msolve decides over Q whether the system has a complex solution.
An empty answer proves that no sextic with three simple roots placed at 0, 1, infinity has the
stated kernel (the projected set contains the true locus). Usage:
    python scripts/msolve_partner_check.py N [--kernel=K] [--projections=k] [--relation=NAME --index=i]
With a relation, "empty" means the relation vanishes on every point of the locus off repeated roots.
"""
import json, os, subprocess, sys, tempfile, time
sys.path.insert(0, os.path.dirname(__file__))
from singular_partner_check import script, relations, poly_str


def main(n, kernel=1, projections=6, relation=None, index=0):
    t = time.time()
    body = script(n, [], projections=projections, check_empty=False, char=0, kernel=kernel).replace("quit;", "")
    tmp = tempfile.mkdtemp()
    sys_path = os.path.join(tmp, "system.ms")
    body += f'''
short=0;
link l=":w {sys_path}";
write(l,"p,q,r,z");
write(l,"0");
poly g={("h*(" + poly_str(relations()[relation][index]) + ")") if relation else "h"};
ideal F=J,1-z*g;
int i;
for(i=1;i<=size(F);i++){{ if(i<size(F)){{write(l,string(F[i])+",");}} else {{write(l,string(F[i]));}} }}
close(l);
quit;
'''
    sing = os.path.join(tmp, "build.sing")
    open(sing, "w").write(body)
    subprocess.run(["Singular", "-q", sing], check=True, capture_output=True)
    out_path = os.path.join(tmp, "out.ms")
    proc = subprocess.run(["msolve", "-f", sys_path, "-o", out_path, "-t", "2"], capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError("msolve failed: " + (proc.stderr or proc.stdout)[-500:])
    out = open(out_path).read() if os.path.exists(out_path) else proc.stdout
    if not out.strip():
        raise RuntimeError("msolve returned no verdict")
    empty = out.strip().startswith("[-1]")
    return {"degree": n, "kernel_at_least": kernel, "relation": f"{relation}{index}" if relation else None,
            "statement": "relation vanishes on the locus" if relation else "locus empty", "field": "Q", "solver": "msolve", "projections": projections,
            "empty": empty, "seconds": round(time.time()-t, 1), "msolve_head": out.strip()[:80]}


if __name__ == "__main__":
    k = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--kernel=")), 1)
    pr = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--projections=")), 6)
    rel = next((a.split("=")[1] for a in sys.argv if a.startswith("--relation=")), None)
    idx = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--index=")), 0)
    print(json.dumps(main(int(sys.argv[1]), k, pr, rel, idx)), flush=True)
