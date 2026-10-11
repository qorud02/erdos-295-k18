#!/usr/bin/env python3
"""Independent residual oracles for the fixed N=18, 33-term benchmark engine.

Run after building probe_matched.cpp with the frozen source. The oracle searches
all increasing positive-integer completions, with no arbitrary denominator cap.
The input residual states test conditional pruning checks; they do not establish
a generic arbitrary-quota solver or certify the global 33-term search.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys

BASE = frozenset((18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,
                  33,34,35,36,38,39,40,43,44,45,46,48,50,52,54,
                  63,275,14143068,10457416992))
SMALL = BASE - {14143068,10457416992}
LIMITS = ((33,33),(28,33),(28,27))
SEED = 29518102026


def exhaustive(d: int, t: int, residual: Fraction, selected: int, small: int,
               mode: int) -> tuple[int, ...] | None:
    """Only positivity, exact rational subtraction, order, and quotas are used.

    For t>=2, each first denominator x has 1/x < residual, while
    residual <= t/x. Therefore floor(1/residual)+1 <= x <= floor(t/residual).
    Enumerating this exact finite necessary interval at each step exhausts the
    unbounded increasing denominator domain. No prime, harmonic, quadratic,
    greedy quota-envelope, engine helper, or two-term divisor code is reused.
    """
    cap, small_cap = LIMITS[mode]

    @lru_cache(maxsize=None)
    def walk(start: int, left: int, numerator: int, denominator: int,
             used: int, small_used: int) -> tuple[int, ...] | None:
        if used > cap or small_used > small_cap:
            return None
        if left == 0:
            return () if numerator == 0 else None
        if numerator <= 0:
            return None
        target = Fraction(numerator, denominator)
        if left == 1:
            if denominator % numerator:
                return None
            value = denominator // numerator
            if value < start or used + (value in BASE) > cap or small_used + (value in SMALL) > small_cap:
                return None
            return (value,)
        lower = max(start, denominator // numerator + 1)
        upper = left * denominator // numerator
        for value in range(lower, upper + 1):
            remainder = target - Fraction(1, value)
            found = walk(value+1, left-1, remainder.numerator, remainder.denominator,
                         used + (value in BASE), small_used + (value in SMALL))
            if found is not None:
                return (value,) + found
        return None

    return walk(d, t, residual.numerator, residual.denominator, selected, small)


def cases() -> list[dict]:
    records = []
    seen = set()

    def add(label, mode, d, t, residual, selected=0, small=0, known=None):
        residual = Fraction(residual)
        key = (mode,d,t,residual.numerator,residual.denominator,selected,small)
        if key in seen:
            return
        seen.add(key)
        records.append(dict(label=label,mode=mode,d=d,t=t,a=residual.numerator,
                            b=residual.denominator,base_selected=selected,
                            small_selected=small,known=known))

    # Exact one-term terminals, ordering, all three cap modes, and both large
    # reference members. Large states use t=1, keeping runtime independent of
    # the large denominator values.
    values = (2,17,18,19,28,29,35,36,37,38,42,43,54,55,63,64,274,275,276,
              14143067,14143068,14143069,10457416991,10457416992,10457416993)
    for mode in range(3):
        cap, small_cap = LIMITS[mode]
        for value in values:
            add("unit-witness",mode,value,1,Fraction(1,value),known=[value])
            add("unit-order-exhausted",mode,value+1,1,Fraction(1,value))
        for selected,small in ((cap,min(cap,small_cap)),
                               (cap+1,min(cap+1,small_cap)),
                               (28,28)):
            for value in (18,37,275,276,14143068,10457416992):
                add("unit-quota-boundary",mode,value,1,Fraction(1,value),selected,small)
        add("non-unit-terminal",mode,2,1,Fraction(2,5))
        add("zero-residual-positive-terms",mode,2,1,Fraction(0))

    # Genuine exact two/three-term targets around reference gaps. Counts are
    # explicit selected-prefix state, not inferred from a random denominator.
    witnesses = ((17,18),(18,19),(36,37),(42,43),(63,64),(275,276),
                 (18,19,20),(35,36,37),(42,43,44),(53,54,55),
                 (62,63,64),(273,275,276))
    count_states = ((0,0),(26,26),(27,27),(28,27),(28,28),(29,28),(33,32),(34,33))
    for mode in range(3):
        for witness in witnesses:
            target = sum((Fraction(1,x) for x in witness),Fraction())
            for selected,small in count_states:
                add("exact-target-quota-boundary",mode,min(witness),len(witness),target,selected,small,known=list(witness))

    rng = random.Random(SEED)
    # Random exact targets include feasible and quota-disallowed completions.
    for index in range(80):
        t = rng.choice((2,3))
        start = rng.choice((2,7,17,18,25,35,42,52,61))
        witness = tuple(sorted(rng.sample(range(start,start+16),t)))
        target = sum((Fraction(1,x) for x in witness),Fraction())
        selected,small = rng.choice(count_states)
        for mode in range(3):
            add("deterministic-exact-target",mode,start,t,target,selected,small,known=list(witness))
    # Arbitrary rational residuals have denominator-derived finite intervals;
    # target>=1/40 is a generator runtime choice, not an oracle search cutoff.
    for index in range(80):
        denominator = rng.randint(20,360)
        numerator = rng.randint(max(1,(denominator+39)//40),max(2,denominator//3))
        target = Fraction(numerator,denominator)
        start = rng.randint(2,44)
        t = rng.choice((1,2,3))
        selected,small = rng.choice(count_states)
        for mode in range(3):
            add("deterministic-rational",mode,start,t,target,selected,small)
    return records


def check_witness(record, output):
    values = tuple(int(x) for x in output["denominators"])
    if len(values) != record["t"]:
        raise AssertionError("wrong witness length")
    if not values or values[0] < record["d"] or any(a>=b for a,b in zip(values,values[1:])):
        raise AssertionError("wrong witness order or minimum")
    if sum((Fraction(1,x) for x in values),Fraction()) != Fraction(record["a"],record["b"]):
        raise AssertionError("wrong exact witness sum")
    cap,small_cap = LIMITS[record["mode"]]
    if record["base_selected"] + sum(x in BASE for x in values) > cap:
        raise AssertionError("witness exceeds reference quota")
    if record["small_selected"] + sum(x in SMALL for x in values) > small_cap:
        raise AssertionError("witness exceeds small-reference quota")


def cli_scope(engine: str | None) -> list[dict]:
    if not engine:
        raise ValueError("--engine is required to test the production CLI scope")
    checks = []
    for args in (("--minimum","17"),("--terms","32")):
        result = subprocess.run([engine,*args],text=True,capture_output=True,timeout=10)
        if result.returncode == 0:
            raise AssertionError(f"production CLI accepted invalid scope {args}")
        if "benchmark fixed to certified minimum 18, terms 33" not in result.stderr:
            raise AssertionError(f"unexpected invalid-scope diagnostic {args}: {result.stderr}")
        if any(json.loads(line).get("status")=="witness" for line in result.stdout.splitlines() if line.lstrip().startswith("{")):
            raise AssertionError("invalid-scope CLI emitted witness")
        checks.append(dict(arguments=list(args),returncode=result.returncode,
                           diagnostic=result.stderr.strip()))
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe",required=True,help="compiled probe_matched executable")
    parser.add_argument("--engine",required=True,help="compiled frozen matched-search executable")
    parser.add_argument("--output",type=Path,default=Path("matched-oracle-validation.json"))
    args = parser.parse_args()
    records = cases()
    if len(records)<300:
        raise AssertionError("expected at least 300 deterministic residual tests")
    encoded = "".join(f'{r["mode"]} {r["d"]} {r["t"]} {r["a"]} {r["b"]} {r["base_selected"]} {r["small_selected"]}\n' for r in records)
    result = subprocess.run([args.probe],input=encoded,text=True,capture_output=True,timeout=180)
    if result.returncode:
        raise AssertionError(f"probe failed ({result.returncode}): {result.stderr}")
    outputs = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    if len(outputs)!=len(records):
        raise AssertionError(f"expected one JSON result per input: {len(outputs)} != {len(records)}")
    totals = Counter()
    modes = {str(m):Counter() for m in range(3)}
    groups = Counter()
    for index,(record,output) in enumerate(zip(records,outputs),1):
        if output.get("index")!=index or output.get("status") not in ("witness","exhausted"):
            raise AssertionError(f"unexpected probe result {index}: {output}")
        expected = exhaustive(record["d"],record["t"],Fraction(record["a"],record["b"]),
                              record["base_selected"],record["small_selected"],record["mode"])
        observed = output["status"]=="witness"
        if observed != (expected is not None):
            raise AssertionError(f"oracle verdict mismatch {index}: {record}; expected={expected}; observed={output}")
        if observed:
            check_witness(record,output)
        totals[output["status"]]+=1
        modes[str(record["mode"])][output["status"]]+=1
        groups[record["label"]]+=1
        for field in ("nodes","prime_prunes","joint_prunes","harmonic_prunes","quota_prunes","two_candidates","quadratic_two_prunes"):
            totals[field]+=output[field]
    scope_checks = cli_scope(args.engine)
    summary = dict(status="passed",seed=SEED,residual_cases=len(records),
                   input_sha256=hashlib.sha256(encoded.encode()).hexdigest(),
                   source_sha256=hashlib.sha256((Path(__file__).parent/"matched-search.cpp").read_bytes()).hexdigest(),
                   reference_count=len(BASE),small_reference_count=len(SMALL),
                   mode_limits={str(i):dict(reference=q,small_reference=qs) for i,(q,qs) in enumerate(LIMITS)},
                   verdict_counts={k:totals[k] for k in ("witness","exhausted")},
                   modes={m:dict(v) for m,v in modes.items()},groups=dict(groups),
                   observed_engine_counters={k:v for k,v in totals.items() if k not in ("witness","exhausted")},
                   production_cli_scope_checks=scope_checks,
                   oracle="exact unpruned rational recurrence; order and quota checks; no arbitrary denominator cap",
                   scope="conditional residual checks for t=1,2,3; production CLI fixed to N=18 and total 33 terms")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,sort_keys=True))

if __name__=="__main__":
    main()
