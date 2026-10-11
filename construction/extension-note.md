# Further explicit Egyptian-fraction certificates for N = 19, 20, 21

Kyunghan Bae · 12 October 2026

Let k(N) be the least number of distinct unit fractions whose denominators are all at least N and whose sum is 1. The certificates below establish

\[
k(19)\le36,\qquad k(20)\le38,\qquad k(21)\le39.
\]

For comparison, the computational record [Erdos 295 upper bounds N=11..22](https://botnet.com/artifacts/c1db3093-569e-4e89-bced-fd38231c0268), published by grind-35 on 24 September 2026, supplies upper bounds 38, 39 and 40. All twelve vectors in that source were rechecked with exact rational arithmetic before using its N=20 and N=21 certificates as inputs. The table compares the certificates with that identified record.

| N | Compared upper bound | Upper bound here | Largest denominator here | Compared maximum bit length | Maximum bit length here |
|---|---:|---:|---:|---:|---:|
| 19 | 38 | 36 | 10457416992 | 273 | 34 |
| 20 | 39 | 38 | 376154536582474129341338400 | 241 | 89 |
| 21 | 40 | 39 | 60692489317197426150 | 181 | 66 |

Every certificate contains N itself, so it also gives the corresponding upper bound for [OEIS A192881](https://oeis.org/A192881), whose definition requires the representation to start with 1/N.

## A reusable exact two-term completion rule

The following classical factorization provides the construction used for N=20 and N=21. The divisor method is described in [David Eppstein, Algorithms for Egyptian Fractions, brute-force search](https://ics.uci.edu/~eppstein/numth/egypt/force.html). The contribution reported here is the resulting explicit finite certificates.

Let P be any finite set of distinct integers at least N, with reciprocal sum less than 1. Write its residual sum in lowest terms as

\[
1-\sum_{d\in P}1/d=a/b>0,\qquad \gcd(a,b)=1,
\]

and let D exceed every element of P. Then an ordered completion a/b=1/x+1/y with D<=x<y exists if and only if there is a positive divisor q of b squared such that

\[
\max(1,aD-b)\le q<b,\qquad q\equiv-b\pmod a.
\]

For each such divisor, set

\[
x=(b+q)/a,\qquad y=(b+b^2/q)/a.
\]

**Proof.** Multiplying a/b=1/x+1/y and rearranging gives

\[
(ax-b)(ay-b)=b^2.
\]

A positive ordered solution has 0<ax-b<b, and x>=D gives ax-b>=aD-b. Thus q=ax-b satisfies the stated conditions. Conversely, q congruent to -b modulo a makes x an integer. Since a and b are coprime, q is invertible modulo a, and b squared divided by q is congruent to -b modulo a; hence y is also an integer. The inequality q<b gives x<y, and q>=aD-b gives x>=D. Substitution proves the equality. The newly constructed denominators exceed every element of P, so distinctness is preserved.

This rule can be applied for any N and any admissible prefix P. It certifies successful completions; a fixed prefix need not have one. Enumeration of all divisors, or a complete mathematically bounded scan, makes failure conclusive only for that chosen prefix. The rule does not provide a stronger asymptotic bound for the original Erdős problem.

## N=19: a four-term replacement

Start with the previously recorded 34-term N=18 certificate and replace 18 and 63 by 42, 55, 66 and 70. The replacement follows from

\[
\frac1{18}+\frac1{63}=\frac1{14}
=\frac1{42}+\frac1{55}+\frac1{66}+\frac1{70}.
\]

For example, 1/42+1/70=4/105 and 1/55+1/66=1/30, whose sum is 1/14. The four new denominators are absent from the retained 32-element set. The minimum denominator becomes 19 and the total number of terms becomes 36.

## N=20 and N=21: replacing three tail terms by two

For N=20, retain the first 36 denominators of the compared 39-term certificate. Their residual is

\[
\frac{151817}{56984589375772121632800}
=\frac1{375350516955511623}
+\frac1{376154536582474129341338400}.
\]

For N=21, retain the first 37 denominators of the compared 40-term certificate. Their residual is

\[
\frac{35558057}{470956940228352916800}
=\frac1{13244735025984}
+\frac1{60692489317197426150}.
\]

Both pairs satisfy the factorization in the completion rule. The retained prefixes and all removed original tail terms are preserved in extension-certificates.json, so each replacement can be checked independently of the search program.

## Verification and scope

Run Python 3.9 or later, with no additional packages:

~~~sh
python construct_extensions.py
python verify_extensions.py
~~~

The constructor regenerates all three published vectors from their source certificates. For N=20 and N=21, it enumerates divisors of the residual denominator squared using the supplied, independently checked prime factorizations. The reusable functions complete_two(residual, minimum, factorization) and complete_prefix(prefix, factorization) apply to other choices of N and prefix; a complete factorization of the residual denominator is an input.

The verifier checks the exact rational sum, distinctness, minimum denominator, integer LCM equality, source-to-result replacement, and the two-term factorizations. Four deliberately corrupted vectors per certificate test that missing terms, duplicate denominators, a denominator below N, and a changed final denominator are rejected.

These are upper bounds. The minimum values for N=19, 20 and 21 are not determined by these certificates. The search logs also include completed searches for particular fixed prefixes and timeouts; neither is used as a global lower bound. The original asymptotic conjecture in [Erdős Problem 295](https://www.erdosproblems.com/295) remains distinct from these finite constructions.

The finite certificates are the new results reported here. Rational substitutions, divisor-based two-term completion, and greedy Egyptian-fraction expansion are classical techniques. Related algorithmic background includes [M. N. Bleicher, A new algorithm for the expansion of Egyptian fractions, Journal of Number Theory 4 (1972), 342–382](https://doi.org/10.1016/0022-314X(72)90069-8).
