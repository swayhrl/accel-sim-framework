import pathlib,json,subprocess,time
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
ids=['C8_SDK42_VECTOR_SIZE4000000_A001','C8_SDK42_VECTOR_SIZE6000000_A001'];rows=[];deadline=time.time()+7200
for ident in ids:
 assert time.time()<deadline
 dest=C.parent/'derived_prepared_v1'/(ident+'_CTA_STRIDE_40_V1')
 with(C/(ident+'_DERIVE_C8_TWO_V1.log')).open('x')as f:p=subprocess.run(['python3','-B',str(C/'derive_complete_cta_v2.py'),str(B/'objects'/ident),str(dest)],stdout=f,stderr=subprocess.STDOUT,timeout=3600)
 assert p.returncode==0
 with(C/(ident+'_PUBLISH_C8_TWO_V1.log')).open('x')as f:p=subprocess.run(['python3','-B',str(C/'publish_one_derived_v1.py'),str(dest)],stdout=f,stderr=subprocess.STDOUT,timeout=3600)
 assert p.returncode==0
 rows.append({'parent_asset_id':ident,'derived':dest.name,'status':'COMMITTED_VERIFIED','source_KEEP':True})
 tmp=C/'DERIVED_C8_TWO_VECTOR_BATCH_V1.json.tmp';tmp.write_text(json.dumps({'pid':__import__('os').getpid(),'deadline':deadline,'rows':rows},indent=2)+'\n');__import__('os').replace(tmp,C/'DERIVED_C8_TWO_VECTOR_BATCH_V1.json')
