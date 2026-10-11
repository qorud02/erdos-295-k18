# Independent audit of the original-Sage cloud pilot

The downloaded records from [workflow run 38176293521](https://github.com/qorud02/erdos-295-k18/actions/runs/38176293521) pass the local artifact audit. The three matched C++ modes each exhausted all 53 fixed prefix subtrees. The original Sage API exhausted 48 and reached the declared time limit on five. All completed proof answers agree. These results concern the declared subtrees of the N=18, 33-term search.

The pilot contains one measurement per implementation and case. The full frozen manifest has 224 cases; the pilot retains every tenth broad case by zero-based ordinal, all 31 structural cases, and the three control cases. Both implementations recorded CPU affinity [0] within the same workflow job. Ordinary cases had a five-second budget and the three subtree controls had 30 seconds. The original Sage implementation used one map-reduce worker.

| Family | Declared | C++ OFF / single / nested completed | Sage completed | Sage censored |
| --- | ---: | ---: | ---: | ---: |
| broad | 19 | 19 / 19 / 19 | 17 | 2 |
| structural | 31 | 31 / 31 / 31 | 29 | 2 |
| control | 3 | 3 / 3 / 3 | 2 | 1 |
| all | 53 | 53 / 53 / 53 | 48 | 5 |

All six original-Sage API controls passed. The audit independently enumerated their small exact solution sets and checked the returned answers, including the complete four-term enumeration. The 972-case residual-oracle artifact reports 349 witnesses and 623 exhausted states. Its generated input digest was independently reproduced. That small suite recorded zero prime and joint-prime prunes; its coverage concerns residual terminals and quota checks, alongside the separately retained engine validation.

## Matched quota ablation on all 53 cases

The following totals use the same C++ source, executable, exact arithmetic, traversal, prime pruning, joint-prime pruning, and memo limits. Only the quota mode changes. Times are sums of the recorded internal solver seconds, with no startup or premise-construction charge.

| Family | OFF nodes | Single nodes | Nested nodes | OFF seconds | Single seconds | Nested seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| broad | 62,034 | 62,034 | 62,034 | 0.130876 | 0.132363 | 0.132212 |
| structural | 80,858 | 72,742 | 35,595 | 0.186833 | 0.183240 | 0.096245 |
| control | 51,909 | 51,909 | 51,881 | 0.224596 | 0.230749 | 0.227354 |
| all | 194,801 | 186,685 | 149,510 | 0.542305 | 0.546352 | 0.455811 |

Across this fixed pilot, nested quotas reduced nodes from 194,801 to 149,510, a reduction of 45,291 (23.25%). Internal solver time changed from 0.542305 to 0.455811 seconds, a reduction of 0.086494 seconds (15.95%). Summed process wall time was 0.670149 seconds for OFF, 0.677252 for single, and 0.583803 for nested. These subsecond totals are one-run measurements.

The structural family accounts for 45,263 of the 45,291 saved nodes. Its node reduction was 55.98%, and its solver-time total changed from 0.186833 to 0.096245 seconds. Broad cases had identical node counts in all three modes; nested time was slightly higher than OFF. The control family saved 28 nodes and also had a slightly higher nested time total. Nodes decreased in 16 cases, stayed equal in 37, and increased in none. This concentration in the preselected structural cases gives the scope of the observed quota effect.

## Original Sage accounting

The Sage timeouts were broad-045-046, broad-046-048, structural-049, structural-050, and control-next-31. They remain censored records, with solver-time lower bounds of 5, 5, 5, 5, and 30 seconds. Their completed answers and full solution times are unknown.

The 48 common completed cases comprised 17 broad, 29 structural, and two controls. For that completion-selected subset, summed internal seconds were 68.666638 for original Sage, 0.185344 for C++ OFF, 0.190610 for single, and 0.136761 for nested. These are separate implementation measurements on that subset. Completion-selected ratios are not generalized to the full input family. Differences between original Sage and GMP also include language, runtime, and pre-existing pruning changes, so that comparison does not isolate the overlap-quota effect.

Sage case process wall time totaled 120.526471 seconds across all 53 cases, including watchdog cleanup. Completed solver time totaled 68.666638 seconds; the five censored cases contribute a further lower bound of 50 seconds. The six API controls used 0.147661 internal seconds and 0.226183 wall seconds. Source retrieval and Sage loading took 4.114717 seconds. Compilation, container retrieval, and the rest of the workflow are outside those recorded components. No full-workflow elapsed time is reconstructed from them.

The previously recorded premise-construction cost is 353.406 seconds (95.781 plus 257.625) from another environment. It stays a historical cost entry. It is neither converted to this CPU nor added as a measured cloud cold-start time. The present matched timings exclude premise construction and compilation.

## Integrity and reproducibility

The audit checked all 224 frozen prefix residuals by exact Fraction arithmetic, the 53-case selection, 159 C++ raw records, 59 Sage records including six API controls, completion and censor states, and the 159 C++ stdout digests against their stored result objects. It independently recomputed family totals and checked the saved comparison table. No solver was executed during this audit.

- Frozen input SHA-256: 826fa365f2abb26cfdd197b76bc71723e90911d17f8beb5a0a82cd7c9e7d4628.
- C++ source SHA-256: 4d3f59a15beeaeec519bbc9dd65f03d14c4135b29deba3b4e131acfcdcedad2a.
- Compiled executable receipt: 875630ecdb678bc77e4cb07ece282c384db4a62bc419490d104348b6e35008dd.
- Original Sage commit: 8680599e77683a9057ee55871a0893bb319300e8; upstream source receipt: 4febfdbee3710f05775f41bc15a9046984c69da1f7a53f105116579a663ad480.
- Executed Sage wrapper SHA-256: 49f054863b0b54dd3a74255bbd315c369d3da87bc304673655c0661f6929ec8a.
- Actual image receipt: sagemath/sagemath@sha256:e2e4747b0e1ea8753a9cb5a399314a8b2c25fcefaf69ba85b22ee075829d09ea, Linux amd64, Sage 10.8.
- Compiler: g++ 13.3.0. C++ host glibc was 2.39; the Sage container reported glibc 2.35.

The artifact contains the executable and upstream-source hash receipts, but not those byte files. The C++ source, Sage wrapper, and input manifest were rehashed locally; the executable and original upstream source receipts were matched to metadata. The executed wrapper verifies the fetched upstream source against its pinned hash before execution.

Machine-readable results and a 230-file artifact hash inventory are in [cloud-summary-audit.json](cloud-summary-audit.json). The reproduction script is [audit_cloud_results.py](audit_cloud_results.py).
