from pathlib import Path
import json,hashlib,subprocess,shlex,copy,datetime,re
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');O=A/'agents/A_structure_config_v1';O.mkdir(parents=True,exist_ok=True)
CORE=Path('/root/data/dtc_failure_repair_20261025_v1/core');COMMIT='9eedb3131937748f0492fa83aad37d3691118d70';AUTH=A/'control/INPUT_AUTHORITY.fixed.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,obj):p=O/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n');return {'path':str(p),'sha256':sha(p)}
assert sha(AUTH)=='0b9cd6dfe3c397e32ce286ef068717ac4dd563b65855dd245a4fceb08fdadfa1';auth=json.loads(AUTH.read_text());variants=auth['first_batch_variants']+auth['other_variants'];assert len(set(variants))==6
baseline=Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/DTC/env/DH_P0');basefiles=sorted(baseline.glob('config-*.config'));assert len(basefiles)==4
D={
 'TAG64x16_PHYS640':{'-gpgpu_dtc_l1_logical_ways':'16'},
 'PHYS768_TAG64x8':{'-gpgpu_dtc_l1_physical_lines':'768'},
 'TAG128x8_PHYS640':{'-gpgpu_dtc_l1_logical_sets':'128'},
 'PHYS1024_TAG64x8':{'-gpgpu_dtc_l1_physical_lines':'1024'},
 'OO_PIB192':{'-gpgpu_dtc_l1_oo_pib_entries':'192'},
 'TAG4BANK_PERBANK2_TOTAL8':{'-gpgpu_dtc_l1_tag_req_per_bank':'2','-gpgpu_dtc_l1_tag_req_per_cycle':'8'}}
# Pure text parsing of supplied options; continuation-aware through shlex, last assignment wins.
def parsefiles(paths):
 t=[]
 for p in paths:t+=shlex.split(Path(p).read_text(),comments=True)
 out={};n=0
 while n<len(t):
  assert t[n].startswith('-'),(n,t[n]);key=t[n];n+=1;vals=[]
  while n<len(t)and not t[n].startswith('-'):vals.append(t[n]);n+=1
  out[key]=[word for val in vals for word in val.split()]
 return out
bp=parsefiles(basefiles); configs=[]
for v in variants:
 d=O/'configs'/v;d.mkdir(parents=True,exist_ok=True);files=[]
 for n,p in enumerate(basefiles):
  b=p.read_bytes()
  if n==3:b+=('\n# Performance-first V1 exact authorized structure delta; planning file only.\n'+''.join(k+' '+val+'\n'for k,val in D[v].items())).encode()
  q=d/p.name;q.write_bytes(b);files.append(q)
 opts=parsefiles(files);actual={k:{'from':bp.get(k),'to':opts[k]}for k in set(bp)|set(opts)if bp.get(k)!=opts.get(k)}
 assert set(actual)==set(D[v]);assert all(actual[k]['to']==[z]for k,z in D[v].items())
 for k in ['-gpgpu_dtc_l1_physical_lines','-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways','-gpgpu_dtc_l1_allocation_width','-gpgpu_dtc_l1_finite_service','-gpgpu_dtc_l1_tag_banks','-gpgpu_clock_domains','-gpgpu_cache:dl2']:
  if k not in D[v]:assert opts[k]==bp[k]
 held=v.startswith('TAG64x16')or v.startswith('TAG128x8');st='CPU_PROGRESS_NEGATIVE_HOLD'if held else'CPU_ONLY_CONFIG_AND_HEADER_QUALIFIED'
 configs.append(dict(variant=v,status=st,model_start_granted_by_this_packet=False,delta=actual,configs=[dict(path=str(p),sha256=sha(p))for p in files],effective_supplied_options=opts,tag_entries=int(opts['-gpgpu_dtc_l1_logical_sets'][0])*int(opts['-gpgpu_dtc_l1_logical_ways'][0]),physical_bytes_per_SM=int(opts['-gpgpu_dtc_l1_physical_lines'][0])*128,active_OO_PIB=int(opts['-gpgpu_dtc_l1_oo_pib_entries'][0]),lower_create_queue_bound=int(opts['-gpgpu_dtc_l1_oo_pib_entries'][0]),tag_banks=4,tag_grant_per_bank=int(opts['-gpgpu_dtc_l1_tag_req_per_bank'][0]),tag_grant_total=int(opts['-gpgpu_dtc_l1_tag_req_per_cycle'][0])))
source_ranges={
 'src/gpgpu-sim/dtc-l1-common.h':[(31,48),(516,556),(571,589),(637,698),(801,862),(1064,1087),(1090,1147)],
 'src/gpgpu-sim/dtc-l1-tag-index.h':[(1,54)],
 'src/gpgpu-sim/shader.cc':[(2745,2756),(3349,3456),(3461,3518),(3597,3659),(4414,4477)],
 'src/gpgpu-sim/shader.h':[(2147,2164),(2429,2437)],
 'src/gpgpu-sim/gpu-sim.cc':[(410,480)]}
