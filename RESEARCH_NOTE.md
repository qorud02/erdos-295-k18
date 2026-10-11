# Exact Egyptian-fraction certificates and overlap-constrained search

**Kyunghan Bae**  
2026-10-12  
DOI: [10.5281/zenodo.23305279](https://doi.org/10.5281/zenodo.23305279)

**Abstract.** We give explicit expansions of 1 into distinct unit fractions establishing k(18)≤34, k(19)≤36, k(20)≤38 and k(21)≤39. Each upper bound has a finite certificate verified by exact rational and integer arithmetic. An elementary cancellation lemma converts complete families of local shortening exclusions into overlap restrictions on every shorter representation. For the 34-term reference, completed five-to-four and fixed-core six-to-five searches give overlap capacities 28 and 27. Classical quota optimization supplies exact reciprocal upper envelopes. A fixed 53-branch pilot compares three modes of one C++/GMP engine with a pinned original Sage implementation: the three matched modes exhaust all 53 branches; Sage exhausts 48 and times out on five, with no contradictory completed answers. These are finite computational results. The existence of a 33-term expansion at N=18 and the asymptotic question in Erdős problem 295 remain open.

## 1. Problem and contribution

For a positive integer N, let k(N) be the least cardinality of a finite set D of distinct integers at least N such that

$$\sum_{d\in D}\frac1d=1.$$

The main results are the four explicit finite identities below. Compared with the identified computational certificates, their term counts are:

| N | Cited certificate term count | Term count here |
|---|---:|---:|
| 18 | 35 | 34 |
| 19 | 38 | 36 |
| 20 | 39 | 38 |
| 21 | 40 | 39 |

The N=18 construction shortens the 35-term expansion recorded by White with Claude [2]. The comparisons for N=19,20,21 use the vectors published by grind-35 on 24 September 2026 [3]. All source vectors used in the comparisons were rechecked with exact rational arithmetic. Each resulting expansion includes N itself, so these witnesses also give upper bounds for OEIS A192881, whose definition requires the first denominator to equal N. The comparison is to the specified records.

Fixed-length enumeration and divisor-based two-term completion are classical [4]. Alekseyev supplies related exact enumeration software in Sage [5]. Greedy optimization on matroids and laminar capacity families is established theory [6,7]; membership-pattern dynamic programming and weak duality are also standard methods. Here these methods accompany the explicit certificates, complete local-exclusion records and their elementary transfer into two concrete overlap restrictions. Finite allowed-denominator enumeration, as studied by Martin and Shi [8], is a related problem; the representation searches below allow unbounded denominators.

## 2. Four finite certificates

**Proposition 1.** The following sets D_N consist of the stated number of distinct integers at least N and satisfy Σ(d∈D_N)1/d=1.

**N=18, 34 terms:**

```text
18,19,20,21,22,23,24,25,26,27,28,29,30,31,
32,33,34,35,36,38,39,40,43,44,45,46,
48,50,52,54,63,275,14143068,10457416992
```

**N=19, 36 terms:**

```text
19,20,21,22,23,24,25,26,27,28,29,30,31,32,
33,34,35,36,38,39,40,42,43,44,45,46,48,50,
52,54,55,66,70,275,14143068,10457416992
```

**N=20, 38 terms:**

```text
20,21,22,23,24,25,26,27,28,29,30,31,32,33,
34,35,36,37,38,39,40,41,42,43,44,45,46,
48,50,51,52,53,54,72,9512,316569706,
745735753538714400,755732875917998385
```

**N=21, 39 terms:**

```text
21,22,23,24,25,26,27,28,29,30,31,32,33,34,
35,36,37,38,39,40,41,42,44,45,46,48,49,50,
52,53,54,55,56,57,58,64,3162192,
13244735025984,60692489317197426150
```

**Proof.** Let L_N be the least common multiple of the displayed denominators. Exact integer addition gives the following certificates:

| N | L_N = Σ(d∈D_N)L_N/d |
|---|---:|
| 18 | 6209352774424800 |
| 19 | 6209352774424800 |
| 20 | 2772929439982611617430667744800 |
| 21 | 207311948389939355504942400 |

Each denominator divides its stated L_N, and the sum of the integer quotients is L_N. Dividing by L_N proves the reciprocal identity. Cardinality, increasing order and minimum denominator can be checked directly from the lists. Thus the asserted upper bounds follow. ∎

The authoritative machine-readable lists and all these integers are in `certificates-extension.json`, with large integers encoded as decimal strings. Their verification is independent of how the search found them.

## 3. Construction and classical completion

For N=18, retain 30 terms of the earlier 35-term certificate [2] and use the exact substitution

$$\frac1{42}+\frac1{640}+\frac1{337280}+\frac1{1735650}+\frac1{68479214496}
=\frac1{46}+\frac1{275}+\frac1{14143068}+\frac1{10457416992}.$$

Multiplication by 636856694812800 gives 16160598373892 on each side. The four replacement denominators are distinct and absent from the retained terms. For N=19, replace 18 and 63 in D_18 by 42,55,66,70, using

$$\frac1{18}+\frac1{63}=\frac1{14}
=\frac1{42}+\frac1{55}+\frac1{66}+\frac1{70}.$$

The N=20 and N=21 constructions keep respectively the first 36 and 37 denominators of the cited 39- and 40-term certificates [3]. Their remaining three terms are replaced by the two-term tails displayed below:

$$\frac{151817}{56984589375772121632800}
=\frac1{745735753538714400}+\frac1{755732875917998385},$$

$$\frac{35558057}{470956940228352916800}
=\frac1{13244735025984}+\frac1{60692489317197426150}.$$

For completeness, the classical two-term rule [4] is as follows. Write a positive residual as a/b in lowest terms, and let D exceed all retained denominators. A completion a/b=1/x+1/y with D≤x<y exists exactly when a divisor q of b² satisfies

$$\max(1,aD-b)\le q<b,\qquad q\equiv-b\pmod a.$$

Then x=(b+q)/a and y=(b+b²/q)/a. Indeed,

$$ (ax-b)(ay-b)=b^2. $$

For a solution, q=ax−b has the stated properties. Conversely, gcd(a,b)=1 and q≡−b (mod a) imply b²/q≡−b (mod a), so both denominators are integers; the inequalities give D≤x<y. The case a=1 is immediate. Complete divisor enumeration decides completion for a specified prefix, rather than for all prefixes. In the N=20 construction, the reported pair minimizes the larger denominator among the completions of its fixed retained prefix; no global size optimum is asserted.

## 4. An elementary transfer lemma

Let U be a universe, w:U→R any weight function, and W(S)=Σ(x∈S)w(x) for finite S. Fix A⊆U with |A|=m. Let 1≤d≤r≤m and fix C⊆A with |C|≤r. A target is a set B with |B|=m−d and W(B)=W(A).

For R⊆A of size r, call T an admissible replacement when

$$|T|=r-d,\qquad T\cap(A\setminus R)=\varnothing,\qquad W(T)=W(R).$$

**Removed elements may reappear in T.** Only the retained elements A\R are forbidden. This convention is needed when padding a smaller difference between two representations.

**Lemma 2 (fixed-core transfer).** Suppose every r-element subset R of A containing C has no admissible replacement. Then every target B satisfies

$$|B\cap(A\setminus C)|\le m-r-1.$$

**Proof.** For a fixed R, a replacement T produces the target B=(A\R)∪T containing A\R; disjointness gives its cardinality, and cancellation gives its weight. Conversely, if a target B contains A\R, then T=B\(A\R) has cardinality r−d, avoids A\R and has weight W(R). Thus replacement existence is equivalent to the existence of a target containing the retained set.

Now let K=A\B. If |K∪C|≤r, extend K∪C to an r-element subset R⊆A. Then A\R⊆B, yielding a replacement by the preceding equivalence, contrary to the premise. Consequently |K∪C|≥r+1. Taking complements inside A gives

$$|B\cap(A\setminus C)|=m-|K\cup C|\le m-r-1.$$

This proof uses neither positivity nor rationality of the weights. ∎

For C empty, every target overlaps A in at most m−r−1 elements. The lemma is an elementary cancellation argument; the substantive premise in a computational application is the complete family of exclusions.

## 5. Completed premises and reciprocal bounds

Take A=D_18 and C={14143068,10457416992}. The preserved local searches use distinct denominators at least 18 and forbid exactly the retained terms. Their completed coverage is:

| Removed / replacement terms | Removed-subset family | Completely searched subsets | Recorded seconds |
|---|---|---:|---:|
| 5 / 4 | Every 5-subset of A | C(34,5)=278256 | 95.781 |
| 6 / 5 | Every 6-subset containing C | C(32,4)=35960 | 257.625, including replay |

There are 314216 completed subsets in these two families. In the second family, the first log completes indices 0 through 33953 and interrupts index 33954. The resumed run replays index 33954 and completes through 35959. The interrupted attempt is not counted as a completed case. `search-records/verify_local_premises.py` verifies coverage and this boundary.

These are searches without a denominator cap. At a positive reduced remainder a/b with t≥2 terms remaining and lower endpoint D, the next denominator lies in the finite necessary interval

$$\max(D,\lfloor b/a\rfloor+1)\le x\le\lfloor tb/a\rfloor.$$

Distinctness, exact harmonic bounds and proved arithmetic conditions prune branches. With two terms left, y=bx/(ax−b) is checked exactly. The final denominator has no imposed maximum. Full recurrence and arithmetic details are supplied in `proofs.md` and `SEARCH_STATUS.md`.

Lemma 2 gives, for every 33-term representation B with denominators at least 18,

$$|B\cap A|\le28,\qquad |B\cap(A\setminus C)|\le27.$$

These restrictions apply on the entire unbounded denominator universe. For a selected prefix P, subtract its overlap counts from the two capacities. Among t remaining denominators at least D=max(P)+1, accept denominators in increasing order whenever both residual capacities permit them. The reciprocal sum of these t accepted denominators is the exact maximum under these nested quotas, by classical greedy optimization for a truncated laminar matroid [6,7]. A negative residual capacity, or a target exceeding this maximum, excludes the branch.

For crossing finite quota groups, partition denominators into membership patterns. For each pattern and chosen count, take the smallest denominators in that pattern; dynamic programming over the counts gives the exact upper envelope. Only the first t denominators of each pattern are needed. This finite support is for evaluating a bound, not a denominator restriction on the representation search. Exact nonnegative multipliers also give standard weak-duality bounds. Proofs, resource guards and executable checks are in `STRUCTURE.md` and `structure/`.

## 6. A controlled original-Sage pilot

The fixed input corpus has 224 prefixes, each extended to a possible 33-term representation of 1 with minimum denominator 18. It comprises 190 prefixes {18,…,28}∪{30,…,44}∪{u,v}, 45≤u<v≤64; 31 prefixes formed from the first 27 elements of A followed by z=49,…,79; and three controls {18,…,28}∪{z} for z=31,32,33. The 53-case pilot includes all structural prefixes and controls plus every tenth broad prefix in lexicographic (u,v) order, starting with ordinal zero. Selection was fixed before timing.

The pilot executed on one Linux runner CPU, with one repetition per case. The unchanged original Sage source [5] was fetched at commit `8680599e77683a9057ee55871a0893bb319300e8` and checked against SHA-256 `4febfdbee3710f05775f41bc15a9046984c69da1f7a53f105116579a663ad480`. It ran in SageMath 10.8 with one map-reduce worker. The wrapper called `one_rep` on the exact residual, with `distinct=True`, the correct lower endpoint and no maximum denominator. Six API controls passed, including exact enumeration of all six four-term distinct expansions of 1 with denominators at least 2.

The C++/GMP engine ran three modes of one source: OFF; full-reference quota 28; and nested quotas 28/27. All modes shared arithmetic, traversal, prime and quadratic pruning, and memo limits. Each ordinary case had a five-second solver budget; each frontier control had 30 seconds. Outcomes were:

| Solver / mode | Branches exhausted | Timed out | Errors |
|---|---:|---:|---:|
| Original Sage | 48 | 5 | 0 |
| Matched GMP, OFF | 53 | 0 | 0 |
| Matched GMP, single quota | 53 | 0 | 0 |
| Matched GMP, nested quotas | 53 | 0 | 0 |

All 48 branches completed by both programs agreed on absence. No contradictory completed answer occurred. The five Sage timeouts remain censored baseline runs. The completed matched searches exclude these specified branches; they do not exhaust all 33-term possibilities. Saved records, source/image hashes and the successful workflow are available in [9].

The inter-program comparison includes C++/GMP versus Sage/Python execution, different tail routines, harmonic/prime/quadratic pruning and worker-management costs. Its timing difference therefore does not isolate overlap-quota effects. The three matched modes provide the relevant ablation. For example, `structural-052` visits 9444 states in OFF mode, 7276 with one quota and 1 with nested quotas, with the same exhausted verdict. This demonstrates a concrete quota exclusion in the selected family. A single pilot and selected structural branches do not establish a general runtime advantage.

Solver timers exclude compilation, Sage startup/source loading and deriving the local-exclusion premises. Sage API timing includes worker setup and cleanup; separate wall times are retained. The two historical premise times above were measured separately and are not hardware-normalized to the cloud pilot. Timeouts and late answers stay in the records.

Independent unpruned rational enumeration checked 972 conditional residual states with one, two or three terms left: 349 admitted a witness and 623 were exhausted. Verdicts agreed with the matched engine, and every returned witness passed exact sum, order, distinctness and quota checks. These controls exercise implementation and boundary behavior; they are not a global 33-term exclusion.

### Repeated local quota ablation

A separate Windows run executed all 224 cases in all three matched modes, with three repetitions: 2016 solver runs in total. The declared solver budget was two seconds per ordinary case and 30 seconds per control. Strict post-processing censored nine raw timeouts and four answers returned after their deadline; all 2016 records are retained. There were no errors or contradictory completed verdicts. Exactly 213 cases finished within budget in all nine runs.

For each case and mode, take the median of its three solver times. The table reports the sum of these medians for OFF divided by the sum for nested quotas, restricted in each row to cases with all nine runs completed within budget. A ratio above 1 favors nested quotas on this conditional measure.

| Family | All-nine-complete / declared cases | OFF / nested, ratio of summed medians |
|---|---:|---:|
| All | 213 / 224 | 1.05244 |
| Broad | 181 / 190 | 1.01684 |
| Structural | 29 / 31 | 1.67216 |
| Controls | 3 / 3 | 0.92689 |

The overall difference is modest, with the larger effect concentrated in the selected structural family. The broad family changes little, while controls take longer with nested quotas on this measure. These ratios concern online solver time on a common completed subset; they exclude premise computation and compilation, and do not measure the full suite including censored runs. For the same 213 instances, sums of median external wall times were 108.386984 seconds for OFF and 109.278968 for nested quotas. Process launch, output collection and validation therefore removed the small aggregate internal-time gain in this execution. The Windows repetitions and the Linux Sage pilot are separate experiments.

## 7. Reproducibility and remaining questions

The code and records are available at [10]. The four identities can be checked with Python 3.9+ and its standard library:

```sh
python verify-extension.py
node verify-extension-bigint.mjs
python structure/general_theorem_oracle.py
```

The first command checks exact fraction sums, integer LCM identities, term counts, order, minima and source-to-result substitutions. Twenty deliberately corrupted records are rejected. The JavaScript program separately checks the same finite identities using BigInt arithmetic. The local-exclusion audits and search programs are preserved separately; search is unnecessary for verifying Proposition 1.

The accompanying release reproduces the previously reported exclusion of exactly 32 terms at N=18, using the same mathematical recurrence in separately written exact-arithmetic implementations. The logged run has 814918 visited states; all two-term states are rejected before candidate enumeration. Excluding 32 terms excludes every shorter expansion: repeatedly replace the largest denominator d by d+1 and d(d+1), using 1/d=1/(d+1)+1/[d(d+1)], until 32 terms are reached. New denominators exceed every retained one. Thus the recorded bounds are 33≤k(18)≤34. Whether k(18)=33 or 34 remains unresolved here.

Erdős problem 295 asks whether k(N)−(e−1)N tends to positive infinity [1]. The four finite certificates and overlap exclusions do not settle that asymptotic question. Further progress would require a completed minimum proof, a quantitatively stronger family of constructions or a broader controlled study of the pruning rules.

**Computational contribution.** Kyunghan Bae initiated the project; OpenAI Codex agents implemented and ran the searches, found the certificates, and assisted with verification and exposition.

## References

1. Thomas Bloom, ed. [Erdős Problem #295](https://www.erdosproblems.com/295).
2. Patrick White with Claude. [Erdős #295 computational report](https://erdosproblemaday.com/day/295-k17-exact), including the earlier 35-term N=18 certificate; original construction and provenance are preserved in `NOTE.md`.
3. grind-35. [Erdos 295 upper bounds N=11..22](https://botnet.com/artifacts/c1db3093-569e-4e89-bced-fd38231c0268), 24 September 2026.
4. David Eppstein. [Algorithms for Egyptian Fractions: Brute Force Methods](https://ics.uci.edu/~eppstein/numth/egypt/force.html).
5. Max A. Alekseyev. [egypt_rep.sage](https://github.com/maxale/egyptian-fractions/blob/8680599e77683a9057ee55871a0893bb319300e8/egypt_rep.sage), version 20251028, commit 8680599e77683a9057ee55871a0893bb319300e8, accessed 12 October 2026.
6. Jack Edmonds. Matroids and the greedy algorithm. *Mathematical Programming* 1 (1971), 127–136. [DOI](https://doi.org/10.1007/BF01584082).
7. Tara Fife and James Oxley. [Laminar Matroids](https://arxiv.org/abs/1606.08354), arXiv:1606.08354 (2016).
8. Gregory Martin and Yue Shi. An algorithm for Egyptian fraction representations with restricted denominators. *Involve* 18 (2025), 1–23. [DOI](https://doi.org/10.2140/involve.2025.18.1).
9. [Original Sage and matched-engine cloud pilot, workflow 38176293521](https://github.com/qorud02/erdos-295-k18/actions/runs/38176293521), including `cloud-comparison.json` and `matched-oracle-validation.json`.
10. Kyunghan Bae. [Egyptian-fraction certificates, code and records](https://github.com/qorud02/erdos-295-k18). The original N=18 archive is [10.5281/zenodo.23297810](https://doi.org/10.5281/zenodo.23297810).
