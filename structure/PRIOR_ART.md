# Structural-method prior art

Checked on 2026-10-12. This is a targeted primary-source comparison, rather than a comprehensive novelty search. The proofs in STRUCTURAL_THEOREMS.md stand independently of the attribution assessment below.

## Egyptian-fraction exact search

**David Eppstein, Algorithms for Egyptian Fractions, “Brute Force Methods.”** [Author's university page](https://ics.uci.edu/~eppstein/numth/egypt/force.html).

The short-sequence method already bounds the next denominator using the residual and remaining cardinality, recurses over a finite range, and finishes a two-term residual by factoring the square of its denominator. The page also contains divisor-subset dynamic programming. These are direct predecessors of the baseline enumeration and two-term completion used here. Ordinary harmonic bounds, divisor completions, exact rational enumeration, and using dynamic programming for Egyptian fractions should be attributed as existing methods. The page inspected does not provide the core-conditioned overlap certificate developed in this note.

**Greg Martin and Yue Shi, An algorithm for Egyptian fraction representations with restricted denominators.** Involve 18 (2025). [Published DOI](https://doi.org/10.2140/involve.2025.18.1), [author-hosted published paper](https://personal.math.ubc.ca/~gerg/papers/downloads/AEFRRD.pdf), [arXiv record](https://arxiv.org/abs/2107.05076), [full preprint](https://arxiv.org/html/2107.05076v1).

Their algorithm generates all representations from a given finite denominator multiset. Its exact branching treats prime-power divisibility and reserves or removes denominators; termination and completeness are central properties. Any use of p-adic pruning, finite allowed-denominator enumeration, or reserving/removing terminology must acknowledge this work and its cited predecessors. Our atom calculation instead maximizes a reciprocal-sum relaxation on an infinite universe with finite exceptional groups; it does not enumerate all equal-sum representations. The full preprint and journal metadata were inspected. The author-hosted published PDF timed out in this lane, so numbering of published results was not independently checked here.

## Local improvements and subset sums

**C. A. J. Hurkens and A. Schrijver, On the Size of Systems of Sets Every t of which Have an SDR, with an Application to the Worst-Case Ratio of Heuristics for Packing Problems.** SIAM Journal on Discrete Mathematics 2(1) (1989), 68–72. [Publisher](https://epubs.siam.org/doi/10.1137/0402008).

The article derives structural extremal bounds and worst-case guarantees relevant to packing heuristics. It is an established example of obtaining global consequences from restrictions on small configurations or improvements. Its set-packing/SDR setting differs from the additive equality and fixed deficit in the present cancellation lemma. The publisher abstract and bibliographic information were inspected; no full-paper equivalence claim is made.

**Diptesh Ghosh and Nilotpal Chakravarti, A competitive local search heuristic for the subset sum problem.** Computers & Operations Research 26(3) (1999), 271–279. [DOI](https://doi.org/10.1016/S0305-0548(98)00046-X), [publisher abstract](https://www.sciencedirect.com/science/article/pii/S030505489800046X).

The primary abstract identifies an established local-search heuristic for approximately solving subset-sum problems. This establishes prior use of local search in subset sum, rather than the specific exact-exclusion transfer or its mandatory-core form. The abstract and publication details were inspected. Exact local exhaustion and an approximate heuristic have different proof requirements.

## Weighted selection under quotas

**Jack Edmonds, Matroids and the greedy algorithm.** Mathematical Programming 1 (1971), 127–136. [Publisher and DOI](https://link.springer.com/article/10.1007/BF01584082).

Maximum-weight selection by greedy on a matroid is classical. Consequently, the single-group envelope and the disjoint-group partition-matroid corollary are applications of existing optimization theory. The publisher metadata and abstract were inspected; the full article requires subscription. STRUCTURAL_THEOREMS.md supplies a direct exchange argument for the family used here instead of relying on inaccessible details.

**Tara Fife and James Oxley, Laminar Matroids.** arXiv:1606.08354 (2016). [Primary manuscript record](https://arxiv.org/abs/1606.08354).

The authors explicitly study capacity constraints on laminar families and the matroids they define. This directly covers the nested/disjoint quota family arising from the full 34-term source and its 32-element core complement. Laminar greedy and its exchange property are existing theory. Crossing quota groups require another method, as the reciprocal counterexample in STRUCTURAL_THEOREMS.md demonstrates.

The arbitrary-overlap atom DP is an ordinary finite integer dynamic program over membership patterns and used capacities. The exact support reduction follows from selecting the largest weights within each pattern. Neither the generic DP technique nor matroid greedy is presented as newly invented here.

## Forbidden intersections

**Peter Frankl and R. M. Wilson, Intersection theorems with geometric consequences.** Combinatorica 1(4) (1981), 357–368. [Publisher and DOI](https://link.springer.com/article/10.1007/BF02579457), [original article PDF hosted by a university researcher](https://www.cs.umd.edu/~gasarch/TOPICS/CRT/FW.pdf).

The publisher abstract concerns uniform set families whose pairwise intersections satisfy specified modular restrictions, leading to bounds on family cardinality. Our core theorem compares each target with a fixed reference and follows by additive cancellation and padding. It is a useful intersection restriction, but should not be described as a new Frankl–Wilson-type theorem. The abstract and primary PDF availability were checked; no dependence on its polynomial method is used.

## Contribution assessment and publication wording

The strongest defensible contribution of the present structural work is the explicit transfer:

    complete core-conditioned local exclusion
      -> a quota on every smaller equal-sum representation
      -> an exact reciprocal branch envelope under one or several quotas.

The mandatory-core statement makes a targeted family of removed subsets useful globally even when a target contains members of the core. The finite atom API provides an exact, reusable implementation for crossing reference groups while retaining the infinite permitted-denominator universe. Its proof, resource-failure behavior, and independent oracles are part of the computational contribution.

The cancellation theorem is elementary; the quota optimization uses classical matroid and dynamic-programming ideas. This search has not established priority for their combination in Egyptian-fraction minimum proofs. Suitable wording is “an elementary core-exclusion lemma and exact quota envelopes for certified Egyptian-fraction searches.” A claim of a major new general theory, an asymptotic improvement, or a solved minimum requires additional evidence.

A paper becomes materially stronger if these constraints complete a previously unresolved minimum proof, certify a new family of exclusions with reproducible independent checks, or show a measured improvement against the unmodified exact search. Comparisons should separately track ordinary harmonic pruning, one-quota pruning, nested core quotas, and crossing-group dual/atom bounds. No speedup figure follows from the present mathematical statements alone.