sources=[]
for rel,ranges in source_ranges.items():
 p=CORE/rel;b=p.read_bytes();git=subprocess.check_output(['git','-C',str(CORE),'show',COMMIT+':'+rel]);assert b==git,rel;lines=b.decode().splitlines();sources.append(dict(path=str(p),git_path=rel,commit=COMMIT,sha256=sha(p),working_bytes_equal_fixed_git_blob=True,excerpts=[dict(first_line=a,last_line=min(z,len(lines)),text='\n'.join(f'{n}: {lines[n-1]}'for n in range(a,min(z,len(lines))+1)))for a,z in ranges]))
save('SOURCE_EVIDENCE.json',dict(core_commit=COMMIT,sources=sources))
inputs=[];candidates=[];ref_checks=0
for item in auth['inputs']:
 pop=item['population'];refs=item['P0_references'];dh=next(r for r in refs if r['source_cell']=='DH');ch=next(r for r in refs if r['source_cell']=='CH')
 for r in refs:
  assert sha(r['source_RESULT_path'])==r['source_RESULT_sha256'];res=json.loads(Path(r['source_RESULT_path']).read_text());assert res['uuid']==r['source_uuid']and res['cycles']==r['cycles'];assert r['accepted'];alias=r.get('legal_prior_P0_alias');proof=res.get('proof',{})
  if alias:
   assert sha(alias['underlying_RESULT_path'])==alias['underlying_RESULT_sha256'];u=json.loads(Path(alias['underlying_RESULT_path']).read_text());assert u['uuid']==alias['underlying_execution_uuid']==r['source_uuid'];proof=u['proof']
  assert proof['effective_options']==r['effective_options'];ref_checks+=1
 bind=dh['input_binding'];assert sha(bind['path'])==bind['sha256'];b=json.loads(Path(bind['path']).read_text());assert b['input_digest']==pop['input_digest'];entry=Path(b['asset']['trace_entry']);assert entry.is_file();assert sha(entry)==b['asset']['commandlist_sha256'];assert b['qualification']['issues']==[]
 for k,v in bp.items():assert dh['effective_options'][k]==v,(pop['program'],k,dh['effective_options'].get(k),v)
 inputs.append(dict(**pop,input_binding=bind,trace_entry=str(entry),commandlist_sha256=sha(entry),trace_members_prior_frozen_SHA=b['asset']['members'],expected=dh['expected'],capture_scope=b['qualification']['capture_complete_native_input'],native_numerical_correctness=b['qualification']['native_numerical_correctness'],CH_P0=ch,DH_P0=dh))
 for cfg in configs:
  e=copy.deepcopy(dh['effective_options']);e.update({k:[v]for k,v in D[cfg['variant']].items()});diff={k:dict(before=dh['effective_options'].get(k),after=e.get(k))for k in set(e)|set(dh['effective_options'])if e.get(k)!=dh['effective_options'].get(k)};assert set(diff)==set(D[cfg['variant']]);plan='PLAN-PERFFIRST-'+pop['input_digest'][:16]+'-DH-'+cfg['variant'];candidates.append(dict(plan_candidate_id=plan,**pop,variant=cfg['variant'],status=cfg['status'],registered=False,native_UUID=None,scientific_model_started=False,configs=cfg['configs'],config_delta=diff,expected_effective_options=e,input_binding=bind,trace_entry=str(entry),commandlist_sha256=sha(entry),expected=dh['expected'],DH_P0_reference={k:dh[k]for k in ['source_RESULT_path','source_RESULT_sha256','source_uuid','legal_prior_P0_alias']},CH_P0_reference={k:ch[k]for k in ['source_RESULT_path','source_RESULT_sha256','source_uuid','legal_prior_P0_alias']}))
assert len(candidates)==48;assert sum(x['status']=='CPU_PROGRESS_NEGATIVE_HOLD'for x in candidates)==16;assert len(set(x['plan_candidate_id']for x in candidates))==48
first=[next(x for x in candidates if x['program']==p and x['variant']==v)for p in auth['first_batch_programs']for v in auth['first_batch_variants']];assert len(first)==8;assert sum(x['status']=='CPU_PROGRESS_NEGATIVE_HOLD'for x in first)==4
save('INPUT_REFERENCE_QUALIFICATION.json',dict(authority=dict(path=str(AUTH),sha256=sha(AUTH)),read_scope='small binding/command lists and accepted RESULT proof; no trace body reread/raw log/restore audit',P0_reference_n=ref_checks,inputs=inputs))
save('CONFIG_VARIANTS.json',dict(schema='DTC_PERF_FIRST_CPU_STRUCTURE_VARIANTS_V1',baseline_config_records=[dict(path=str(p),sha256=sha(p))for p in basefiles],variants=configs))
save('CANDIDATE_MATRIX48.json',dict(schema='PLAN_ONLY_DTC_PERF_FIRST_STRUCTURE48_V1',authority_sha256=sha(AUTH),candidate_n=48,CPU_PROGRESS_NEGATIVE_HOLD_n=16,CPU_ONLY_qualified_n=32,model_starts=0,candidates=candidates))
save('FIRST_BATCH8.json',dict(schema='FIXED_FIRST8_PLAN_IDENTITIES_V1',no_substitution=True,programs=auth['first_batch_programs'],variants=auth['first_batch_variants'],HOLD_n=4,CPU_only_qualified_n=4,candidates=first))
print('READY',O,'48 cells; 16HOLD/32CPUqualified; first8 4HOLD/4CPUqualified; P0refs',ref_checks)

