"""Exact three-term terminal loop, avoiding factorization of rejected x values."""
from pathlib import Path
import importlib.util
from fractions import Fraction
spec=importlib.util.spec_from_file_location('early_backend',Path(__file__).with_name('search-earlyterminal.py'))
early=importlib.util.module_from_spec(spec);spec.loader.exec_module(early)
math=early.math
json=early.json

class Search(early.Search):
    def fast_two(self,d,a,b,primes,prefix):
        self.stats['fast_two_calls']=self.stats.get('fast_two_calls',0)+1
        if self.stats['fast_two_calls']&8191==0:
            self.prefix=prefix;self.tick()
        lo=max(d,b//a+1)
        hi=2*b//a
        if self.cap is not None:hi=min(hi,self.cap-1)
        if hi<lo:return None
        # Negative f(lo) implies positive discriminant and hi < a/2;
        # f is decreasing on the entire allowed interval, so all fail.
        if lo*lo-a*lo+b<0:
            self.stats['fast_two_prunes']=self.stats.get('fast_two_prunes',0)+1
            return None
        if a*a>4*b:
            delta=a*a-4*b;s=math.isqrt(delta)
            if s*s<delta:s+=1
            hi=min(hi,(a-s)//2)
        if hi<lo:
            self.stats['fast_two_prunes']=self.stats.get('fast_two_prunes',0)+1
            return None
        if hi-lo>10000:
            # In this rare branch, enrich certified factors for the old MITM.
            certified=set(primes)
            for x in prefix:certified.update(early.terminal.strong.small_prime_factors(x))
            return self.two(d,a,b,tuple(sorted(certified)))
        for x in range(lo,hi+1):
            self.stats['fast_two_candidates']=self.stats.get('fast_two_candidates',0)+1
            y,rem=divmod(b*x,a*x-b)
            if rem==0 and y>x and (self.cap is None or y<=self.cap):return (x,y)
        return None

    def dfs(self,d,t,a,b,primes,prefix):
        if t not in (2,3) or a<=0 or b<=0:
            return super().dfs(d,t,a,b,primes,prefix)
        self.stats['nodes']+=1
        if t==2:return self.fast_two(d,a,b,primes,prefix)
        if self.stats['nodes']&1023==0:self.prefix=prefix;self.tick()
        if t*b<a*d or not self.enough(d,t,a,b):
            self.stats['harmonic_prunes']+=1;return None
        if self.prime_obstruction(d,t,a,b,primes):
            self.stats['prime_prunes']+=1;return None
        key=(a,b,d,t)
        if key in self.failed:self.stats['memo_hits']+=1;return None
        lo=max(d,b//a+1);hi=self.next_upper(lo,t,a,b)
        for x in range(lo,hi+1):
            aa=a*x-b;bb=b*x;gg=math.gcd(aa,bb)
            tail=self.fast_two(x+1,aa//gg,bb//gg,primes,prefix+(x,))
            if tail:return (x,)+tail
        if len(self.failed)<self.memo_size:self.failed.add(key)
        return None

def main():
    early.terminal.strong._base.Search=Search
    early.terminal.strong._base.main()
if __name__=='__main__':main()
