"""Build a restartable partition from the exact DFS stack at interruption.

The interrupted subtree is replayed in full. Only earlier, completed siblings
are omitted. Right siblings are represented as exact finite integer intervals.
This requires the preserved ascending DFS order, without branch reordering.
"""
from fractions import Fraction as F
from pathlib import Path
import json,argparse

p=argparse.ArgumentParser();p.add_argument('--log',default='checkpoint-next30-60s.jsonl');p.add_argument('--output',default='resume-frontier.json');args=p.parse_args()
rows=[json.loads(x) for x in Path(args.log).read_text().splitlines()]
r=next(x for x in rows if x.get('event')=='result')
assert r['status']=='timeout'
root=r['prefix'];current=r['checkpoint_prefix'];assert current[:len(root)]==root
assert len(current)<33 and all(a<b for a,b in zip(current,current[1:]))
tasks=[{'kind':'prefix','prefix':current,'action':'replay interrupted subtree from its beginning'}]
for i in range(len(current)-1,len(root)-1,-1):
    prefix=current[:i];residual=1-sum((F(1,x) for x in prefix),F());t=33-i
    lo=current[i]+1;hi=(t*residual.denominator-1)//residual.numerator
    left=lo-1;right=hi
    while left<right:
        mid=(left+right+1)//2
        if sum((F(1,mid+j) for j in range(t)),F())>=residual:left=mid
        else:right=mid-1
    hi=left
    if hi>=lo:tasks.append({'kind':'next-denominator-interval','prefix':prefix,'minimum_next':str(lo),'maximum_next':str(hi),
                            'residual_numerator':str(residual.numerator),'residual_denominator':str(residual.denominator),'terms_remaining':t})
other=list(range(18,30)) if root==list(range(18,29))+[30] else list(range(18,29))+[30] if root==list(range(18,30)) else None
out={'minimum':18,'terms':33,'root_prefix':root,'source_log':args.log,
     'source_nodes':r['nodes'],'source_elapsed_seconds':r['elapsed_seconds'],
     'status':'incomplete','no_denominator_cap':True,'tasks':tasks,
     'other_global_surviving_root_prefix':other,
     'conditional_quotas':{'reference':r.get('base_quota'),'small_reference':r.get('small_reference_quota')},
     'coverage_argument':'Ascending depth-first search completes every earlier sibling before entering the recorded stack. Replay the interrupted node and then all right siblings of each ancestor. This covers the entire unfinished part of the root subtree without discarding any unsearched branch.'}
Path(args.output).write_text(json.dumps(out,indent=2))
print(json.dumps({'status':'checkpoint_partition_created','tasks':len(tasks),'checkpoint_terms':len(current)}))
