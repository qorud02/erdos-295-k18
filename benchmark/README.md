# Fixed-instance search benchmarks

This directory compares three modes of one exact GMP engine: no overlap quota, full-reference capacity 28, and nested capacities 28/27. Inputs are fixed before timing, and possible tail denominators are unbounded. The capacities follow from the completed local exclusion families in [SEARCH_STATUS.md](../SEARCH_STATUS.md).

The completed local experiment recorded all 2,016 runs for 224 fixed inputs and three repetitions per mode. Its strict deadline analysis retained 213 instances completed by every mode in every repetition. The completed cloud pilot compared all three GMP modes with the original Sage implementation on 53 fixed inputs. Results, censor counts, timings and preparation costs are documented here:

- [Local three-repetition results](local-results/RESULTS.md), with the original executed runner and all raw records.
- [Original-Sage cloud pilot and independent artifact audit](CLOUD_RESULTS.md), with the [machine-readable audit receipt](cloud-summary-audit.json).

## Run a new local experiment

Run these commands from this directory, with Python 3.9+ and GMP development headers installed:

```sh
g++ -O2 -std=c++17 matched-search.cpp -lgmp -o matched-search
python run_benchmark.py --binary ./matched-search --source matched-search.cpp --out-dir rerun --repeats 3 --seconds 2 --control-seconds 30
python analyze_deadlines.py rerun
```

Choose a fresh output directory. Before generating the manifest or starting a solver, the runner saves its exact bytes as run_benchmark.executed.py and records their SHA-256 in runner-source-receipt.json and metadata.json. The deadline audit verifies that receipt and imports the recorded runner. It preserves raw completed answers and separately censors answers returned after the declared budget. A source snapshot already present in an output directory is also protected from overwrite.

## Recheck the saved results

The local audit can be reproduced on a copy, preserving the published files:

```sh
python -c "from shutil import copytree; copytree('local-results', 'local-recheck')"
python analyze_deadlines.py local-recheck
python audit_cloud_results.py --run-dir cloud-results --output cloud-recheck.json
```

The original implementation is Max Alekseyev's [egypt_rep.sage](https://github.com/maxale/egyptian-fractions/blob/8680599e77683a9057ee55871a0893bb319300e8/egypt_rep.sage). run_upstream.sage fetches that pinned source, checks its hash, and invokes it unchanged in SageMath 10.8. The upstream source stays outside this repository. The [cloud workflow](../.github/workflows/upstream-benchmark.yml) records the selected inputs, API and residual controls, source receipts, compiler and container versions.

The saved local experiment and cloud pilot are complete. Their matched quota comparisons show that gains concentrate in the preselected structural family; broad cases have equal node counts across modes. The Sage-to-GMP comparison also changes language and existing pruning implementation. Compilation and deriving the local exclusion premises are recorded as separate costs.
