"""Independent exact Egyptian-fraction search for the finite k(18) question.

All successful witnesses and all arithmetic prunes use integers/Fraction.
No denominator cap is imposed unless --max-denominator is supplied.
An interrupted run is never a nonexistence certificate.
"""
from __future__ import annotations

import argparse
import bisect
import functools
import json
import math
import time
from fractions import Fraction


class SearchTimeout(Exception):
    pass


@functools.lru_cache(maxsize=250000)
def harmonic_window(first: int, terms: int) -> Fraction:
    return sum((Fraction(1, first + j) for j in range(terms)), Fraction())


@functools.lru_cache(maxsize=100000)
def small_prime_factors(n: int) -> tuple[int, ...]:
    """Return certified prime factors found by trial division; may be partial."""
    ans = []
    d = 2
    while d * d <= n and d <= 10000:
        if n % d == 0:
            ans.append(d)
            while n % d == 0:
                n //= d
        d = 3 if d == 2 else d + 2
    if n > 1 and d * d > n:
        ans.append(n)
    return tuple(ans)


class Search:
    def __init__(self, seconds: float, cap: int | None, memo_size: int, prime_prune: bool):
        self.start = time.monotonic()
        self.deadline = self.start + seconds
        self.cap = cap
        self.memo_size = memo_size
        self.prime_prune = prime_prune
        self.failed: set[tuple[int, int, int, int]] = set()
        self.stats = {"nodes": 0, "harmonic_prunes": 0, "prime_prunes": 0,
                      "memo_hits": 0, "terminal_scans": 0, "terminal_divisors": 0}
        self.next_report = self.start + 15
        self.prefix: tuple[int, ...] = ()

    def tick(self):
        now = time.monotonic()
        if now >= self.deadline:
            raise SearchTimeout
        if now >= self.next_report:
            print(json.dumps({"event": "progress", "elapsed_seconds": round(now-self.start, 2),
                              "stats": self.stats, "current_prefix": self.prefix}, ensure_ascii=False), flush=True)
            self.next_report = now + 15

    @staticmethod
    def enough(first: int, terms: int, a: int, b: int) -> bool:
        h = harmonic_window(first, terms)
        return h.numerator * b >= a * h.denominator

    def next_upper(self, d: int, t: int, a: int, b: int) -> int:
        hi = (t * b) // a
        if self.cap is not None:
            hi = min(hi, self.cap - t + 1)
        lo = d - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.enough(mid, t, a, b):
                lo = mid
            else:
                hi = mid - 1
        return lo

    def prime_obstruction(self, d: int, t: int, a: int, b: int,
                          primes: tuple[int, ...]) -> bool:
        """If p^e divides reduced b, a future denominator must have v_p >= e."""
        if not self.prime_prune or b == 1 or t <= 1:
            return False
        h = None
        for p in primes:
            bb = b
            pe = 1
            while bb % p == 0:
                pe *= p
                bb //= p
            if pe == 1:
                continue
            q = ((d + pe - 1) // pe) * pe
            if self.cap is not None and q > self.cap:
                return True
            if q < d + t:
                continue
            if h is None:
                h = harmonic_window(d, t-1)
            numerator = h.numerator * q + h.denominator
            denominator = h.denominator * q
            if numerator * b < a * denominator:
                return True
        return False

    def two(self, d: int, a: int, b: int, primes: tuple[int, ...]):
        lo = max(d, b // a + 1)
        hi = self.next_upper(lo, 2, a, b)
        if lo > hi:
            return None
        rem = b
        factors = []
        divisor_count = 1
        for p in primes:
            exponent = 0
            while rem % p == 0:
                rem //= p
                exponent += 1
            if exponent:
                factors.append((p, 2*exponent))
                divisor_count *= 2*exponent + 1
        if rem == 1 and 2*math.isqrt(divisor_count) < hi-lo+1:
            self.stats["terminal_divisors"] += 1
            lower_u = max(1, a*lo-b)
            upper_u = min(b-1, a*hi-b)
            halves = [[], []]
            counts = [1, 1]
            for p,e in sorted(factors,key=lambda pe:pe[1],reverse=True):
                index = 0 if counts[0] <= counts[1] else 1
                halves[index].append((p,e))
                counts[index] *= e+1
            def divisors(ff):
                out = [1]
                for p,e in ff:
                    nxt = []
                    for u in out:
                        for _ in range(e+1):
                            if u > upper_u:
                                break
                            nxt.append(u)
                            u *= p
                    out = nxt
                return out
            lhs,rhs = divisors(halves[0]),divisors(halves[1])
            buckets = {}
            for u in rhs:
                buckets.setdefault(u%a,[]).append(u)
            for bucket in buckets.values():
                bucket.sort()
            for j,u1 in enumerate(lhs):
                if j & 1023 == 0:
                    self.tick()
                residue = (-b*pow(u1,-1,a))%a if a>1 else 0
                bucket = buckets.get(residue)
                if not bucket:
                    continue
                low2 = (lower_u+u1-1)//u1
                high2 = upper_u//u1
                if self.cap is not None:
                    # y=(b^2/u+b)/a <= cap gives a lower bound for u.
                    if a*self.cap <= b:
                        continue
                    low2=max(low2,(b*b+u1*(a*self.cap-b)-1)//(u1*(a*self.cap-b)))
                index=bisect.bisect_left(bucket,low2)
                if index<len(bucket) and bucket[index]<=high2:
                    u=u1*bucket[index]
                    v=b*b//u
                    x,y=(u+b)//a,(v+b)//a
                    if (v+b)%a==0 and x>=d and y>x and (self.cap is None or y<=self.cap):
                        return (x,y)
            return None
        self.stats["terminal_scans"] += 1
        for x in range(lo, hi+1):
            if x & 1023 == 0:
                self.tick()
            numerator = b*x
            denominator = a*x-b
            y, rem = divmod(numerator, denominator)
            if rem == 0 and y > x and (self.cap is None or y <= self.cap):
                return (x, y)
        return None

    def dfs(self, d: int, t: int, a: int, b: int, primes: tuple[int, ...], prefix: tuple[int, ...]):
        self.stats["nodes"] += 1
        if self.stats["nodes"] & 1023 == 0:
            self.prefix = prefix
            self.tick()
        if a <= 0 or t <= 0:
            return None
        if t == 1:
            if b % a == 0:
                x = b // a
                if x >= d and (self.cap is None or x <= self.cap):
                    return (x,)
            return None
        if t*b < a*d or not self.enough(d, t, a, b):
            self.stats["harmonic_prunes"] += 1
            return None
        if self.prime_obstruction(d, t, a, b, primes):
            self.stats["prime_prunes"] += 1
            return None
        key = (a,b,d,t)
        if key in self.failed:
            self.stats["memo_hits"] += 1
            return None
        if t == 2:
            result = self.two(d,a,b,primes)
            if not result and len(self.failed) < self.memo_size:
                self.failed.add(key)
            return result
        lo = max(d, b//a+1)
        hi = self.next_upper(lo,t,a,b)
        for x in range(lo,hi+1):
            aa, bb = a*x-b, b*x
            gg = math.gcd(aa,bb)
            aa //= gg
            bb //= gg
            new_primes = tuple(sorted(set(primes).union(small_prime_factors(x))))
            tail = self.dfs(x+1,t-1,aa,bb,new_primes,prefix+(x,))
            if tail:
                return (x,)+tail
        if len(self.failed) < self.memo_size:
            self.failed.add(key)
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minimum", type=int, default=18)
    ap.add_argument("--terms", type=int, default=33)
    ap.add_argument("--seconds", type=float, default=60)
    ap.add_argument("--max-denominator", type=int)
    ap.add_argument("--prefix", default="")
    ap.add_argument("--memo-size", type=int, default=200000)
    ap.add_argument("--no-prime-prune", action="store_true")
    args = ap.parse_args()
    prefix = tuple(map(int,args.prefix.split(','))) if args.prefix else ()
    if prefix and (prefix[0] < args.minimum or any(a>=b for a,b in zip(prefix,prefix[1:]))):
        ap.error("prefix must be strictly increasing and start at minimum or above")
    remaining = 1-sum((Fraction(1,d) for d in prefix),Fraction())
    s = Search(args.seconds,args.max_denominator,args.memo_size,not args.no_prime_prune)
    primes = tuple(sorted(set(p for d in prefix for p in small_prime_factors(d))))
    status = "exhausted"
    result = None
    try:
        tail = s.dfs(prefix[-1]+1 if prefix else args.minimum,args.terms-len(prefix),
                     remaining.numerator,remaining.denominator,primes,prefix)
        if tail:
            result = prefix+tail
            status = "witness"
    except SearchTimeout:
        status = "timeout"
    if result:
        assert len(result) == args.terms
        assert len(set(result)) == len(result)
        assert min(result) >= args.minimum
        assert sum((Fraction(1,d) for d in result),Fraction()) == 1
    print(json.dumps({"event":"result","status":status,"minimum":args.minimum,
                      "terms":args.terms,"prefix":prefix,"max_denominator":args.max_denominator,
                      "denominators":result,"elapsed_seconds":round(time.monotonic()-s.start,3),
                      "stats":s.stats,"failed_states":len(s.failed)},ensure_ascii=False),flush=True)


if __name__ == "__main__":
    main()
