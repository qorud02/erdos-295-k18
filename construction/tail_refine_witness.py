"""Witness search with partial divisor blocks; negative results are heuristic only."""
from pathlib import Path
import importlib.util,json,time,math,bisect
from fractions import Fraction
HERE=Path(__file__).resolve().parent
OLD=HERE/'search-deps'
spec=importlib.util.spec_from_file_location('engine',OLD/'search-earlyterminal.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
base=e.terminal.strong._base
class WitnessSearch(e.Search):
    def two(self,d,a,b,primes):
        lo=max(d,b//a+1);hi=self.next_upper(lo,2,a,b)
        if lo>hi:return None
        if hi-lo<=10000:return super().two(d,a,b,primes)
        rem=b;factors=[]
        for p in primes:
            exp=0
            while rem%p==0:exp+=1;rem//=p
            if exp:factors.append((p,2*exp))
        if rem>1:factors.append((rem,2));self.stats['partial_divisor_blocks']=self.stats.get('partial_divisor_blocks',0)+1
        # The remaining composite is a block, so generated products always divide b^2.
        # Some other divisors may be missed. This is solely a positive-witness search.
        halves=[[],[]];counts=[1,1]
        for p,exp in sorted(factors,key=lambda pe:pe[1],reverse=True):
            i=0 if counts[0]<=counts[1] else 1
            halves[i].append((p,exp));counts[i]*=exp+1
        if max(counts)>1000000:
            self.stats['divisor_size_skips']=self.stats.get('divisor_size_skips',0)+1;return None
        qlo=max(1,a*lo-b);qhi=min(b-1,a*hi-b)
        def divs(fs):
            ans=[1]
            for p,exp in fs:
                old=ans;ans=[];power=1
                for _ in range(exp+1):
                    ans.extend(x*power for x in old if x*power<=qhi);power*=p
            return ans
        left,right=divs(halves[0]),divs(halves[1]);buckets={}
        for q in right:buckets.setdefault(q%a,[]).append(q)
        for bucket in buckets.values():bucket.sort()
        self.stats['witness_divisor_calls']=self.stats.get('witness_divisor_calls',0)+1
        for j,u in enumerate(left):
            if j%1024==0:self.tick()
            target=(-b*pow(u,-1,a))%a if a>1 else 0
            bucket=buckets.get(target,())
            vlow=(qlo+u-1)//u;vhi=qhi//u
            ix=bisect.bisect_left(bucket,vlow)
            if ix<len(bucket) and bucket[ix]<=vhi:
                q=u*bucket[ix];x=(b+q)//a;yn=b+b*b//q
                if yn%a==0:
                    y=yn//a
                    if x>=d and y>x and Fraction(1,x)+Fraction(1,y)==Fraction(a,b):return(x,y)
        return None

def main():
    old=json.loads((HERE/'tail-refinement-results.json').read_text());seeds={int(n):ds for n,ds in old['best'].items()};records=[]
    for N in [20,21,22]:
        ds=seeds[N];target=len(ds)-1
        for t in range(2,9):
            fixed=ds[:target-t];r=1-sum((Fraction(1,d) for d in fixed),Fraction())
            s=WitnessSearch(seconds=12,cap=None,memo_size=1000,prime_prune=True)
            try:
                ans=s.dfs(fixed[-1]+1,t,r.numerator,r.denominator,base.small_prime_factors(r.denominator),())
                status='found' if ans else 'no_witness_in_partial_divisor_scope'
            except base.SearchTimeout:ans=None;status='timeout'
            rec={'minimum':N,'target':target,'tail_terms':t,'fixed_prefix':fixed,'status':status,'counters':s.stats,'elapsed_seconds':time.monotonic()-s.start}
            if ans:
                full=fixed+list(ans);assert len(full)==target and len(full)==len(set(full)) and min(full)>=N and sum((Fraction(1,d) for d in full),Fraction())==1
                rec['denominators']=full;seeds[N]=full
            records.append(rec);print(json.dumps(rec),flush=True)
            (HERE/'witness-tail-refinement-results.json').write_text(json.dumps({'scope':'Partial-divisor positive-witness search; negative results are not exclusions.','records':records,'best':seeds},indent=2))
            if ans:break
if __name__=='__main__':main()
