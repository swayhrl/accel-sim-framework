"""Metadata-only closure audit for the unchanged finite 115-asset execution.

Does not start processes remotely, acquire transfer locks, hash large bodies,
modify checkpoints, or alter scientific qualification. The existing publisher
includes these task-local reports on its next normal publication.
"""
import sys
sys.dont_write_bytecode=True
from local_common import *
import csv,io,collections

OUT=R/'t2'
PRIOR=Path('D:/repo/ep-dtc-trace-migration-20261024-v1/docs/ep_l2/operations/174new_ep_dtc_trace_migration_20261024_v1')
CLOSURE=Path('D:/repo/original174-large-trace-evidence-closure-20261024-v1/docs/ep_l2/operations/original174_trace_evidence_closure_20261024_v1')

AUDIT=r'''
import pathlib,os,json,gzip,hashlib,time,collections
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');N=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets')
h=lambda b:hashlib.sha256(b).hexdigest()
def js(p):return json.loads(P(p).read_bytes())
raw=(T/'control/FROZEN_SCOPES.json.gz').read_bytes();assert h(raw)=='718f30ec3bc8e5ece20df02cd472ebee17eac320f7b5a9e5b5e69841cc63cc04'
q=json.loads(gzip.decompress(raw))['scopes'];byid={x['asset_id']:x for x in q};ledger=[json.loads(z) for z in (T/'control/LEDGER.jsonl').read_text().splitlines()];done={x['asset_id']:x for x in ledger if x['status']=='ARCHIVED_CONTENT_VERIFIED'}
state=js(T/'control/STATE.json');sup=js(T/'control/CONTINUATION_SUPERVISOR.json');committed=[];members=[];errors=[]
proc=P('/proc')/str(state['driver_pid']);driver_live=False
try:driver_live=int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])==state.get('driver_start_ticks') and str(T/'tools/offload_driver.py').encode() in (proc/'cmdline').read_bytes().split(b'\0')
except OSError:pass
for aid,row in done.items():
 try:
  b=P(row['true164_bundle'].replace('/home/shared','/root/share/mnt164',1));c=js(b/'COMMIT.json');mr=(b/'SOURCE_MANIFEST.json').read_bytes();m=json.loads(mr);ranges=js(b/'RANGE_INDEX.json');traw=(b/'TREE_VERIFICATION.json').read_bytes();tree=json.loads(traw);eof=js(b/'SOURCE_CURRENT_EOF_SHA_PROOFS.json');receipt=js(b/'RECEIPT.json')
  assert h((b/'COMMIT.json').read_bytes())==row['commit_sha256']
  assert c['manifest_sha256']==h(mr)==row['manifest_sha256'] and c['range_index_sha256']==h((b/'RANGE_INDEX.json').read_bytes()) and c['tree_verification_sha256']==h(traw)
  assert c['object_id']==m['object_id']==receipt['object_id']
  scope=byid[aid];frozen={x['relative_path']:x for x in scope['files']};actual={x['relative_path']:x for x in m['members']}
  assert set(frozen)==set(actual) and sum(x['size'] for x in actual.values())==scope['expected_bytes']==m['source_data_bytes']
  assert [(x['path'],x['size'],x['sha256']) for x in eof]==[(x['relative_path'],x['size'],x['sha256']) for x in m['members']]
  assert receipt['Source_full_SHA_matches'] and receipt['true164_closed_reopen_whole_SHA_matches']
  proof={x['relative_path']:x for x in tree};assert set(proof)==set(actual)
  for name,x in actual.items():
   f=frozen[name]
   for k in ['dev','inode','size','mtime_ns','ctime_ns','uid','gid','mode','type']:
    v=int(f[k],8) if k=='mode' and isinstance(f[k],str) else f[k]
    assert x[k]==v,(aid,name,k)
   if f.get('sha256'):assert f['sha256']==x['sha256']
   coverage=0
   for part in ranges[name]:assert part['offset']==coverage and 0<part['size']<=134217728;coverage+=part['size']
   assert coverage==x['size'] and proof[name]['sha256']==x['sha256'] and proof[name]['size']==x['size']
   dest=b/'tree'/name;assert dest.is_file() and not dest.is_symlink() and dest.stat().st_size==x['size']
   members.append(dict(asset_id=aid,source_root=m['source_root'],relative_path=name,size=x['size'],sha256=x['sha256'],uid=x['uid'],gid=x['gid'],mode=x['mode'],mtime_ns=x['mtime_ns'],true164_path=m['new_true164_bundle']+'/tree/'+name))
  ordered=m.get('ordered_kernel_members',[]);missing=[z for z in ordered if z not in actual]
  if m['entry_name']!='__NO_SELECTED_COMMANDLIST__':
   commands=bytes.fromhex(m['commandlist_bytes_hex']);assert (b/'tree'/m['entry_name']).read_bytes()==commands
   assert ordered==[z.strip() for z in commands.decode().splitlines() if z.strip().endswith(('.trace','.traceg'))]
  restore=js(T/'restore'/(aid+'.json'));helper=(b/'trace_copy.py').read_text();assert (b/'RESTORE.sh').is_file() and (b/'server_resources.py').is_file()
  committed.append(dict(asset_id=aid,source_root=scope['source_root'],kind=scope['kind'],bytes=scope['expected_bytes'],files=len(actual),commit_sha256=row['commit_sha256'],manifest_sha256=h(mr),object_id=m['object_id'],true164_bundle=m['new_true164_bundle'],restore_entry=m['new_true164_bundle']+'/RESTORE.sh',native_restore_status=restore['status'],full_native_restore_performed=restore['status']=='RESTORE_VERIFIED_NATIVE_TARGET',bounded_helper_limit_bytes=251658240,large_full_native_restore_requires_separate_admission=m['source_data_bytes']>251658240,raw_trace_files=sum(z.endswith('.trace') for z in actual),processed_traceg_files=sum(z.endswith('.traceg') for z in actual),ordered_kernel_members=ordered,missing_commandlist_members=missing,source_EOF_and_full_tree_SHA_receipts_verified=True,all_commit_links_verified=True,current_payload_rehash=False,scientific_acceptance_granted=c.get('scientific_acceptance_granted',False),unselected_symlink_metadata=m.get('source_unselected_symlink_references',[])))
 except Exception as e:errors.append(dict(asset_id=aid,error=str(e),exception=type(e).__name__))
prior=[]
for old in PRIOR:
 try:
  if not old.get('true164_bundle'):
   cp=P(old['actual_existing_commit_path']);cr=cp.read_bytes();c=json.loads(cr);m=old['_reuse_manifest'];assert h(cr)==old['actual_target_commit_sha256']
   if cp.name=='TRACE_COMMIT.json':
    assert c['status']=='TRACE_MEMBERS_ARCHIVE_AND_CLOSED_REOPEN_SHA_VERIFIED' and c['scope_sha256']==h((cp.parent/'INPUT_SCOPE.json').read_bytes())
    expected={z['relative_path']:(z['size'],z['sha256']) for z in m['members']};actual={z['relative_path']:(z['size'],z['sha256']) for z in c['members']};assert actual==expected
   else:
    assert c['manifest_sha256']==h((cp.parent/'SOURCE_MANIFEST.json').read_bytes())
    expected={z['relative_path']:(z['size'],z['sha256']) for z in m['members']};legacy=js(cp.parent/'SOURCE_MANIFEST.json')['rows'];actual={z['name']:(z['bytes'],z['sha256']) for z in legacy};assert actual==expected
    assert all(z['closed_reopened_sha256']==z['sha256'] for z in legacy)
   for name,(size,sha) in expected.items():assert (cp.parent/'tree'/name).is_file() and (cp.parent/'tree'/name).stat().st_size==size
   prior.append(dict(asset_id=old['asset_id'],selector_id=old['selector_id'],source_root=old['source_root'],bytes=old['original_bytes'],COMMIT_sha256=h(cr),true164_bundle=str(cp.parent).replace('/root/share/mnt164','/home/shared',1),actual_existing_commit_path=old['actual_existing_commit_path'],member_names=list(expected),control_readback='PASS',native_restore_status=old['RESTORE_VERIFIED_NATIVE_TARGET'],new_transfer_bytes=0,legacy_adapter=True));continue
  b=P(old['true164_bundle'].replace('/home/shared','/root/share/mnt164',1));cr=(b/'COMMIT.json').read_bytes();c=json.loads(cr);m=js(b/'SOURCE_MANIFEST.json')
  assert h(cr)==old['actual_target_commit_sha256'] and c['object_id']==old['object_id'] and c['manifest_sha256']==h((b/'SOURCE_MANIFEST.json').read_bytes())
  assert c['range_index_sha256']==h((b/'RANGE_INDEX.json').read_bytes()) and c['tree_verification_sha256']==h((b/'TREE_VERIFICATION.json').read_bytes())
  prior.append(dict(asset_id=old['asset_id'],selector_id=old['selector_id'],source_root=old['source_root'],bytes=old['original_bytes'],COMMIT_sha256=h(cr),true164_bundle=old['true164_bundle'],member_names=[x['relative_path'] for x in m['members']],control_readback='PASS',native_restore_status=old['RESTORE_VERIFIED_NATIVE_TARGET'],new_transfer_bytes=0))
 except Exception as e:prior.append(dict(asset_id=old['asset_id'],selector_id=old['selector_id'],source_root=old['source_root'],control_readback='HOLD',reason=str(e),new_transfer_bytes=0))
release=js(T/'release/COMPLETE.json');package=js(T/'release/POLYBENCH_PACKAGE_COMPLETE.json');retire={}
for role in ['SOURCE','TARGET']:
 p=T/'release'/(role+'.jsonl');rows=[json.loads(z) for z in p.read_text().splitlines()];intents={x['path']:x for x in rows if x['event']=='INTENT'};closed={x['path']:x for x in rows if x['event']=='DONE'}
 retire[role]=dict(intents=len(intents),done=len(closed),unclosed=sorted(set(intents)-set(closed)),unlinked_file_allocated_bytes=sum(x['expected_allocated_bytes'] for x in closed.values()),journal_sha256=h(p.read_bytes()))
resources={}
for name in ['/root/data','/root/share','/root/share/mnt164']:
 f=os.statvfs(name);resources[name]=dict(available_bytes=f.f_bavail*f.f_frsize,free_inodes=f.f_favail)
print(json.dumps(dict(schema='LANE_T2_METADATA_CLOSURE_AUDIT_V1',unix=time.time(),frozen_sha256=h(raw),scope=115,ledger=ledger,state=state,driver_live=driver_live,supervisor=sup,committed=committed,committed_ledger_count=len(done),audit_errors=errors,member_SHA_rows=members,prior20_reuse=prior,retirement=dict(initial=retire,initial_pool_observed_interval_delta=release['actual_observed_shared_SSD_free_increase_bytes'],initial_Source_observed_interval_delta=release['source']['df_after_bytes']-release['source']['df_before_bytes'],package=package,all_prior_retirements_replayed=False),resources=resources)))
'''

