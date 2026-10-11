"""Exact quadratic necessary condition for a two-unit-fraction tail.

If a/b = 1/x + 1/y is reduced and x<y, put g=gcd(x,b),
x=g*u,b=g*v. The integer y=g*v*u/(a*u-v) implies a*u-v | g,
since gcd(a*u-v,u*v)=1. Hence a*x-b <= g*g <= x*x.
When a*a>4*b the allowed x interval is below a/2, so
x <= floor((a-sqrt(a*a-4*b))/2). All arithmetic is exact.
"""
from pathlib import Path
import importlib.util
from fractions import Fraction
spec=importlib.util.spec_from_file_location('strong_backend',Path(__file__).with_name('search-strong.py'))
strong=importlib.util.module_from_spec(spec);spec.loader.exec_module(strong)
math=strong.math
json=strong.json

class Search(strong.Search):
    def two(self,d,a,b,primes):
        if a*a>4*b:
            lo=max(d,b//a+1)
            delta=a*a-4*b
            s=math.isqrt(delta)
            if s*s<delta:s+=1
            upper=(a-s)//2
            if self.cap is not None:upper=min(upper,self.cap-1)
            if upper<lo:
                self.stats['quadratic_two_prunes']=self.stats.get('quadratic_two_prunes',0)+1
                return None
            if upper-lo>10000:
                return super().two(d,a,b,primes)
            # No valid x exceeds the small quadratic root: the generic
            # two-term upper bound is <a/2 whenever a*a>4*b.
            for x in range(lo,upper+1):
                if x&1023==0:self.tick()
                self.stats['quadratic_two_candidates']=self.stats.get('quadratic_two_candidates',0)+1
                num=b*x;den=a*x-b
                y,rem=divmod(num,den)
                if rem==0 and y>x and (self.cap is None or y<=self.cap):
                    return (x,y)
            return None
        return super().two(d,a,b,primes)

def main():
    strong.Fraction=Fraction
    strong._base.Fraction=Fraction
    strong._base.Search=Search
    strong._base.main()

if __name__=='__main__':main()
