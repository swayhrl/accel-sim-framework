"""Stage an independently reviewed pair in next V2; push/readback/pointer are separate."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import subprocess

from acceptance import load_current_authority,current_manifest,MANIFEST
from package_r0 import freeze_checksums
from registry import Registry,ACTIVE
from run import digest,require

REPO=Path(__file__).resolve().parents[3]
HANDOFF=REPO/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5'


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--pair-pack',required=True,type=Path);ap.add_argument('--acceptance-pack',required=True,type=Path);ap.add_argument('--extra-release',type=Path);ap.add_argument('--extra-review',type=Path);a=ap.parse_args()
    require(not a.acceptance_pack.exists(),'Frozen acceptance revision exists')
    for line in (a.pair_pack/'SHA256SUMS').read_text().splitlines():
        sha,name=line.split('  ',1);require(digest(a.pair_pack/name)==sha,'Pair pack changed')
    state=load_current_authority();ledger=current_manifest(state);old_count=len(ledger['rows']);old_rows=json.dumps(ledger['rows'],sort_keys=True)
    review_path=a.pair_pack/'SCIENTIFIC_REVIEW.json';review=json.loads(review_path.read_text())
    require(review['status']=='INDEPENDENT_TERMINAL_AND_CURRENT_AUTHORITY_REVIEW_PASS' and review['checked_current_authority']['manifest_sha256']==state['binding']['manifest_sha256'],'Stale/unreviewed pair')
    require(not any(r['status'] in ACTIVE for r in Registry().snapshot()['runs'].values()),'Publish scientific pointer at no-active-simulator boundary')
    rows=review['scientific_acceptance_rows_proposed'];require(len(rows)==2 and {r['mode'] for r in rows}=={'B16_BANKED','U_WB16'},'Incomplete pair')
    require(all(r['scientific_acceptance']=='CURRENT_ACCEPTED' and r['original_terminal_status']=='COMPLETE_VALID' for r in rows),'Nonvalid accepted proposal')
    require(not ({r['run_key'] for r in rows}&{r['run_key'] for r in ledger['rows']}),'Existing result cannot be overwritten')
    proof={'path':str(review_path.relative_to(REPO)),'sha256':digest(review_path)}
    ledger['rows'] += [{**r,'independent_review':proof} for r in rows]
    require(json.dumps(ledger['rows'][:old_count],sort_keys=True)==old_rows,'Historical acceptance rows changed')
    ledger['supersedes']={'manifest_sha256':state['binding']['manifest_sha256'],'publication_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()}
    ledger['generation']+=1;ledger['revision']='FT20261017_LANE5_A1_B1_'+review['workload'].upper()+'_ACCEPTED_r1';ledger['updated_at']=datetime.now(timezone.utc).isoformat();ledger['supersession_evidence'].append(proof)
    if a.extra_release:
        require(a.extra_review is not None,'Missing extra adapter review');release=json.loads(a.extra_release.read_text());require(release['status']=='INDEPENDENTLY_QUALIFIED','Extra release unqualified')
        for feature in release['qualified_feature_vectors']:
            ledger['launch_authorizations'].append({**{k:release[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')},'feature_vector':feature,'ideal_vector':{'meta':False,'read_hit':False,'wb':False},'qualified_release_sha256':digest(a.extra_release),'status':'CURRENT_QUALIFIED_FOR_LAUNCH','application_scope':'FULL_NATIVE_NONATOMIC_ONLY_WITH_PER_SPEC_COMPLETE_CONTENT_PROOF'})
        ledger['supersession_evidence'].append({'path':str(a.extra_review.relative_to(REPO)),'sha256':digest(a.extra_review)})
    accepted=[r for r in ledger['rows'] if r['scientific_acceptance']=='CURRENT_ACCEPTED'];pairs=len(accepted)//2
    ledger['status']=f'{pairs}_CURRENT_ACCEPTED_REPAIRED_RELEASE_PAIRS';path=REPO/MANIFEST;path.write_text(json.dumps(ledger,indent=2,sort_keys=True)+'\n')
    a.acceptance_pack.mkdir(parents=True);shutil.copyfile(path,a.acceptance_pack/'SCIENTIFIC_ACCEPTANCE_V2.json')
    delivery={'schema_version':'EPL2_LANE5_TO_LANE6_CURRENT_ACCEPTED_PAIR_V1','status':'CURRENT_ACCEPTED_PENDING_REMOTE_POINTER_INSTALL','workload':review['workload'],'pair_pack':str(a.pair_pack.relative_to(REPO)),'acceptance_pack':str(a.acceptance_pack.relative_to(REPO)),'ledger_generation':ledger['generation'],'ledger_sha256':digest(path),'current_accepted_pairs':pairs,'all5_required_before_geomean':True,'rows':rows,'comparison':json.loads((a.pair_pack/'COMPARISON.json').read_text()),'source_manifest_sha256':digest(a.pair_pack/'SOURCE_MANIFEST.json')}
    (a.acceptance_pack/'LANE6_HANDOFF.json').write_text(json.dumps(delivery,indent=2,sort_keys=True)+'\n');(a.acceptance_pack/'REVIEW.md').write_text('# '+review['workload']+' current scientific acceptance\n\nBoth exact new terminals passed independent reparse, full input/source/binary/qualification/current-authority review. Next V2 adds both accepted rows, preserving every historical row. Remote readback and central pointer install precede delivery. No result selection, no numeric SASS claim, no group geomean until all five.\n');freeze_checksums(a.acceptance_pack)
    receipt_path=HANDOFF/'RECEIPT.json';receipt=json.loads(receipt_path.read_text());receipt.update(status=f'R0_1_A1_B1_{pairs}_CURRENT_ACCEPTED_PAIRS',updated_at=ledger['updated_at'],active_runs=[])
    receipt['artifacts']=list(dict.fromkeys(receipt['artifacts']+[str(a.pair_pack.relative_to(REPO)),str(a.acceptance_pack.relative_to(REPO))]));receipt['validation']['scientifically_accepted_R0_application_runs']=len(accepted);receipt['validation']['scientifically_accepted_R0_application_pairs']=pairs
    receipt['formal_R0_1_campaign']={'status':'ROLLING_CURRENT_ACCEPTED' if pairs<5 else 'ALL5_CURRENT_ACCEPTED','accepted_pairs':pairs,'accepted_rows':accepted,'remaining_workloads':[w for w in ('sad','vectorAdd_4M','cfd_097k','convolutionSeparable','FWT_7_21') if w not in {r['workload'] for r in accepted}],'geomean_computed':False};receipt['bounded_continue']['latest_pair_delivery']=delivery;receipt['bounded_continue']['next_action']='Remote readback/pointer install and immediate Lane6 handoff; continue frozen remaining order';receipt_path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    (HANDOFF/'STATUS.md').write_text('# Lane5 — '+str(pairs)+'/5 repaired official R0.1 pairs accepted\n\nLatest '+review['workload']+' pair passed independent raw reparse/full identity/current V2 review. Current generation'+str(ledger['generation'])+' preserves old withdrawals and adds both new CURRENT_ACCEPTED rows. Exact results/identities/closures in '+str(a.pair_pack.relative_to(REPO))+', delivery in '+str(a.acceptance_pack.relative_to(REPO))+'. No group geomean until5.\n\nGoal ACTIVE to original12:19:03UTC deadline. All11 actual source gates passed; five full native input sets non-atomic, ordinary symbolic32B sector/lifecycle scope only. Same Core7b8e6ac7/Framework9bd17f9d/vendorf90c430c/binary23094a9d. TVD/RO/Ideal excluded; C1 legacy headroom excluded from causal claims. No active long simulator at this publication boundary. Next remote readback/current pointer, handoff and next frozen pair under standard48GiB/64GiB/Share40GiB/max2long quota. No compiler, waiter, migration or cleanup by Lane5.\n')
    print(json.dumps({'status':'STAGED_NEXT_V2_REQUIRES_REMOTE_READBACK_AND_POINTER','generation':ledger['generation'],'accepted_pairs':pairs,'manifest_sha256':digest(path)}))


if __name__=='__main__':main()
