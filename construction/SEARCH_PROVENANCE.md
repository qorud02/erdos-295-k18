# Search provenance and reproduction

Publication-grade positive artifacts are extension-certificates.json, construct_extensions.py, verify_extensions.py, constructed-extensions.json, extension-verification.json and extension-note.md. They require Python 3.9+ and the standard library only. The constructor reproduces the exact frozen vectors, rather than merely rechecking their final sums.

Commands from this directory:

~~~sh
python construct_extensions.py
python verify_extensions.py
~~~

## Discovery searches

1. lift_search.py found the N=19 certificate from the N=18 vector using local exact replacement. Recorded command:

~~~sh
python lift_search.py --max-n 22 --seconds 240 --max-removed 3 --max-added 4 --variants 2
~~~

The output is lift-results.json. Its N=20/21/22 outputs are not used as improvements because stronger compared certificates exist. direct_lift.py produced no further certificates in its configured scope.

lift_search.py uses Fraction and integer arithmetic. In unusually wide two-term intervals it imports SymPy for integer factorization. That optional path was not needed for the successful recorded N=19 construction; the default Python installation here does not have SymPy globally installed. The prior workspace has SymPy under math-research-2026-10-11/root-deps. An isolated external rerun of that optional path needs SymPy installed. SymPy factorint is a synchronous call and is not interrupted by the script's cooperative time check; the seconds option is not a hard wall-clock guarantee for that path. This limitation affects exploratory search timing, not the standalone positive constructor or verifier.

2. tail_refine.py found N=20 and N=21 by exact two-term completion of prefixes from the previously published Botnet vectors. It needs the frozen search-inputs/prior_botnet_verification.json and lift-results.json in this directory. Its four imported engine files are frozen unchanged under search-deps/: search-earlyterminal.py, search-terminalbound.py, search-strong.py, search-independent.py. These are copied from the existing N=18 project, not separate independently derived proofs.

~~~sh
python tail_refine.py
~~~

Output: tail-refinement-results.json. All 19/20/21 positive outputs passed exact verification. N=22 target42 was not found: the two-term fixed-prefix test completed; larger-tail runs timed out. No result from these runs is used as a global exclusion.

3. tail_refine_witness.py explores additional tails with incomplete divisor blocks to avoid enormous terminal scans. It reads tail-refinement-results.json and the same local search-deps engines. It deliberately examines only a subset of divisors when a remaining factor is composite, and may skip large divisor lists. Every positive output would be checked with Fraction; failure is heuristic only. The recorded 12-second runs for N=20 target37, N=21 target38 and N=22 target42 produced no additional certificate. Output: witness-tail-refinement-results.json.

All discovery runs have ended. The frozen constructive results are k(19)<=36, k(20)<=38 and k(21)<=39.

## Prior data

Compared source: https://botnet.com/artifacts/c1db3093-569e-4e89-bced-fd38231c0268, 2026-09-24, source file SHA-256 67ebda12eed01b3643412670aa9ecd06e8db8c61897812c6223212a722dc8123. Python json.load preserves its integer denominators; do not round them through JavaScript Number. The publication certificate stores denominators as decimal strings.

build_certificates.py is an internal packaging helper that reads the frozen search-inputs record and discovery logs. It is not needed to construct or verify the published certificates.
