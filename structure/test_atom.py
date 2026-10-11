"""Independent exact checks of the atom envelope; standard library only."""
import argparse
from fractions import Fraction
from itertools import combinations
import importlib.util
import json
from pathlib import Path
import random
import sys

from atom_tools import AtomLimitExceeded, reciprocal_atom_envelope


def load_optional(name, paths):
    for path in paths:
        if path.is_file():
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module, path.name
    return None, None


def brute(D, t, references, quotas, forbidden, last):
    # This interval is deliberately larger than the atom support. In the
    # generated cases every exceptional integer is <=D+6 and t<=4, so the
    # first t members of the complement are <=D+10. It therefore contains
    # the infinite-universe optimum without imposing a solution-size cap.
    allowed = [d for d in range(D, last + 1) if d not in forbidden]
    best = None
    subsets = feasible = 0
    for chosen in combinations(allowed, t):
        subsets += 1
        if any(len(set(chosen) & A) > q for A, q in zip(references, quotas)):
            continue
        feasible += 1
        weight = sum((Fraction(1, d) for d in chosen), Fraction())
        if best is None or weight > best:
            best = weight
    assert best is not None
    return best, subsets, feasible


def one_quota_formula(D, t, A, q, forbidden):
    inside = sorted(d for d in A if d >= D and d not in forbidden)[:t]
    outside = []
    d = D
    while len(outside) < t:
        if d not in A and d not in forbidden:
            outside.append(d)
        d += 1
    return max(sum((Fraction(1, d) for d in inside[:j] + outside[:t-j]), Fraction())
               for j in range(min(q, t, len(inside)) + 1))


