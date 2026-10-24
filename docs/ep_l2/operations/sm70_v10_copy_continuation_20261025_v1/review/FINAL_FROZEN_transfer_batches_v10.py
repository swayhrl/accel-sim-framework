from pathlib import Path
import sys,json,time,subprocess,hashlib,fcntl
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
EXPECTED_ENGINE_V10='7e5b290e330cbc1fcc845b6a9c7ce3487d181677d117a8d77a31c60d12a42521'
assert hashlib.sha256((R/'tools/library_copy_v10.py').read_bytes()).hexdigest()==EXPECTED_ENGINE_V10
sys.path.insert(0,str(R/'tools'));import library_copy_v10 as e
held=(R/'control/TRANSFER_DRIVER.lock').open('a');fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
promotion=json.loads((R/'control/ENGINE_V10_PROMOTION.json').read_text());assert promotion['status']=='PASS_ROOT_APPROVED_COPY_ONLY_V10_AT_CLOSED_BATCH_BOUNDARY'
assert promotion['engine_sha256']==EXPECTED_ENGINE_V10
assert hashlib.sha256(e.SELF_BYTES).hexdigest()==promotion['engine_sha256']
name=sys.argv[1];batches=json.loads((R/'control'/name).read_text());log=R/'logs'/('transfer_'+Path(name).stem+'.jsonl')
for i,b in enumerate(batches):
 receipt=R/'control'/('BATCH_'+b['id']+'.json')
 if receipt.exists():continue
 manifest=Path(b['manifest']);assert hashlib.sha256(manifest.read_bytes()).hexdigest()==b['sha256']
 state={'stage':'TRANSFER','batch_list':name,'ordinal':i+1,'total':len(batches),'batch':b,'observed_unix':time.time(),'selected_engine_sha256':promotion['engine_sha256']}
 (R/'control/TRANSFER_PROGRESS.json').write_text(json.dumps(state)+'\n')
 with log.open('a') as out:
  cp=subprocess.run(['python3','-B',str(e.__file__),'migrate',str(manifest)],stdout=out,stderr=out)
 if cp.returncode:raise RuntimeError('batch held; inspect '+str(log))
 m=json.loads(manifest.read_text());bundle=Path(m['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1));proof=e.verify_committed(bundle)
 actual=hashlib.sha256((bundle/'trace_copy.py').read_bytes()).hexdigest()
 receipt.write_text(json.dumps({'status':'PASS_COMMITTED_BATCH','batch':b,'proof':proof,'selected_engine_sha256':promotion['engine_sha256'],'committed_object_restore_engine_sha256':actual},indent=2)+'\n')
 print(json.dumps({'batch_done':i+1,'total':len(batches),'id':b['id'],'bytes':b['bytes']}),flush=True)
(R/'control'/(Path(name).stem+'_TRANSFER_COMPLETE.json')).write_text(json.dumps({'status':'PASS','batches':len(batches)})+'\n')