def dump(name,x):
    OUT.mkdir(exist_ok=True);p=OUT/name;p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def table(name,rows,fields):
    OUT.mkdir(exist_ok=True);s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows);(OUT/name).write_text(s.getvalue(),encoding='utf-8')

def main():
    prior=load(PRIOR/'TRUE164_TRACE_RECOVERY_INDEX.json')['records']
    for item in prior:
        if not item.get('true164_bundle'):
            raw=(PRIOR/item['all_original_numeric_metadata_and_SHA']).read_bytes()
            assert hashlib.sha256(raw).hexdigest()==item['source_manifest_Git_file_sha256']
            item['_reuse_manifest']=json.loads(raw)
    result=remote('hrl-174-new','PRIOR='+repr(prior)+'\n'+AUDIT,240)
    dump('CONTENT_AND_RESTORE_CLOSURE.json',{k:v for k,v in result.items() if k not in ['ledger','member_SHA_rows']})
    rows=result['member_SHA_rows'];s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=list(rows[0]) if rows else ['asset_id']);w.writeheader();w.writerows(rows);raw=s.getvalue().encode();(OUT/'MEMBER_SHA_INDEX.csv.gz').write_bytes(gzip.compress(raw,mtime=0))
    dump('MEMBER_SHA_INDEX.json',dict(rows=len(rows),uncompressed_sha256=hashlib.sha256(raw).hexdigest(),uncompressed_bytes=len(raw),compressed_file='MEMBER_SHA_INDEX.csv.gz',payload_bodies_rehashed=False))
    summarize(result)
    print(json.dumps(dict(audited_committed=len(result['committed']),ledger_committed=result['committed_ledger_count'],pending=115-result['committed_ledger_count'],errors=result['audit_errors'],prior20_PASS=sum(x['control_readback']=='PASS' for x in result['prior20_reuse']),frozen_sha256=result['frozen_sha256'])))