def assert_certificate(maximum, certificate, D, t, references, quotas, forbidden):
    chosen = tuple(map(int, certificate["attaining_denominators"]))
    assert certificate["complete"] is True
    assert len(chosen) == len(set(chosen)) == t
    assert all(d >= D and d not in forbidden for d in chosen)
    assert all(len(set(chosen) & A) <= q for A, q in zip(references, quotas))
    assert sum((Fraction(1, d) for d in chosen), Fraction()) == maximum
    assert Fraction(certificate["maximum"]) == maximum


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).with_name("atom-test-results.json"))
    parser.add_argument("--dual-module", type=Path)
    parser.add_argument("--quota-module", type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    dual_paths = [args.dual_module] if args.dual_module else [
        here / "dual_tools.py", here.parent / "repo" / "structure" / "dual_tools.py"]
    quota_paths = [args.quota_module] if args.quota_module else [
        here / "quota_tools.py", here.parent / "search33" / "quota_tools.py"]
    dual, dual_source = load_optional("checked_dual", dual_paths)
    quota, quota_source = load_optional("checked_quota", quota_paths)
    rng = random.Random(29520261012)
    totals = {"random_cases": 0, "enumerated_subsets": 0,
              "feasible_subsets": 0, "single_quota_formula_checks": 0,
              "single_quota_api_checks": 0, "laminar_api_checks": 0,
              "dual_bound_checks": 0, "resource_guard_checks": 0,
              "invalid_input_checks": 0}
    for _ in range(500):
        D = rng.randint(1, 10)
        t = rng.randrange(5)
        s = rng.randrange(4)
        exceptional = list(range(max(1, D - 2), D + 7))
        references = [{d for d in exceptional if rng.randrange(2)} for _ in range(s)]
        quotas = [rng.randrange(t + 2) for _ in range(s)]
        forbidden = {d for d in exceptional if rng.randrange(6) == 0}
        actual, cert = reciprocal_atom_envelope(D, t, references, quotas, forbidden)
        expected, count, feasible = brute(D, t, references, quotas, forbidden, D + 11)
        assert actual == expected, (D, t, references, quotas, forbidden, actual, expected)
        assert_certificate(actual, cert, D, t, references, quotas, forbidden)
        totals["random_cases"] += 1
        totals["enumerated_subsets"] += count
        totals["feasible_subsets"] += feasible
        if s == 1:
            assert actual == one_quota_formula(D, t, references[0], quotas[0], forbidden)
            totals["single_quota_formula_checks"] += 1
            if quota is not None:
                no_forbidden, _ = reciprocal_atom_envelope(D, t, references, quotas)
                assert no_forbidden == quota.quota_harmonic_bound(references[0], D, t, quotas[0])
                totals["single_quota_api_checks"] += 1
        if dual is not None:
            multipliers = [Fraction(rng.randrange(7), rng.randint(1, 30)) for _ in range(s)]
            upper, _ = dual.reciprocal_dual_bound(D, t, references, quotas, multipliers, forbidden)
            assert upper >= actual, (actual, upper)
            totals["dual_bound_checks"] += 1

    for _ in range(200):
        D = rng.randint(1, 10)
        t = rng.randrange(5)
        whole = set(range(D, D + 7))
        left = {d for d in whole if d % 2 == 0}
        right = whole - left
        nested = {d for d in left if rng.randrange(2)}
        references = [whole, left, right, nested]
        quotas = [rng.randrange(t + 2) for _ in references]
        actual, cert = reciprocal_atom_envelope(D, t, references, quotas)
        expected, count, feasible = brute(D, t, references, quotas, set(), D + 11)
        assert actual == expected
        assert_certificate(actual, cert, D, t, references, quotas, set())
        totals["random_cases"] += 1
        totals["enumerated_subsets"] += count
        totals["feasible_subsets"] += feasible
        if quota is not None:
            assert actual == quota.laminar_quota_bound(references, D, t, quotas)
            totals["laminar_api_checks"] += 1

    maximum, crossing = reciprocal_atom_envelope(
        10, 2, [{10, 11, 13}, {10, 12, 13}], [1, 1])
    assert maximum == Fraction(23, 132)
    assert crossing["attaining_denominators"] == ["11", "12"]
    naive = Fraction(1, 10) + Fraction(1, 14)
    assert naive == Fraction(6, 35) < maximum
    if dual is not None:
        upper, _ = dual.reciprocal_dual_bound(
            10, 2, [{10, 11, 13}, {10, 12, 13}], [1, 1],
            [Fraction(3, 154), Fraction(1, 84)])
        assert upper == maximum
        totals["dual_bound_checks"] += 1

    # Huge sparse exceptional denominators must not create a scanning cap.
    huge = 10 ** 80 + 123
    value, sparse = reciprocal_atom_envelope(10, 3, [{10, huge}], [0], [11])
    assert value == Fraction(1, 12) + Fraction(1, 13) + Fraction(1, 14)
    assert sparse["attaining_denominators"] == ["12", "13", "14"]
    empty, _ = reciprocal_atom_envelope(1, 0, [{1, 2}], [0])
    assert empty == 0

    for options in [{"max_states": 1}, {"max_transitions": 1}]:
        try:
            reciprocal_atom_envelope(10, 2, [{10, 11, 13}, {10, 12, 13}], [1, 1], **options)
        except AtomLimitExceeded:
            totals["resource_guard_checks"] += 1
        else:
            raise AssertionError("resource guard did not raise")
    invalid = [
        (0, 1, [], [], ()), (True, 1, [], [], ()),
        (1, -1, [], [], ()), (1, 1.0, [], [], ()),
        (1, 1, [{1}], [], ()), (1, 1, [{1}], [-1], ()),
        (1, 1, [{True}], [1], ()), (1, 1, [{1.5}], [1], ()),
        (1, 1, [], [], [0]), (1, 1, [], [], [False])]
    for arguments in invalid:
        try:
            reciprocal_atom_envelope(*arguments)
        except ValueError:
            totals["invalid_input_checks"] += 1
        else:
            raise AssertionError(("invalid input accepted", arguments))
    results = {"passed": True, "python": sys.version,
               "seed": 29520261012, "totals": totals,
               "dual_module_checked": dual_source,
               "quota_module_checked": quota_source,
               "crossing_counterexample": {"exact_maximum": str(maximum),
                   "attaining_denominators": ["11", "12"],
                   "naive_greedy_sum": str(naive)},
               "sparse_exceptional_denominator_digits": len(str(huge)),
               "finite_oracle_window": "D..D+11; all generated exceptions <=D+6 and t<=4"}
    args.output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
