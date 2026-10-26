#!/usr/bin/env python3
"""Tiny CPU-only fixture adapter, synthetic IDs exclusively."""
import pathlib,json,sys,hashlib,time,os
wall=time.time();cpu=time.process_time()
def canon(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def ref(p):
 p=pathlib.Path(p);b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
ctxpath=pathlib.Path(sys.argv[1]);ctx=json.loads(ctxpath.read_text());scopepath=pathlib.Path(ctx['scope_path']);scope=json.loads(scopepath.read_text());row=scope['rows'][ctx['row_index']]
assert row['queue_id'].startswith('SYNTHETIC_AUDIT_') and row['queue_id']==ctx['queue_id']
jobpath=pathlib.Path(row['job_snapshot_path']);job=json.loads(jobpath.read_text());assert job['task']['binary_sha256']==row['binary_sha256'] and job['task']['argv']==row['argv']
refs=[ref(ctxpath),ref(scopepath),ref(jobpath)]
binding={'queue_id':row['queue_id'],'job_sha256':row['job_sha256'],'binary_sha256':row['binary_sha256'],'declared_identity_sha256':row['declared_identity_sha256'],'argv_sha256':canon(row['argv'])}
result={'schema':'AUTO161_ADAPTER_RESULT_V1','adapter_id':ctx['adapter_id'],'adapter_profile':ctx['adapter_profile'],'profile':ctx['adapter_profile'],'attempt_id':ctx['attempt_id'],'nonce':ctx['nonce'],'queue_id':row['queue_id'],'row_index':ctx['row_index'],'scope_sha256':ctx['scope_sha256'],'frozen_row_sha256':ctx['frozen_row_sha256'],'stage':'METADATA_IDENTITY_STATIC','status':'HOLD','stage_execution_complete':True,'checks':[{'name':x,'passed':True} for x in ['scope_raw_sha','exact_synthetic_row','CPU_metadata_read']],'inputs':refs,'evidence':[],'missing_proofs':[{'proof_id':'SYNTHETIC_NO_TRACE','binding':binding,'required_evidence':['Independent Root-admitted real GPU evidence would be required for a real workload'],'satisfied':False,'next_adapter_id':'fixture_future_not_launched','next_adapter_ABI':'AUTO161_ARTIFACT_V1'}],'family_keys':['SYNTHETIC_ONLY'],'next_stage':'WAIT_ISA_ADAPTER','qualification_granted':False,'historical_queue_mutated':False,'gpu_executed':False,'simulation_executed':False,'historical_actual_input_equality_granted':False,'actual_GPU_producer_profile_inferred_from_legacy55':False,'execution_evidence':{'pid':os.getpid(),'started_unix':wall,'ended_unix':time.time(),'cpu_seconds':time.process_time()-cpu,'actual_distinct_file_reads':len(refs),'actual_metadata_bytes_read':sum(x['bytes'] for x in refs),'operations':['CPU_read_scope','CPU_read_context','exact_SHA_and_row_join']}}
pathlib.Path(ctx['output_path']).write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
