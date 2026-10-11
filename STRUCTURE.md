# From local exclusions to overlap-constrained reciprocal bounds

Kyunghan Bae · 12 October 2026

This note turns a completed family of local searches into a constraint on every shorter representation. The implication works for arbitrary additive weights. For unit fractions, the resulting overlap constraints give exact, finitely computable reciprocal-sum envelopes, even though the permitted denominators are unbounded.

The arguments use elementary cancellation, classical matroid greedy optimization, and Lagrangian weak duality. The results here comprise the transfer proofs, verified local-exclusion premises, and reusable exact envelopes.

## 1. A forbidden retained set

Let U be a universe, w:U→R an arbitrary weight function, and write W(S)=Σ(x∈S)w(x) for a finite set S. Fix a finite reference A⊆U of size m, a deficit 1≤d≤m, and the target weight W(A).

For R⊆A with |R|=r≥d, an admissible replacement is a finite set T⊆U of size r−d with

$
T\cap(A\setminus R)=\varnothing,\qquad W(T)=W(R).
$

Elements of R may reappear in T. This convention is essential for the compression below.

**Lemma 1.** Such a replacement exists if and only if there is a set B⊆U with |B|=m−d, W(B)=W(A), and A\R⊆B.

**Proof.** Given T, take B=(A\R)∪T. Conversely, take T=B\(A\R). In both directions disjointness gives the stated cardinality and cancellation gives the weight identity. ∎

Consequently, exhausting this one replacement search proves the inequality

$
|B\cap(A\setminus R)|\le m-r-1
$

for every target B. A family of completed searches supplies a family of these constraints. This implication never treats a time limit as a completed exclusion.

## 2. Compressing a full family into one quota

Fix a core C⊆A and assume |C|≤r≤m and d≤r. Suppose that **every** r-element R⊆A containing C has no admissible replacement.

**Theorem 2.** Every B⊆U with |B|=m−d and W(B)=W(A) satisfies

$
\boxed{|B\cap(A\setminus C)|\le m-r-1.}
$

**Proof.** Let K=A\B. If |K∪C|≤r, extend K∪C to an r-element set R⊆A. Then A\R⊆B, which contradicts Lemma 1. Hence |K∪C|≥r+1. Taking its complement inside A gives

$
|B\cap(A\setminus C)|=m-|K\cup C|\le m-r-1.
$

No positivity or rationality assumption is needed for this implication. ∎

When C=∅, this says |A∩B|≤m−r−1. Therefore B adds at least r−d+1 elements outside A, and removes at least r+1 elements of A. At r=m, the negative quota says that no target B exists. For positive weights, the r=d boundary already excludes a nonempty positive-weight set being replaced by the empty set.

## 3. Exact reciprocal envelopes for one or nested quotas

Now take U={D,D+1,…} minus a finite forbidden set and w(x)=1/x, where D≥1. Suppose a t-element continuation X must satisfy |X∩J|≤q for a finite set J and q≥0.

Scan denominators in increasing order, accept a denominator unless it would exceed the quota, and stop after t acceptances. Write the result g₁<⋯<gₜ.

**Theorem 3.** Every feasible continuation x₁<⋯<xₜ satisfies gⱼ≤xⱼ for each j, and therefore

$
\max_X\sum_{x\in X}\frac1x=\sum_{j=1}^t\frac1{g_j}.
$

**Proof.** Among permitted denominators ≤z, the greatest feasible cardinality is the number outside J plus the smaller of q and the number inside J. Thus the greedy jth denominator is the first z at which that cardinality reaches j. Any feasible xⱼ has reached it. ∎

For a laminar family of finite sets Jᵢ (each pair is nested or disjoint), accepting the next denominator whenever all quotas remain satisfied also maximizes reciprocal weight at a fixed feasible cardinality. This is classical greedy optimization for a truncated laminar matroid. The infinite universe reduces to the finite pool in §4. Crossing sets require a different optimization; greedy is not valid in general.

For a chosen prefix P, replace each quota qᵢ by qᵢ−|P∩Jᵢ| and use D=max(P)+1. A negative residual quota excludes the branch. If the residual rational target exceeds the envelope, the branch is impossible. Increasing D can only decrease the envelope, so the condition also gives a safe next-denominator upper bound.

## 4. Several crossing quotas: an exact finite optimization

