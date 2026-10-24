#!/usr/bin/env python3
"""Conservative logical identity. Physical executable equality is a separate alias."""
import json,hashlib
def physical(t):
 return hashlib.sha256(json.dumps([t.get('binary_sha256'),t.get('argv',[])[1:]],sort_keys=True).encode()).hexdigest()
def identity(t):
 source=t.get('source_files',t.get('sources',[]))
 if not source and t.get('source'):source=[{'path':t['source'],'sha256':t.get('source_sha256')}]
 inp=t.get('input_files',t.get('input_identity'))
 runtime=t.get('runtime_links',[])
 env=dict(t.get('env',{}));env.update(t.get('runtime_env',{}))
 o={'schema':'SCIENTIFIC_EXECUTION_IDENTITY_V2','suite':t.get('suite'),'source_version':t.get('version',t.get('source_version')),'source_head':t.get('source_head'),'program':t.get('program'),'implementation_variant':t.get('variant'),'source_files':source,'binary_sha256':t.get('binary_sha256'),'argv':t.get('argv'),'declared_working_directory':t.get('cwd',t.get('sample_path')),'working_directory_policy':t.get('cwd_policy','ABSENT private attempt'),'runtime_overlay':runtime,'declared_inputs':inp,'input_role_policy':'Manifest input_files are preserved conservatively; reference-only role requires explicit source annotation; no exclusion inferred','reference_output':t.get('golden_output'),'reference_checker':t.get('correctness',{}).get('postcheck_command'),'controlled_environment':env,'common_capture_environment':{'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','CUDA_VISIBLE_DEVICES':'GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59','producer_sha256':'55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73'},'generated_input_rule':t.get('input_identity') if not isinstance(t.get('input_identity'),list) else None,'actual_runtime_bytes_status':'Declared source/file identity only; time-seeded/uninitialized data requires HtoD snapshot proof'}
 return o
def key(t):return hashlib.sha256(json.dumps(identity(t),sort_keys=True,separators=(',',':')).encode()).hexdigest()
