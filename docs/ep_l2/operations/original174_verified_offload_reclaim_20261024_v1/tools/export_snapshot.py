"""Read only this finite task's metadata; never walk raw trees or hash bodies."""
from local_common import *
import csv,io

SERVER=r'''
import os,json,time,pathlib,hashlib
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1')
state=json.loads((T/'control/STATE.json').read_bytes());p=P('/proc')/str(state['driver_pid'])
live=None
if p.exists():
 s=(p/'stat').read_text().rsplit(')',1)[1].split();live=dict(pid=state['driver_pid'],start_ticks=int(s[19]),state=s[0],command=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
ledger=[json.loads(z) for z in (T/'control/LEDGER.jsonl').read_text().splitlines()];latest={};committed=[]
for row in ledger:
 latest[row['asset_id']]=row
for aid,row in latest.items():
 if row['status']!='ARCHIVED_CONTENT_VERIFIED':continue
 bundle=P(row['true164_bundle'].replace('/home/shared','/root/share/mnt164',1));raw=(bundle/'COMMIT.json').read_bytes();c=json.loads(raw);m=(bundle/'SOURCE_MANIFEST.json').read_bytes();ranges=(bundle/'RANGE_INDEX.json').read_bytes();tree=(bundle/'TREE_VERIFICATION.json').read_bytes();h=lambda b:hashlib.sha256(b).hexdigest()
 assert h(raw)==row['commit_sha256'] and h(m)==c['manifest_sha256'] and h(ranges)==c['range_index_sha256'] and h(tree)==c['tree_verification_sha256']
 mf=json.loads(m);rest=json.loads((T/'restore'/(aid+'.json')).read_bytes())
 committed.append(dict(ledger=row,COMMIT=c,current_control_hash_links_verified=True,manifest_original_bytes=mf['source_data_bytes'],regular_files=len(mf['members']),directories=len(mf.get('directory_metadata',{})),symlinks=len(mf.get('source_unselected_symlink_references',[])),native_restore=rest,restore_entry=mf['new_true164_bundle']+'/RESTORE.sh'))
reg=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json');r=json.loads(reg.read_bytes());reserves={k:dict(state=v.get('state'),reserved_write_bytes=v.get('reserved_write_bytes'),budget=v.get('budget'),remaining=v.get('remaining')) for k,v in r['registered_future_requests'].items()}
s=os.statvfs('/root/data');a=os.statvfs('/root/share/mnt164');print(json.dumps(dict(unix=time.time(),state=state,live_process=live,ledger=ledger,committed=committed,SSD_available_bytes=s.f_bavail*s.f_frsize,true164_available_bytes=a.f_bavail*a.f_frsize,native_registry_observation=reserves)))
'''

def csvfile(name,rows,fields):
    s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows);(R/name).write_bytes(s.getvalue().encode())

def main():
    x=remote('hrl-174-new',SERVER);queue=load(OLD/'FROZEN_AUTHORIZED_EXECUTION_SCOPES.json')['scopes'];done={z['ledger']['asset_id']:z for z in x['committed']};latest={z['asset_id']:z for z in x['ledger']};arch=[];pending=[];recovery=[]
    for q in queue:
        aid=q['asset_id'];base=dict(asset_id=aid,kind=q['kind'],source=q['source_root'],original_bytes=q['expected_bytes'],frozen_regular_files=len(q['files']))
        if aid in done:
            z=done[aid];v=z['ledger'];arch.append(dict(base,status='ARCHIVED_CONTENT_VERIFIED',true164_bundle=v['true164_bundle'],commit_sha256=v['commit_sha256'],this_goal_unique_verified_payload_bytes=q['expected_bytes'],last_invocation_new_payload_bytes=v['new_transferred_bytes'],same_goal_range_reuse_bytes=v['reused_range_bytes'],native_restore_status=z['native_restore']['status'],Source_disposition=v['source_disposition']))
            recovery.append(dict(asset_id=aid,source=q['source_root'],true164=v['true164_bundle'],complete_original_file_metadata=v['true164_bundle']+'/SOURCE_MANIFEST.json',file_SHA='SOURCE_MANIFEST.json members[].sha256',restore_entry=z['restore_entry'],commit_sha256=v['commit_sha256'],native_restore_status=z['native_restore']['status'],native164_restore_claimed=False))
        else:
            active=x['state'].get('asset_id')==aid and x['live_process'] is not None;prev=latest.get(aid,{})
            pending.append(dict(base,status='IN_PROGRESS_'+x['state']['phase'] if active else 'PENDING' if not prev else prev['status'],reason='' if active else prev.get('reason','Await finite ordered queue; no independent asset failure claimed')))
    fields=['asset_id','kind','source','original_bytes','frozen_regular_files','status','true164_bundle','commit_sha256','this_goal_unique_verified_payload_bytes','last_invocation_new_payload_bytes','same_goal_range_reuse_bytes','native_restore_status','Source_disposition']
    csvfile('FINAL_ARCHIVED_ASSETS.csv',arch,fields);csvfile('REMAINING_HOLD_AND_COPY_QUEUE.csv',pending,['asset_id','kind','source','original_bytes','frozen_regular_files','status','reason'])
    (R/'ARCHIVE_EXECUTION_LEDGER.jsonl').write_bytes(b''.join((json.dumps(z,separators=(',',':'))+'\n').encode() for z in x['ledger']))
    final=len(done)==115
    save('SOURCE_TO_TRUE164_RECOVERY_MAP.json',dict(status='FINAL_COMPLETE' if final else 'ACTIVE_SNAPSHOT_NOT_COMPLETION',original_scope=115,new_verified_entries=recovery,old_recovery_map='9a34666c025474367b9176764d2ae67e03b22b49:SOURCE_TO_TRUE164_RECOVERY_MAP.json',current_Source_retirement_overrides=['Four approved BICG/ATAX source kernel files','Exact Source polybench.tgz cold backup'],retirement_evidence='release/ and checkpoint/release/; original immutable SOURCE_KEEP receipts are historical as-of proofs'))
    save('FULL_SHA_AND_COMMIT_RECEIPTS.json',dict(status='FINAL_COMPLETE' if final else 'ACTIVE_SNAPSHOT',committed=x['committed'],no_data_body_rehash_by_export=True))
    save('NATIVE_RESTORE_VERIFICATION.json',dict(status='FINAL_COMPLETE' if final else 'ACTIVE_SNAPSHOT',records=[dict(asset_id=z['ledger']['asset_id'],proof=z['native_restore']) for z in x['committed']],native164_claimed=False))
    save('RESOURCE_AND_ACTIVE_SCIENCE_AUDIT.json',{k:v for k,v in x.items() if k not in ['committed','ledger']})
    counts=dict(status='COMPLETE' if final else 'ACTIVE_NOT_COMPLETE',scope=115,committed=len(done),pending=len(pending),trace_committed=sum(z['kind']=='TRACE' for z in arch),DTC_raw_committed=sum(z['kind']=='DTC_RAW' for z in arch),Q05_committed=sum(z['kind']=='Q05_FIXED10000' for z in arch),this_goal_unique_committed_payload_bytes=sum(z['original_bytes'] for z in arch),all_completed_regular_files=sum(z['frozen_regular_files'] for z in arch),observed_pool_reclaim_intervals_bytes=18936295424,observed_Source_unlink_intervals_bytes=18420580352,live_process=x['live_process'],observed_unix=x['unix'])
    save('COUNTS_AND_CURRENT_STATE.json',counts);print(json.dumps(counts))

if __name__=='__main__':main()
