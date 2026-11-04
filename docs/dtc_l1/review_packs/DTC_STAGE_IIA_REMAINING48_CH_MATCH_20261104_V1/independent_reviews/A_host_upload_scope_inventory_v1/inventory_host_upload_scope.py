from pathlib import Path
import json,hashlib,re,gzip,collections,subprocess,sys,datetime
sys.dont_write_bytecode=True;P=Path
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');O=A/'agents/A_host_upload_scope_inventory_v1';O.mkdir(exist_ok=True);CONTRACT=A/'agents/B_runtime_analysis_v1/CORE32_REFERENCE_CONTRACT.json';CONTRACT_SHA='9627c0fad4395ddf2414e958b897f8f4b73347cf29b70e31ca7f9fa912f0cc6b';CORE=Path('/root/data/dtc_failure_repair_20261025_v1/core');FW=Path('/root/data/dtc_failure_repair_20261025_v1/framework');CC='9eedb3131937748f0492fa83aad37d3691118d70';FC='02775fd795cde5aae1480d81cee6eb481d0a08f4';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();H=lambda b:hashlib.sha256(b).hexdigest();rd=lambda p:json.loads(Path(p).read_bytes());pin=lambda p:dict(path=str(p),sha256=sha(p),bytes=Path(p).stat().st_size);put=lambda n,v:(O/n).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');assert sha(CONTRACT)==CONTRACT_SHA
GEOMETRY_KEYS=['-gpgpu_n_clusters','-gpgpu_n_cores_per_cluster','-gpgpu_shader_core_pipeline']
KEYS=['-gpgpu_perf_sim_memcpy','-gpgpu_flush_l1_cache','-gpgpu_flush_l2_cache','-gpgpu_dtc_l1_invalidate_on_source_event']
def parse_commands(raw,expected_names):
 try:text=raw.decode('utf-8')
 except UnicodeDecodeError:return dict(status='UNKNOWN_COMMANDLIST_ENCODING',kernel_count=None,copy_count=None,copy_bytes=None,positions=None,events=[],unknown_lines=[])
 commands=[];unknown=[]
 for line_no,line in enumerate(text.splitlines(),1):
  if not line:continue
  if line!=line.strip():unknown.append(dict(line=line_no,reason='WHITESPACE_DIFFERS_FROM_FROZEN_PARSER_LITERAL_PREFIX'));continue
  if line.startswith('MemcpyHtoD'):
   m=re.fullmatch(r'MemcpyHtoD,((?:0[xX])?[0-9a-fA-F]+),([0-9]+)',line)
   if not m:unknown.append(dict(line=line_no,reason='HTOD_FORMAT_UNBOUND'));continue
   commands.append(dict(type='HtoD',line=line_no,destination_hex='0x'+format(int(m.group(1),16),'x'),bytes=int(m.group(2)),declared_command=line))
  elif line.startswith('kernel')and re.fullmatch(r'kernel[^\s,]*\.traceg(?:\.(?:gz|xz))?',line):commands.append(dict(type='kernel',line=line_no,file=line))
  else:unknown.append(dict(line=line_no,reason='UNSUPPORTED_DECLARED_COMMAND_NOT_INVENTORIED'))
 names=[x['file']for x in commands if x['type']=='kernel']
 if names!=expected_names or not names:unknown.append(dict(reason='KERNEL_SEQUENCE_DOES_NOT_MATCH_FROZEN_BODY_BINDING'))
 if unknown:return dict(status='UNKNOWN_UNBOUND_FORMAT_OR_SEQUENCE',kernel_count=None,copy_count=None,copy_bytes=None,positions=None,events=[],unknown_lines=unknown)
 n=len(names);k=0;events=[];positions={x:dict(copy_count=0,copy_bytes=0)for x in ['BEFORE_FIRST_KERNEL','BETWEEN_KERNELS','AFTER_LAST_KERNEL']}
 for ci,c in enumerate(commands,1):
  if c['type']=='kernel':k+=1;continue
  pos='BEFORE_FIRST_KERNEL'if k==0 else'AFTER_LAST_KERNEL'if k==n else'BETWEEN_KERNELS';e=dict(c,command_ordinal=ci,position=pos,after_kernel_ordinal=k or None,before_kernel_ordinal=k+1 if k<n else None);events.append(e);positions[pos]['copy_count']+=1;positions[pos]['copy_bytes']+=c['bytes']
 return dict(status='BOUND_DECLARED_COMMANDLIST_EVENTS',kernel_count=n,copy_count=len(events),copy_bytes=sum(x['bytes']for x in events),positions=positions,events=events,unknown_lines=[],count_scope='Declared frozen commandlist order, not actual runtime hook timing/data-value change/address-read overlap')

