"""Four-current extension of the exact output-coordinate lattice projection.

This computes image coordinates, never a kernel by itself. A projected
rank is a lower bound on full rank. Intermediate states are not truncated.
"""
from collections import defaultdict
from itertools import product
from .asterion_lattice_projection import ProjectedLatticeE8VOA


class ProjectedLatticeE8VOA4(ProjectedLatticeE8VOA):
    def _four_root_word(self, word):
        if len(word)!=4 or any(i<8 for _,i in word):
            raise ValueError('four root currents required')
        modes=tuple(n for n,_ in word)
        roots=tuple(self.algebra.index_root[i] for _,i in word)
        pairs=tuple((i,j) for i in range(4) for j in range(i+1,4))
        inner={p:self.inner(roots[p[0]],roots[p[1]]) for p in pairs}
        beta=tuple(sum(a[i] for a in roots) for i in range(8))
        restricted=tuple(tuple(x if i in self.support else 0 for i,x in enumerate(a)) for a in roots)
        sign=1
        # Cocycle of e^a1 ... e^a4 |0>, rightmost factor first.
        tail=(0,)*8
        for a in reversed(roots):
            sign*=self.algebra.cocycle_sign(a,tail)
            tail=tuple(x+y for x,y in zip(a,tail))
            if sum(a)<0:sign=-sign
        key=(modes,restricted,tuple(inner[p] for p in pairs))
        if key in self._root_products:
            return tuple(((beta,osc),sign*z) for osc,z in self._root_products[key])
        out=defaultdict(int)
        h={}; degrees=[0]*4

        def accumulate(column, factor):
            # At column j all outgoing h_(j,k) have already been fixed.
            available=modes[column]-1-sum(inner[column,k]-h[column,k] for k in range(column+1,4))
            if available<0:return
            if column==0:
                degrees[0]=available
                if sum(degrees)>self.maximum_weight:
                    raise ValueError('lattice state exceeds configured weight')
                schurs=[self._schur_minus(a,d) for a,d in zip(restricted,degrees)]
                for terms in product(*schurs):
                    osc=tuple(sorted(sum((t[0] for t in terms),())))
                    value=factor
                    for _,z in terms:value*=z
                    out[osc]+=value
                return

            def choose(row, remaining, coefficient):
                if row==column:
                    degrees[column]=remaining
                    accumulate(column-1,coefficient)
                    return
                for value in range(remaining+1):
                    c=self._binomial_expansion(inner[row,column],value)
                    if c:
                        h[row,column]=value
                        choose(row+1,remaining-value,coefficient*c)
            choose(0,available,factor)

        accumulate(3,1)
        result=tuple((osc,z) for osc,z in out.items() if z)
        self._root_products[key]=result
        return tuple(((beta,osc),sign*z) for osc,z in result)

    def _projected_word(self, word):
        if len(word)>4:
            raise ValueError('projected evaluator covers at most four currents')
        if len(word)==4 and all(i>=8 for _,i in word):
            if word not in self._projected_words:
                if len(self._projected_words)>=100000:self._projected_words.clear()
                self._projected_words[word]=self._four_root_word(word)
            return self._projected_words[word]
        return super()._projected_word(word)
