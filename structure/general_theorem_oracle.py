"""Independent finite oracles for exchange, overlap quotas and dual bounds.

No production search or optimizer is imported. Exact Fraction arithmetic only.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
from random import Random
import json

def total(items, weights):
    return sum((weights[x] for x in items), Q())

def exchange_exists(U, A, weights, d, r, reuse=True, core=frozenset()):
    for R in combinations(sorted(A), r):
        if not set(R) >= set(core):
            continue
        kept = A-set(R)
        allowed = sorted(U-(kept if reuse else A))
        for C in combinations(allowed, r-d):
            if total(R, weights) == total(C, weights):
                return True
    return False

exchange_cases = 0
# Exhaust every nonempty reference subset and every positive {1,2}-weighting
# on a five-element universe, including r=d and r=m edges.
U = set(range(5))
for values in product((1, 2), repeat=5):
    weights = dict(enumerate(map(Q, values)))
    for size in range(1, 6):
        for aa in combinations(sorted(U), size):
            A = set(aa); m = len(A)
            for d in range(1, m+1):
                all_B = [set(bb) for bb in combinations(sorted(U), m-d)
                         if total(bb, weights) == total(A, weights)]
                for r in range(d, m+1):
                    local = exchange_exists(U, A, weights, d, r)
                    global_overlap = any(len(A & B) >= m-r for B in all_B)
                    assert local == global_overlap
                    if not local:
                        assert all(len(A & B) <= m-r-1 for B in all_B)
                    exchange_cases += 1

# The no-reuse variant is false, even for actual unit fractions.
UU = {2, 3, 6, 7, 42}; AA = {2, 3, 7, 42}; BB = {2, 3, 6}
ww = {x: Q(1, x) for x in UU}
assert total(AA, ww) == total(BB, ww) == 1
assert not exchange_exists(UU, AA, ww, 1, 4, reuse=False)
assert exchange_exists(UU, AA, ww, 1, 4, reuse=True)

fixed_core_cases = 0
core_rng = Random(2956)
for _ in range(512):
    UU = set(range(6))
    weights = {i: Q(core_rng.randrange(1, 5)) for i in UU}
    AA = set(core_rng.sample(sorted(UU), core_rng.randrange(1, 7)))
    m = len(AA); d = core_rng.randrange(1, m+1); r = core_rng.randrange(d, m+1)
    core = set(core_rng.sample(sorted(AA), core_rng.randrange(r+1)))
    local = exchange_exists(UU, AA, weights, d, r, core=core)
    BB = [set(B) for B in combinations(sorted(UU), m-d)
          if total(B, weights) == total(AA, weights)]
    assert local == any(len(B & (AA-core)) >= m-r for B in BB)
    if not local:
        assert all(len(B & (AA-core)) <= m-r-1 for B in BB)
    fixed_core_cases += 1

def single_greedy(allowed, A, t, quota):
    selected = []; used = 0
    for n in allowed:
        if n in A and used >= quota:
            continue
        if len(selected) == t:
            break
        selected.append(n); used += n in A
    return selected if len(selected) == t else None

single_cases = 0
universe = tuple(range(2, 10)); n = len(universe)
grouped = {t: [(set(B), sum((Q(1, d) for d in B), Q()))
               for B in combinations(universe, t)] for t in range(n+1)}
for mask in range(1 << n):
    A = {universe[i] for i in range(n) if mask & (1 << i)}
    for t in range(n+1):
        for quota in range(min(t, len(A))+1):
            values = [v for B, v in grouped[t] if len(B & A) <= quota]
            expected = max(values) if values else None
            result = single_greedy(universe, A, t, quota)
            actual = sum((Q(1, d) for d in result), Q()) if result is not None else None
            assert actual == expected
            if result is not None:
                for B, _ in grouped[t]:
                    if len(B & A) <= quota:
                        assert all(g <= b for g, b in zip(result, sorted(B)))
            single_cases += 1

def pool_and_dual(D, t, references, quotas, lambdas, forbidden):
    union = set().union(*references)
    pool = {n for n in union if n >= D and n not in forbidden}
    outside = []; n = D
    while len(outside) < t:
        if n not in union and n not in forbidden:
            outside.append(n)
        n += 1
    pool.update(outside)
    def adjusted(n):
        return Q(1, n)-sum((lam for A, lam in zip(references, lambdas) if n in A), Q())
    top = sum(sorted((adjusted(n) for n in pool), reverse=True)[:t], Q())
    bound = top+sum((lam*q for lam, q in zip(lambdas, quotas)), Q())
    return pool, top, bound, adjusted

def atom_enumeration(pool, references, quotas, t):
    atoms = {}
    for n in sorted(pool):
        mask = tuple(i for i, A in enumerate(references) if n in A)
        atoms.setdefault(mask, []).append(n)
    data = list(atoms.items()); best = None
    def visit(i, chosen, used, score):
        nonlocal best
        if i == len(data):
            if chosen == t:
                best = score if best is None else max(best, score)
            return
        mask, values = data[i]
        addition = Q()
        for j in range(min(t-chosen, len(values))+1):
            if all(used[k]+j <= quotas[k] for k in mask):
                new = list(used)
                for k in mask:new[k] += j
                visit(i+1, chosen+j, new, score+addition)
            if j < len(values):addition += Q(1, values[j])
    visit(0, 0, [0]*len(references), Q())
    return best

rng = Random(29520261012)
dual_cases = subsets = feasible = atom_cases = 0
for _ in range(160):
    D = rng.randrange(2, 6); t = rng.randrange(0, 4)
    refs = [{n for n in range(2, 10) if rng.randrange(3) == 0}
            for _ in range(rng.randrange(0, 4))]
    quotas = [rng.randrange(t+1) for _ in refs]
    lambdas = [Q(rng.randrange(8), rng.randrange(1, 14)) for _ in refs]
    forbidden = {n for n in range(2, 11) if rng.randrange(10) == 0}
    pool, top, dual, adjusted = pool_and_dual(D, t, refs, quotas, lambdas, forbidden)
    # This horizon contains all exceptions plus at least t ordinary terms.
    full = [n for n in range(D, 17) if n not in forbidden]
    assert pool <= set(full)
    assert top == sum(sorted((adjusted(n) for n in full), reverse=True)[:t], Q())
    primal = None
    for B in combinations(full, t):
        subsets += 1
        if all(len(set(B) & A) <= q for A, q in zip(refs, quotas)):
            value = sum((Q(1, n) for n in B), Q())
            feasible += 1
            primal = value if primal is None else max(primal, value)
            assert value <= dual
    assert primal is not None
    # A separate atom-count enumeration, rather than a subset optimizer,
    # must match the exhaustive constrained optimum exactly.
    assert atom_enumeration(pool, refs, quotas, t) == primal
    dual_cases += 1; atom_cases += 1

A1 = {10, 11, 13}; A2 = {10, 12, 13}
assert Q(1, 10)+Q(1, 14) == Q(6, 35) < Q(23, 132) == Q(1, 11)+Q(1, 12)
_, top, bound, adjusted = pool_and_dual(10, 2, [A1, A2], [1, 1],
                                     [Q(3, 154), Q(1, 84)], set())
assert adjusted(11) == adjusted(12) == adjusted(14) == Q(1, 14)
assert bound == Q(23, 132)

# Negative multipliers invalidate quota substitution: a single known feasible
# set violates the apparent "bound" from the same formula.
_, _, invalid_bound, _ = pool_and_dual(2, 1, [{2}], [1], [Q(-1)], set())
# This particular example is not necessarily a counterexample; use a quota
# larger than any possible overlap to make the unjustified negative penalty
# decisive while feasibility is unchanged.
_, _, invalid_bound, _ = pool_and_dual(2, 1, [{2}], [3], [Q(-1)], set())
assert Q(1, 2) > invalid_bound

result = {'status': 'passed', 'exchange_equivalence_cases': exchange_cases,
          'fixed_core_exchange_cases': fixed_core_cases,
          'single_quota_exact_cases': single_cases, 'dual_random_cases': dual_cases,
          'dual_subsets_enumerated': subsets, 'dual_feasible_subsets': feasible,
          'atom_exact_cases': atom_cases, 'crossing_quota_optimum': '23/132',
          'edge_counterexamples': ['forbidding_removed_term_reuse', 'negative_multiplier']}
Path(__file__).with_name('general_theorem_oracle_result.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