def actual_field(options,key):return dict(status='PRESENT_IN_ACCEPTED_EFFECTIVE_OPTIONS',tokens=options[key])if key in options else dict(status='UNKNOWN_NOT_IN_PROOF',tokens=None)

def excerpt(repo,commit,rel,a,b):
 p=repo/rel;raw=p.read_bytes();assert raw==subprocess.check_output(['git','-C',str(repo),'show',commit+':'+rel]);lines=raw.decode().splitlines();return dict(commit=commit,path=rel,native_path=str(p),sha256=H(raw),line_start=a,line_end=b,text='\n'.join(str(i)+': '+lines[i-1]for i in range(a,b+1)))
defs={'-gpgpu_perf_sim_memcpy':dict(default='1',source=excerpt(CORE,CC,'src/gpgpu-sim/gpu-sim.cc',239,242)),'-gpgpu_flush_l1_cache':dict(default='0',source=excerpt(CORE,CC,'src/gpgpu-sim/gpu-sim.cc',806,808)),'-gpgpu_flush_l2_cache':dict(default='0',source=excerpt(CORE,CC,'src/gpgpu-sim/gpu-sim.cc',809,811)),'-gpgpu_dtc_l1_invalidate_on_source_event':dict(default='0',source=excerpt(CORE,CC,'src/gpgpu-sim/dtc-l1-invalidation.h',24,30))}
contract=rd(CONTRACT);assert len(contract['population'])==32;p0=[x for x in contract['original128_references']if x['source_profile']=='P0'];assert len(p0)==64;by={};optionrows=[];aliasn=0;checks=[]
for ref in p0:
 path=Path(ref['source_RESULT_path']);assert sha(path)==ref['source_RESULT_sha256'];r=rd(path);p=r['proof'];assert ref['accepted']is True and p['performance_accepted']is True and p['input_digest']==ref['input_digest']and p['cell']==ref['source_cell'];assert(p.get('profile')or p.get('downstream_profile'))=='P0';assert r['uuid']==ref['source_uuid'];under=None
 if ref.get('legal_prior_P0_alias'):
  aliasn+=1;a=ref['legal_prior_P0_alias'];up=Path(a['underlying_RESULT_path']);assert sha(up)==a['underlying_RESULT_sha256'];u=rd(up);assert r['reference_result_path']==str(up)and r['reference_result_sha256']==a['underlying_RESULT_sha256']and u['uuid']==r['uuid']==a['underlying_execution_uuid']and u['cohort']==a['underlying_RESULT_declared_cohort'];assert u['proof']==p;under=dict(**a,underlying_state=u['state'],underlying_source_profile=u['proof'].get('profile')or u['proof'].get('downstream_profile'),underlying_proof_cohort=u['proof']['cohort'])
 opts=p.get('effective_options',{});row=dict(program=ref['program'],suite=ref['suite'],input_digest=ref['input_digest'],design=ref['source_cell'],comparison_profile='P0',actual_proof_source_profile=p.get('profile')or p.get('downstream_profile'),source_registered_slot_cohort=ref['source_registered_slot_cohort'],wrapper_RESULT_cohort=r['cohort'],proof_actual_cohort=p['cohort'],actual_execution_uuid=r['uuid'],RESULT=dict(path=str(path),sha256=ref['source_RESULT_sha256']),legal_P0_alias_underlying=under,actual_option_fields={key:dict(**actual_field(opts,key),source_declared_default=defs[key]['default'],default_source_ref='OPTION_DEFAULT_SOURCE.json:'+key,value_origin='UNKNOWN_CONFIG_OR_DEFAULT_PRECEDENCE_NOT_INFERRED_FROM_VALUE_ALONE')for key in KEYS},actual_geometry_fields={key:actual_field(opts,key)for key in GEOMETRY_KEYS},actual_trace_option=opts.get('-trace'),native_numeric_or_coherence_certification='NOT_ADDED');optionrows.append(row);by[(ref['input_digest'],ref['source_cell'])]=ref;checks.append(ref['source_registered_slot_cohort']+'_accepted_P0_source_SHA_identity')
