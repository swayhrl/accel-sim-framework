"""Stage an independently reviewed pair in next V2; push/readback/pointer are separate."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import subprocess

from acceptance import load_current_authority,current_manifest,MANIFEST,require_publication_boundary,authorize_launch,reject_withdrawn
from package_r0 import freeze_checksums
from registry import Registry,ACTIVE
from run import digest,require

REPO=Path(__file__).resolve().parents[3]
HANDOFF=REPO/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5'



def recheck_review_currentness(review,pack,state):
    """Cache immutable payload review; recheck exact target qualification/currentness."""
    require(review['status']=='INDEPENDENT_TERMINAL_AND_CURRENT_AUTHORITY_REVIEW_PASS','Unreviewed payload')
    if review['checked_current_authority']['manifest_sha256']==state['binding']['manifest_sha256']:
        return {'status':'SAME_CURRENT_V2','authority':state['binding']}
    require(review['checked_current_authority']['generation']<state['binding']['generation'],'Authority did not advance monotonically')
    source=json.loads((pack/'SOURCE_MANIFEST.json').read_text())
    for row in source['runs']:
        reject_withdrawn(row['identity'],current_manifest(state))
        spec=json.loads((pack/row['mode']/'input_spec.json').read_text())
        require(digest(spec['qualified_release'])==row['qualification_sha256'],'Target qualification changed since cached review')
        auth=authorize_launch(row['identity'],row['qualification_sha256'],state)
        require(auth==row['input_audit']['scientific_launch_authorization'],'Exact target authorization changed')
    return {'status':'UNCHANGED_FROZEN_PAYLOAD_TARGETS_RECHECKED_UNDER_NEW_CURRENT_V2',
            'reviewed_authority':review['checked_current_authority'],'current_authority':state['binding'],
            'source_manifest_sha256':digest(pack/'SOURCE_MANIFEST.json'),
            'full_trace_simulation_repeated':False,'target_qualification_and_withdrawal_rechecked':True}


def stage_qualification(release_path,review_path,pack):
    """Add positive downstream envelopes to existing V2; preserve all result rows."""
    from headroom_config import EXPERIMENT,validate as validate_condition
    require(not pack.exists(),'Qualification acceptance pack exists')
    state=load_current_authority();ledger=current_manifest(state)
    require_publication_boundary(Registry())
    release=json.loads(release_path.read_text());review=json.loads(review_path.read_text())
    require(release['status']=='INDEPENDENTLY_QUALIFIED' and release['qualified_by']=='lane5','Missing independent envelope')
    binding=release['downstream_config_qualification']
    require(Path(binding['path']).resolve()==review_path.resolve() and digest(review_path)==binding['sha256'],'Condition qualification bytes differ')
    require(review['status']=='INDEPENDENT_CONFIG_PASS' and review['experiment_id'] in (EXPERIMENT,'EPL2_PARALLEL_POTENTIAL_20261017_V1'),'Condition checks not independently closed')
    for ev in review['evidence']:require(digest(ev['path'])==ev['sha256'],'Qualification evidence changed')
    require(review.get('producer_publication_verified',review.get('lane1_publication_verified')) is True and review.get('independent_affected_production_pass') is True,'Missing Lane1 remote or independent affected production check')
    require(review['evidence'],'No actual affected evidence')
    # Each mode must pass the identical positive whitelist used at run admission.
    from run import asset_manifest
    for spec_path in review['spec_paths']:
        spec=json.loads(Path(spec_path).read_text());require(Path(spec['qualified_release']).resolve()==release_path.resolve(),'Different spec envelope')
        validate_condition(spec,release,asset_manifest(spec['configs'],ordered=True),asset_manifest(spec['auxiliary_assets']) if spec['auxiliary_assets'] else [])
    original_rows=json.dumps(ledger['rows'],sort_keys=True);original_auth=list(ledger['launch_authorizations'])
    require(not any(r['qualified_release_sha256']==digest(release_path) for r in original_auth),'Envelope already authorized')
    vectors=release.get('qualified_modes') or [{'feature_vector':f,'ideal_vector':{'meta':False,'read_hit':False,'wb':False}} for f in release['qualified_feature_vectors']]
    for mode in vectors:
        require(mode['feature_vector'] in release['qualified_feature_vectors'],'Qualified mode feature missing')
        ledger['launch_authorizations'].append({**{k:release[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')},'feature_vector':mode['feature_vector'],'ideal_vector':mode['ideal_vector'],'qualified_release_sha256':digest(release_path),'status':'CURRENT_QUALIFIED_FOR_LAUNCH','application_scope':'FULL_NATIVE_NONATOMIC_ONLY_WITH_PER_SPEC_COMPLETE_CONTENT_PROOF','experiment_id':review['experiment_id'],'regime':review['regime']})
    proof={'path':str(review_path.relative_to(REPO)),'sha256':digest(review_path)}
    ledger['supersession_evidence'].append(proof);ledger['supersedes']={'manifest_sha256':state['binding']['manifest_sha256'],'publication_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()}
    ledger['generation']+=1;ledger['revision']='FT20261017_LANE5_'+('R19_' if review['experiment_id']==EXPERIMENT else 'PARALLEL_')+review['regime']+'_'+release['release_name']+'_CONFIG_QUALIFIED_r1';ledger['updated_at']=datetime.now(timezone.utc).isoformat()
    require(json.dumps(ledger['rows'],sort_keys=True)==original_rows and ledger['launch_authorizations'][:len(original_auth)]==original_auth,'Prior rows/auth changed')
    path=REPO/MANIFEST;path.write_text(json.dumps(ledger,indent=2,sort_keys=True)+'\n');pack.mkdir(parents=True)
    shutil.copyfile(path,pack/'SCIENTIFIC_ACCEPTANCE_V2.json')
    (pack/'RECEIPT.json').write_text(json.dumps({'status':'CONDITION_QUALIFIED_PENDING_REMOTE_POINTER_INSTALL','experiment_id':review['experiment_id'],'regime':review['regime'],'new_applications':0,'all_old_rows_and_authorizations_preserved':True,'generation':ledger['generation'],'manifest_sha256':digest(path),'qualified_release_sha256':digest(release_path)},indent=2,sort_keys=True)+'\n');freeze_checksums(pack)
    print(json.dumps({'status':'STAGED_CONDITION_QUALIFICATION_REQUIRES_REMOTE_READBACK','generation':ledger['generation'],'regime':review['regime']}))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--pair-pack',type=Path);ap.add_argument('--acceptance-pack',required=True,type=Path);ap.add_argument('--extra-release',type=Path);ap.add_argument('--extra-review',type=Path);ap.add_argument('--qualification-only',action='store_true');a=ap.parse_args()
    if a.qualification_only:
        require(a.extra_release is not None and a.extra_review is not None and a.pair_pack is None,'Qualification-only requires exact release/review, no pair');stage_qualification(a.extra_release,a.extra_review,a.acceptance_pack);return
    require(a.pair_pack is not None,'Pair pack required')
    require(not a.acceptance_pack.exists(),'Frozen acceptance revision exists')
    for line in (a.pair_pack/'SHA256SUMS').read_text().splitlines():
        sha,name=line.split('  ',1);require(digest(a.pair_pack/name)==sha,'Pair pack changed')
    state=load_current_authority();ledger=current_manifest(state);old_count=len(ledger['rows']);old_rows=json.dumps(ledger['rows'],sort_keys=True)
    review_path=a.pair_pack/'SCIENTIFIC_REVIEW.json';review=json.loads(review_path.read_text())
    currentness=recheck_review_currentness(review,a.pair_pack,state)
    require_publication_boundary(Registry())
    rows=review['scientific_acceptance_rows_proposed'];require(len(rows)==2 and {r['mode'] for r in rows}=={'B16_BANKED','U_WB16'},'Incomplete pair')
    require(all(r['scientific_acceptance']=='CURRENT_ACCEPTED' and r['original_terminal_status']=='COMPLETE_VALID' for r in rows),'Nonvalid accepted proposal')
    require(not ({r['run_key'] for r in rows}&{r['run_key'] for r in ledger['rows']}),'Existing result cannot be overwritten')
    proof={'path':str(review_path.relative_to(REPO)),'sha256':digest(review_path)}
    ledger['rows'] += [{**r,'independent_review':proof} for r in rows]
    require(json.dumps(ledger['rows'][:old_count],sort_keys=True)==old_rows,'Historical acceptance rows changed')
    ledger['supersedes']={'manifest_sha256':state['binding']['manifest_sha256'],'publication_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()}
    ledger['generation']+=1;ledger['revision']='FT20261017_LANE5_'+(('R19_'+review['regime']+'_') if review.get('experiment_id') else 'A1_B1_')+review['workload'].upper()+'_ACCEPTED_r1';ledger['updated_at']=datetime.now(timezone.utc).isoformat();ledger['supersession_evidence'].append(proof)
    if a.extra_release:
        require(a.extra_review is not None,'Missing extra adapter review');release=json.loads(a.extra_release.read_text());require(release['status']=='INDEPENDENTLY_QUALIFIED','Extra release unqualified')
        for feature in release['qualified_feature_vectors']:
            ledger['launch_authorizations'].append({**{k:release[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')},'feature_vector':feature,'ideal_vector':{'meta':False,'read_hit':False,'wb':False},'qualified_release_sha256':digest(a.extra_release),'status':'CURRENT_QUALIFIED_FOR_LAUNCH','application_scope':'FULL_NATIVE_NONATOMIC_ONLY_WITH_PER_SPEC_COMPLETE_CONTENT_PROOF'})
        ledger['supersession_evidence'].append({'path':str(a.extra_review.relative_to(REPO)),'sha256':digest(a.extra_review)})
    accepted=[r for r in ledger['rows'] if r['scientific_acceptance']=='CURRENT_ACCEPTED'];pairs=sum(not r.get('experiment_id') for r in accepted)//2
    diagnostic_pairs=sum(r.get('experiment_id')=='EPL2_DOWNSTREAM_HEADROOM_R19' for r in accepted)//2
    parallel_rows=sum(r.get('experiment_id')=='EPL2_PARALLEL_POTENTIAL_20261017_V1' for r in accepted)
    ledger['status']=f'{pairs}_CURRENT_ACCEPTED_H0_PAIRS_{diagnostic_pairs}_R19_DIAGNOSTIC_PAIRS_{parallel_rows}_PARALLEL_ROWS';path=REPO/MANIFEST;path.write_text(json.dumps(ledger,indent=2,sort_keys=True)+'\n')
    a.acceptance_pack.mkdir(parents=True);shutil.copyfile(path,a.acceptance_pack/'SCIENTIFIC_ACCEPTANCE_V2.json')
    (a.acceptance_pack/'CURRENTNESS_RECHECK.json').write_text(json.dumps(currentness,indent=2,sort_keys=True)+'\n')
    delivery={'schema_version':'EPL2_LANE5_TO_LANE6_CURRENT_ACCEPTED_PAIR_V1','status':'CURRENT_ACCEPTED_PENDING_REMOTE_POINTER_INSTALL','workload':review['workload'],'pair_pack':str(a.pair_pack.relative_to(REPO)),'acceptance_pack':str(a.acceptance_pack.relative_to(REPO)),'ledger_generation':ledger['generation'],'ledger_sha256':digest(path),'current_accepted_pairs':pairs,'all5_required_before_geomean':True,'rows':rows,'comparison':json.loads((a.pair_pack/'COMPARISON.json').read_text()),'source_manifest_sha256':digest(a.pair_pack/'SOURCE_MANIFEST.json')}
    if review.get('experiment_id'):
        delivery.update(experiment_id=review['experiment_id'],regime=review['regime'],H0_accepted_pairs=pairs,r19_accepted_pairs=diagnostic_pairs,all5_required_before_geomean=False,diagnostic_only=True)
    (a.acceptance_pack/'LANE6_HANDOFF.json').write_text(json.dumps(delivery,indent=2,sort_keys=True)+'\n');(a.acceptance_pack/'REVIEW.md').write_text('# '+review['workload']+' current scientific acceptance\n\nBoth exact new terminals passed independent reparse, full input/source/binary/qualification/current-authority review. Next V2 adds both accepted rows, preserving every historical row. Remote readback and central pointer install precede delivery. No result selection or numeric SASS claim. '+('Diagnostic means require the two complete predeclared workloads under the same condition; never mix H0 five-workload mean.' if review.get('experiment_id') else 'No group geomean until all five.')+'\n');freeze_checksums(a.acceptance_pack)
    if review.get('experiment_id'):
        receipt_path=HANDOFF/('R19_CONTINUE_RECEIPT.json' if review['experiment_id']=='EPL2_DOWNSTREAM_HEADROOM_R19' else 'PARALLEL_CONTINUE_RECEIPT.json');receipt=json.loads(receipt_path.read_text()) if receipt_path.exists() else {'experiment_id':review['experiment_id']};receipt.update(status='ACTIVE_ROLLING_R19_CURRENT_ACCEPTED',latest_pair_delivery=delivery,r19_accepted_pairs=diagnostic_pairs,current_V2_generation=ledger['generation'],next_action='Push remote readback, current pointer install, immediate Lane6 delivery; next r19 pair');receipt_path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        main_path=HANDOFF/'RECEIPT.json';main=json.loads(main_path.read_text());main.update(status='ACTIVE_ROLLING_'+review['experiment_id'],**{('r19_continue' if review['experiment_id']=='EPL2_DOWNSTREAM_HEADROOM_R19' else 'parallel_continue'):receipt});main['artifacts']=list(dict.fromkeys(main['artifacts']+[str(a.pair_pack.relative_to(REPO)),str(a.acceptance_pack.relative_to(REPO))]));main_path.write_text(json.dumps(main,indent=2,sort_keys=True)+'\n')
        (HANDOFF/'STATUS.md').write_text('# Lane5 — r19 rolling diagnostics\n\nH0 five accepted pairs and geomean1.0016002037656606 retained. '+str(diagnostic_pairs)+' r19 diagnostic pairs accepted in staged V2 generation'+str(ledger['generation'])+'; latest '+review['regime']+'/'+review['workload']+'. Remote readback and shared pointer install required before announcing delivery. Existing full-input/64slice/current V2 and original resource protections remain. T0 07:09:16UTC, deadline17:09:16UTC. No compiler, migration, extra waiter. Exact identity/results in '+str(a.pair_pack.relative_to(REPO))+'.\n')
        print(json.dumps({'status':'STAGED_NEXT_V2_REQUIRES_REMOTE_READBACK_AND_POINTER','generation':ledger['generation'],'H0_pairs':pairs,'r19_pairs':diagnostic_pairs,'manifest_sha256':digest(path)}));return
    receipt_path=HANDOFF/'RECEIPT.json';receipt=json.loads(receipt_path.read_text());receipt.update(status=f'R0_1_A1_B1_{pairs}_CURRENT_ACCEPTED_PAIRS',updated_at=ledger['updated_at'],active_runs=[])
    receipt['artifacts']=list(dict.fromkeys(receipt['artifacts']+[str(a.pair_pack.relative_to(REPO)),str(a.acceptance_pack.relative_to(REPO))]));receipt['validation']['scientifically_accepted_R0_application_runs']=len(accepted);receipt['validation']['scientifically_accepted_R0_application_pairs']=pairs
    receipt['formal_R0_1_campaign']={'status':'ROLLING_CURRENT_ACCEPTED' if pairs<5 else 'ALL5_CURRENT_ACCEPTED','accepted_pairs':pairs,'accepted_rows':accepted,'remaining_workloads':[w for w in ('sad','vectorAdd_4M','cfd_097k','convolutionSeparable','FWT_7_21') if w not in {r['workload'] for r in accepted}],'geomean_computed':False};receipt['bounded_continue']['latest_pair_delivery']=delivery;receipt['bounded_continue']['next_action']='Remote readback/pointer install and immediate Lane6 handoff; continue frozen remaining order';receipt_path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    (HANDOFF/'STATUS.md').write_text('# Lane5 — '+str(pairs)+'/5 repaired official R0.1 pairs accepted\n\nLatest '+review['workload']+' pair passed independent raw reparse/full identity/current V2 review. Current generation'+str(ledger['generation'])+' preserves old withdrawals and adds both new CURRENT_ACCEPTED rows. Exact results/identities/closures in '+str(a.pair_pack.relative_to(REPO))+', delivery in '+str(a.acceptance_pack.relative_to(REPO))+'. No group geomean until5.\n\nGoal ACTIVE to original12:19:03UTC deadline. All11 actual source gates passed; five full native input sets non-atomic, ordinary symbolic32B sector/lifecycle scope only. Same Core7b8e6ac7/Framework9bd17f9d/vendorf90c430c/binary23094a9d. TVD/RO/Ideal excluded; C1 legacy headroom excluded from causal claims. No active long simulator at this publication boundary. Next remote readback/current pointer, handoff and next frozen pair under standard48GiB/64GiB/Share40GiB/max2long quota. No compiler, waiter, migration or cleanup by Lane5.\n')
    print(json.dumps({'status':'STAGED_NEXT_V2_REQUIRES_REMOTE_READBACK_AND_POINTER','generation':ledger['generation'],'accepted_pairs':pairs,'manifest_sha256':digest(path)}))


if __name__=='__main__':main()
