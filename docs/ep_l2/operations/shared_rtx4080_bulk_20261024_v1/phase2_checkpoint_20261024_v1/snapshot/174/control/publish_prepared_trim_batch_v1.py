import pathlib,json,subprocess,time,os
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
deadline=time.time()+12*3600
rows=json.loads((C/'DERIVED_PREPARED_INDEX_V1.json').read_text())['rows'];receipts=[]
for x in rows:
 if time.time()>deadline:break
 source=pathlib.Path(x['path']);ident=json.loads((source/'ASSET.json').read_text())['asset_id']
 if (B/'objects'/ident/'COMMIT.json').exists():receipts.append({'id':ident,'status':'EXISTING_COMMIT_PRESERVED'});continue
 with (C/(ident+'_PUBLISH_V1.log')).open('x') as f:
  cp=subprocess.run(['python3','-B',str(C/'publish_one_derived_v1.py'),str(source)],stdout=f,stderr=subprocess.STDOUT,timeout=8000)
 receipts.append({'id':ident,'exit':cp.returncode,'status':'COMMITTED_VERIFIED' if cp.returncode==0 else 'FAILED_RETAINED'})
 tmp=C/'DERIVED_BATCH_PUBLISH_V1.json.tmp';tmp.write_text(json.dumps({'pid':os.getpid(),'deadline_unix':deadline,'rows':receipts},indent=2)+'\n');os.replace(tmp,C/'DERIVED_BATCH_PUBLISH_V1.json')
