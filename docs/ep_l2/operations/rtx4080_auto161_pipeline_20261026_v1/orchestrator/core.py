"""Exact161 private CPU orchestration shared validation. No import-time execution."""
import pathlib,json,hashlib,os,time,stat
N=pathlib.Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1')
D=N/'auto161_pipeline_20261026_v1/orchestrator'
SCOPE=N/'root/UNIFIED_EXACT161_RESEARCH_TODO_V1.json'
SCOPE_SHA='b48a9007274459184c332b77f10784c1fbb8b1c1df213543c65d18a4d8e5327a'
ROOT_ACCEPT=N/'auto161_pipeline_20261026_v1/root/ROOT_SCOPE_AND_ACCEPTANCE_V1.json'
ROOT_ACCEPT_SHA='71189b911b93201e043f6a5eeb32a62b2db16d1be3beb125bf515f2fcbe84881'
STAGE='METADATA_IDENTITY_STATIC'
WAIT={'WAIT_EXISTING_AVAILABILITY_REVIEW','WAIT_ISA_ADAPTER','WAIT_ACTUAL_INPUT_ADAPTER','WAIT_MAPPING_ADAPTER','WAIT_SOURCE_RUNTIME_ADAPTER','WAIT_ROOT_GPU_EXACT','WAIT_ROOT_GPU_VARIANT','WAIT_ROOT_GPU_SDK_ARMED','WAIT_CONSUMER_QUALIFICATION'}
ROUTES={'READONLY_EXISTING_WORKLOAD_AVAILABILITY_ROUTE_REVIEW_NO_HISTORICAL_ALIAS':'WAIT_EXISTING_AVAILABILITY_REVIEW','ISA_PROFILE_SPECIALIST_PREPARATION_REQUIRED':'WAIT_ISA_ADAPTER','ACTUAL_INPUT_LIFETIME_SNAPSHOT_PREPARATION_REQUIRED':'WAIT_ACTUAL_INPUT_ADAPTER','MAPPING_PROOF_HOLD':'WAIT_MAPPING_ADAPTER','SDK42_DEFAULT50000_MICROWINDOW_ARMED_NOT_EXECUTED':'WAIT_ROOT_GPU_SDK_ARMED','EXACT_RUNTIME_OR_STATIC_EVIDENCE_REVIEW_REQUIRED':'WAIT_SOURCE_RUNTIME_ADAPTER','SOURCE_INPUT_ORACLE_AND_GPU_ADMISSION_REVIEW_REQUIRED':'WAIT_SOURCE_RUNTIME_ADAPTER','ROOT_GPU_PILOT_REQUIRED_EXACT_SOURCE_BINARY':'WAIT_ROOT_GPU_EXACT','SEPARATE_REPAIRED_VARIANT_GPU_REQUIRED_NO_V3_SUPERSESSION':'WAIT_ROOT_GPU_VARIANT'}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def canon(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def rawsha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_bytes())
def save(p,o,exclusive=False):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);body=canon(o)+b'\n'
 if exclusive:
  with p.open('xb')as f:f.write(body);f.flush();os.fsync(f.fileno())
 else:
  tmp=p.with_name(p.name+'.writing')
  with tmp.open('wb')as f:f.write(body);f.flush();os.fsync(f.fileno())
  os.replace(tmp,p)
def secure_file(p,root=N,max_bytes=16*1024**2):
 p=pathlib.Path(p);root=pathlib.Path(root)
 need(p.is_absolute() and '..'not in p.parts,'absolute safe evidence path required')
 need(p==root or root in p.parents,'evidence outside private specialist root')
 for q in [p,*p.parents]:
  if q==root.parent:break
  need(not q.is_symlink(),'symlink evidence path')
 s=p.stat();need(stat.S_ISREG(s.st_mode)and 0<=s.st_size<=max_bytes,'evidence type/size')
 return p
