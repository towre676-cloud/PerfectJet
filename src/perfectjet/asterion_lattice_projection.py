"""Exact output-coordinate projection of the established Frenkel--Kac evaluator.

Output coordinates are taken in the exact lattice vertex-product formula.
Intermediate states are never truncated.
Projected rank is a certified lower bound on full lattice rank, not an equality
unless an independent null-space bound also matches it.
"""
from collections import defaultdict
from math import comb
from .asterion_primitives import LatticeE8VOA


class ProjectedLatticeE8VOA(LatticeE8VOA):
    def __init__(self, jets=None, support=(0, 1), maximum_weight=8):
        super().__init__(jets, maximum_weight)
        self.support = frozenset(support)
        self._projected_words = {}
        self._root_products = {}
        if not self.support or not self.support <= set(range(8)):
            raise ValueError('support must be nonempty Cartan indices')

    @staticmethod
    def _binomial_expansion(power, order):
        if power >= 0:
            return (-1)**order*comb(power,order) if order <= power else 0
        return comb(-power+order-1,order)

    def _three_root_word(self, word):
        """Project a three-root word using the same lattice vertex product.

        Y(e^a,z1)Y(e^b,z2)Y(e^c,z3)|0> has scalar factor
        epsilon(b,c)epsilon(a,b+c) prod_(i<j)(zi-zj)^(ai,aj).
        Expanding in |z1|>|z2|>|z3| leaves three Schur factors. Unlike
        projecting intermediate states, taking output coordinates here is exact.
        Returns SCALE^3 times the projected word image.
        """
        roots=[self.algebra.index_root[i] for _,i in word]
        n1,n2,n3=[n for n,_ in word]
        a,b,c=roots
        k12,k13,k23=self.inner(a,b),self.inner(a,c),self.inner(b,c)
        beta=tuple(x+y+z for x,y,z in zip(a,b,c))
        bc=tuple(x+y for x,y in zip(b,c))
        sign=self.algebra.cocycle_sign(b,c)*self.algebra.cocycle_sign(a,bc)
        for root in roots:
            if sum(root)<0:
                sign=-sign
        restricted=[tuple(x if i in self.support else 0 for i,x in enumerate(root)) for root in roots]
        product_key=(tuple(n for n,_ in word),tuple(restricted),(k12,k13,k23))
        if product_key in self._root_products:
            return tuple(((beta,osc),sign*z) for osc,z in self._root_products[product_key])
        out=defaultdict(int)
        for h23 in range(n3):
            w23=self._binomial_expansion(k23,h23)
            if not w23:
                continue
            for h13 in range(n3-h23):
                w13=self._binomial_expansion(k13,h13)
                if not w13:
                    continue
                d3=n3-1-h13-h23
                for h12 in range(max(0,n2-k23+h23)):
                    w12=self._binomial_expansion(k12,h12)
                    d1=n1-1-k12-k13+h12+h13
                    d2=n2-1-k23-h12+h23
                    if not w12 or min(d1,d2)<0:
                        continue
                    if d1+d2+d3 > self.maximum_weight:
                        raise ValueError('lattice state exceeds configured weight')
                    schurs=[self._schur_minus(root,d) for root,d in zip(restricted,(d1,d2,d3))]
                    factor=sign*w12*w13*w23
                    for x,u in schurs[0]:
                        for y,v in schurs[1]:
                            xy=tuple(sorted(x+y))
                            for z,w in schurs[2]:
                                out[beta,tuple(sorted(xy+z))]+=factor*u*v*w
        result=tuple((k,z) for k,z in out.items() if z)
        self._root_products[product_key]=tuple((osc,sign*z) for (_,osc),z in result)
        return result

    def _two_root_word(self, word):
        (n1,i),(n2,j)=word
        a,b=self.algebra.index_root[i],self.algebra.index_root[j]
        k=self.inner(a,b)
        beta=tuple(x+y for x,y in zip(a,b))
        sign=self.algebra.cocycle_sign(a,b)
        for root in (a,b):
            if sum(root)<0:
                sign=-sign
        ra,rb=[tuple(x if q in self.support else 0 for q,x in enumerate(root)) for root in (a,b)]
        product_key=((n1,n2),(ra,rb),(k,))
        if product_key in self._root_products:
            return tuple(((beta,osc),sign*z) for osc,z in self._root_products[product_key])
        out=defaultdict(int)
        for h in range(n2):
            coefficient=sign*self._binomial_expansion(k,h)
            d1,d2=n1-1-k+h,n2-1-h
            if not coefficient or d1<0:
                continue
            for x,u in self._schur_minus(ra,d1):
                for y,v in self._schur_minus(rb,d2):
                    out[beta,tuple(sorted(x+y))]+=coefficient*u*v
        result=tuple((key,z) for key,z in out.items() if z)
        self._root_products[product_key]=tuple((osc,sign*z) for (_,osc),z in result)
        return result

    def _projected_word(self, word):
        """Exact projected image, scaled by SCALE^len(word).

        Commute negative Heisenberg modes left before projection. The
        commutator has one fewer current and receives one additional SCALE.
        Root-only tails use the exact vertex-product generating functions.
        """
        cached=self._projected_words.get(word)
        if cached is not None:
            return cached
        if not word:
            result=((( (0,)*8,()),1),)
        elif word[0][1]<8:
            (n,i),tail=word[0],word[1:]
            result=tuple(((beta,tuple(sorted(osc+((n,i),)))),z*self.SCALE)
                         for (beta,osc),z in self._projected_word(tail)) if i in self.support else ()
        else:
            position=next((q for q,(_,i) in enumerate(word) if i<8),None)
            if position is not None:
                left=position-1
                (n,i),(m,j)=word[left:position+1]
                swapped=word[:left]+((m,j),(n,i))+word[position+1:]
                out=dict(self._projected_word(swapped))
                for index,coefficient in self.jets.bracket(i,j):
                    shorter=word[:left]+((n+m,index),)+word[position+1:]
                    for key,z in self._projected_word(shorter):
                        out[key]=out.get(key,0)+coefficient*z*self.SCALE
                result=tuple((key,z) for key,z in out.items() if z)
            elif len(word)==3:
                result=self._three_root_word(word)
            elif len(word)==2:
                result=self._two_root_word(word)
            elif len(word)==1:
                (n,i),=word
                alpha=self.algebra.index_root[i]
                restricted=tuple(x if q in self.support else 0 for q,x in enumerate(alpha))
                sign=1 if sum(alpha)>0 else -1
                result=tuple(((alpha,osc),sign*z) for osc,z in self._schur_minus(restricted,n-1))
            else:
                raise ValueError('projected evaluator covers at most three currents')
        if len(self._projected_words)>=100000:
            self._projected_words.clear()
        self._projected_words[word]=result
        return result

    def _accumulate(self, words):
        out=defaultdict(int)
        for word,factor in words.items():
            if sum(n for n,_ in word)>self.maximum_weight:
                raise ValueError('lattice state exceeds configured weight')
            for key,z in self._projected_word(word):
                out[key]+=factor*z
        return out

    def clear_cache(self):
        super().clear_cache()
        self._projected_words.clear()
        self._root_products.clear()
