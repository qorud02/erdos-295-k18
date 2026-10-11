#!/usr/bin/env python3
"""Independent local-record audit; never launches a solver or uses the network."""
from __future__ import annotations
import argparse
from collections import Counter
from decimal import Decimal
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import re

BASE=(18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,38,39,40,43,44,45,46,48,50,52,54,63,275,14143068,10457416992)
MODES=('off','single','nested')
UPSTREAM_COMMIT='8680599e77683a9057ee55871a0893bb319300e8'
UPSTREAM_SHA='4febfdbee3710f05775f41bc15a9046984c69da1f7a53f105116579a663ad480'
IMAGE_DIGEST='sagemath/sagemath@sha256:e2e4747b0e1ea8753a9cb5a399314a8b2c25fcefaf69ba85b22ee075829d09ea'


def require(condition,message):
    if not condition:raise ValueError(message)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def rows(path):return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]
def total(items,key):return float(sum((Decimal(str(x[key])) for x in items),Decimal()))


def all_representations(target,terms,minimum):
    if terms==1:
        if target>0 and target.numerator==1 and target.denominator>=minimum:return [(target.denominator,)]
        return []
    if target<=0:return []
    result=[]
    for x in range(max(minimum,target.denominator//target.numerator+1),terms*target.denominator//target.numerator+1):
        result.extend((x,)+tail for tail in all_representations(target-Fraction(1,x),terms-1,x+1))
    return result


def main():
    here=Path(__file__).resolve().parent
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir',type=Path,default=here/'cloud-results',help='downloaded cloud artifact directory (default: alongside this script)')
    p.add_argument('--output',type=Path,default=here/'cloud-summary-audit.json',help='audit receipt path')
    p.add_argument('--manifest',type=Path,default=here/'inputs'/'manifest.json',help='frozen 224-case input manifest')
    p.add_argument('--source-dir',type=Path,default=here,help='directory containing matched-search.cpp, run_upstream.sage and validate_matched.py')
    args=p.parse_args();run=args.run_dir.resolve();benchmark=args.source_dir.resolve()
    manifest=args.manifest.resolve();obj=load(manifest);instances=obj['instances']
    expected=[]
    for u in range(45,65):
        for v in range(u+1,65):expected.append((f'broad-{u:03d}-{v:03d}','broad',list(range(18,29))+list(range(30,45))+[u,v]))
    for z in range(49,80):expected.append((f'structural-{z:03d}','structural',list(BASE[:27])+[z]))
    for z in (31,32,33):expected.append((f'control-next-{z}','control',list(range(18,29))+[z]))
    require(len(instances)==224 and len(expected)==224,'manifest length')
    selection=[];ordinal=0
    for record,(identity,family,prefix) in zip(instances,expected):
        residual=Fraction(1)-sum((Fraction(1,x) for x in prefix),Fraction())
        require(record['id']==identity and record['family']==family and record['prefix']==prefix,'frozen manifest prefix')
        require(record['minimum']==18 and record['terms']==33 and record['terms_remaining']==33-len(prefix),'manifest problem scope')
        require(residual>0 and residual==Fraction(int(record['residual_numerator']),int(record['residual_denominator'])),'exact residual')
        keep=family!='broad' or ordinal%10==0
        if family=='broad':ordinal+=1
        if keep:selection.append(record)
    require(len(selection)==53,'pilot selection count')
    selected={x['id']:x for x in selection};ids=list(selected)
    manifest_sha=sha(manifest)
    cm=load(run/'matched-cloud-results'/'metadata.json');sm=load(run/'upstream-cloud-results'/'metadata.json')
    cc=load(run/'cloud-comparison.json');cs=load(run/'matched-cloud-results'/'summary.json');ss=load(run/'upstream-cloud-results'/'summary.json')
    oracle=load(run/'matched-oracle-validation.json');choice=load(run/'upstream-cloud-results'/'selection.json')
    require(all(x==manifest_sha for x in (cm['manifest_sha256'],sm['manifest_sha256'],cc['manifest_sha256'],ss['manifest_sha256'],choice['full_manifest_sha256'])),'manifest hash agreement')
    require(choice['instance_ids']==ids and choice['selected_instances']==53 and choice['full_manifest_instances']==224,'saved Sage selection')
    require(cm['cpu_affinity']==sm['cpu_affinity']==cc['same_cpu_affinity']==[0],'same single CPU')
    require(sm['sage_map_reduce_workers']==1 and sm['sage_version']=='10.8','Sage worker/version')
    source_sha=sha(benchmark/'matched-search.cpp');wrapper_sha=sha(benchmark/'run_upstream.sage')
    require(source_sha==cm['source_sha256']==oracle['source_sha256'],'C++ source hash')
    require(wrapper_sha==sm['wrapper_sha256'],'Sage wrapper hash')
    require(sm['upstream_commit']==UPSTREAM_COMMIT and sm['upstream_sha256']==UPSTREAM_SHA,'original Sage source pin')
    compiled={name:digest for digest,name in (line.split() for line in (run/'compiled-sha256.txt').read_text().splitlines() if line.strip())}
    require(compiled['matched-search.cpp']==source_sha and compiled['matched-search']==cm['binary_sha256'],'compiler source/binary receipts')
    image=load(run/'sage-image-inspect.json');require(len(image)==1 and IMAGE_DIGEST in image[0]['RepoDigests'] and image[0]['Architecture']=='amd64' and image[0]['Os']=='linux','actual Sage image receipt')
    cpp=rows(run/'matched-cloud-results'/'runs.jsonl');sage_all=rows(run/'upstream-cloud-results'/'runs.jsonl')
    controls=[x for x in sage_all if x['family']=='api-control'];sage=[x for x in sage_all if x['family']!='api-control']
    require(len(cpp)==159 and len(sage)==53 and len(controls)==6,'raw record cardinalities')
    cg={(x['instance_id'],x['mode']):x for x in cpp};sg={x['instance_id']:x for x in sage}
    require(len(cg)==159 and set(cg)=={(i,m) for i in ids for m in MODES},'C++ unique exact coverage')
    require(len(sg)==53 and set(sg)==set(ids),'Sage unique exact coverage')
    require(all(x['status']=='control-passed' and x['complete'] and not x['censored'] for x in controls),'API controls passed')
    definitions={x['id']:x for x in choice['api_controls']};require(len(definitions)==6 and set(definitions)=={x['instance_id'] for x in controls},'API control identities')
    for control in controls:
        definition=definitions[control['instance_id']];target=Fraction(definition['target']);terms=definition['terms'];minimum=definition['minimum']
        exhaustive=set(all_representations(target,terms,minimum));require(exhaustive=={tuple(x) for x in definition['expected']},'independent API expected sets')
        if definition['api']=='all_rep':
            actual=[tuple(x) for x in control['value']]
            require(len(actual)==len(set(actual)) and set(actual)==exhaustive,'all_rep exact control enumeration')
        else:require((control['value'] is None and not exhaustive) or tuple(control['value'] or ()) in exhaustive,'one_rep exact control answer')
    stdout_checks=0
    for (identity,mode),row in cg.items():
        case=selected[identity];limit=30 if case['family']=='control' else 5;result=row['result']
        require(row['family']==case['family'] and row['seconds_limit']==limit,'C++ family/budget')
        require(row['status']==row['answer_status']==result['status']=='exhausted' and row['complete'] and not row['censored'],'C++ exact completion status')
        require(result['minimum']==18 and result['terms']==33 and result['prefix']==case['prefix'] and result['quota_mode']==MODES.index(mode),'C++ result identity')
        require(result['elapsed_seconds']<limit and result['denominators'] is None and result['max_denominator'] is None,'C++ censor/scope')
        command=row['command']
        require(command[command.index('--prefix')+1]==','.join(map(str,case['prefix'])) and command[command.index('--quota-mode')+1]==mode and '--joint' in command,'C++ command input/pruning')
        raw=run/'matched-cloud-results'/'logs'/(identity+'-'+mode+'.jsonl');require(sha(raw)==row['stdout_sha256'],'stdout digest')
        events=rows(raw);require([x for x in events if x.get('event')=='result']==[result],'raw stdout final result')
        stdout_checks+=1
    for identity,row in sg.items():
        case=selected[identity];limit=30 if case['family']=='control' else 5
        require(row['family']==case['family'] and row['prefix']==case['prefix'] and row['minimum']==18 and row['terms']==33 and row['terms_remaining']==case['terms_remaining'] and row['seconds_limit']==limit,'Sage input identity')
        require(Fraction(int(row['residual_numerator']),int(row['residual_denominator']))==Fraction(int(case['residual_numerator']),int(case['residual_denominator'])) and row['max_denominator'] is None,'Sage exact residual and unbounded scope')
        if row['status']=='exhausted':
            require(row['answer_status']=='exhausted' and row['complete'] and not row['censored'] and row['solver_seconds']<=limit and row['value'] is None and row['denominators'] is None,'Sage exhausted answer')
        elif row['status']=='timeout':
            require(not row['complete'] and row['censored'] and row['solver_seconds'] is None and row['solver_seconds_lower_bound']==limit and 'answer_status' not in row,'Sage timeout remains unresolved')
        else:raise ValueError('unexpected Sage status')
    common=[i for i in ids if sg[i]['complete'] and all(cg[i,m]['complete'] for m in MODES)]
    require(len(common)==48 and cc['all_four_complete_cases']==48 and not cc['answer_mismatches'],'four-way completed counts')
    require([x['id'] for x in cc['complete_paired_cases']]==common,'published comparison row selection')
    for pair in cc['complete_paired_cases']:
        identity=pair['id'];require(pair['sage_seconds']==sg[identity]['solver_seconds'],'paired Sage time')
        for mode in MODES:require(pair['cpp'][mode]=={'seconds':cg[identity,mode]['result']['elapsed_seconds'],'nodes':cg[identity,mode]['result']['nodes']},'paired C++ metrics')
    require(cs['cases']==53 and cs['runs']==159 and cs['errors']==0 and cs['source_unchanged'] and cs['binary_unchanged'],'C++ summary consistency')
    require(ss['complete_cases']==48 and ss['censored_cases']==5 and ss['errors']==0 and ss['api_controls_passed'],'Sage summary consistency')
    require(oracle['status']=='passed' and oracle['residual_cases']==972 and sum(oracle['verdict_counts'].values())==972,'saved residual oracle outcome')
    spec=importlib.util.spec_from_file_location('saved_residual_generator',benchmark/'validate_matched.py')
    generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)
    regenerated=generator.cases()
    encoded=''.join(f'{r["mode"]} {r["d"]} {r["t"]} {r["a"]} {r["b"]} {r["base_selected"]} {r["small_selected"]}\n' for r in regenerated)
    require(len(regenerated)==972 and hashlib.sha256(encoded.encode()).hexdigest()==oracle['input_sha256'],'regenerated independent-oracle input digest')

    def cpp_metrics(identities,mode):
        records=[cg[i,mode] for i in identities];results=[r['result'] for r in records]
        return dict(cases=len(records),completed=sum(r['complete'] for r in records),solver_seconds=total(results,'elapsed_seconds'),wall_seconds=total(records,'wall_seconds'),nodes=sum(x['nodes'] for x in results),quota_prunes=sum(x['base_quota_prunes'] for x in results),prime_prunes=sum(x['prime_prunes'] for x in results),joint_prunes=sum(x['joint_prunes'] for x in results),two_candidates=sum(x['two_candidates'] for x in results))
    families={}
    for family in ('broad','structural','control','all'):
        identities=[i for i in ids if family=='all' or selected[i]['family']==family];common_ids=[i for i in identities if i in common]
        srows=[sg[i] for i in identities];completed=[r for r in srows if r['complete']];censored=[r for r in srows if r['censored']]
        modes={m:cpp_metrics(identities,m) for m in MODES};cmodes={m:cpp_metrics(common_ids,m) for m in MODES}
        off=modes['off'];nested=modes['nested']
        families[family]=dict(declared_cases=len(identities),four_way_completed_cases=len(common_ids),cpp=modes,sage=dict(completed=len(completed),censored=len(censored),completed_solver_seconds=total(completed,'solver_seconds'),censored_solver_seconds_lower_bound=sum(x['solver_seconds_lower_bound'] for x in censored),case_wall_seconds=total(srows,'wall_seconds'),statuses=dict(Counter(x['status'] for x in srows))),matched_nested_vs_off=dict(solver_seconds_saved=off['solver_seconds']-nested['solver_seconds'],off_over_nested_solver_time_ratio=off['solver_seconds']/nested['solver_seconds'] if nested['solver_seconds'] else None,nodes_saved=off['nodes']-nested['nodes'],node_reduction_fraction=(off['nodes']-nested['nodes'])/off['nodes'] if off['nodes'] else None),four_way_completed_subset=dict(cases=len(common_ids),sage_solver_seconds=total([sg[i] for i in common_ids],'solver_seconds'),cpp=cmodes))
    changed=[i for i in ids if cg[i,'off']['result']['nodes']!=cg[i,'nested']['result']['nodes']]
    reduced=[i for i in ids if cg[i,'nested']['result']['nodes']<cg[i,'off']['result']['nodes']]
    increased=[i for i in ids if cg[i,'nested']['result']['nodes']>cg[i,'off']['result']['nodes']]
    timeout_ids=[i for i in ids if sg[i]['censored']]
    artifact_hashes={str(path.relative_to(run)).replace('\\','/'):sha(path) for path in sorted(run.rglob('*')) if path.is_file() and path.name!='cloud-summary-audit.json'}
    result=dict(status='passed',workflow_run_id='38176293521',audit_scope='independent local artifact/hash/input/status/aggregate audit; no solver run or external access',checks=dict(frozen_manifest_cases=224,exact_prefix_residual_checks=224,pilot_cases=53,raw_cpp_rows=159,raw_sage_rows=59,api_controls=6,api_control_expected_sets_independently_enumerated=True,cpp_stdout_hashes_checked=stdout_checks,residual_oracle_input_digest_recomputed=True,same_cpu_affinity=[0],proof_answer_mismatches=0),provenance=dict(manifest_sha256=manifest_sha,matched_source_sha256=source_sha,matched_binary_sha256_receipt=cm['binary_sha256'],binary_bytes_in_artifact=False,binary_receipt_matches_metadata=True,sage_wrapper_sha256=wrapper_sha,upstream_commit=UPSTREAM_COMMIT,upstream_source_sha256_receipt=UPSTREAM_SHA,upstream_source_bytes_in_artifact=False,original_source_sha_verified_by_executed_wrapper=True,sage_version=sm['sage_version'],sage_image_repo_digest=IMAGE_DIGEST,compiler_version=(run/'compiler-version.txt').read_text().splitlines()[0]),families=families,nested_node_changes=dict(changed_cases=len(changed),reduced_cases=len(reduced),increased_cases=len(increased),unchanged_cases=53-len(changed),case_ids=changed),sage_timeout_case_ids=timeout_ids,api_controls_solver_seconds=total(controls,'solver_seconds'),api_controls_wall_seconds=total(controls,'wall_seconds'),sage_source_fetch_and_load_seconds=sm['source_fetch_and_Sage_load_seconds'],residual_oracle_summary=dict(cases=972,witness=oracle['verdict_counts']['witness'],exhausted=oracle['verdict_counts']['exhausted'],observed_prime_prunes=oracle['observed_engine_counters']['prime_prunes'],observed_joint_prunes=oracle['observed_engine_counters']['joint_prunes']),historical_preprocessing=dict(seconds=353.406,components=[95.781,257.625],same_environment_measurement=False,cold_start_conversion_performed=False),interpretation_limits=['Single repetition; fixed selected subtrees, not the full 33-term domain.','The 48-case common completion subset is selected by completion; no average-ratio generalization.','Original Sage versus GMP includes implementation language, runtime and pre-existing pruning differences; no attribution to overlap quotas.','Matched OFF/single/nested uses the same binary and supports only this fixed-suite quota ablation.','Historical 353.406-second premise construction cost was measured in another environment and is not converted to this CPU.','Binary and original upstream source bytes were not included; their recorded hashes cannot be independently recomputed from this artifact.'],artifact_sha256=artifact_hashes)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],checks=result['checks'],families=families,nested_node_changes=result['nested_node_changes'],sage_timeout_case_ids=timeout_ids)))

if __name__=='__main__':main()