def file_ref(p,root=N):
 p=secure_file(p,root);return {'path':str(p),'sha256':rawsha(p),'bytes':p.stat().st_size}
def verify_ref(ref,root=N):
 need(isinstance(ref,dict)and set(['path','sha256','bytes'])<=set(ref),'malformed file_ref')
 need(type(ref['bytes'])is int and ref['bytes']>=0,'file_ref bytes type')
 need(isinstance(ref['sha256'],str)and len(ref['sha256'])==64 and all(x in '0123456789abcdef'for x in ref['sha256']),'file_ref digest')
 p=secure_file(ref['path'],root);need(p.stat().st_size==ref['bytes']and rawsha(p)==ref['sha256'],'file_ref current bytes/SHA mismatch');return p
def identity(pid):
 try:
  s=pathlib.Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()
  return {'pid':int(pid),'start_ticks':int(s[19]),'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'state':s[0],'parent_pid':int(s[1])}
 except (FileNotFoundError,ProcessLookupError):return None
def live(proof):
 q=identity(proof['pid'])
 return q is not None and q['state']not in ['Z','X']and all(q[k]==proof[k]for k in ['pid','start_ticks','boot_id'])
def admission(row,index,scope_sha=SCOPE_SHA):
 o={'schema':'AUTO161_ADMISSION_V1','queue_id':row['queue_id'],'row_index':index,'scope_sha256':scope_sha,'frozen_row_sha256':digest(row)}
 return dict(o,admission_sha256=digest(o))
def load_scope(path=SCOPE,sha=SCOPE_SHA,count=161):
 need(rawsha(path)==sha,'frozen scope changed');o=load(path);rows=o['rows'];need(len(rows)==count,'scope count');need(len({r['queue_id']for r in rows})==count,'duplicate admission')
 for r in rows:need(r['next_step']in ROUTES,'unknown route')
 return rows
def check_result(result,ctx,context_ref,root=N):
 need(isinstance(result,dict),'result object')
 expected={'schema':'AUTO161_ADAPTER_RESULT_V1','queue_id':ctx['queue_id'],'row_index':ctx['row_index'],'scope_sha256':ctx['scope_sha256'],'frozen_row_sha256':ctx['frozen_row_sha256'],'stage':STAGE,'attempt_id':ctx['attempt_id'],'nonce':ctx['nonce'],'adapter_id':ctx['adapter_id']}
 for k,v in expected.items():need(result.get(k)==v,'result binding '+k)
 need(result.get('adapter_profile')==ctx['adapter_profile'],'adapter profile mismatch')
 need(result.get('status')in ['PASS','HOLD'],'unknown result status')
 need(result.get('stage_execution_complete')is True,'gate not executed')
 for k in ['qualification_granted','historical_queue_mutated','gpu_executed','simulation_executed']:need(result.get(k)is False,'forbidden result claim '+k)
 need(result.get('next_stage')in WAIT,'forbidden next stage')
 checks=result.get('checks');need(isinstance(checks,list)and len(checks)>=3,'insufficient executed checks')
 for c in checks:need(isinstance(c,dict)and isinstance(c.get('name'),str)and type(c.get('passed'))is bool,'check schema')
 refs=result.get('inputs',[])+result.get('evidence',[]);need(2<=len(refs)<=64,'evidence count')
 for ref in refs:verify_ref(ref,root)
 need(any(r==context_ref for r in refs),'context not reopened and bound')
 need(any(r['path']==str(ctx['scope_path'])and r['sha256']==ctx['scope_sha256']for r in refs),'scope ref missing')
 need(all(c['passed']for c in checks),'metadata binding failure cannot be hidden by HOLD')
 need(len({x['name']for x in checks})==len(checks),'duplicate check names')
 need(isinstance(result.get('missing_proofs'),list)and isinstance(result.get('family_keys'),list),'gaps/family schema')
 for dep in ctx.get('dependency_artifacts',[]):need(any(dep==r for r in refs),'dependency not reopened by worker')
 return True
