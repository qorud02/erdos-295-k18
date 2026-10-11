"""Check exact baseline arithmetic and the completed-run coverage receipts.

This audits coverage metadata; mathematical validity also depends on the
preserved enumerator and its pruning proofs. It does not replace a rerun.
"""
from fractions import Fraction as F
from math import comb,lcm
from pathlib import Path
import hashlib,json
from local_surgery import BASE
from quota_tools import exclusion_group

def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines()]
all5=read('surgery5-all.jsonl');a6=read('surgery6-large2.jsonl');b6=read('surgery6-large2-resume.jsonl')
assert len(BASE)==len(set(BASE))==34 and min(BASE)==18 and sum((F(1,x) for x in BASE),F())==1
L=lcm(*BASE);assert sum(L//x for x in BASE)==L
assert all5[0]['args']['remove']==5 and all5[0]['args']['required_large']==0 and all5[0]['args']['start']==0
assert all5[-1]['status']=='family_exhausted' and all5[-1]['cases_timed_out']==0 and all5[-1]['cases_exhausted']==comb(34,5)
for rows in (a6,b6):assert rows[0]['args']['remove']==6 and rows[0]['args']['required_large']==2
assert a6[0]['args']['start']==0 and a6[-1]['cases_exhausted']==33954
assert a6[-1]['cases_timed_out']==1 and next(x for x in a6 if x.get('status')=='timeout')['index']==33954
assert b6[0]['args']['start']==33954 and b6[-1]['status']=='family_exhausted' and b6[-1]['cases_timed_out']==0
assert b6[-1]['cases_exhausted']==2006 and b6[-1]['next_index']==comb(32,4)==35960
group,q=exclusion_group(BASE,BASE[-2:],6,1);assert group==BASE[:-2] and q==27
out={'status':'passed','baseline_exact_sum':'1','baseline_lcm':str(L),'baseline_weighted_sum':str(L),
     'full_five_to_four_cases':comb(34,5),'core_six_to_five_cases':comb(32,4),
     'core_first_complete_index_interval':[0,33953],'core_resume_complete_index_interval':[33954,35959],
     'boundary_interrupted_case_replayed':33954,
     'conditional_capacity_groups':[{'denominators':[str(x) for x in BASE],'capacity':28,'premise':'all 5-to-4 surgeries excluded'},
                                    {'denominators':[str(x) for x in group],'capacity':q,'premise':'all 6-to-5 surgeries whose removed set contains the two specified large denominators excluded'}],
     'core':[str(x) for x in BASE[-2:]],'enumerator_sha256':hashlib.sha256(Path('local_surgery.py').read_bytes()).hexdigest(),
     'scope':'Coverage and baseline arithmetic audit. Run validity requires the preserved exact enumerator and mathematical pruning lemmas.'}
Path('local-premises-validation.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:out[k] for k in ['status','full_five_to_four_cases','core_six_to_five_cases','boundary_interrupted_case_replayed']}))