assert aliasn==6
inventory=[];events=[]
for pop in contract['population']:
 d=pop['input_digest'];ch,dh=(by[(d,c)]for c in ['CH','DH']);x=dict(pop,status='UNKNOWN_UNBOUND',kernel_count=None,copy_count=None,copy_bytes=None,positions=None,unknowns=[])
 try:
  assert ch['input_binding']==dh['input_binding'];bp=Path(ch['input_binding']['path']);assert sha(bp)==ch['input_binding']['sha256'];bd=rd(bp);assert bd['input_digest']==d;q=bd['qualification'];assert q['status']=='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS'and not q['issues'];trace=P(q['trace_entry']);raw=trace.read_bytes();assert H(raw)==bd['asset']['commandlist_sha256'];names=[P(r['path']).name for r in q['rows']];parsed=parse_commands(raw,names);x.update({k:v for k,v in parsed.items()if k!='events'});x.update(input_binding=ch['input_binding'],trace_entry=str(trace),commandlist_sha256=H(raw),expected_kernel_count=ch['expected']['kernels'],frozen_capture_extent=bd['asset']['extent'],capture_complete_native_input=q['capture_complete_native_input'],numeric_correctness=q['native_numerical_correctness'],actual_P0_trace_paths=[])
  assert ch['expected']==dh['expected'];assert len(names)==ch['expected']['kernels']
  for ref in [ch,dh]:
   opts=rd(ref['source_RESULT_path'])['proof']['effective_options'];values=opts.get('-trace');tp=P(values[0])if values and len(values)==1 else None
   if tp is None:raise ValueError('P0_TRACE_OPTION_UNKNOWN')
   th=sha(tp);assert th==H(raw),'P0_TRACE_COMMAND_SHA_DISAGREES';x['actual_P0_trace_paths'].append(dict(design=ref['source_cell'],path=str(tp),sha256=th,source_RESULT_sha256=ref['source_RESULT_sha256']))
  if parsed['status']=='BOUND_DECLARED_COMMANDLIST_EVENTS':events.append(dict(program=pop['program'],input_digest=d,commandlist_sha256=H(raw),events=parsed['events']));checks.append(pop['program']+'_command_SHA_P0_paths_and_ordinal_binding')
 except(Exception)as e:x.update(status='UNKNOWN_BINDING_OR_FORMAT',kernel_count=None,copy_count=None,copy_bytes=None,positions=None);x['unknowns'].append(repr(e))
 inventory.append(x)
put('OPTION_DEFAULT_SOURCE.json',dict(fixed_Core=CC,fields=defs,default_is_not_used_to_fill_missing_actual_proof_fields=True,matching_default_does_not_prove_runtime_inheritance=True))
put('P0_EFFECTIVE_OPTIONS64.json',dict(schema='DTC_CORE32_FROZEN_P0_UPLOAD_RELATED_OPTIONS_V1',contract=pin(CONTRACT),rows=optionrows,legal_alias_count=aliasn,total_sources=64,missing_actual_field_policy='UNKNOWN; known source declaration is not substituted',no_simulation_raw_read=True))
put('CORE32_HTOD_INVENTORY.json',dict(schema='DTC_CORE32_FROZEN_DECLARED_HOST_UPLOAD_SCOPE_V1',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),authority_contract=pin(CONTRACT),fixed_population=32,rows=inventory,no_performance_selection=True,numeric_coherence_or_complete_application_certification=False,unknown_is_not_zero=True))
with (O/'HTOD_EVENTS.json.gz').open('wb')as f:
 with gzip.GzipFile(fileobj=f,mode='wb',mtime=0)as gz:gz.write((json.dumps(dict(schema='DTC_CORE32_DECLARED_HTOD_EVENTS_V1',programs=events),sort_keys=True,separators=(',',':'))+'\n').encode())
