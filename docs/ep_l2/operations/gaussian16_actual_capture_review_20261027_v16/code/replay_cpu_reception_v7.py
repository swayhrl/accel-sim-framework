"""Fixed CPU derivation of already-captured a004. No GPU, service, lease, or grant."""
import pathlib,sys,json,hashlib,subprocess,os,resource,argparse,time
D=pathlib.Path(__file__).resolve().parent
R=D.parent/'gaussian16_inner_manifest_closure_repair_20261027_v6/runtime'
SOURCE=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/gaussian16_inner_manifest_closure_repair_20261027_v6/runtime/runtime/gaussian16_actual_20261027_a004')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def need(v,m):
 if not v:raise RuntimeError(m)
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def save(p,x):
 with p.open('x')as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def closure():
 read=lambda n:json.loads((SOURCE/n).read_text())
 prop=read('REMOTE_CLOSED_PROPOSAL.json');ack=read('NATIVE_CLEANUP_ACK.json');cons=read('REMOTE_ACK_CONSUMED.json');witness=read('REMOTE_CONSUMED_WITNESS.json');released=read('NATIVE_RELEASED.json')
 rootsha=sha(SOURCE/'ROOT_AUTHORITY_RAW.json')
 need(prop['Root_sha256']==rootsha and prop['unknown_owned_state']is False and prop['owned_descendants']==[]and prop['guard_closed_sha256']==sha(SOURCE/'GUARD_CLOSED.json'),'original remote exact closed proposal')
 need(ack['Root_sha256']==cons['Root_sha256']==witness['Root_sha256']==released['Root_sha256']==rootsha,'original Root across cleanup chain')
 need(ack['proposal_sha256']==cons['proposal_sha256']==witness['proposal_sha256']==released['proposal_sha256']==sha(SOURCE/'REMOTE_CLOSED_PROPOSAL.json'),'exact same closed proposal')
 need(cons['ACK_sha256']==released['ACK_sha256']==sha(SOURCE/'NATIVE_CLEANUP_ACK.json'),'one exact Native ACK')
 need(witness['consumed_sha256']==sha(SOURCE/'REMOTE_ACK_CONSUMED.json')and witness['leases_closed']is True and witness['owned_descendants']==[]and released['consumed_witness_sha256']==sha(SOURCE/'REMOTE_CONSUMED_WITNESS.json'),'independent remote closure witness before release')
 need(released['status']=='FOUR_LEASES_RELEASED_AFTER_EXACT_REMOTE_CLOSURE'and read('REMOTE_ENTRY_TERMINAL.json')['status']=='OWNED_CLOSED_ONCE_ACKED_NATIVE_RELEASED'and read('NATIVE_ENTRY_TERMINAL.json')['status']=='CLOSED','both original entries terminated normally')
 names=['REMOTE_CLOSED_PROPOSAL.json','GUARD_CLOSED.json','NATIVE_CLEANUP_ACK.json','REMOTE_ACK_CONSUMED.json','REMOTE_CONSUMED_WITNESS.json','NATIVE_RELEASED.json','REMOTE_ENTRY_TERMINAL.json','NATIVE_ENTRY_TERMINAL.json']
 return dict(status='ORIGINAL_CAPTURE_WINDOW_OWNED_CLOSED',refs=[ref(SOURCE/n)for n in names],fresh_absence_evidence_ref=ref(D/'FRESH_OWNED_ABSENCE_V7.json'),Root_did_not_reap_nonchild_processes=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--destination',required=True);p.add_argument('--code-manifest-sha',required=True);a=p.parse_args()
 need(sha(D/'CPU_CODE_MANIFEST_V7.json')==a.code_manifest_sha,'independent Root code manifest pin')
 for row in json.loads((D/'CPU_CODE_MANIFEST_V7.json').read_text())['files']:
  path=D/row['relative'];need(path.stat().st_size==row['bytes']and sha(path)==row['sha256'],'exact CPU component bytes')
 out=pathlib.Path(a.destination);need(out.is_absolute()and not out.exists()and '..'not in out.parts,'new private destination only')
 need(out.resolve().is_relative_to(D.parent.resolve()),'private NAS receipt scope only')
 for q in [out,*out.parents]:need(not q.is_symlink(),'no destination alias')
 os.nice(15);os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2]);resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));out.mkdir()
 root=out/'gaussian16_actual_20261027_a004';root.mkdir();copies=json.loads((D/'SOURCE_AND_DERIVATION_COPY_RECEIPT_V7.json').read_text())['refs']
 for row in copies:
  src=pathlib.Path(row['source']);need(src.is_relative_to(SOURCE)and not src.is_symlink(),'fixed captured source only');raw=src.read_bytes();need(len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'],'captured bytes unchanged')
  target=root/src.relative_to(SOURCE);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 mapfile=R/'gaussian/semantic-map.tsv';need(sha(mapfile)=='09a8918db2494e8a498fdafb84125a79bfde9ea7c871315220dd72ae38b9099b','exact static map CPU context')
 (root/'traces/semantic-map.tsv').write_bytes(mapfile.read_bytes())
 argv=['/usr/bin/python3','-B',str(R/'gaussian/full_reader.py'),'--traces',str(root/'traces'),'--reader',str(D/'build/reader'),'--out',str(root/'FULL_READER_V7.json')]
 with(out/'READER.stdout').open('xb')as f,(out/'READER.stderr').open('xb')as e:r=subprocess.run(argv,stdout=f,stderr=e,stdin=subprocess.DEVNULL,timeout=120)
 need(r.returncode==0,'actual30 grouped CPU reader')
 sys.path[:0]=[str(D/'cpu_components'),str(R)]
 import gaussian_receive_v7 as G
 scientific=G.receive(root,json.loads((root/'FULL_READER_V7.json').read_text()));save(root/'SCIENTIFIC_RECEIVER_V7.json',scientific)
 import capture_control_receive_v7 as C
 scope=json.loads((SOURCE/'CPU_STATIC_SCOPE.json').read_text());control=C.verify(SOURCE,sha(SOURCE/'CPU_STATIC_SCOPE.json'),scope['code_sha256'])
 from receiver_activity_join_v9 import verify as activity
 for name in ['BRIDGE_LAST_ACTIVITY.json','BRIDGE_POST_ACTIVITY.json']:activity(json.loads((SOURCE/name).read_text()),scope)
 for idle in json.loads((SOURCE/'READY.json').read_text())['idle']:activity(idle['activity'],scope)
 start=json.loads((SOURCE/'LEAF_PROCESS_START.json').read_text());worker=json.loads((SOURCE/'WORKER_START.json').read_text())
 for line in(SOURCE/'ACTIVITY_SAMPLES.jsonl').read_text().splitlines():activity(json.loads(line),scope,start['proof'],worker)
 save(root/'CAPTURE_CONTROL_RECEIVER_V7.json',control)
 closed=closure();save(root/'ORIGINAL_WINDOW_CLOSURE_JOIN_V7.json',closed)
 receipt=dict(schema='PRIVATE_GAUSSIAN16_A004_CPU_POST_DERIVATION_RECEIVER_V7',status='PRIVATE_EXACT_INPUT_CAPTURE_AND_CPU_DERIVATION_CANDIDATE_PASS',source_run=str(SOURCE),source_root_authority_ref=ref(SOURCE/'ROOT_AUTHORITY_RAW.json'),original_post_failed_retained=True,original_APP_STARTED_false_is_known_post_completion_marker_bug=True,WORKER_COMPLETE_fabricated=False,actual_capture_proof_ref=ref(SOURCE/'EXECUTION.json'),scientific=scientific,control=control,closure=closed,exact_observed_launch_configuration=dict(Fan1=dict(grid=[1,1,1],block=[128,1,1]),Fan2=dict(grid=[1,1,1],block=[16,16,1]),basis='actual binary stdout + 30 raw headers + 12column stats + independent device EXIT + exact frozen source configurable macros'),derived_refs=[ref(root/n)for n in ['FULL_READER_V7.json','SCIENTIFIC_RECEIVER_V7.json','CAPTURE_CONTROL_RECEIVER_V7.json','ORIGINAL_WINDOW_CLOSURE_JOIN_V7.json']],Source_KEEP=True,no_GPU_recapture=True,generic_CALL_RET_qualification=False,public_catalog_qualified=False,consumer_qualified=False,timing_qualified=False,science_qualified=False,Root_independent_acceptance_required=True)
 save(out/'CPU_DERIVATION_RECEIVER_V7.json',receipt)
 print(json.dumps(dict(status=receipt['status'],output=str(out/'CPU_DERIVATION_RECEIVER_V7.json'),sha256=sha(out/'CPU_DERIVATION_RECEIVER_V7.json'))))
if __name__=='__main__':main()
