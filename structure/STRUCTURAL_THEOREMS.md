# Local exclusion certificates and exact overlap envelopes

Date: 2026-10-12. This note separates the algebraic theorem, the computational premise needed to apply it, and the optimization of its resulting quotas.

## 1. Definitions

Let U be a universe with positive weights w:U -> R_{>0}. For finite E, write w(E)=sum_{x in E} w(x). Fix A subset U, |A|=m, and integers 1<=d<=r<=m with d<m. A target is any finite B subset U with |B|=m-d and w(B)=w(A).

An exact r-to-(r-d) replacement consists of R subset A with |R|=r and a set T subset U minus (A minus R) with |T|=r-d and w(T)=w(R). The condition forbids reusing retained elements. It permits reusing removed elements, so T may intersect R. The resulting representation is (A minus R) union T.

A genuine replacement additionally requires T disjoint from A. Its removed cardinality p may be smaller than r.

**Padding lemma.** Absence of every exact r-to-(r-d) replacement with removed-element reuse is equivalent to absence of every genuine p-to-(p-d) replacement for d+1<=p<=r.

Proof. Cancel Q=R intersect T from both sides of an exact replacement. The remaining removed set R'=R minus Q has size p, the added set T'=T minus Q is outside A and has size p-d, and their weights agree. Positivity rules out p=d, since that would equate a nonempty positive-weight set with the empty set. Conversely, pad a genuine p-replacement with any r-p members P of A minus R'. Such P exist because r<=m. Set R=R' union P and T=T' union P. These have sizes r and r-d, equal weight, and T avoids A minus R. QED.

Checking only genuine replacements at exactly r does not imply this lemma's premise. Example: source weights 1,2,4,8 and one outside element of weight 3 admit the target weights 3,4,8. There is a genuine 2-to-1 replacement, but no genuine 3-to-2 replacement because the outside universe has only one element. Reusing a removed weight 4 produces the padded 3-to-2 replacement {1,2,4} -> {3,4}.

## 2. Core exclusion theorem

**Theorem 1 (mandatory removed core).** Fix C subset A, |C|<=r. Suppose that for every R subset A of size r containing C, no exact r-to-(r-d) replacement exists under the reuse convention above. Then every target B satisfies

    |B intersect (A minus C)| <= m-r-1.                         (1)

Proof. Put K=A minus B. If |K union C|<=r, extend K union C to an r-element subset R of A. Then A minus R is contained in B. Define

    T = B minus (A minus R).

Since |B|=m-d and |A minus R|=m-r, we have |T|=r-d. Also

    w(T)=w(B)-w(A minus R)=w(A)-w(A minus R)=w(R).

By definition, T avoids A minus R. Thus R,T constitute a forbidden replacement. Hence |K union C|>=r+1. Its complement in A is B intersect (A minus C), proving (1). QED.

The proof uses finite-set cancellation; positivity is only needed for the genuine-move interpretation in Section 1. There is no assumption that B contains or avoids C. This last point allows a certificate computed with a mandatory removed core to impose an unconditional quota on A minus C.

**Corollary 1 (no core).** Taking C empty gives |A intersect B|<=m-r-1. Equivalently, a smaller equal-sum representation must replace at least r+1 source elements. When r=m, the conclusion has right-hand side -1 and therefore certifies that no target exists.

**Corollary 2 (several certificates).** Every certified triple (A_i,C_i,r_i), with |A_i|=m and w(A_i)=w(A), supplies a quota on G_i=A_i minus C_i:

    |B intersect G_i| <= |A_i|-r_i-1.

All such quotas hold simultaneously. They may be nested, disjoint, or crossing. Sources of different sizes are allowed if each local deficit is chosen as d_i=|A_i|-|B| and its theorem hypotheses hold.

**Concrete conditional application.** For the 34-term source A and 33-term target B, a completed exclusion of every padded 5-to-4 replacement gives |B intersect A|<=28. A completed exclusion of every 6-to-5 replacement whose removed set contains the two largest source denominators gives |B intersect (A minus C)|<=27. The latter family has choose(32,4)=35,960 removed sets. These groups are nested. Each conclusion depends on a complete search or mathematical proof of its own exclusion premise; a timeout or a bounded trial cannot supply that premise.

