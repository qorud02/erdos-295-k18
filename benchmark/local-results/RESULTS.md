# Matched overlap-quota benchmark: local results

Nested quotas reduced search work in the declared structural family. Across the broader fixed suite, the runtime change was small and included slower cases. The experiment is a matched OFF/single/nested comparison within one GMP executable.

## Execution and exact answers

The input manifest was fixed before timing: all 190 broad-family prefixes, all 31 structural-family prefixes, and controls ending in 31, 32 and 33. Every input is a genuine fixed-prefix subproblem for 33 distinct reciprocal terms summing to 1 with denominators at least 18. All three modes used the same arithmetic, candidate order, prime and joint pruning, and memo-size limits; enabled quotas add their necessary count state and bound calculations. Three serial repetitions rotated the mode order. There was no imposed bound on tail denominators.

All **2,016 declared runs** were recorded. There were **0 errors, 0 answer disagreements and 0 witnesses**. Raw completed runs all returned exhausted for their specified prefix. The original soft time budgets were 2 seconds for the two five-term-tail families and 30 seconds for controls. The watchdog checks time after each 1,024 DFS states or two-term candidate tests. Nine runs timed out, and four completed after their declared solver budget. All raw answers and timings remain in runs.jsonl.

| Mode | Runs | Raw exhausted | Timeouts | Late exhausted | Exhausted within budget |
|---|---:|---:|---:|---:|---:|
| off | 672 | 667 | 5 | 3 | 664 |
| single | 672 | 669 | 3 | 0 | 669 |
| nested | 672 | 671 | 1 | 1 | 670 |

The strict analysis counts late completions as censored. **213 of the 224 fixed instances** completed within budget in every mode in all three repetitions. The table below uses exactly those instances; the remaining 11 stay in the manifest, raw records and censor counts. All repeated complete node and two-term-candidate counts were deterministic.

## Paired measurements

Each reported time is the sum, over the retained instances, of the per-instance median of three solver elapsed times. Internal solver time includes prefix reduction and factor preparation. Ratios above 1 favor nested mode. These are conditional online measurements on the stated complete subset.

| Family | Complete instances / declared | OFF seconds | Single seconds | Nested seconds | OFF / nested | OFF / nested DFS states |
|---|---:|---:|---:|---:|---:|---:|
| broad | 181/190 | 20.837992 | 20.740587 | 20.492893 | 1.017 | 256259 / 256259 |
| structural | 29/31 | 4.493229 | 5.187156 | 2.687073 | 1.672 | 53385 / 24615 |
| control | 3/3 | 6.907334 | 6.914860 | 7.452153 | 0.927 | 51909 / 51881 |
| all | 213/224 | 32.238555 | 32.842603 | 30.632119 | 1.052 | 361553 / 332755 |

The structural family was chosen in advance to exercise the overlap lemma: the first 27 baseline denominators followed by every z from 49 through 79. Four of those fixed prefixes already violate the nested small-reference capacity. On its 29 fully completed instances, nested mode reduced DFS states from **53,385 to 24,615** and solver time from **4.493229 to 2.687073 seconds**. Single mode was slower than OFF on that same family.

In the broad family, all three modes explored exactly **256,259 DFS states** on the 181 strictly completed instances. Its roughly 1.017 OFF/nested time ratio therefore supplies little evidence of useful runtime improvement. Nested mode was slower on the three controls. Across all 213 retained instances, nested mode explored **332,755** states versus **361,553** for OFF; internal solver time was **30.632119** versus **32.238555 seconds**.

Fresh process startup dominated many short instances. For the same 213 instances, sums of median external wall times were **108.386984 seconds OFF, 113.232720 single and 109.278968 nested**. Thus the small aggregate internal-time gain did not produce an aggregate external-wall-time gain in this execution. External wall time includes process launch, output collection and result validation.

## Scope and preparation cost

The broad and structural families are deterministic fixed-prefix corridors, not a random sample of all Egyptian-fraction searches. Their tails and the control searches have no denominator cap. The exact results concern those listed subproblems; the global value k(18) remains 33 or 34.

Deriving the quota premises is separate from applying them. The preserved historical searches took 95.781 seconds for the complete 5-to-4 family and a further 257.625 seconds, including replay, for the fixed-core 6-to-5 family. Those historical times were not rerun on this benchmark host and are not normalized to its timing. Compilation and premise derivation are excluded from the online table. No cold-start saving or amortized break-even is established by this measurement.

Sage/upstream comparisons belong to a separate experiment. A Sage-to-GMP change also changes implementation language and pruning implementation; it cannot be attributed to the overlap quotas. The separate deadline audit records eight local completed runs whose actual solver time exceeded 5 seconds, and nine runs censored at the shorter 2-second budget. A 2-second timeout gives no outcome at a 5-second deadline.

## Provenance and reproduction

Host: Windows 11 build 26300; Intel Core i5-1334U, 12 logical processors; Python 3.12.9; MSVC 19.44.35228 with /O2 and C++17; GMP 6.3.0. The same executable was used for all modes. Source and binary hashes were unchanged at completion.

- C++ source SHA-256: `4d3f59a15beeaeec519bbc9dd65f03d14c4135b29deba3b4e131acfcdcedad2a`
- Executed binary SHA-256: `667e27b4e4b043f977b9595f0501217846e5ba705eed70dbb2b0f425e1cf4d9f`
- Executed runner SHA-256: `081766dc49d1a4081401fe812b2f2e24ef45556a204adf7dd878319e97ae9351`
- Input manifest SHA-256: `826fa365f2abb26cfdd197b76bc71723e90911d17f8beb5a0a82cd7c9e7d4628`

The executed runner is retained verbatim as run_benchmark.executed.py. Its outputs are manifest.json, metadata.json, runs.jsonl and summary.json. The separate analyze_deadlines.py produces strict-deadline-summary.json and deadline-audit.json without altering raw records. The 2,016 individual stdout logs are preserved in logs.zip with an archive and per-file hash receipt. Solvers and runtime DLLs are represented by hashes and build instructions.

After compiling matched-search.cpp with GMP, reproduce with:

```sh
python run_benchmark.py --binary ./matched-search --source matched-search.cpp --out-dir rerun --seconds 2 --control-seconds 30 --repeats 3
```

Use a fresh output directory. The run refuses to overwrite an existing manifest or raw-record file. The full input family and censor policy remain fixed when rerunning.
