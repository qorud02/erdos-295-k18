# A 34-term unit-fraction expansion with minimum denominator 18

**Kyunghan Bae**  
11 October 2026

Let \(k(N)\) be the least integer \(k\) for which distinct integers
\(N\le d_1<\cdots<d_k\) satisfy \(\sum_{i=1}^k 1/d_i=1\).
We give an explicit certificate for \(k(18)\le34\). Together with the previously reported computational lower bound, independently reproduced in the accompanying code, this gives

\[
33\le k(18)\le34.
\]

## The construction

**Theorem.** The following set \(D\) consists of 34 distinct integers at least 18 and satisfies \(\sum_{d\in D}1/d=1\):

~~~text
18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
32, 33, 34, 35, 36, 38, 39, 40, 43, 44, 45, 46,
48, 50, 52, 54, 63, 275, 14143068, 10457416992
~~~

**Proof.** The least common multiple of these denominators is
\(L=6\,209\,352\,774\,424\,800\). Exact integer addition gives

\[
\sum_{d\in D}L/d=6\,209\,352\,774\,424\,800=L.
\]

Dividing by \(L\) proves the identity. The order, cardinality, and minimum of the displayed set give \(k(18)\le34\). ∎

The construction can also be obtained from the 35-term certificate published by Patrick White with Claude on 11 August 2026 [1]. Replace five of its terms using

\[
\frac1{42}+\frac1{640}+\frac1{337280}
+\frac1{1735650}+\frac1{68479214496}
=
\frac1{46}+\frac1{275}
+\frac1{14143068}+\frac1{10457416992}.
\]

Multiplication by \(M=636\,856\,694\,812\,800\) turns both sides into the integer \(16\,160\,598\,373\,892\). The four replacement denominators are distinct and absent from the 30 retained terms.

## Lower bound and the remaining case

White's report gives \(33\le k(18)\le35\), with exhaustive exclusions of 31 and 32 terms [1]. We reproduced the 32-term exclusion using separately written Python exact integers and fractions, C# BigInteger, and C++ GMP implementations. Each completed with 814,918 visited states, 134,999 prime-condition prunes, 648,193 quadratic terminal prunes, and 31,726 stored failed states. The programs share the same mathematical recurrence; their agreement cross-checks implementation and arithmetic.

At a positive reduced remainder \(a/b\), with \(t\ge2\) terms left and minimum allowed denominator \(D_0\), the next denominator belongs to the finite interval

\[
\max(D_0,\lfloor b/a\rfloor+1)\le x\le\lfloor tb/a\rfloor.
\]

Exact harmonic upper bounds and prime-power conditions prune impossible branches. At two terms, the forced final denominator is \(y=bx/(ax-b)\). Its integrality is checked exactly, without an imposed denominator cap. The accompanying [proof details](proofs.md), [Python log](early-n18-t32.log), [C# records](independent-native-validation.jsonl), and [C++ log](cpp-n18-t32.log) describe the completed exclusion.

Excluding exactly 32 terms also excludes every shorter expansion: replace its largest denominator \(d\) by \(d+1\) and \(d(d+1)\), using
\(1/d=1/(d+1)+1/[d(d+1)]\), and repeat until there are 32 terms. The new denominators exceed every retained denominator. Thus \(k(18)\ge33\).

Whether a 33-term expansion exists remains open in this work. The asymptotic question in Erdős problem 295, \(k(N)-(e-1)N\to+\infty\), also remains open [2].

## Reproducing the upper certificate

This self-contained Python 3.9+ check uses only the standard library:

~~~python
from fractions import Fraction
from math import lcm

D = [18,19,20,21,22,23,24,25,26,27,28,29,30,31,
     32,33,34,35,36,38,39,40,43,44,45,46,
     48,50,52,54,63,275,14143068,10457416992]
assert len(D) == len(set(D)) == 34 and D == sorted(D)
assert min(D) == 18
assert sum((Fraction(1,d) for d in D), Fraction()) == 1
L = lcm(*D)
assert L == 6209352774424800
assert sum(L//d for d in D) == L
old = [42,640,337280,1735650,68479214496]
new = [46,275,14143068,10457416992]
M = lcm(*old, *new)
assert M == 636856694812800
assert sum(M//d for d in old) == sum(M//d for d in new)
assert sum(M//d for d in old) == 16160598373892
print('34-term certificate verified exactly')
~~~

The full certificate was also checked with an independently written JavaScript BigInt calculation. The upper-bound proof depends only on this finite identity, so its verification does not require running the search or installing an optimization solver.

## Computational contribution

This research was initiated by Kyunghan Bae. OpenAI Codex (GPT-6 session) agents developed the search and verification code, found the displayed construction, performed the exact arithmetic checks, and assisted in preparing this note.

## References

[1] Patrick White with Claude. “Erdős #295: k(17) = 32, and now 33 ≤ k(18) ≤ 35 by exact exhaustion.” Erdős Problem a Day, updated 11 August 2026. [Research report](https://erdosproblemaday.com/day/295-k17-exact).

[2] Thomas Bloom, ed. “Erdős Problem #295.” [Problem statement](https://www.erdosproblems.com/295).