The current ../search-records/local_surgery.py implements the needed convention: it constructs kept=set(BASE)-set(removed) and passes kept to Search as its forbidden set. Therefore removed denominators remain available to the replacement search. Earlier discovery scripts that forbade all source denominators use a different convention and cannot alone supply the exact-r padding premise.

## 3. Sharpness for general positive weights

For any 1<=d<=r<=m-1, the no-core bound m-r-1 is sharp in the class of arbitrary positive integer weights.

Let q=r+1-d and W=q*ceil(r/q)+1. Then W>r and gcd(W,q)=1. Take r+1 source elements R: r of weight q and one of weight q(W-r). Their total weight is qW. Add m-r-1 common source elements, each with any positive weight divisible by q. Outside the source, take exactly q distinct elements T, each of weight W. The target (A minus R) union T has size m-d, equal weight, and overlap m-r-1.

A genuine p-to-(p-d) move with p<=r would add j=p-d outside elements, where 0<=j<q. For j=0 positivity excludes equality. For 1<=j<q, their sum jW is nonzero modulo q, whereas every removed source sum is divisible by q. Thus no such move exists. By the padding lemma there is no padded exact-r replacement either.

This construction concerns weighted elements; its equal weights are permitted. It does not establish sharpness for distinct reciprocal weights.

## 4. Exact one-quota reciprocal envelope

Now take U_D={D,D+1,...} minus F, where D>=1 and F is finite. Fix a finite reference group G and nonnegative quota u. For any subset X of U_D, let H_X(j) be the sum of reciprocals of its j smallest elements, with H_X(0)=0. A request exceeding a finite X's cardinality is inadmissible. Write G_D=G intersect U_D and O_D=U_D minus G.

**Theorem 2 (one quota).** Among all t-element sets E subset U_D satisfying |E intersect G|<=u, the exact largest reciprocal sum is

    M = max_j [H_{G_D}(j)+H_{O_D}(t-j)],                     (2)
    0<=j<=min(u,t,|G_D|).

Proof. For fixed j, replacing each within-group choice by the j smallest members of G_D, and each outside choice by the t-j smallest members of O_D, preserves cardinalities and the quota and cannot decrease the sum. Those two initial segments attain the displayed value. Maximizing over j proves the statement. QED.

The maximum is over allowable j, rather than always j=u. An equivalent implementation scans permitted denominators in increasing order, accepts a group member while its quota remains positive, and stops after t accepted denominators.

For a fixed increasing search prefix P and global quota |B intersect G|<=c, the remaining quota is u=c-|P intersect G|. If u<0, the state is infeasible. With t remaining terms, next denominator D, and residual reciprocal sum rho, every completion must satisfy rho<=M. A strict rho>M rules out that branch. M is exact for the cardinality-and-quota relaxation; the original equal-sum constraint is a separate condition.

## 5. Disjoint and laminar quota groups

A finite family G_1,...,G_s is laminar if two groups are disjoint or one contains the other. For nonnegative integer quotas u_i, the subsets satisfying |E intersect G_i|<=u_i form the independent sets of a laminar matroid. Disjoint groups give the partition-matroid special case. Adding |E|<=t is matroid truncation.

Consequently the maximum reciprocal sum among feasible t-element sets is obtained by scanning permitted denominators increasingly and accepting d whenever adding it respects every group containing d. There are infinitely many integers outside the finite union of groups and F, so the scan can always reach t accepted terms. The classical finite weighted-greedy theorem applies after the finite-support reduction in Section 6. See Edmonds (1971) and Fife–Oxley in PRIOR_ART_STRUCTURAL.md.

For completeness, the exchange property behind this use of greedy is elementary. Given feasible I,J with |I|<|J|, suppose no x in J minus I can be added to I. Each such x lies in a saturated group G with |I intersect G|=u_G. Choose the inclusion-maximal saturated groups; laminarity makes them disjoint, and they cover J minus I. In each such group, |J intersect G|<=|I intersect G|, so |(J minus I) intersect G|<=|(I minus J) intersect G|. Summing over the disjoint cover gives |J minus I|<=|I minus J|, contrary to |J|>|I|. Thus an augmenting x exists, establishing the matroid exchange axiom.

