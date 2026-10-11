"""Reusable exact bounds conditional on a certified local-shortening exclusion.

All functions use Python integers and fractions.Fraction. The arithmetic
function below derives a quota from a theorem premise; it does not certify
the premise. A completed exhaustive search or a proof must supply that fact.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Iterable

def intersection_quota(reference_size: int, removed_terms: int, deficit: int) -> int:
    """Return m-r-1, conditional on absence of every r -> r-deficit surgery.

    Reference and target have equal positive reciprocal sum. Reference size
    is m and target size is m-deficit. Each forbidden surgery retains every
    term outside its removed r-subset. For r=m, -1 means no target exists.
    """
    m,r,d=reference_size,removed_terms,deficit
    if not all(isinstance(x,int) for x in (m,r,d)) or not (1<=d<=r<=m and m-d>=1):
        raise ValueError('require integer 1 <= deficit <= removed_terms <= reference_size and positive target size')
    return m-r-1

def exclusion_group(reference: Iterable[int], mandatory_removed: Iterable[int],
                    removed_terms: int, deficit: int) -> tuple[tuple[int,...],int]:
    """Group capacity conditional on all surgeries containing a fixed core C.

    If every r -> r-deficit surgery with C contained in the removed set is
    excluded, every target shares at most m-r-1 terms with A minus C. Terms
    of C may be removed and then reinserted by the replacement; thus this
    capacity is unconditional on whether the target itself contains C.
    """
    A=_reference(reference);C=_reference(mandatory_removed)
    q=intersection_quota(len(A),removed_terms,deficit)
    if not C<=A or len(C)>removed_terms:
        raise ValueError('mandatory removed core must be contained in reference and fit the removed cardinality')
    return tuple(sorted(A-C)),q

def _reference(values: Iterable[int]) -> frozenset[int]:
    values=tuple(values)
    if any(not isinstance(x,int) or isinstance(x,bool) or x<=0 for x in values):
        raise ValueError('reference denominators must be positive integers')
    if len(set(values))!=len(values):
        raise ValueError('reference denominators must be distinct')
    return frozenset(values)

def greedy_quota_denominators(reference: Iterable[int], minimum: int,
                              terms: int, remaining_quota: int) -> tuple[int,...] | None:
    """The t smallest distinct integers >=minimum using <=q reference terms.

    None means the quota itself is already infeasible (q<0). For a finite
    reference, the infinite complement supplies any finite number of terms.
    The returned set maximizes the reciprocal sum under these constraints.
    """
    A=_reference(reference)
    if not isinstance(minimum,int) or minimum<=0 or not isinstance(terms,int) or terms<0 or not isinstance(remaining_quota,int):
        raise ValueError('minimum must be positive; terms nonnegative; quota integer')
    if remaining_quota<0:return None
    q=remaining_quota;chosen=[];x=minimum
    while len(chosen)<terms:
        if x in A:
            if q==0:x+=1;continue
            q-=1
        chosen.append(x);x+=1
    return tuple(chosen)

def quota_harmonic_bound(reference: Iterable[int], minimum: int,
                         terms: int, remaining_quota: int) -> Fraction | None:
    ds=greedy_quota_denominators(reference,minimum,terms,remaining_quota)
    return None if ds is None else sum((Fraction(1,x) for x in ds),Fraction())

def laminar_quota_denominators(groups: Iterable[Iterable[int]], minimum: int,
                               terms: int, remaining_quotas: Iterable[int]) -> tuple[int,...] | None:
    """Exact greedy maximum for disjoint or nested finite capacity groups.

    Arbitrarily overlapping groups are rejected: greedy is not generally
    valid for that case. Infeasible negative remaining capacity returns None.
    """
    groups=tuple(_reference(g) for g in groups);quotas=list(remaining_quotas)
    if len(groups)!=len(quotas) or any(not isinstance(q,int) for q in quotas):
        raise ValueError('one integer quota per group is required')
    if not isinstance(minimum,int) or minimum<=0 or not isinstance(terms,int) or terms<0:
        raise ValueError('positive minimum and nonnegative number of terms required')
    if any(q<0 for q in quotas):return None
    for i,A in enumerate(groups):
        for B in groups[i+1:]:
            if A&B and not (A<=B or B<=A):raise ValueError('capacity groups must be laminar: nested or disjoint')
    out=[];x=minimum
    while len(out)<terms:
        memberships=[i for i,g in enumerate(groups) if x in g]
        if all(quotas[i]>0 for i in memberships):
            out.append(x)
            for i in memberships:quotas[i]-=1
        x+=1
    return tuple(out)

def laminar_quota_bound(groups: Iterable[Iterable[int]], minimum: int,
                        terms: int, remaining_quotas: Iterable[int]) -> Fraction | None:
    ds=laminar_quota_denominators(groups,minimum,terms,remaining_quotas)
    return None if ds is None else sum((Fraction(1,x) for x in ds),Fraction())

def prefix_quota_state(reference: Iterable[int], prefix: Iterable[int],
                       minimum: int, target_terms: int, quota: int,
                       target_sum: Fraction=Fraction(1)) -> dict:
    """Exact residual and conditional feasibility bound for a fixed prefix."""
    A=_reference(reference);P=tuple(prefix)
    if any(not isinstance(x,int) or x<minimum for x in P) or any(x>=y for x,y in zip(P,P[1:])):
        raise ValueError('prefix must be strictly increasing and at least minimum')
    t=target_terms-len(P)
    if t<0:raise ValueError('prefix exceeds target cardinality')
    c=sum(x in A for x in P);q=quota-c;d=P[-1]+1 if P else minimum
    residual=Fraction(target_sum)-sum((Fraction(1,x) for x in P),Fraction())
    bound=quota_harmonic_bound(A,d,t,q)
    return {'prefix':P,'next_minimum':d,'terms_remaining':t,'selected_reference_terms':c,
            'reference_quota_remaining':q,'residual':residual,'upper_bound':bound,
            'passes_necessary_bound':bound is not None and residual>=0 and bound>=residual}

def next_denominator_upper(reference: Iterable[int], minimum: int, terms: int,
                            remaining_quota: int, residual: Fraction) -> int | None:
    """Largest x passing the quota harmonic test; None if the whole state fails.

    This bounds a possible first denominator. The greedy set may skip x
    when x itself belongs to a saturated reference group, which only enlarges
    the permitted range and therefore preserves the necessary-condition use.
    """
    residual=Fraction(residual)
    if residual<=0 or terms<1:raise ValueError('positive residual and terms required')
    A=_reference(reference)
    h=quota_harmonic_bound(A,minimum,terms,remaining_quota)
    if h is None or h<residual:return None
    lo=minimum;hi=(terms*residual.denominator)//residual.numerator
    while lo<hi:
        mid=(lo+hi+1)//2
        if quota_harmonic_bound(A,mid,terms,remaining_quota)>=residual:lo=mid
        else:hi=mid-1
    return lo