def summarize(x):
    q=json.loads(gzip.decompress((R/'FROZEN_SCOPES.json.gz').read_bytes()))['scopes']
    done={z['asset_id']:z for z in x['committed']};latest={z['asset_id']:z for z in x['ledger']};state=x['state'];baseline_path=OUT/'TAKEOVER_BASELINE.json'
    if not baseline_path.exists():
        dump('TAKEOVER_BASELINE.json',dict(goal='LANE_T2_FROZEN115_ARCHIVE_COMPLETE_V1',original_execution_goal='ORIGINAL174_VERIFIED_OFFLOAD_AND_SSD_RECLAIM_V1',unix=x['unix'],github_head=git('ls-remote','origin','refs/heads/hrl/ops-original174-verified-offload-reclaim-exec-20261024-v1').decode().split()[0],committed_asset_ids=sorted(done),committed_bytes=sum(z['bytes'] for z in done.values()),scope_sha256=x['frozen_sha256'],driver_pid=state['driver_pid'],driver_start_ticks=state['driver_start_ticks'],supervisor=x['supervisor'],publisher_pid=32272,publisher_creation_time='2026-10-25T01:06:02+08:00',execution_processes_started_by_T2=0,queue_recreated=False,counters_reset=False))
    baseline=load(baseline_path);rows=[]
    for a in q:
        aid=a['asset_id'];p=latest.get(aid,{});v=done.get(aid)
        status='COMMITTED' if v else 'IN_PROGRESS' if aid==state.get('asset_id') and x['driver_live'] else 'HOLD' if p.get('status')=='HOLD_EXACT_ASSET' and p.get('unix',0)>baseline['unix'] else 'PENDING'
        rows.append(dict(asset_id=aid,kind=a['kind'],source_root=a['source_root'],expected_bytes=a['expected_bytes'],status=status,reason=p.get('reason','') if status=='HOLD' else '',prior_historical_hold=p.get('reason','') if status!='COMMITTED' and p.get('status')=='HOLD_EXACT_ASSET' else '',true164_bundle=v['true164_bundle'] if v else '',commit_sha256=v['commit_sha256'] if v else '',native_restore_status=v['native_restore_status'] if v else '',scientific_acceptance='UNCHANGED_NO_NEW_SCIENTIFIC_QUALIFICATION',new_in_T2=aid not in baseline['committed_asset_ids'] and bool(v)))
    table('FROZEN115_FINAL_STATE_TABLE.csv',rows,list(rows[0]));dump('PROGRESS_SUMMARY.json',dict(unix=x['unix'],scope=115,counts=dict(collections.Counter(z['status'] for z in rows)),committed_bytes=sum(z['bytes'] for z in done.values()),new_T2_committed_assets=sum(z['new_in_T2'] for z in rows),new_T2_committed_bytes=sum(z['expected_bytes'] for z in rows if z['new_in_T2']),audit_errors=x['audit_errors'],driver=state,supervisor=x['supervisor'],resources=x['resources']))
    table('NEW_T2_COMMITTED_ASSETS.csv',[z for z in rows if z['new_in_T2']],list(rows[0]))
    dump('RECLAIM_ACCOUNTING.json',dict(unix=x['unix'],**x['retirement'],current_resources=x['resources'],archived_logical_bytes_counted_as_reclaimed_space=False,Source_new_retirement_by_T2=0))

if __name__=='__main__':main()