Crossing groups need another method. With D=10, t=2, G_1={10,11,13}, G_2={10,12,13}, and both quotas 1, increasing greedy chooses 10 and then 14, with sum 6/35. The feasible set {11,12} has the larger sum 23/132 and is optimal. Therefore unrestricted multi-quota greedy is invalid.

## 6. Exact membership-atom envelope for crossing groups

For arbitrary finite groups G_1,...,G_s, partition U_D by membership patterns sigma subset {1,...,s}:

    X_sigma = {d in U_D: d belongs to G_i exactly when i in sigma}.

Let H_sigma(j) be the reciprocal sum of the j smallest members of X_sigma. Only X_empty can be infinite. The other atoms partition a subset of the finite union of reference groups.

**Theorem 3 (atom optimization).** The exact reciprocal envelope under all quotas is

    max sum_sigma H_sigma(n_sigma),                          (3)

where the nonnegative integers n_sigma satisfy

    sum_sigma n_sigma=t,
    sum_{sigma containing i} n_sigma<=u_i for every i.

Each n_sigma is bounded by its atom's cardinality when that atom is finite.

Proof. A feasible set has an atom-count vector satisfying these constraints. Replacing its members in each atom by that atom's n_sigma smallest members preserves every quota and maximizes its contribution. Conversely those initial segments realize every admissible count vector. There are finitely many vectors since every count is at most t. QED.

**Finite support.** Only the first min(t,|X_sigma|) members of each atom are needed. The empty atom's first t members are found by scanning from D while skipping the finite union of all groups and F. If h is the number of exceptional integers at least D, the scan finishes by D+t+h-1 when t>0. Large sparse reference denominators do not require scanning up to their values. This is an exact finite support for the maximization relaxation; it places no maximum-denominator restriction on solutions of a prescribed equal-sum equation.

**Dynamic program.** Process the nonempty atoms one by one. A state stores the selected cardinality k, each used quota count c_i, the best exact reciprocal sum, and an attaining set. For an atom sigma, try j=0,...,min(t-k,|X_sigma|,min_{i in sigma}(u_i-c_i)); add H_sigma(j), update k and the applicable c_i, and keep the best value for each state. After processing all nonempty atoms, fill t-k elements from the empty atom. Taking the largest final value gives (3).

The implemented state count is at most (t+1)*product_i(min(t,u_i)+1); there may be up to min(2^s,1+sum_i |G_i|) occupied atoms. A transition tries at most t+1 counts. These are elementary dynamic-programming bounds, not a claim of tractability when s or t is large. The implementation raises AtomLimitExceeded at a configured state or transition limit; it does not return an incomplete value as a certified maximum.

## 7. Files and reproduction

The standard-library API is in atom_tools.py:

    reciprocal_atom_envelope(minimum, terms, references, quotas,
                             forbidden=(), *, max_states=200000,
                             max_transitions=5000000)
        -> (fractions.Fraction, certificate_dictionary)

It validates positive integer denominators, nonnegative quotas, exact cardinality, and resource guards. The caller supplies finite reference and forbidden iterables. The certificate records the finite atom candidates, rational prefix sums, attaining denominators, realized quotas, and state counts. Denominators in the certificate use decimal strings, preserving large integers in JSON consumers.

From the workspace root:

    python outputs/erdos-295-extension-2026-10-12/general/test_atom.py

The seeded tests compare 700 generated cases with direct finite enumeration of 82,582 subsets, of which 53,937 satisfy the quotas. The independent enumeration interval contains the infinite-universe optimum by the explicit exceptional-set bound. There are also 125 agreements with the one-quota formula and search33/quota_tools.py, 200 agreements with its laminar API, and 501 comparisons with repo/structure/dual_tools.py verifying dual bound >= exact atom envelope. Resource limits, invalid input, empty target, and an 81-digit sparse exceptional denominator are checked. Results are recorded in atom-test-results.json.

## 8. What this method establishes

The method converts a fully established local exclusion into a necessary condition on every smaller equal-sum representation. It then computes the strongest reciprocal upper bound obtainable from those quotas, cardinality, minimum denominator, and finite forbidden set alone.

A complete minimum proof still needs to cover every surviving global branch or derive a further mathematical obstruction. Finite witness upper bounds, local exhaustion, and quota envelopes have distinct roles in that proof. The finite certificates and their stated deficits must be matched exactly before a quota is used.
