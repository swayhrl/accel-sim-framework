"""One finite E controller process: Conv then FWT, publish each finished pair.

Existing samecampaign ledger/lock/T0 and all resource/science gates are required.
No waiter, detached second controller, reinitialization or automatic failed-run retry.
"""
from pathlib import Path
import json,sys,time,subprocess,os
sys.path.insert(0,'/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e')
import coordinator as c
from controller import step
p=Path(__file__).resolve().parent;root=p.parents[3]


def publish(queue,result,coord):
    snapshot=coord.snapshot();data=json.loads((c.SHARED/'RUN_REGISTRY.json').read_text())
    relevant=[a for a in snapshot['attempts'] if a['identity']['binary_sha256']==snapshot['final_source_identity']['binary_sha256']]
    receipt=dict(schema='E_NEW773_FORMAL_PAIR_RESULT_CHECKPOINT_V1',at_unix=time.time(),campaign_id=c.CAMPAIGN,
      source_identity=snapshot['final_source_identity'],T0=snapshot['t0_unix'],maximum_actual_starts=40,
      actual_starts=snapshot['actual_starts'],remaining=snapshot['remaining_start_capacity'],controller=snapshot['controller'],
      attempts=[{k:a.get(k) for k in ['attempt_id','run_key','profile','state','actual_start','process','budget_bucket','receipt_path','receipt_sha256']} for a in snapshot['attempts']],
      accepted_results=snapshot['accepted_results'],accepted_pairs=snapshot['accepted_pairs'],
      active_runs={k:r for k,r in data['runs'].items() if r['status'] in c.ACTIVE},
      active_leases={k:r for k,r in data['resource_leases'].items() if r['status'] in c.ACTIVE},
      resources=c.local_resources(),output_usage=c.output_usage(),E_source_publication=json.loads((c.HANDOFF/'CLIENT_CONTRACT.json').read_text())['source_publication_commit'],
      CLIENT_sha256=c.digest(c.HANDOFF/'CLIENT_CONTRACT.json'),queue=queue,controller_result=result,
      source_start_deadline=c.START_DEADLINE,result_intake_deadline=c.INTAKE_DEADLINE,
      historical3_starts_and_raw_preserved=True,btree='HOLD_UNCHANGED',R35_extra_joint='FAILED_UNQUALIFIED_PENDING_B_C; NOT_A_PASSED_OR_REPLACEMENT_GATE')
    original=json.loads((p.parent/'MS20261020_E_NEW773_INTAKE_r1/PARSER_REVIEW.json').read_text())
    for name,h in original['raw_and_status_hashes'].items():c.require(c.digest(name)==h,'historical raw/status unexpectedlychanged')
    checkpoint=p/(queue['workload']+'_RESULT_CHECKPOINT.json');c.write_json(checkpoint,receipt)
    for attempt in relevant:
        if attempt.get('receipt_path'):
            c.require(c.digest(attempt['receipt_path'])==attempt['receipt_sha256'],'result receipt changed')
            c.write_json(p/(attempt['attempt_id']+'_RUN_STATUS.json'),json.loads(Path(attempt['receipt_path']).read_text()))
    e=root/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/e'
    c.write_json(e/'RECEIPT.json',receipt)
    (e/'STATUS.md').write_text('# Lane E — new773 formal result checkpoint\n\n'+
        f"{queue['workload']}: {result['status']}. Actual starts {snapshot['actual_starts']}/40, remaining {snapshot['remaining_start_capacity']}; current accepted points {len(snapshot['accepted_results'])}, pairs {len(snapshot['accepted_pairs'])}.\n\n"+
        'Core27ec10bd / Framework9dd1ee57 / main773271ac. Parserfix exact E source a1a68b8ed1155950c0e81645133f7229667a1cab. Original11+7 gates independently accepted after current24 affectednative and newsourceOFF. R35 extra128B joint fixture remains failed/unqualified pendingB/C; no reuse_seen change.\n\n'+
        'OldE001/E002/E003 and raw/status/holds retained; oldbinary results not used as newbinary endpoints. Btree HOLD, no DWT rescan. SameT0/40=32+8/cutoffs/6+20GiBresults/workspace5GiB+2GiBmonitor/Share40GiB/RAM64GiB/CPU and default2sim constraints. This is a bounded sequential queue controller; next input only after currentpair is accepted and published.\n')
    paths=[checkpoint,p/(queue['workload']+'_CONTROLLER_RESULT.json'),e/'STATUS.md',e/'RECEIPT.json']+[p/(a['attempt_id']+'_RUN_STATUS.json') for a in relevant if a.get('receipt_path')]
    def git(args,**kw):return subprocess.check_output(['git','-c','gc.auto=0']+args,cwd=root,**kw)
    git(['add','-f']+[str(x.relative_to(root)) for x in paths])
    if git(['diff','--cached','--name-only']).strip():git(['commit','-m','docs(ep-l2-e): publish new773 '+queue['workload']+' actual result checkpoint'])
    env=dict(os.environ,GIT_SSH_COMMAND='ssh -p 443 -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=yes')
    git(['-c','pack.threads=1','push','git@ssh.github.com:swayhrl/accel-sim-framework.git','HEAD:refs/heads/hrl/ep-l2-ms20261019-e-eval-v1'],env=env,stderr=subprocess.STDOUT)
    git(['-c','url.https://github.com/.insteadOf=git@github.com:','-c','credential.helper=!gh auth git-credential','fetch','--no-tags','origin','hrl/ep-l2-ms20261019-e-eval-v1'],stderr=subprocess.STDOUT)
    head=git(['rev-parse','HEAD'],text=True).strip();c.require(head==git(['rev-parse','FETCH_HEAD'],text=True).strip(),'remote HEAD mismatch')
    for x in paths:c.require(git(['show',head+':'+str(x.relative_to(root))])==x.read_bytes(),'remote artifact readback mismatch')
    readback=dict(remote_commit=head,verified_unix=time.time(),checkpoint=str(checkpoint),checkpoint_sha256=c.digest(checkpoint),all_result_paths_verified=[str(x) for x in paths])
    c.write_json(p/(queue['workload']+'_RESULT_REMOTE_READBACK.json'),readback)
    c.write_json(c.HANDOFF/'events'/('E_TO_D_NEW773_'+queue['workload']+'_RESULT_REMOTE.json'),readback)
    print(json.dumps(dict(status='ACTUAL_RESULT_PUSH_REMOTE_READBACK_VERIFIED',**readback)),flush=True)


def main():
    receipt=json.loads((p/'RECEIPT.json').read_text());coord=c.Coordinator()
    c.require(coord.snapshot()['final_source_identity']==receipt['source_identity'],'source changed before controller')
    for queue in receipt['queues']:
        c.require(c.digest(queue['path'])==queue['sha256'],'frozen queue changed')
        result=step(coord,queue['path'])
        c.write_json(p/(queue['workload']+'_CONTROLLER_RESULT.json'),result)
        publish(queue,result,coord)
        pair=coord.snapshot()['accepted_pairs'].get(queue['pair_id'])
        if not pair or pair['status']!='CURRENT_ACCEPTED':
            print(json.dumps(dict(status='AFFECTED_PAIR_REVIEW_REQUIRED_NO_FURTHER_DISPATCH',queue=queue,controller=result)),flush=True);break
        print(json.dumps(dict(status='PAIR_CURRENT_ACCEPTED_DELIVERED_TO_D',pair=pair)),flush=True)
if __name__=='__main__':main()
