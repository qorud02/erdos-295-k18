# A 34-term unit-fraction expansion with minimum denominator 18

**Kyunghan Bae · 11 October 2026**

DOI: https://doi.org/10.5281/zenodo.23297810

An explicit set of 34 distinct integer denominators, all at least 18, has reciprocal sum exactly one. This proves **k(18) ≤ 34**. Combined with the previously reported and reproduced computational lower bound, **33 ≤ k(18) ≤ 34**.

Read the [research note](NOTE.md) for the construction, integer proof, five-to-four replacement, and references.

~~~text
18,19,20,21,22,23,24,25,26,27,28,29,30,31,
32,33,34,35,36,38,39,40,43,44,45,46,
48,50,52,54,63,275,14143068,10457416992
~~~

Their least common multiple is 6209352774424800. The sum of L/d over the displayed denominators equals L exactly.

## Check the certificate

Python 3.9 or later, standard library only:

~~~sh
python verify-certificate.py
~~~

The checker verifies the rational sum, the integer LCM sum, distinctness, ordering, and the replacement identity against the original 35-term certificate.

## Reproduce the lower bound

~~~sh
python search-runner.py --engine search-earlyterminal.py --minimum 18 --terms 32 --seconds 600
~~~

Expected final status: exhausted. Expected counters: nodes 814918, prime_prunes 134999, quadratic_early_prunes 648193, failed_states 31726. A timeout is an incomplete run. No denominator limit is imposed.

The [pruning arguments](proofs.md) explain the exact search. Completed results are preserved in the Python, C#, and C++ logs. The implementations share mathematical lemmas, and their agreement checks implementations and arithmetic.

The 33-term case and the original asymptotic Erdős conjecture remain unresolved in this work.

## Files

- NOTE.md and erdos295-note.tex: English research note
- certificate-34-independent.json and verify-certificate.py: standalone certificate and checker
- search-*.py, search-native.cs, run-native.ps1, search-cpp.cpp: reproduction sources
- early-n18-t32.log, cpp-n18-t32.log, independent-native-validation.jsonl: completed runs
- manifest-sha256.json: checksums of release files

## Sources and computational contribution

The comparison is with [Patrick White with Claude's 35-term construction, updated 11 August 2026](https://erdosproblemaday.com/day/295-k17-exact). The original question is [Erdős Problem #295](https://www.erdosproblems.com/295).

This research was initiated by Kyunghan Bae. OpenAI Codex (GPT-6 session) agents developed the search and verification code, found the construction, performed exact arithmetic checks, and assisted with the write-up. Earlier-publication priority remains a literature question.

Code is available under the MIT License. The research note and explanatory documents are licensed CC BY 4.0. See LICENSE and LICENSES.md.
