from pathlib import Path
import sys,json,time,subprocess,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy as e
name=sys.argv[1];batches=json.loads((R/'control'/name).read_text());log=R/'logs'/('transfer_'+Path(name).stem+'.jsonl')
for i,b in enumerate(batches):
 receipt=R/'control'/('BATCH_'+b['id']+'.json')
 if receipt.exists():continue
 manifest=Path(b['manifest']);assert hashlib.sha256(manifest.read_bytes()).hexdigest()==b['sha256']
 state={'stage':'TRANSFER','batch_list':name,'ordinal':i+1,'total':len(batches),'batch':b,'observed_unix':time.time()}
 (R/'control/TRANSFER_PROGRESS.json').write_text(json.dumps(state)+'\n')
 # Engine is a finite single sender/receiver transaction; all progress events
 # are kept in the native journal and no second receiver is started.
 with log.open('a') as out:
  cp=subprocess.run(['python3','-B',str(R/'tools/library_copy.py'),'migrate',str(manifest)],stdout=out,stderr=out)
 if cp.returncode:raise RuntimeError('batch held; inspect '+str(log))
 m=json.loads(manifest.read_text());bundle=Path(m['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1));proof=e.verify_committed(bundle)
 receipt.write_text(json.dumps({'status':'PASS_COMMITTED_BATCH','batch':b,'proof':proof},indent=2)+'\n')
 print(json.dumps({'batch_done':i+1,'total':len(batches),'id':b['id'],'bytes':b['bytes']}),flush=True)
(R/'control'/(Path(name).stem+'_TRANSFER_COMPLETE.json')).write_text(json.dumps({'status':'PASS','batches':len(batches)})+'\n')
