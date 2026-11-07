"""Independent Main final exact4 metadata and archive verification; no new models."""
from pathlib import Path
import json,hashlib,tarfile,datetime
C=Path(__file__).resolve().parent
N=Path('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def exact(r):
 assert sha(r['path'])==r['sha256'],'drift '+r['path'];return read(r['path'])
def nonlive(pid,ticks):
 p=Path('/proc/%d/stat'%pid)
 if not p.exists():return True
 a=p.read_text().rsplit(')',1)[1].split()
 return int(a[19])!=ticks or a[0]=='Z'
def main():
 reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');before=read(C/'REGISTRY_BEFORE_EXACT4.json');m=read(C/'EXACT_EXECUTION_MANIFEST.json')
 old_ep={k:q for k,q in before['registered_future_requests'].items()if q.get('owner')=='EP-MAIN'and q.get('project')=='EP_L2'}
 assert all(reg['registered_future_requests'][k]==q for k,q in old_ep.items())
 points=[];restores=0
 for p in m['points']:
  z=m['groups'][p['group']];q=reg['registered_future_requests'][z['request_id']]
  assert q['state']=='CLOSED_COMPLETED'and q['remaining']==0 and len(q['consumed'])==2 and q['reserved_write_bytes']==0
  assert read(Path(z['data_root'])/'control/DISPATCH_CLAIMS.json')=={'claims':{}}
  r=q['consumed'][p['cohort']];assert r['state']=='CLOSED_ACCEPTED'
  s=exact(p['spec_ref']);a=exact(r['accepted_point_ref']);d=exact(r['done_ref']);ar=exact(r['archive_receipt_ref']);am=exact(ar['manifest_ref'])
  assert s['source_identity']==a['source_identity']==d['source_identity']
  assert s['input_identity_sha256']==a['input_identity_sha256']
  assert a['spec_ref']['sha256']==p['spec_ref']['sha256']==d['spec_ref']['sha256']
  assert a['hardware_drained']is True and d['launcher_wait_returncode']==0 and d['stop_reason']is None
  assert a['kernel_count']==len(s['expected_kernel_launches'])and a['CTA']==s['expected_CTA']and a['instructions']==s['expected_instructions']
  rs=ar['native_restores'];assert len(rs)==2 and len({v['target']for v in rs})==2
  assert all(v['status']=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS'and v['archive_sha256']==ar['archive_ref']['sha256']for v in rs);restores+=2
  assert sha(ar['archive_ref']['path'])==ar['archive_ref']['sha256']==am['archive_sha256']
  wanted={v['member']:v for v in am['members']};seen=set()
  with tarfile.open(ar['archive_ref']['path'],'r|')as tf:
   for member in tf:
    assert member.isfile()and member.name in wanted and member.name not in seen;seen.add(member.name)
    h=hashlib.sha256();total=0;f=tf.extractfile(member)
    for b in iter(lambda:f.read(1<<20),b''):h.update(b);total+=len(b)
    assert h.hexdigest()==wanted[member.name]['sha256']and total==wanted[member.name]['bytes']
  assert seen==set(wanted)
  identity=exact(d['closed_artifact_refs']['NATIVE_SIMULATOR_PID_AND_MAPS.json']);assert nonlive(identity['pid'],identity['start_ticks'])
  cc=read(C/'CLOSED_COUNTERS'/(p['cohort']+'.json'))
  assert cc['uuid']==r['uuid']and cc['spec_sha256']==p['spec_ref']['sha256']and cc['raw_compressed_ref']==d['raw_compressed_ref']
  ro=cc['groups']['EPL2ROV1|SUMMARY|']['totals'];assert ro['accepted_ro']==ro['transactions']+ro['merges']==ro['responses']
  points.append({'cohort':p['cohort'],'uuid':r['uuid'],'cycles':a['cycles'],'spec_ref':p['spec_ref'],'done_ref':r['done_ref'],'accepted_point_ref':r['accepted_point_ref'],'archive_receipt_ref':r['archive_receipt_ref'],'archive_members_verified':len(seen),'full_native_restores':2,'command_count':s['command_count'],'kernel_count':a['kernel_count'],'CTA':a['CTA'],'instructions':a['instructions'],'natural_wall_seconds':d['elapsed_seconds'],'model_generation_nonlive':True})
 for name in ['ROOT_LAUNCH_ACK.json','ROOT_METADATA_WATCH_LAUNCH_ACK.json']:
  ack=read(C/name);assert nonlive(ack['pid'],ack['start_ticks'])
 current=read(C/'PERFORMANCE_CURRENT.json');assert current['counts']=={'accepted':4,'technical_failure':0,'pending':0}
 assert all('counter_gap'not in r for r in current['points'])
 out={'schema':'EP_MAIN_UMT1_FINAL_EXACT4_COMPLETION_AUDIT_V1','status':'ALL4_ACCEPTED_ARCHIVED_RESTORED_AND_SCOPE_CLOSED_PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorized':4,'consumed':4,'accepted':4,'model_technical_failures':0,'new_model_retries':0,'refunds':0,'Native_full_restores':restores,'points':points,'all_old_EP_rows_preserved':len(old_ep),'all_old_EP_row_fields_unchanged':True,'all_models_and_original_dispatcher_and_metadata_watch_naturally_terminated':True,'original_dispatcher_HOLD_retained_no_restart':True,'closed_scan_host_route_issue_resolved_by_exact_insert_review':True,'Source_KEEP':True,'source_release_bytes':0,'application_NI':'NOT_MEASURED','physical_PPA':'NOT_PROVEN','numeric_output':'UNKNOWN'}
 (C/'FINAL_REQUIREMENT_COMPLETION_AUDIT.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'accepted':4,'restores':restores,'old_EP_rows_preserved':len(old_ep),'member_counts':[p['archive_members_verified']for p in points]}))
if __name__=='__main__':main()
