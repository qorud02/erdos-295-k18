"""Finite exhaustive oracles and exact edge cases for the dual bound."""
from fractions import Fraction
from itertools import combinations
from random import Random
from dual_tools import reciprocal_dual_bound
import json


def main():
    rng = Random(295)
    checked = feasible = rankings = 0
    for case in range(240):
        D = rng.randrange(1, 12)
        t = rng.randrange(0, 5)
        universe = list(range(D, D+9))
        references = [{d for d in universe if rng.randrange(3) == 0}
                      for _ in range(rng.randrange(0, 4))]
        quotas = [rng.randrange(0, t+1) for _ in references]
        multipliers = [Fraction(rng.randrange(0, 15), rng.randrange(1, 20))
                       for _ in references]
        forbidden = {d for d in universe if rng.randrange(12) == 0}
        bound, certificate = reciprocal_dual_bound(
            D, t, references, quotas, multipliers, forbidden)
        # Larger finite universe includes every reference exception and more
        # than t permitted ordinary terms. Exhaustive ranking is independent
        # of the pool reduction used by the production implementation.
        horizon = D+14
        allowed = [d for d in range(D, horizon+1) if d not in forbidden]
        adjusted = lambda d: Fraction(1, d)-sum(
            (w for A, w in zip(references, multipliers) if d in A), Fraction())
        brute_top = sum(sorted((adjusted(d) for d in allowed), reverse=True)[:t],
                        Fraction())
        assert Fraction(certificate['top_sum']) == brute_top
        rankings += 1
        for B in combinations(allowed, t):
            checked += 1
            if all(len(set(B) & A) <= q for A, q in zip(references, quotas)):
                feasible += 1
                assert sum((Fraction(1, d) for d in B), Fraction()) <= bound

    # Crossing quotas defeat "take the smallest permitted denominator".
    A = [{10, 11, 13}, {10, 12, 13}]
    assert Fraction(1, 10)+Fraction(1, 14) < Fraction(1, 11)+Fraction(1, 12)
    bound, certificate = reciprocal_dual_bound(
        10, 2, A, [1, 1], [Fraction(3, 154), Fraction(1, 84)])
    assert bound == Fraction(23, 132)
    # No reference quotas reduces to the ordinary distinct harmonic bound.
    b, _ = reciprocal_dual_bound(18, 33, [], [], [])
    assert b == sum((Fraction(1, d) for d in range(18, 51)), Fraction())
    rejected = 0
    for args in [
        (0, 2, [], [], []), (10, -1, [], [], []),
        (10, 2, A, [1], [0, 0]), (10, 2, A, [1, 1], [-1, 0]),
        (10, 2, A, [1, 1], [0.1, 0]), (10, 2, [{0}], [1], [0])]:
        try:
            reciprocal_dual_bound(*args)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("invalid premise accepted")
    print(json.dumps({"status": "passed", "random_cases": rankings,
                      "enumerated_subsets": checked, "feasible_subsets": feasible,
                      "invalid_inputs_rejected": rejected,
                      "crossing_example_optimum": str(bound)}, indent=2))


if __name__ == '__main__':
    main()
