# Exact local shortening and the 33-term search frontier

Sources and logs in this note are in `search-records/`. Run its commands from that directory. General proofs are in [STRUCTURE.md](STRUCTURE.md).

These computations concern the finite question whether k(18) is 33 or 34.
The minimum remains unresolved. The known 34-term certificate is the baseline
stored in `local_surgery.py`; its exact reciprocal sum is checked on import.

## Completed local result

No choice of five denominators from the baseline can be replaced by four
distinct denominators at least 18 while preserving all other baseline terms.
All C(34,5)=278,256 subsets were exhausted, with no denominator cap, in
95.781 seconds and 1,139,247 recursive states. The log is
`surgery5-all.jsonl`. Exact integer arithmetic is used throughout; there is
no heuristic arithmetic rejection, candidate truncation, or skipped tail.

Consequently, every 33-term representation, if one exists, shares at most
28 denominators with this 34-term certificate. To see this, suppose it shared
at least 29. Remove the differing baseline terms, and if fewer than five were
removed, also remove enough common terms to make five. The new representation
then replaces those five terms by four, contrary to the completed search.

Additional completed checks are:

| Removed / replacement | Removed-subset family | Cases | States | Seconds |
|---|---|---:|---:|---:|
| 3 / 2 | All subsets | 5,984 | 5,984 | 0.375 |
| 4 / 3 | All subsets | 46,376 | 69,812 | 6.172 |
| 4 / 3 | Both large tail denominators included | 496 | 5,353 | 0.328 |
| 5 / 4 | Both large tail denominators included | 4,960 | 366,109 | 13.125 |
| 6 / 5 | Both large tail denominators included | 35,960 | See two logs | 257.625 including replay |

The last family was completed across `surgery6-large2.jsonl` and
`surgery6-large2-resume.jsonl`. The first run completed indices 0..33953,
then interrupted index 33954. The second run restarted at 33954 and completed
through 35959. Thus every subset in the family was completely searched.

## Exact enumeration

After removing S, the unchanged denominators are forbidden to new terms.
For a reduced positive residual a/b and t>=2 remaining terms, the smallest
next denominator x satisfies floor(b/a)+1 <= x < t*b/a. This is a finite
interval. The sum of reciprocals of the t smallest permitted denominators
starting at x is an upper bound, so values above its exact harmonic cutoff
are excluded.
For a two-term tail, y=bx/(ax-b) must be an integer greater than x.
The necessary inequality x^2-a*x+b>=0 sharpens the finite interval; it is
proved in the earlier release's `proofs.md`, section 3. The final denominator
is computed exactly and has no imposed upper limit.

`validate_local.py` passed 1,000 seeded genuine-witness controls with forbidden
denominators and 2,000 comparisons to unpruned exact two-term enumeration.
Results are in `local-validation.json`.

## Global prefix restriction and unfinished work

`audit_frontier.py` combines the preserved, completed earlier prefix runs
with exact harmonic bounds. Its `frontier-manifest.json` records every
coverage step. Every possible 33-term representation must contain the
consecutive initial denominators 18 through 28. Its next denominator must
be 29 or 30: the alternatives 31, 32 and 33 were exhausted in the new runs;
all larger values fail the harmonic bound.

The prefix ending in 31 was exhausted both with joint prime-cover pruning
(51,877 states, 3.573 seconds) and without it (74,325 states, 3.839 seconds).
The preserved C++ engine's validation passed 10,000 square-root controls,
10,000 rational-reduction controls, 1,000 two-term oracles, 10,000 genuine
prime-cover controls, and 100 small full searches with pruning on and off.

The surviving prefix 18,...,28,30 timed out with joint pruning after
90.074 seconds / 1,797,120 states and without it after 180.045 seconds /
4,846,592 states. The earlier 18,19,20,21 pilot also timed out after
90.008 seconds / 3,894,272 states. These are incomplete searches.

`checkpoint-search.cpp` changes only the final output of the preserved
`cpp-source-used.cpp`, adding the actual DFS stack at interruption. The
completed prefix ending in 31 checks that counters agree after this change.
`checkpoint_frontier.py` converts a 60-second interrupted run into a
restartable partition, `resume-frontier.json`. Its interrupted subtree is
replayed in full, and all right siblings are retained as finite intervals.
The global branch 18,...,29 also remains unsearched in this extension.

## Reusable conditional quota bound

