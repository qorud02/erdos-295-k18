"""Independent review of arithmetic and the distinct-forced-denominator relaxation.

The central joint-bound check solves a finite assignment problem by enumerating
all denominator sets and all injections of labelled lower bounds. It does not
call any search implementation from the repository.
"""
from fractions import Fraction as F
from itertools import combinations, combinations_with_replacement, permutations
from pathlib import Path
import json
from math import gcd, lcm

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
D = json.loads((ROOT / 'repo/certificate-34-independent.json').read_text())['denominators']

def reciprocal_sum(ds):
    return sum((F(1, d) for d in ds), F())

assert len(D) == len(set(D)) == 34 and reciprocal_sum(D) == 1
assert reciprocal_sum([18, 63]) == reciprocal_sum([42, 55, 66, 70]) == F(1, 14)
assert {18, 63} <= set(D)
assert not ({42, 55, 66, 70} & (set(D) - {18, 63}))
D19 = sorted((set(D) - {18, 63}) | {42, 55, 66, 70})
assert len(D19) == 36 and min(D19) == 19 and reciprocal_sum(D19) == 1

quadratic_cases = 0
for x in range(2, 301):
    for y in range(x + 1, 351):
        r = F(1, x) + F(1, y)
        a, b = r.numerator, r.denominator
        g = gcd(x, b)
        assert x*x - a*x + b >= 0
        assert g*g % (a*x-b) == 0
        quadratic_cases += 1

def factor_powers(b):
    ans = []
    p = 2
    while p*p <= b:
        q = 1
        while b % p == 0:
            b //= p
            q *= p
        if q > 1:
            ans.append((p, q))
        p += 1
    if b > 1:
        ans.append((b, b))
    return ans

padic_cases = 0
padic_prime_conditions = 0
for t in range(2, 6):
    for ds in combinations(range(2, 22), t):
        r = reciprocal_sum(ds)
        a, b = r.numerator, r.denominator
        for p, q in factor_powers(b):
            forced = [d for d in ds if d % q == 0]
            assert forced
            if len(forced) == 1:
                x = forced[0]
                assert x % (q*p) != 0
                assert ((x//q)*a - b//q) % p == 0
            padic_prime_conditions += 1
        padic_cases += 1

def relaxed_bound(d, t, bounds):
    free = t-len(bounds)
    result = sum((F(1, d+i) for i in range(free)), F())
    prev = d+free-1
    for bound in sorted(bounds):
        prev = max(prev+1, bound)
        result += F(1, prev)
    return result

# Independent finite optimization oracle: an actual t-element set is feasible
# iff some injection of the m labels to its elements meets every lower bound.
# Unlike the implementation, no free-prefix ordering or sorted matching is used.
assignment_scenarios = 0
assignment_feasible_sets = 0
for d in range(2, 5):
    for t in range(3, 6):
        universe = range(d, d+9)
        candidates = [(ds, reciprocal_sum(ds)) for ds in combinations(universe, t)]
        for m in range(2, min(3, t)+1):
            for bounds in combinations_with_replacement(range(d, d+5), m):
                best = F()
                for ds, total in candidates:
                    feasible = any(all(x >= q for x, q in zip(assigned, bounds))
                                   for assigned in permutations(ds, m))
                    if feasible:
                        assignment_feasible_sets += 1
                        best = max(best, total)
                proposed = relaxed_bound(d, t, bounds)
                assert proposed >= best, (d, t, bounds, proposed, best)
                # Here all greedy denominators fit in the finite universe;
                # the relaxation's bound therefore equals the brute maximum.
                assert proposed == best, (d, t, bounds, proposed, best)
                assignment_scenarios += 1

result = {
    'status': 'passed',
    'k19_certificate': {'terms': len(D19), 'minimum': min(D19),
                        'denominators': D19, 'sum': str(reciprocal_sum(D19)),
                        'replacement_sum': '1/14', 'lcm': str(lcm(*D19))},
    'quadratic_actual_solutions': quadratic_cases,
    'padic_actual_sets': padic_cases,
    'padic_prime_conditions': padic_prime_conditions,
    'joint_distinct_bound_bruteforce_scenarios': assignment_scenarios,
    'joint_distinct_bound_feasible_sets': assignment_feasible_sets,
    'note': 'Tests supplement the algebraic proof, rather than establish universal validity.'
}
(OUT / 'independent_lemma_review_result.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k != 'k19_certificate'}))
print('k(19)<=36 exact certificate passed')
