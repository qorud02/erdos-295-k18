"""Standalone exact verification; Python 3.9+, standard library only."""
from pathlib import Path
from fractions import Fraction
from math import lcm
import json
HERE=Path(__file__).resolve().parent

def valid(ds,N,count):
    if len(ds)!=count or len(ds)!=len(set(ds)) or min(ds)<N:return False
    return sum((Fraction(1,d) for d in ds),Fraction())==1

def main():
    bundle=json.loads((HERE/'extension-certificates.json').read_text())
    checked=[]
    for item in bundle['results']:
        N=item['N'];k=item['upper_bound'];ds=list(map(int,item['denominators']))
        assert valid(ds,N,k)
        L=lcm(*ds);scaled=sum(L//d for d in ds)
        assert str(L)==item['lcm'] and str(scaled)==item['scaled_sum'] and L==scaled
        source=list(map(int,item['source_denominators']))
        old=list(map(int,item['removed']));new=list(map(int,item['added']))
        assert len(source)==len(set(source)) and sum((Fraction(1,d) for d in source),Fraction())==1
        assert set(old).issubset(source) and set(new).isdisjoint(set(source)-set(old))
        assert sorted((set(source)-set(old))|set(new))==ds
        r=sum((Fraction(1,d) for d in old),Fraction())
        assert r==sum((Fraction(1,d) for d in new),Fraction()) and str(r)==item['replacement_sum']
        if len(new)==2:
            x,y=new;a,b=r.numerator,r.denominator
            assert (a*x-b)*(a*y-b)==b*b and 0<a*x-b<b
            assert (a*x-b)%a==(-b)%a
        negative=[ds[:-1], [ds[1]]+ds[1:], [N-1]+ds[1:], ds[:-1]+[ds[-1]+1]]
        assert all(not valid(x,N,k) for x in negative)
        checked.append({'N':N,'upper_bound':k,'fraction_sum':'1','lcm_equal_scaled_sum':True,'replacement_verified':True,'negative_controls':len(negative),'passed':True})
    result={'all_passed':True,'checks':checked}
    (HERE/'extension-verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
