from pathlib import Path
from fractions import Fraction
from math import prod
import json,bisect,time,importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('constructor',HERE/'construct_extensions.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
bundle=json.loads((HERE/'extension-certificates.json').read_text());results=[]
for c in bundle['results']:
 if c['N'] not in (20,21):continue
 started=time.monotonic();N=c['N'];source=list(map(int,c['source_denominators']));P=source[:-3]
 r=1-sum((Fraction(1,d) for d in P),Fraction());a,b=r.numerator,r.denominator
 factors=m.FACTORS[N];assert prod(p**e for p,e in factors)==b and all(m.prime(p) for p,e in factors)
 halves=[[],[]];counts=[1,1]
 for p,e in sorted(((p,2*e) for p,e in factors),key=lambda pe:pe[1],reverse=True):
  i=0 if counts[0]<=counts[1] else 1;halves[i].append((p,e));counts[i]*=e+1
 high=b-1;low=max(1,a*(max(P)+1)-b)
 def divs(fs):
  out=[1]
  for p,e in fs:
   old=out;out=[];power=1
   for _ in range(e+1):out.extend(v*power for v in old if v*power<=high);power*=p
  return out
 left,right=divs(halves[0]),divs(halves[1]);buckets={}
 for v in right:buckets.setdefault(v%a,[]).append(v)
 for bucket in buckets.values():bucket.sort()
 bestq=None;solutions=0
 for u in left:
  bucket=buckets.get((-b*pow(u,-1,a))%a,())
  lo=(low+u-1)//u;hi=high//u
  j=bisect.bisect_right(bucket,hi);k=bisect.bisect_left(bucket,lo);solutions+=j-k
  if j>k:
   q=u*bucket[j-1]
   if bestq is None or q>bestq:bestq=q
 assert bestq is not None
 x=(b+bestq)//a;yn=b+b*b//bestq;assert yn%a==0;y=yn//a
 ds=P+[x,y];assert x<y and len(ds)==len(set(ds)) and sum((Fraction(1,d) for d in ds),Fraction())==1
 result={'N':N,'upper_bound':len(ds),'q':str(bestq),'pair':[str(x),str(y)],'denominators':[str(d) for d in ds],'fixed_prefix':[str(d) for d in P],'residual':str(r),'complete_factorization':[(str(p),e) for p,e in factors],'total_divisor_pairs_examined_by_mitm':len(left),'right_divisor_count':len(right),'number_of_admissible_pairs':solutions,'enumeration_complete':True,'optimality_scope':'Minimizes the larger denominator over all exact two-term completions of this fixed prefix.','old_maximum':c['new_largest_denominator'],'new_maximum':str(y),'old_max_bits':c['new_max_bit_length'],'new_max_bits':y.bit_length(),'elapsed_seconds':time.monotonic()-started}
 results.append(result);print(json.dumps(result),flush=True)
(HERE/'best-size-result.json').write_text(json.dumps({'results':results},indent=2))
