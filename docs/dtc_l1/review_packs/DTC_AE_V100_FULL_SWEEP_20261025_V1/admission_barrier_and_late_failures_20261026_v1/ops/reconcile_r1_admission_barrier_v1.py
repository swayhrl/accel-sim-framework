"""Default read-only. No model, signal, entry, or scientific ledger operations.

--apply --plan PLAN requires a matching exact locked authority preimage and uses
the original native update_authority transaction. R16 may call release_barrier
inside its own activation transaction; this program never unseals on its own.
"""
import argparse,copy,datetime,fcntl,hashlib,importlib.util,json,os,pathlib,re
P=pathlib.Path
N=P('/root/data/ep_l2_dtc_l1_native_v2');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');F=P('/root/data/dtc_failure_repair_20261025_v1');V=F/'validation'
ORIGINAL='DTC_AE_V100_FULL_SWEEP_20261025_V1';R1='DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1'
G=1024**3;M=1024**2;ROUND=64*M
STATUS='NEW_ORIGINAL_ADMISSION_PAUSED_FOR_QUALIFIED_REPAIR_SUPPLEMENT'
CONSUMER='9c9a2b9861dffef390b273b1b6aa272576af14168a9fde629b15e1b442cc6384'
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def read(p):return json.loads(P(p).read_bytes())
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(P(p).read_bytes())
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def exclusive(p,b):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
def json_bytes(x):return (json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def q_span(body,key):
 text=body.decode();matches=list(re.finditer(re.escape(json.dumps(key))+r'\s*:\s*',text));require(len(matches)==1,'request key not unique')
 start=matches[0].end();obj,end=json.JSONDecoder().raw_decode(text[start:]);require(obj==json.loads(body)['registered_future_requests'][key],'q span mismatch');return text[start:start+end].encode()
def prefix(q):return digest(canonical({'admitted_specs':q['admitted_specs'],'consumed':{c:{k:v for k,v in r.items() if k!='execution_receipt'} for c,r in q['consumed'].items()},'budget':q['budget'],'remaining':q['remaining'],'sealed':q.get('sealed',[])}))
def live(b):
 try:s=(P('/proc')/str(b['pid'])/'stat').read_text().rsplit(')',1)[1].split();return int(s[19])==b['start_ticks'] and s[0]not in ['Z','X']
 except (FileNotFoundError,ProcessLookupError):return False
def claims(root):return read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
def gather_rows(q):
 rows=[]
 for c,r in sorted(q['consumed'].items()):
  sp=V/'control/specs'/(c+'.json');s=read(sp);require(sha(sp)==q['admitted_specs'][c],'spec pin changed')
  cp=V/'control'/('OPERATIONAL_OUTPUT_CAP_'+c+'.json');cap=read(cp);require(sha(cp)==s['operational_output_cap_sha256'],'cap pin changed')
  out=V/'DTC/run/results'/r['uuid'];pid=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';alive=pid.exists() and live(read(pid));done=V/'control/qualification_ledger'/(c+'.DONE.json');ap=V/'control'/(c+'_ARCHIVE_RECEIPT.json');pp=V/'analysis/postprocess_v2'/(c+'.POSTPROCESS_V2.RESULT.json')
  size=sum(p.stat().st_size for p in out.rglob('*') if p.is_file());verified=False;pins={str(sp):sha(sp),str(cp):sha(cp)}
  if ap.exists():
   require(done.exists() and pp.exists() and not alive,'archive lacks independent closed proof')
   rr=read(pp);proof=P(rr['proof_path']);receipt=rr['archive']['receipt']
   require(rr['cohort']==c and rr['uuid']==r['uuid'] and rr['consumer_sha256']==CONSUMER,'V2 identity/consumer mismatch')
   require(P(rr['DONE_path'])==done and rr['DONE_sha256']==sha(done) and rr['proof_sha256']==sha(proof),'V2 DONE/proof hash mismatch')
   dd=read(done);require(dd['cohort']==c and dd['uuid']==r['uuid'],'DONE identity mismatch')
   require(rr['state'] in ['PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE','FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY'],'V2 terminal state not qualified')
   pb=read(proof);require(pb['cohort']==c and pb['uuid']==r['uuid'],'proof identity mismatch')
   require(rr['model_starts']==rr['model_retries']==0 and rr['registered_R14_result_preserved'] is True,'V2 not independent')
   require(receipt['cohort']==c and receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and rr['archive']['independently_verified_restored_entries']>0,'archive restore proof absent')
   ar=read(ap);require(ar==receipt or ar.get('receipt')==receipt,'archive receipt exact mismatch')
   pins.update({str(p):sha(p) for p in [done,ap,pp,proof]});verified=True
  rows.append(dict(cohort=c,uuid=r['uuid'],closed=done.exists(),model_live=alive,archived_verified=verified,cap_bytes=cap['effective_result_cap_bytes'],frozen_cap_bytes=s['limits']['max_result_directory_bytes'],size_bytes=size,pins=pins))
 return rows
def ceiling(q,cs,rows):
 require(q['budget']==23 and q['remaining']==0 and len(q['consumed'])==23,'R1 not exact fully spent 23')
 require(set(cs)<=set(q['consumed']),'R1 has unspent claims')
 require(len(rows)==23 and {r['cohort'] for r in rows}==set(q['consumed']),'R1 rows incomplete')
 total=G
 for r in rows:
  require(r['uuid']==q['consumed'][r['cohort']]['uuid'],'row UUID mismatch')
  require(0<r['cap_bytes']<=r['frozen_cap_bytes'] and r['size_bytes']>=0,'unsafe cap')
  if r['archived_verified']:require(r['closed'] and not r['model_live'],'archived live/unclosed');continue
  total+=max(2*r['cap_bytes'],r['size_bytes']+16*M)
 return ((total+ROUND-1)//ROUND)*ROUND
def build_plan(reg,epoch,rb,eb,oc,rc,rows):
 require(epoch['native_registry_sha256']==digest(rb),'registry epoch mismatch')
 oq=reg['registered_future_requests'][ORIGINAL];q=reg['registered_future_requests'][R1]
 require('operational_repair_admission_barrier' not in oq,'barrier already exists; no repeat/rollback')
 require(not q.get('operational_write_reservation_release_history'),'R1 ceiling already reconciled; no repeat')
 require(set(oc)<=set(oq['consumed']),'original has unspent claims')
 require(set(oq.get('sealed',[]))<=set(oq['admitted_specs']),'unknown original sealed member')
 target=ceiling(q,rc,rows)
 closed=str(q.get('state','')).startswith('CLOSED')
 require(not closed or all(x['archived_verified'] for x in rows),'CLOSED without full independent archives')
 # A closed consumer owns zero reservation; do not resurrect its floor or state.
 new=q['reserved_write_bytes'] if closed else target
 require(closed or 0<=new<=q['reserved_write_bytes'],'ceiling would rise')
 added=sorted(set(oq['admitted_specs'])-set(oq['consumed'])-set(oq.get('sealed',[])))
 return dict(schema='R1_RECONCILIATION_AND_ORIGINAL_BARRIER_PLAN_V1',tool_sha256=sha(__file__),authority_writer_sha256=sha(T/'tools/sweep_native_cap1m.py'),observed_utc=now(),registry_sha256=digest(rb),epoch_sha256=digest(eb),original_q_sha256=digest(q_span(rb,ORIGINAL)),r1_q_sha256=digest(q_span(rb,R1)),original_prefix_sha256=prefix(oq),r1_prefix_sha256=prefix(q),original_claims=oc,r1_claims=rc,original_sealed=copy.deepcopy(oq.get('sealed',[])),added_cells=added,old_reserved_write_bytes=q['reserved_write_bytes'],new_reserved_write_bytes=new,r1_closed_noop=closed,formula='ceil64MiB(1GiB + SUM unarchived max(2*effective_output_cap, native_size+16MiB)); CLOSED no-op',rows=rows,scientific_models_started=0,signals=0,authority_changes=0)
def mutate(reg,plan,plan_sha):
 before=copy.deepcopy(reg);oq=reg['registered_future_requests'][ORIGINAL];q=reg['registered_future_requests'][R1]
 require(prefix(oq)==plan['original_prefix_sha256'] and prefix(q)==plan['r1_prefix_sha256'],'prefix changed')
 require('operational_repair_admission_barrier' not in oq and not q.get('operational_write_reservation_release_history'),'one shot already applied')
 require(not(set(plan['added_cells'])&set(oq['consumed'])),'cannot seal old live/spent cohorts')
 oq['sealed']=sorted(set(plan['original_sealed'])|set(plan['added_cells']))
 oq['operational_repair_admission_barrier']=dict(status=STATUS,utc=now(),plan_sha256=plan_sha,tool_sha256=plan['tool_sha256'],original_sealed=plan['original_sealed'],added_cells=plan['added_cells'],prior_registry_sha256=plan['registry_sha256'],prior_epoch_sha256=plan['epoch_sha256'],prior_original_q_sha256=plan['original_q_sha256'],source_authorization='User: all failure repairs; 5GiB + known future writes; no scientific count changes',release_requires='R16 locked activation exact added_cells; preserve original HOLD and consumed')
 if not plan['r1_closed_noop']:
  require(not str(q.get('state','')).startswith('CLOSED'),'consumer closed concurrently')
  q['reserved_write_bytes']=plan['new_reserved_write_bytes'];q.setdefault('operational_write_reservation_release_history',[]).append(dict(utc=now(),plan_sha256=plan_sha,tool_sha256=plan['tool_sha256'],old_bytes=plan['old_reserved_write_bytes'],new_bytes=plan['new_reserved_write_bytes'],formula=plan['formula'],prior_registry_sha256=plan['registry_sha256'],prior_r1_q_sha256=plan['r1_q_sha256'],remaining=0,consumed=23))
 expected=copy.deepcopy(before)
 for key in ['sealed','operational_repair_admission_barrier']:expected['registered_future_requests'][ORIGINAL][key]=copy.deepcopy(oq[key])
 if not plan['r1_closed_noop']:
  for key in ['reserved_write_bytes','operational_write_reservation_release_history']:expected['registered_future_requests'][R1][key]=copy.deepcopy(q[key])
 require(reg==expected,'mutation escaped operational whitelist')
 require({k:{f:v for f,v in x.items() if f in ['budget','remaining','consumed']} for k,x in reg['registered_future_requests'].items()}=={k:{f:v for f,v in x.items() if f in ['budget','remaining','consumed']} for k,x in before['registered_future_requests'].items()},'scientific budget or consumed changed')
def release_barrier(q,expected_barrier_sha256,controller_sha256,publication_commit):
 """Pure helper for R16 callback; no I/O, budget or consumed modifications."""
 b=q['operational_repair_admission_barrier'];require(digest(canonical(b))==expected_barrier_sha256,'barrier hash mismatch')
 require(b['status']==STATUS,'barrier not paused / already released')
 require(set(q['sealed'])==set(b['original_sealed'])|set(b['added_cells']),'sealed set drifted')
 require(not set(b['added_cells'])&set(q['consumed']),'paused member was consumed')
 require(len(controller_sha256)==64 and publication_commit,'release publication binding absent')
 q['sealed']=copy.deepcopy(b['original_sealed']);b.update(status='RELEASED_BY_QUALIFIED_R16_ACTIVATION',released_utc=now(),release_controller_sha256=controller_sha256,release_publication_commit=publication_commit)
def locked_snapshot():
 rp=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=N/'control/CURRENT_SCIENCE_EPOCH.json';rb=rp.read_bytes();eb=ep.read_bytes();reg=json.loads(rb);e=json.loads(eb);oc=claims(T);rc=claims(V);rows=gather_rows(reg['registered_future_requests'][R1]);plan=build_plan(reg,e,rb,eb,oc,rc,rows)
 require(claims(T)==oc and claims(V)==rc,'claims changed during snapshot')
 return reg,plan,rb,eb
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--plan',type=P,required=True);ap.add_argument('--output-root',type=P,default=F/'ops/admission_barrier_v1');a=ap.parse_args()
 if not a.apply:
  with (N/'control/science_authority/REGISTRY_UPDATE.lock').open('rb') as lock:
   fcntl.flock(lock,fcntl.LOCK_SH);reg,plan,rb,eb=locked_snapshot()
  exclusive(a.plan,json_bytes(plan));print(json.dumps(dict(status='READ_ONLY_PLAN_NO_AUTHORITY_CHANGE',plan=str(a.plan),sha256=sha(a.plan),new_reserved_write_bytes=plan['new_reserved_write_bytes'],added_cells=len(plan['added_cells']))));return
 plan=read(a.plan);plan_sha=sha(a.plan);require(plan['tool_sha256']==sha(__file__),'tool changed since plan');require(plan['authority_writer_sha256']==sha(T/'tools/sweep_native_cap1m.py'),'original authority writer changed')
 # The original writer owns the EX lock and exact registry/epoch fsync protocol.
 spec=importlib.util.spec_from_file_location('barrier_original_authority',T/'tools/sweep_native_cap1m.py');n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
 def transaction(reg):
  current,fresh,rb,eb=locked_snapshot();require(current==reg,'authority changed inside original writer lock')
  for key in ['registry_sha256','epoch_sha256','original_q_sha256','r1_q_sha256','original_prefix_sha256','r1_prefix_sha256','original_claims','r1_claims','original_sealed','added_cells','old_reserved_write_bytes','r1_closed_noop']:
   require(fresh[key]==plan[key],'plan drift: '+key)
  require(fresh['new_reserved_write_bytes']<=plan['new_reserved_write_bytes'],'write bound grew; regenerate plan')
  # Archive progress after the read-only plan can only reduce demand. Retain
  # its conservative plan upper ceiling, never retrospectively raise it.
  dest=a.output_root/plan_sha;require(not dest.exists(),'apply preimages already exist; inspect prior transaction, no repeat')
  for name,body in [('registry.before.json',rb),('epoch.before.json',eb),('original_q.before.json',q_span(rb,ORIGINAL)),('r1_q.before.json',q_span(rb,R1)),('plan.json',a.plan.read_bytes()),('locked_revalidation.json',json_bytes(fresh))]:exclusive(dest/name,body)
  require(claims(T)==fresh['original_claims'] and claims(V)==fresh['r1_claims'],'claims changed before mutation')
  mutate(reg,plan,plan_sha)
 n.update_authority(transaction)
 # Postcondition readback uses the same original locked reader.
 reg,e=n.read_current_authority();b=reg['registered_future_requests'][ORIGINAL]['operational_repair_admission_barrier'];require(b['plan_sha256']==plan_sha and b['status']==STATUS,'apply readback mismatch')
 receipt=dict(status='APPLIED_OPERATIONAL_METADATA_ONLY',plan_sha256=plan_sha,tool_sha256=sha(__file__),registry_sha256=sha(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'),barrier_sha256=digest(canonical(b)),scientific_models_started=0,signals=0)
 exclusive(a.output_root/plan_sha/'APPLY_RECEIPT.json',json_bytes(receipt));print(json.dumps(receipt))
if __name__=='__main__':main()
