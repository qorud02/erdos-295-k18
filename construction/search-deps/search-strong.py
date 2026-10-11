"""Stronger prime-adic pruning layered over the preserved exact search engine."""
from __future__ import annotations

import functools
import importlib.util
import pathlib
from fractions import Fraction

_spec=importlib.util.spec_from_file_location("independent_base",pathlib.Path(__file__).with_name("search-independent.py"))
_base=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
SearchTimeout=_base.SearchTimeout
small_prime_factors=_base.small_prime_factors
harmonic_window=_base.harmonic_window
math=_base.math
json=_base.json


@functools.lru_cache(maxsize=250000)
def forced_upper(d:int,t:int,forced:tuple[int,...])->Fraction:
    """Largest t-term reciprocal sum with all listed distinct denominators forced."""
    forced=set(forced)
    if len(forced)>t or any(x<d for x in forced):
        raise ValueError("invalid forced denominator set")
    rest=[]
    x=d
    while len(rest)<t-len(forced):
        if x not in forced:
            rest.append(x)
        x+=1
    return sum((Fraction(1,x) for x in tuple(forced)+tuple(rest)),Fraction())


class Search(_base.Search):
    def prime_obstruction(self,d:int,t:int,a:int,b:int,primes:tuple[int,...])->bool:
        if not self.prime_prune or b==1 or t<=1:
            return False
        for p in primes:
            v=b
            pe=1
            while v%p==0:
                pe*=p
                v//=p
            if pe==1:
                continue
            q1=((d+pe-1)//pe)*pe
            if self.cap is not None and q1>self.cap:
                return True
            # If two p^e-multiples fit among the smallest t denominators,
            # the >=2 case can attain the unrestricted harmonic bound.
            q2=q1+pe
            if q2<d+t:
                continue
            two_possible=True
            if self.cap is not None and q2>self.cap:
                two_possible=False
            elif t>=2:
                h2=forced_upper(d,t,(q1,q2))
                two_possible=h2.numerator*b>=a*h2.denominator
            if two_possible:
                continue
            # With exactly one denominator divisible by p^e, its valuation
            # is exactly e and its unit u satisfies 1/u=a/v modulo p.
            # Hence u=v/a modulo p, x=p^e*u modulo p^(e+1).
            unit=(v*pow(a,-1,p))%p
            modulus=pe*p
            residue=pe*unit
            q=residue+max(0,(d-residue+modulus-1)//modulus)*modulus
            if self.cap is not None and q>self.cap:
                return True
            h1=forced_upper(d,t,(q,))
            if h1.numerator*b<a*h1.denominator:
                return True
        return False


def main():
    _base.Fraction=Fraction
    _base.Search=Search
    _base.main()


if __name__=="__main__":
    main()