# Reuse source entry facts only; do not import the myocyte runtime mechanism inference.
cp=A/'agents/C_completed_myocyte_review_v1/FIXED_CORE_INVALIDATION_ENTRY_FACTS.json';assert sha(cp)=='72587e571dfde4f1b834f4cce48176205ec1d4e0ce64dd79ea78d26520fa5697';c=rd(cp)
for sr in c['source_references']:
 p=P(sr['path']);rel=str(p.relative_to(CORE));assert p.read_bytes()==subprocess.check_output(['git','-C',str(CORE),'show',CC+':'+rel])and sha(p)==sr['sha256']
put('FIXED_SOURCE_ENTRY_POINTS.json',dict(reused_C_source_fact=pin(cp),source_references=c['source_references'],direct_selected_entry_fact=c['direct_source_fact'],trace_parser=excerpt(FW,FC,'gpu-simulator/trace-parser/trace_parser.cc',394,445),framework_prefill_call=excerpt(FW,FC,'gpu-simulator/accel-sim.cc',128,145),limits=['Selected idle-cluster/source-event callsites only; not proof OO state is never reset through another path.','Declared HtoD positions do not establish data-value change, exact hook timing or overlap with OO-read addresses.','No interkernel HtoD does not certify GPU-store/other-host/coherence safety.','No safe/unsafe classification or accepted/input downgrade.']))
valid=[x for x in inventory if x['status']=='BOUND_DECLARED_COMMANDLIST_EVENTS'];inter=[x['program']for x in valid if x['positions']['BETWEEN_KERNELS']['copy_count']>0];unknown=[x['program']for x in inventory if x not in valid];patterns=collections.Counter(tuple(tuple(r['actual_option_fields'][k]['tokens']or['UNKNOWN'])for k in KEYS)for r in optionrows);geometry_patterns=collections.Counter(tuple(tuple(r['actual_geometry_fields'][k]['tokens']or['UNKNOWN'])for k in GEOMETRY_KEYS)for r in optionrows)
summary=dict(actual_option_missing_counts={k:sum(r['actual_option_fields'][k]['tokens']is None for r in optionrows)for k in KEYS},actual_geometry_patterns=[dict(fields={k:list(v)for k,v in zip(GEOMETRY_KEYS,pat)},count=n)for pat,n in geometry_patterns.items()],geometry_missing_counts={k:sum(r['actual_geometry_fields'][k]['tokens']is None for r in optionrows)for k in GEOMETRY_KEYS},status='READONLY_DECLARED_SCOPE_INVENTORY_COMPLETE',inputs=32,bound_inputs=len(valid),unknown_inputs=unknown,interkernel_HtoD_programs=inter,programs_without_declared_interkernel_HtoD=[x['program']for x in valid if x['positions']['BETWEEN_KERNELS']['copy_count']==0],P0_sources=64,legal_alias_underlying_sources=6,actual_option_patterns=[dict(fields={k:list(v)for k,v in zip(KEYS,pat)},count=n)for pat,n in patterns.items()],interpretation='Exposure/declared-event inventory only, never safe/unsafe or numerical/coherence certification',new_models_traces_services_or_source_mutations=0);put('SUMMARY.json',summary);put('BINDING_VALIDATION.json',dict(status='PASS'if not unknown else'UNKNOWN_RETAINED',checks=checks,loop_assertion_count=len(checks),independent_invariants=['Fixed32/fullinput and64P0 source identity','Six legal alias underlying UUID/proof preserved','Input-binding and commandlist SHA','Ordered kernel filename match','Every actual P0 trace option SHA matches selected commandlist','Actual fields separate from source defaults; missing staysUNKNOWN'],raw_content_or_live_logs_read=False,new_scientific_actions=0));print(json.dumps(summary))