Let J₁,…,Jₛ be arbitrary finite sets, with residual quotas qᵢ≥0. Partition permitted denominators by the membership pattern

$
C_\sigma=\{x\ge D:\{i:x\in J_i\}=\sigma\},\quad\sigma\subseteq\{1,\ldots,s\}.
$

Let Fσ(n) be the sum of the first n reciprocals in Cσ, with Fσ(0)=0. Disallow n when the atom has fewer than n elements.

**Theorem 4.** The exact maximum reciprocal sum for a t-element continuation is

$
\max\left\{\sum_\sigma F_\sigma(n_\sigma):
\sum_\sigma n_\sigma=t,\quad
\sum_{\sigma\ni i}n_\sigma\le q_i,\quad n_\sigma\in\mathbb Z_{\ge0}\right\}.
$

Only the first t members of each atom are needed. All nonempty-pattern atoms lie in the finite union of Jᵢ, and the empty-pattern atom contributes only its first t members. Thus this is a finite integer dynamic program with no denominator cap.

**Proof.** Fix the atom counts of a feasible set. Within each atom, replacing the chosen denominators by the same number of its smallest members preserves every quota and maximizes their reciprocal sum. Conversely, the first nσ members of the disjoint atoms realize every permitted count vector. ∎

This is exact finite optimization rather than a polynomial-time complexity claim. The number of atoms and states can grow with the number of constraints.

## 5. A cheaper certified bound for crossing quotas

For any exact rational multipliers λᵢ≥0, define

$
v(x)=\frac1x-\sum_{i:x\in J_i}\lambda_i.
$

Let Mₜ(v) be the sum of the t largest adjusted weights among permitted denominators. Classical weak duality gives

$
\boxed{\sum_{x\in X}\frac1x\le
\sum_i\lambda_iq_i+M_t(v).}
$

Indeed, expand the left side as Σv(x)+Σᵢλᵢ|X∩Jᵢ|, then bound its two parts separately. To compute Mₜ exactly, compare all eligible members of ∪Jᵢ with the first t permitted denominators outside that union. Every omitted outside denominator is dominated by those t outside candidates. Negative adjusted weights cause no difficulty because there are infinitely many positive outside weights.

For example, take D=10, t=2, J₁={10,11,13}, J₂={10,12,13}, q₁=q₂=1. Greedy picks 10 and 14, giving 6/35, while 11 and 12 give the larger 23/132. The multipliers λ₁=3/154, λ₂=1/84 give a dual bound exactly 23/132. The example both disproves crossing-quota greedy and certifies the optimum.

`structure/dual_tools.py` computes this bound with exact rational arithmetic and emits the complete finite evaluation certificate.

## 6. Application to the 34-term N=18 certificate

Let A be the 34 denominators in `certificates-extension.json`. Completed searches establish the following premises; their code, coverage, and limits are recorded in `SEARCH_STATUS.md`.

* All C(34,5)=278,256 five-to-four replacement searches completed. Theorem 2 with C=∅ gives **|B∩A|≤28** for every 33-term representation with denominators ≥18.
* All C(32,4)=35,960 six-to-five replacement searches containing C={14,143,068; 10,457,416,992} completed, including the resumed boundary case. Theorem 2 gives **|B∩(A\C)|≤27** for every such B.

These are nested overlap constraints. They apply to the entire unbounded denominator universe, rather than only to a finite candidate list. Together with the exact envelopes they supply sound reusable pruning. They do not decide whether a 33-term representation exists. A faster search is an empirical question; the benchmark record is kept separate from soundness.

## References and provenance

* David Eppstein, [Algorithms for Egyptian Fractions: Brute Force Methods](https://ics.uci.edu/~eppstein/numth/egypt/force.html), for classical fixed-length search and two-term factorization.
* Greg Martin and Yue Shi, [An algorithm for Egyptian fraction representations with restricted denominators](https://personal.math.ubc.ca/~gerg/papers/downloads/AEFRRD.pdf), Involve 18 (2025), DOI [10.2140/involve.2025.18.1](https://doi.org/10.2140/involve.2025.18.1), for a finite-denominator enumeration algorithm using arithmetic restrictions.
* The structural arguments above are supplied in full. Additional primary references on laminar matroids and dual bounds are listed in `structure/PRIOR_ART.md`.
