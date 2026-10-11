# Fixed-instance search benchmarks

This directory compares three modes of one exact GMP engine: no overlap quota, full-reference capacity 28, and nested capacities 28/27. Inputs are fixed before timing. The universe of possible denominators is unbounded. The capacities depend on the completed local exclusion families preserved in search-records/.

The 224 inputs include 190 systematic near-consecutive prefixes, 31 structural prefixes, and 3 completed frontier controls. The 53-case upstream pilot uses all structural and control inputs and every tenth broad input in its fixed ordering. Both sides use exactly these prefixes and exact residuals.

Build with `g++ -O2 -std=c++17 matched-search.cpp -lgmp -o matched-search`. Run `python run_benchmark.py --binary ./matched-search --source matched-search.cpp --out-dir results --repeats 3 --seconds 2 --control-seconds 30`. Run the independent probes as specified by `.github/workflows/upstream-benchmark.yml`.

The original implementation is Max Alekseyev's [egypt_rep.sage](https://github.com/maxale/egyptian-fractions/blob/8680599e77683a9057ee55871a0893bb319300e8/egypt_rep.sage). `run_upstream.sage` fetches that pinned source at runtime, checks its hash, and invokes it unchanged in official SageMath 10.8. Its six API controls include a complete six-solution enumeration. The upstream source is kept outside this repository.

The manual workflow records same-CPU single-run comparisons, every censored or failed case, exact-answer checks, source hashes, compiler and image versions. Compiler setup and deriving the local exclusion premises are separate costs. A completed workflow and its saved outputs establish an execution result; this setup text records the experiment design.
