"""Exact reciprocal upper bounds under several possibly crossing quotas.

The inequality is classical Lagrangian weak duality. Finite exceptional
denominator sets make its infinite-universe evaluation finite and exact.
No local-search exhaustion or novelty assumption is embedded in this API.
"""
from fractions import Fraction
import json


def _integer(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def reciprocal_dual_bound(minimum, terms, references, quotas, multipliers,
                          forbidden=()):
    """Return a rational bound and its finite evaluation certificate.

    Every t-element set B of permitted integers >= minimum satisfying
    |B intersect references[i]| <= quotas[i] has reciprocal sum <= bound.
    Multipliers must be nonnegative exact rationals (never floats).
    The references and forbidden set must be finite.
    """
    D = _integer(minimum, "minimum", 1)
    t = _integer(terms, "terms")
    references = [frozenset(_integer(d, "denominator", 1) for d in A)
                  for A in references]
    quotas = [_integer(q, "quota") for q in quotas]
    if len(references) != len(quotas) or len(quotas) != len(multipliers):
        raise ValueError("references, quotas, multipliers must have equal length")
    weights = []
    for value in multipliers:
        if isinstance(value, (float, bool)):
            raise ValueError("multipliers must be exact rationals")
        weight = Fraction(value)
        if weight < 0:
            raise ValueError("multipliers must be nonnegative")
        weights.append(weight)
    forbidden = frozenset(_integer(d, "forbidden denominator", 1)
                          for d in forbidden)
    union = frozenset().union(*references)
    inside = {d for d in union if d >= D and d not in forbidden}
    outside = []
    d = D
    while len(outside) < t:
        if d not in union and d not in forbidden:
            outside.append(d)
        d += 1
    pool = inside | set(outside)

    def adjusted(d):
        return Fraction(1, d) - sum(
            (weight for A, weight in zip(references, weights) if d in A),
            Fraction())

    ranked = sorted(pool, key=lambda d: (-adjusted(d), d))
    selected = ranked[:t]
    penalty = sum((weight*q for weight, q in zip(weights, quotas)), Fraction())
    top_sum = sum((adjusted(d) for d in selected), Fraction())
    bound = penalty + top_sum
    return bound, {
        "minimum": D, "terms": t,
        "references": [sorted(A) for A in references], "quotas": quotas,
        "multipliers": [str(w) for w in weights],
        "forbidden": sorted(forbidden), "outside_candidates": outside,
        "ranked_pool": [{"denominator": str(d), "adjusted_weight": str(adjusted(d))}
                        for d in ranked],
        "selected": [str(d) for d in selected],
        "penalty": str(penalty), "top_sum": str(top_sum), "bound": str(bound)
    }


if __name__ == "__main__":
    bound, certificate = reciprocal_dual_bound(
        10, 2, [{10, 11, 13}, {10, 12, 13}], [1, 1],
        [Fraction(3, 154), Fraction(1, 84)])
    assert bound == Fraction(1, 11) + Fraction(1, 12)
    print(json.dumps(certificate, indent=2))