Let A be a reference set of m distinct denominators, and let a target
representation have the same reciprocal sum and m-d terms. Suppose every
replacement of r reference terms by r-d terms, retaining the other reference
terms, has been excluded. Then every target representation shares at most
m-r-1 denominators with A. If it shared more, its differing terms could be
padded with common terms to give a forbidden r-to-r-d replacement.

This implication supports arbitrary cardinality deficit d. Its premise is
a mathematical proof or a completed exhaustive local search; the formula
alone does not certify that premise. Here m=34, r=5 and d=1 give quota 28.

At a search state with c reference denominators already selected, at most
q=28-c further reference denominators can be used. Among t distinct remaining
denominators at least D, the largest permitted reciprocal sum is obtained
by taking the smallest denominators in order, skipping reference denominators
after their quota is used. This is the elementary greedy maximum for two
groups with one capacity constraint. Within each group smaller denominators
always dominate larger ones; exchanging a missing greedy term into an optimum
preserves cardinality and the capacity, and cannot decrease the sum.

`quota_tools.py` implements the general formula, the exact greedy maximum,
fixed-prefix bounds, and a monotone next-denominator upper bound for any
finite reference A. It supports arbitrary Python integers. Negative remaining
quota returns an infeasible state. `validate_quota.py` compares its bounds to
3,318 finite exhaustive subset oracles and 200 arbitrary-reference oracles,
checks 200 next-denominator boundaries, and tests 10,000 genuine subset sums.

`quota-search.cpp` is a separate C++ case-study engine. It retains the original
source and logs, counts reference terms at every state, checks the capacity
in one- and two-term tails, and includes the selected-reference count in failed
state memo keys. Its conclusions explicitly depend on the completed 5-to-4
exclusion. `quota-probe.cpp` compares the C++ bound with the validated generic
Python API, including reference denominators above the 32-bit unsigned range.
Quota-based search timeouts remain unfinished searches.

The fixed-core family yields a stronger group statement. If only the r-term
removed subsets containing C have been excluded, then every target obeys
`|B intersect (A minus C)| <= m-r-1`. Indeed, `(A minus B) union C` must have
at least r+1 elements: otherwise pad it to an r-subset and reinsert any removed
common terms in the replacement. In the present certificate, the completed
6-to-5 family fixes C to the two large denominators, so a 33-term target uses
at most 27 of the other 32 reference denominators. Together with the full
reference capacity 28, this gives two nested capacity constraints.

`verify_local_premises.py` checks both completed-family counts and the exact
resume boundary: indices 0..33953 in the first 6-to-5 run, then 33954..35959
in the resumed run. It also checks the baseline rational and LCM sums. Its
receipt is `local-premises-validation.json`.

The generic `laminar_quota_denominators` and `laminar_quota_bound` APIs handle
multiple nested or disjoint capacity groups and reject crossing groups.
`laminar-search.cpp` uses reference capacity 28 and small-reference capacity
27. Both selected counts occur in its failed-state memo key. The implementation
passed 25,578 exact C++/Python bound comparisons and 300 arbitrary nested-group
exhaustive oracles, including the large-denominator edge cases. These tests
verify implementation agreement and the finite upper-bound oracles; they do
not assert that the unfinished 33-term search has completed.

The single-capacity case ending in 29 timed out after 240.032 seconds and
9,402,368 states, with no capacity pruning in that run. The nested-capacity
case ending in 30 timed out after 90.020 seconds and 2,365,440 states, with
395 capacity prunes. These runs establish implementation behavior and retain
restart stacks; they do not establish a general runtime improvement. All three
capacity runs have separately generated unfinished-frontier manifests.

## Reproduction

Python 3.9+ and its standard library suffice for the local result:

```sh
python validate_local.py
python local_surgery.py --remove 5 --required-large 0 --seconds 600 --per-case 30 --output rerun-surgery5-all.jsonl
python audit_frontier.py
```

The C++ sources require GMP. Build `checkpoint-search.cpp` with a C++17
compiler, optimization enabled, and GMP linked. The compiler command below is portable to systems with GMP headers. No external
submission or publication was performed by this computation lane.

For a system with GMP development headers installed:

```sh
c++ -O2 -std=c++17 checkpoint-search.cpp -lgmp -o checkpoint-search
./checkpoint-search --minimum 18 --terms 33 --prefix 18,19,20,21,22,23,24,25,26,27,28,31 --seconds 120 --joint
```
