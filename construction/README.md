# Reproducing the finite constructions

The main general method and its proofs are in ../STRUCTURE.md. These files preserve the discovery path for the finite certificate appendix.

Run from this directory, with Python 3.9+ and the standard library:

~~~sh
python construct_extensions.py
python verify_extensions.py
python optimize_tail_size.py
~~~

The first two commands reproduce and verify the initial N=19,20,21 discoveries in extension-certificates.json. The optimization command enumerates all admissible two-term completions of the fixed N=20 and N=21 prefixes and writes best-size-result.json. Its final N=20 vector matches ../certificates-extension.json and has maximum denominator 755732875917998385; the initial discovery had the same 38 terms and a larger maximum denominator. N=21 has one admissible completion of its fixed prefix.

The final authoritative certificate pack is ../certificates-extension.json and is checked by ../verify-extension.py and ../verify-extension-bigint.mjs.

SEARCH_PROVENANCE.md describes the exploratory searches, including incomplete runs. Broad factorization experiments in lift_search.py use SymPy; the reproduction commands above do not.
