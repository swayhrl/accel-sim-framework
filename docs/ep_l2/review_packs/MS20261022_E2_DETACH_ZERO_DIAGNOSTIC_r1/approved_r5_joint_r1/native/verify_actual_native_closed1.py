"""Read-only bounded posterior over completed actual fixture epochs; never run native."""
import argparse,sys,json,hashlib,importlib.util,io
from pathlib import Path
sys.path.insert(0,'/tmp/e2_r5_parser_candidate');import decoder
P=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1');FP=P/'parser_recovery/decoder_samecycle_close.py';schema=json.loads((P/'runtime_r4/SOURCE_BOUND_SCHEMA_r4.json').read_text());assert hashlib.sha256(FP.read_bytes()).hexdigest()==decoder.FIXED_R4_SHA256
sp=importlib.util.spec_from_file_location('fixed647_native_actual',FP);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def ref(p):p=Path(p);return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def verify(receipt,artifacts,out):
 r=json.loads(receipt.read_text());b=json.loads(artifacts.read_text());binding={**b['source_identity'],'binary_sha256':b['artifacts']['main']['sha256'],'archive_sha256':b['artifacts']['archive']['sha256']};rows=[];total=0;valid=0;invalid=0
 for t in r['tests']:
  p=Path(t['raw_path']);assert p.stat().st_size<=16*2**20;raw=p.read_bytes();total+=len(raw);assert total<=64*2**20;assert ref(p)['sha256']==t['raw_sha256'] and len(raw)==t['raw_bytes'];assert t['actual_native_wait_exit']==0 and not t['timeout'] and not t['output_limit_exceeded']
  frames=[];cur=None
  for lineno,line in enumerate(raw.splitlines(keepends=True),1):
   if line.startswith(b'DETACH_NATIVE_FRAME_BEGIN|'):assert cur is None;cur={'name':line.decode().strip().split('|',1)[1],'start':lineno,'lines':[]}
   elif line.startswith(b'DETACH_NATIVE_FRAME_END|'):assert cur and cur['name']==line.decode().strip().split('|',1)[1];cur['end']=lineno;frames.append(cur);cur=None
   elif cur is not None:cur['lines'].append(line)
  assert cur is None
  row={'id':t['id'],'variant':t['variant'],'native_binary_sha256':t['binary_sha256'],'actual_wait_exit':0,'raw_ref':ref(p),'frames':[],'qualification_granted':False}
  casevalid=0;caserejected=False
  for f in frames:
   r5=[json.loads(x[len(decoder.PREFIX):])for x in f['lines'] if x.startswith(decoder.PREFIX)]
   rr={'name':f['name'],'source_lines':[f['start'],f['end']],'r5_record_count':len(r5)}
   if not r5:rr['status']='NO_R5_RECORDS_IN_THIS_FIXTURE_EPOCH';row['frames'].append(rr);continue
   flags={'T':t['case']!='T_OFF','M':t['case']!='T_OFF','ro_runtime':t['case']!='T_OFF'}
   # Exact existing fixture source: T1M0 subcontrol167-174; explicit UIDs11/12 main264-274.
   catalog=[]
   if t['case']=='ROLLUP_RESIDUAL' and f['name']=='M0_LINE128':flags['M']=False
   if t['case']=='ROLLUP_RESIDUAL' and f['name']=='MAIN_CONTROL':catalog=[11,12]
   feed=decoder.Feed(expected_slices=[0],registered_slice_count=1,expected_kernels=catalog,expected_flags=flags,source_binding=binding,old212_decoder_sha256=decoder.FIXED_R4_SHA256,full_application=False)
   old=m.Decoder(schema,expected_slice_count=1,require_closed=True,expected_T=flags['T'],expected_M=flags['M'],expected_runtime=flags['ro_runtime']).decode(decoder.TappingReader(io.BytesIO(b''.join(f['lines'])),feed));new=feed.finish(old)
   rr.update(status=new['status'],old212_status=old['status'],old212= {'final_cycle':old.get('final_cycle'),'counter_fields':len(old.get('schema_counter_fields',[])),'snapshot_count':old.get('snapshot_count'),'reason':old.get('reason')},r5_result=new)
   if new['status']=='VALID_R5_OBSERVER_DECLARATIONS_ONLY':
    assert new['registered_slice_count']==1 and new['selected_slices']==[0] and new['global_closure_declared'] is True and new['global_epoch_closed_declared'] is True and new['full_application_mode'] is False and new['full_application_qualified'] is False;valid+=1;casevalid+=1
   else:invalid+=1;caserejected=True
   row['frames'].append(rr)
  if t['variant']=='R5_ON':row['r5_selected_math']='PASS_REGISTERED1_CLOSED_NOT_FULL64' if casevalid and not caserejected else 'FAIL_OR_NO_R5_SNAPSHOT'
  else:assert not any(f['r5_record_count']for f in row['frames']);row['r5_selected_math']='NA_R5_DISABLED'
  rows.append(row)
 result={'schema':'E2_R5_TRUE_CLOSED_NATIVE_FRAME_REVIEW_V1','status':'COMPLETED_SUBSET_R5_FRAME_REVIEW_ONLY' if r['status']=='NATIVE_PRECHECK_NOT_COMPLETE' else 'R5_REAL_NATIVE_FRAME_MATH_PASS_NOT_APPLICATION' if not invalid and all(x['r5_selected_math'] in ('PASS_REGISTERED1_CLOSED_NOT_FULL64','NA_R5_DISABLED')for x in rows) else 'R5_NATIVE_FRAME_REJECTED','source_identity':binding,'receipt_ref':ref(receipt),'artifacts_ref':ref(artifacts),'parser_refs':{n:ref(Path('/tmp/e2_r5_parser_candidate')/n)for n in ('decoder.py','math_audit.py')},'actual_native_invocations_reviewed':len(rows),'r5_valid_epochs':valid,'r5_invalid_epochs':invalid,'actual_bytes_read':total,'full64_qualification_granted':False,'new_execution':False,'rows':rows}
 out.mkdir(exist_ok=True);(out/'REVIEW.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ('status','actual_native_invocations_reviewed','r5_valid_epochs','r5_invalid_epochs','actual_bytes_read')},indent=2));print('sha',ref(out/'REVIEW.json')['sha256']);return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--receipt',required=True);a.add_argument('--artifacts',required=True);a.add_argument('--out',required=True);x=a.parse_args();verify(Path(x.receipt),Path(x.artifacts),Path(x.out))
