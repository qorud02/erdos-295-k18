"""Exact reciprocal envelopes for finitely many overlap quotas.

The denominator universe is infinite. Finite membership atoms and the first
terms members of the outside atom give exact finite support for this
upper-envelope relaxation. No cap on actual solution denominators is used.
Only the Python standard library is required.
"""
from fractions import Fraction


class AtomLimitExceeded(RuntimeError):
    """A resource guard was reached; no complete envelope is returned."""


def _integer(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def reciprocal_atom_envelope(minimum, terms, references, quotas, forbidden=(),
                             *, max_states=200000, max_transitions=5000000):
    """Return (exact maximum, finite evaluation certificate).

    Maximize sum(1/d for d in B), where B has exactly terms distinct
    positive integers >= minimum, avoids forbidden, and satisfies
    |B intersect references[i]| <= quotas[i]. References and forbidden must
    be finite iterables of positive integers. The maximum is attained.

    This optimizes cardinality and quotas, not a prescribed reciprocal sum.
    Resource limits raise AtomLimitExceeded instead of returning a partial
    value. All arithmetic affecting the optimum uses fractions.Fraction.
    """
    D = _integer(minimum, "minimum", 1)
    t = _integer(terms, "terms")
    references = [frozenset(_integer(d, "denominator", 1) for d in A)
                  for A in references]
    quotas = [_integer(q, "quota") for q in quotas]
    if len(references) != len(quotas):
        raise ValueError("references and quotas must have equal length")
    forbidden = frozenset(_integer(d, "forbidden denominator", 1)
                          for d in forbidden)
    max_states = _integer(max_states, "max_states", 1)
    max_transitions = _integer(max_transitions, "max_transitions", 1)
    union = frozenset().union(*references)
    atoms = {}
    for d in sorted(union):
        if d < D or d in forbidden:
            continue
        mask = sum(1 << i for i, A in enumerate(references) if d in A)
        atoms.setdefault(mask, []).append(d)
    # Only the t smallest denominators of each atom can help maximize.
    atoms = {mask: values[:t] for mask, values in atoms.items()}
    outside = []
    d = D
    while len(outside) < t:
        if d not in union and d not in forbidden:
            outside.append(d)
        d += 1
    atoms[0] = outside
    prefixes = {}
    for mask, values in atoms.items():
        prefix = [Fraction()]
        for value in values:
            prefix.append(prefix[-1] + Fraction(1, value))
        prefixes[mask] = prefix

    # State = (selected count, tuple of used quotas). Values carry exact
    # weight and a lexicographically deterministic attaining set.
    zero_counts = (0,) * len(references)
    states = {(0, zero_counts): (Fraction(), ())}
    peak_states = 1
    transitions = 0
    layers = []
    for mask in sorted(atoms):
        if mask == 0:
            continue
        indices = tuple(i for i in range(len(references)) if mask >> i & 1)
        candidates = atoms[mask]
        following = {}
        for (selected_count, used), (weight, chosen) in states.items():
            capacity = min(t - selected_count, len(candidates))
            if indices:
                capacity = min(capacity, *(quotas[i] - used[i] for i in indices))
            for count in range(capacity + 1):
                transitions += 1
                if transitions > max_transitions:
                    raise AtomLimitExceeded("max_transitions reached; envelope incomplete")
                new_used = tuple(value + (count if i in indices else 0)
                                 for i, value in enumerate(used))
                key = (selected_count + count, new_used)
                new_weight = weight + prefixes[mask][count]
                new_chosen = tuple(sorted(chosen + tuple(candidates[:count])))
                previous = following.get(key)
                if (previous is None or new_weight > previous[0] or
                        (new_weight == previous[0] and new_chosen < previous[1])):
                    following[key] = (new_weight, new_chosen)
                if len(following) > max_states:
                    raise AtomLimitExceeded("max_states reached; envelope incomplete")
        states = following
        peak_states = max(peak_states, len(states))
        layers.append({"mask": mask, "state_count": len(states)})

    best = None
    for (selected_count, used), (weight, chosen) in states.items():
        count = t - selected_count
        candidate = (weight + prefixes[0][count],
                     tuple(sorted(chosen + tuple(outside[:count]))))
        if (best is None or candidate[0] > best[0] or
                (candidate[0] == best[0] and candidate[1] < best[1])):
            best = candidate
    # Finite reference/forbidden sets leave infinitely many quota-free
    # integers, so a t-element feasible set always exists.
    maximum, attaining = best
    certificate = {
        "complete": True, "minimum": D, "terms": t,
        "references": [[str(d) for d in sorted(A)] for A in references],
        "quotas": quotas, "forbidden": [str(d) for d in sorted(forbidden)],
        "atoms": [{"mask": mask,
                   "membership_indices": [i for i in range(len(references)) if mask >> i & 1],
                   "candidates": [str(d) for d in atoms[mask]],
                   "prefix_sums": [str(w) for w in prefixes[mask]]}
                  for mask in sorted(atoms)],
        "attaining_denominators": [str(d) for d in attaining],
        "realized_counts": [len(set(attaining) & A) for A in references],
        "maximum": str(maximum), "peak_states": peak_states,
        "final_states": len(states), "transitions": transitions,
        "layers": layers,
        "support_note": "Exact finite support for the quota envelope; no bound on denominators in exact-sum solutions."
    }
    return maximum, certificate


if __name__ == "__main__":
    import json
    maximum, certificate = reciprocal_atom_envelope(
        10, 2, [{10, 11, 13}, {10, 12, 13}], [1, 1])
    assert maximum == Fraction(23, 132)
    print(json.dumps(certificate, indent=2))
