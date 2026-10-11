# Exact Egyptian-fraction certificates and overlap-constrained search

**Kyunghan Bae · 12 October 2026 · v1.2.0**

Exact certificates establish **k(18) ≤ 34, k(19) ≤ 36, k(20) ≤ 38, k(21) ≤ 39**. Each expansion starts with its stated N, so the same upper bounds apply to OEIS A192881. The proofs, identities and reproduction details are collected in the [research note](RESEARCH_NOTE.md), available as a [six-page PDF](erdos295-extension.pdf) and [LaTeX source](erdos295-extension.tex).

| N | Cited comparison certificate | Certificate here |
|---|---:|---:|
| 18 | 35 | 34 |
| 19 | 38 | 36 |
| 20 | 39 | 38 |
| 21 | 40 | 39 |

The comparison certificates for 19–21 were published by [grind-35 on 24 September 2026](https://botnet.com/artifacts/c1db3093-569e-4e89-bced-fd38231c0268). The N=18 construction replaces five terms of [Patrick White with Claude’s 35-term witness](https://erdosproblemaday.com/day/295-k17-exact) with four.

Read [EXTENSION.md](EXTENSION.md) for the reusable classical two-term completion rule, proofs, source attribution, and the new finite certificates. [NOTE.md](NOTE.md) contains the original N=18 construction and the corrected account of the lower-bound reproduction.

## Verify all upper certificates

Python 3.9 or later; standard library only:

~~~sh
python verify-certificate.py
python verify-extension.py
python structure/test_dual.py
python structure/general_theorem_oracle.py
~~~

The check covers exact rational sums, integer LCM certificates, term counts, distinctness, minimum denominators, source-to-result replacements, and 20 deliberately corrupted records. All large integers in certificates-extension.json are stored as decimal strings. A separately written JavaScript BigInt calculation checks the same four full identities (`node verify-extension-bigint.mjs`); its results are in extension-bigint-validation.json. General theorem oracles check the exchange equivalence, fixed-core compression, exact quota envelopes, and the crossing-quota dual bound.

## Elementary overlap bounds and the remaining question

The elementary cancellation proof in [STRUCTURE.md](STRUCTURE.md) converts completed local shortening exclusions into global overlap quotas. Exact reciprocal envelopes use classical greedy optimization, dynamic programming and weak duality. The proof applies to arbitrary additive weights.

The previously reported 32-term exclusion was reproduced with the same exact recurrence plus additional pruning. Thus **33 ≤ k(18) ≤ 34**. Every possible 33-term representation shares at most 28 denominators with the current 34-term reference, and at most 27 with its 32 smaller denominators. These follow from completed local exclusions and the general transfer theorem. The 33-term case remains unresolved; [SEARCH_STATUS.md](SEARCH_STATUS.md) records completed prefix exclusions and incomplete runs. The original [Erdős #295 asymptotic question](https://www.erdosproblems.com/295) also remains open.

~~~sh
python search-runner.py --engine search-earlyterminal.py --minimum 18 --terms 32 --seconds 600
~~~

Expected status: exhausted; nodes 814918, prime_prunes 134999, quadratic_early_prunes 648193, failed_states 31726. Every two-term state in that run was rejected before enumeration, so zero terminal candidates were tested. The implementations share mathematical lemmas; their agreement checks arithmetic and implementation.

## Reproducible comparisons

The [benchmark package](benchmark/README.md) includes 224 fixed inputs with three quota modes and three local repetitions, plus a 53-case comparison with [Alekseyev’s original Sage implementation](https://github.com/maxale/egyptian-fractions). The same-cloud-CPU pilot completed 53/53 inputs in each GMP mode and 48/53 in Sage, with 5 Sage timeouts and no conflicting completed answers. Its [workflow](https://github.com/qorud02/erdos-295-k18/actions/runs/38176293521) also passed 972 independent small residual checks. The comparison between implementations includes language and pruning differences; quota effects are measured separately within the GMP engine.

## Archive, review, and reuse

The [v1.0.0 archive](https://doi.org/10.5281/zenodo.23297810) preserves the original 34-term result. [Erdős Problem a Day’s computational review](https://erdosproblemaday.com/submission/urbtgs) independently recomputed that certificate. The [v1.2.0 release](https://github.com/qorud02/erdos-295-k18/releases/tag/v1.2.0) adds fixed-input benchmarks and the original Sage comparison to the exact certificates, proofs and search records. Its preserved record is [10.5281/zenodo.23305279](https://doi.org/10.5281/zenodo.23305279).

Kyunghan Bae initiated the project. OpenAI Codex agents implemented and ran the searches, found the certificates, and assisted with verification and exposition.

Code: MIT License. Research notes: CC BY 4.0. See LICENSE and LICENSES.md.
