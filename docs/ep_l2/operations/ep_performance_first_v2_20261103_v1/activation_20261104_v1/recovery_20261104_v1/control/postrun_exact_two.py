from pathlib import Path
import argparse,json,hashlib,subprocess,os,datetime
C=Path(__file__).resolve().parent
REG=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
GLOBAL=Path('/root/data/ep_l2_dtc_l1_native_v2/bin/native')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def exact(r):assert sha(r['path'])==r['sha256'],'immutable evidence drift';return read(r['path'])
def live(pid,ticks):
 try:z=(Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split();return int(z[19])==ticks and z[0]not in ['Z','X']
 except FileNotFoundError:return False

def check(case):
 permit=read(C/'MAIN_EXACT_TWO_POSTRUN_QUALIFICATION.json');assert permit['status']=='MAIN_QUALIFIED_EXACT_TWO_SEALED_RESULTS_POSTRUN_ONLY';assert permit['code_sha256']==sha(__file__)
 assert case in permit['cases'],'outside exact two consumed cases';p=permit['cases'][case]
 assert sha(GLOBAL)==permit['qualified_current_global_sha256'],'current global change needs review'
 h=exact(permit['idle_stop_ref']);assert not live(h['prior_process']['pid'],h['prior_process']['start_ticks']),'old controller generation alive'
 q=read(REG)['registered_future_requests'][p['request_id']];row=q['consumed'][case]
 assert row['state']=='NATURAL_COMPLETE_PENDING_VALIDATION','only sealed pending result; no replay'
 assert row['uuid']==p['uuid'] and row['done_ref']==p['done_ref'] and row['intent_ref']==p['intent_ref']
 assert q['admitted_specs'][case]==p['spec_ref']['sha256'];s=exact(p['spec_ref']);done=exact(p['done_ref']);intent=exact(p['intent_ref'])
 assert s['source_identity']==done['source_identity']==intent['source_identity']==p['source_identity']
 assert done['launcher_wait_returncode']==0 and done['stop_reason']is None
 assert q['native_entry_ref']==p['native_entry_ref']and sha(p['native_entry_ref']['path'])==p['native_entry_ref']['sha256']
 for z in done['closed_artifact_refs'].values():assert sha(z['path'])==z['sha256']
 pid=read(Path(done['output'])/'NATIVE_SIMULATOR_PID_AND_MAPS.json');assert not live(pid['pid'],pid['start_ticks'])
 return p,q

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--case',required=True);ap.add_argument('--apply',action='store_true');args=ap.parse_args();p,q=check(args.case)
 if not args.apply:print(json.dumps(dict(status='EXACT_SEALED_POSTRUN_QUALIFICATION_PASS_NO_ACCEPT_CALL',case=args.case,model_starts=0)));return
 before=(q['budget'],q['remaining'],len(q['consumed']));cmd=[p['native_entry_ref']['path'],'experiment','accept',args.case,'--project','EP_L2'];r=subprocess.run(cmd,capture_output=True,text=True)
 (C/(args.case+'.native_accept.stdout')).write_text(r.stdout);(C/(args.case+'.native_accept.stderr')).write_text(r.stderr)
 after=read(REG)['registered_future_requests'][p['request_id']];assert before==(after['budget'],after['remaining'],len(after['consumed'])),'postrun must not consume/refund'
 receipt=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),case=args.case,argv=cmd,returncode=r.returncode,state=after['consumed'][args.case]['state'],new_model_starts=0,old_Spec_Source_raw_preserved=True,budget_unchanged=True)
 (C/(args.case+'.postrun_receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));assert r.returncode==0,'native postrun did not close; preserve HOLD'
if __name__=='__main__':main()
