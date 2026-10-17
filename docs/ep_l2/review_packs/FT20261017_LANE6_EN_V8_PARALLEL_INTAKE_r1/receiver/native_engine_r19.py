from pathlib import Path
import subprocess,json,hashlib,importlib.util,sys,os,copy,datetime,collections,re,shutil,difflib,unittest
R=Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane6-v1')
P=R/'docs/ep_l2/review_packs/FT20261017_LANE6_R17_SAD_INTAKE_r1'
OLD=R/'docs/ep_l2/review_packs/FT20261016_LANE6_PAPER_PPA_r3'
os.environ.update(PYTHONDONTWRITEBYTECODE='1',GIT_CONFIG_COUNT='2',GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf',GIT_CONFIG_VALUE_0='git@github.com:',GIT_CONFIG_KEY_1='credential.helper',GIT_CONFIG_VALUE_1='!gh auth git-credential')
sys.dont_write_bytecode=True
def git(*args):return subprocess.check_output(['git','-C',str(R),'-c','gc.auto=0',*args],timeout=35)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(name,value):
 p=P/name;p.parent.mkdir(parents=True,exist_ok=True)
 if isinstance(value,bytes):p.write_bytes(value)
 elif isinstance(value,str):p.write_text(value)
 else:p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def live_reader():
 import http.client
 token=subprocess.check_output(['gh','auth','token'],timeout=10,text=True).strip();connection=None
 def current(repo):
  nonlocal connection
  for attempt in range(3):
   try:
    if connection is None:connection=http.client.HTTPSConnection('api.github.com',timeout=10)
    connection.request('GET','/repos/swayhrl/accel-sim-framework/git/ref/heads/hrl/ep-l2-ft20261016-lane5-v1',headers={'Authorization':'Bearer '+token,'User-Agent':'EP-L2-Lane6-evidence-intake','Accept':'application/vnd.github+json','Cache-Control':'no-cache'})
    response=connection.getresponse();raw=response.read();assert response.status==200,'Current GitHub authority unavailable';value=json.loads(raw)['object']['sha'];assert re.fullmatch('[0-9a-f]{40}',value);return value
   except (OSError,http.client.HTTPException):
    if connection is not None:connection.close()
    connection=None
    if attempt==2:raise
  raise ValueError('No current authority; no cached fallback')
 return current
def prepare():
 assert not P.exists(),'Do not overwrite frozen revision';(P/'validation').mkdir(parents=True);(P/'upstream_editorial').mkdir()
 source={'start_HEAD':git('rev-parse','HEAD').decode().strip(),'coordination_commit':'3e3920a42a865c90af37330ffe95b6bbb9d61537','sources':[]}
 def read(c,path):
  raw=git('show',c+':'+path);source['sources'].append({'commit':c,'path':path,'sha256':sha(raw),'bytes':len(raw)});return raw
 write('validation/COORDINATION_R17.md',read(source['coordination_commit'],'docs/ep_l2/chatgpt_handoff/fast_track_2026_10_17_review_r17/FIRST_CURRENT_ACCEPTED_SAD_AND_NEXT_FOUR.md'))
 ed=git('rev-parse','origin/hrl/ep-l2-iscas2027-english-editorial-v1').decode().strip();source['editorial_commit']=ed
 for name in ['README.md','EP_L2_EN_v5.tex']:write('upstream_editorial/'+name,read(ed,'docs/ep_l2/paper/english_en_v5/'+name))
 current=git('rev-parse','origin/hrl/ep-l2-ft20261016-lane5-v1').decode().strip();source['initial_lane5_HEAD']=current
 for name in ['STATUS.md','RECEIPT.json']:write('validation/LANE5_'+name.replace('.','_'),read(current,'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/'+name))
 h=json.loads(read('0677446bb61fef2e8dd0b85f3963d77b07f5d855','docs/ep_l2/review_packs/FT20261017_LANE5_R0_1_A1_B1_SAD_ACCEPTANCE_r1/LANE6_HANDOFF.json'));write('ORIGINAL_SAD_HANDOFF.json',h)
 adapter={'qualification_publication':h['qualification_publication'],'qualification_path':'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/R0_1_A1_B1_INDEPENDENTLY_QUALIFIED.json','producer_publication':h['producer_publication'],'producer_contract_path':'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1/BASELINE_CONTRACT_R0_1_A1_B1_V1.json','native_pairs':[{'publication_commit':h['pair_artifact_publication'],'pair_repository_path':h['pair_pack']}],'result_root':'/workspace/results/ep_l2_ft20261016'}
 write('NATIVE_ADAPTER_SAD.json',adapter)
 old=read('70675cc3b2cd63e29fc7ab2b0b54dc924011f5e4',str((OLD/'native_pair_intake.py').relative_to(R))).decode();needle='require(q["data_correctness_scope"] == "SYMBOLIC_32B_SECTOR_VERSIONS_AND_REQUEST_IDENTITY_NOT_NUMERIC_SASS_PAYLOAD", "Do not broaden data scope")';assert old.count(needle)==1
 function='''\nALLOWED_SYMBOLIC_SCOPES = {\n    "SYMBOLIC_32B_SECTOR_VERSIONS_AND_REQUEST_IDENTITY_NOT_NUMERIC_SASS_PAYLOAD",\n    "SYMBOLIC_32B_SECTOR_VERSIONS_REQUEST_IDENTITY_NOT_NUMERIC_SASS_PAYLOAD",\n}\n\ndef require_scope_compatibility(certificate):\n    require(certificate.get("data_correctness_scope") in ALLOWED_SYMBOLIC_SCOPES, "Unknown symbolic data scope")\n    require(certificate.get("application_input_scope") == "FULL_NATIVE_NONATOMIC_ONLY", "Only complete native nonatomic application scope is supported")\n\n'''
 updated=old.replace(needle,'require_scope_compatibility(q)').replace('def file_hash(path):',function+'def file_hash(path):');write('native_pair_intake_v2a.py',updated)
 write('validation/NATIVE_ADAPTER_DELTA.patch',''.join(difflib.unified_diff(old.splitlines(True),updated.splitlines(True),fromfile='frozen_r3/native_pair_intake.py',tofile='r17/native_pair_intake_v2a.py')))
 write('SOURCE_MANIFEST.json',source)
 print(json.dumps({'prepared':str(P),'editorial':ed,'current_authority_candidate':current}))

def receive():
 assert not (P/'SAD_NATIVE_INTAKE.json').exists()
 helper=module('r17_previous',(R/'docs/ep_l2/review_packs/FT20261016_LANE6_PAPER_PPA_r4/current_pair_intake.py'))
 # Same current GitHub branch reference through the bounded HTTPS API;
 # no cached fallback on transport failures.
 helper.live_head=live_reader()
 api=helper.vendor_api();c=helper.live_head(R);git('fetch','--no-tags','--no-recurse-submodules','origin',c)
 read=lambda path:git('show',c+':'+path)
 raw=read(api.MANIFEST);meta=json.loads(raw);state=api.bind_manifest(raw,{'kind':'FETCHED_GITHUB_BRANCH','publication_commit':c,'manifest_sha256':sha(raw),'generation':meta['generation'],'revision':meta['revision']},read);context=helper.bridge(R,state)
 write('APPLICATION_ACCEPTANCE.json',raw);write('validation/CURRENT_AUTHORITY.json',state['binding'])
 adapter=json.loads((P/'NATIVE_ADAPTER_SAD.json').read_text())
 original=adapter.get('original_pair_artifact_publication',adapter['native_pairs'][0]['publication_commit']);adapter['original_pair_artifact_publication']=original
 for name in ['PAIR_RECEIPT.json','RESULTS.csv']:
  path=adapter['native_pairs'][0]['pair_repository_path']+'/'+name;assert git('show',original+':'+path)==git('show',c+':'+path)
 adapter['native_pairs'][0]['publication_commit']=c;write('NATIVE_ADAPTER_SAD.json',adapter);spec={**adapter,'current_acceptance':context.provenance()}
 _,legacy,results=helper.legacy_modules(R)
 # The frozen H0 adapter cannot accept new overlays; do not bypass a failure.
 # Use the positive, published condition envelope mapping in the r19 native reader.
 native=module('r19_native',P/'native_pair_intake_r19.py');packet=native.read_native_packet(R,spec,context);summary=results.summarize(packet,context)
 print('SUMMARY KEYS',list(summary))
 pair=json.loads(git('show',adapter['native_pairs'][0]['publication_commit']+':'+adapter['native_pairs'][0]['pair_repository_path']+'/PAIR_RECEIPT.json'))
 qraw=git('show',adapter['qualification_publication']+':'+adapter['qualification_path']);q=json.loads(qraw);hash_cache={};bound=[];metrics=[];slices={}
 def file_digest(path):
  path=Path(path);stat=path.stat();key=(str(path.resolve()),stat.st_size,stat.st_mtime_ns)
  if key not in hash_cache:
   h=hashlib.sha256()
   with path.open('rb') as f:
    for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
   hash_cache[key]=h.hexdigest()
  return hash_cache[key]
 for spec0,result in zip(pair['specs'],pair['results']):
  ident=spec0['identity'];key=result['run_key'];directory=Path(result['allocation']['result_directory']);proofref=spec0['atomic_input_scope'];proofraw=Path(proofref['path']).read_bytes();proof=json.loads(proofraw)
  assert sha(proofraw)==proofref['sha256']==result['audit']['atomic_input_scope']['sha256'];assert proof['status']=='COMPLETE_NATIVE_OPCODE_AUDIT'
  # Lane5 run.py:validate_atomic_input_scope deliberately binds this input-only
  # proof to source/Framework/binary/trace, independently of the B/U mode hash.
  for field in ['core_source_commit','framework_source_commit','binary_sha256','trace_content_sha256','workload','epoch_range','termination_contract']:assert proof['identity'][field]==ident[field]
  assert proof['input_scope']=='COMPLETE_INPUT_HAS_NO_NATIVE_ATOMIC_OPCODE_RECORDS';assert proof['global_atomic_records_with_repeats']==proof['shared_atomic_records_with_repeats']==0
  assert proof['trace_content_manifest']==result['audit']['traces'];assert sha(json.dumps(result['audit']['traces'],sort_keys=True,separators=(',',':')).encode())==ident['trace_content_sha256']
  assert all(t['atomic_absence'] is True and t['global_atomic_records']==t['shared_atomic_records']==0 and t['status']=='COMPLETE_NATIVE_OPCODE_COVERAGE' for t in proof['trace_files'])
  assert proof['producer_publication']==adapter['producer_publication'];assert proof['tool_sha256']==q['atomic_input_auditor_sha256']
  relative=proofref['path'][proofref['path'].index('docs/ep_l2/'):];assert git('show',adapter['qualification_publication']+':'+relative)==proofraw
  paths={t['name']:Path(t['path']) for t in spec0['trace_files']};expected={t['name']:t for t in result['audit']['traces']};assert paths.keys()==expected.keys();assert len(paths)==len(spec0['trace_files'])
  for name,path in paths.items():assert file_digest(path)==expected[name]['sha256'] and path.stat().st_size==expected[name]['bytes']
  commands=paths[spec0['entry_trace_name']].read_text().splitlines();kernel_names=[x.strip() for x in commands if x.strip().endswith(('.traceg','.traceg.xz','.traceg.bz2'))];assert len(kernel_names)==proof['ordered_kernel_instances'];assert set(kernel_names)==set(paths)-{spec0['entry_trace_name']}
  assert sum(t['active_lane_instruction_records'] for t in proof['trace_files'])==result['summary']['instructions']
  assert json.loads((directory/'input_spec.json').read_text())==spec0;assert json.loads((directory/'input_audit.json').read_text())==result['audit'];assert json.loads((directory/'terminal_summary.json').read_text())==result['summary'];assert json.loads((directory/'run_status.json').read_text())==result
  parserraw=git('show',ident['framework_source_commit']+':util/ep_l2/ft_lane1/parse_ft_terminal.py');assert sha(parserraw)==spec0['parser']['sha256'];assert Path(spec0['parser']['path']).read_bytes()==parserraw;assert Path(spec0['qualified_release']).read_bytes()==qraw
  parser={};exec(compile(parserraw,'frozen_parse_ft_terminal.py','exec'),{'__name__':'r17_parser'},parser)
  # exec needs one shared namespace for function globals.
  parser={'__name__':'r17_parser'};exec(compile(parserraw,'frozen_parse_ft_terminal.py','exec'),parser);reparsed=parser['parse'](directory/'raw.log',spec0);assert reparsed==result['summary']
  ft={};term={};inv={};app={}
  for line in (directory/'raw.log').open(errors='strict'):
   if not line.startswith(('EPL2FTV1|','EPL2B0V1|')):continue
   parts=line.strip().split('|');values=dict(v.split('=',1) for v in parts[1:] if '=' in v)
   if 'slice' not in values:continue
   sid=int(values['slice'])
   if line.startswith('EPL2FTV1|SUMMARY|'):ft[sid]={k:int(v) for k,v in values.items()}
   elif line.startswith('EPL2FTV1|TERMINAL|'):term[sid]={k:int(v) for k,v in values.items()}
   elif line.startswith('EPL2B0V1|INVARIANT|') and values.get('kernel_uid')=='18446744073709551615':inv[sid]={k:int(v) for k,v in values.items()}
   elif values.get('scope')=='application' and values.get('interval')=='application_cumulative':app[sid]=values
  if set(app)!=set(range(64)):
   print('DEBUG SET COUNTS',len(ft),len(term),len(inv),len(app))
   for line in (directory/'raw.log').open():
    if 'bank_logical_ops=' in line and ('application' in line or 'cumulative' in line):print('DEBUG APP LINE',line[:1000]);break
  assert set(ft)==set(term)==set(inv)==set(app)==set(range(64));total=lambda rows,k:sum(int(x[k]) for x in rows.values())
  fields=['bank_logical_ops','bank_grants','bank_wait_cycles','c7d_bank_resident_hit_read','c7d_bank_resident_write','c7d_bank_fill_write','c7d_bank_wb_readout','c7d_bank_bypass_fill','c7d_bank_bypass_read','c7d_wad_full_events','c7d_wad_hazard_events','c7e_dram_successful_write_bytes']
  arm={'workload':ident['workload'],'mode':spec0['mode'],'run_key':key,'cycles':reparsed['cycles'],'instructions':reparsed['instructions'],**{k:total(ft,k) for k in ['copy_lines','staging_reads','wb_created','wb_completed','wb_lower_accept','wbuf_full','pool_full']},**{k:total(app,k) for k in fields}}
  assert sum(arm[k] for k in fields[3:9])==arm['bank_logical_ops'];metrics.append(arm);slices[spec0['mode']]={'summary':ft,'terminal':term,'invariant':inv,'application_cumulative':app}
  bound.append({'mode':spec0['mode'],'identity':ident,'run_key':key,'result_directory':str(directory),'raw_log_sha256':file_digest(directory/'raw.log'),'binary_sha256':file_digest(directory/'accel-sim.out'),'ordered_configs':result['audit']['configs'],'traces_rehashed':result['audit']['traces'],'complete_input_proof_path':proofref['path'],'complete_input_proof_sha256':sha(proofraw),'parser_source_sha256':sha(parserraw),'hardware_terminal_reparsed':reparsed,'all64_slice_sets_checked':True})
 b,u=metrics;assert b['mode']=='B16_BANKED' and u['mode']=='U_WB16';assert b['instructions']==u['instructions'];assert b['cycles']>0 and u['cycles']>0
 # No universal copy-to-application-operation identity is assumed for later workloads.
 context.assert_fresh();write('SAD_NATIVE_INTAKE.json',{'current_authority':state['binding'],'adapter':adapter,'packet':packet,'summary':summary,'scope_compatibility':'Two exact symbolic certificate spellings only; per-spec complete-native nonatomic proof additionally checked','group_geomean':None});write('SAD_IDENTITY_AND_CLOSURE.json',bound);write('SAD_RAW_METRICS.json',metrics);write('SAD_64_SLICE_EVIDENCE.json',slices);write('validation/TRACE_BODY_REHASH.json',{'distinct_files':len(hash_cache),'total_distinct_bytes':sum(k[1] for k in hash_cache),'hashes':[{'path':k[0],'bytes':k[1],'sha256':v} for k,v in hash_cache.items()],'full_native_body_rehashed':True,'simulators_started':0})
 write('validation/SCOPE_NEGATIVE_CHECKS.json',scope_checks(native,q,api,state,pair))
 print(json.dumps({'status':'SAD_NATIVE_V2_INTAKE_PASS','authority':state['binding'],'cycles':[x['cycles'] for x in metrics],'copy':[x['copy_lines'] for x in metrics],'bank_logical_ops':[x['bank_logical_ops'] for x in metrics],'group_geomean':None}))

def scope_checks(native,q,api,state,pair):
 checks=[]
 for scope in native.ALLOWED_SYMBOLIC_SCOPES:
  z=copy.deepcopy(q);z['data_correctness_scope']=scope;native.require_scope_compatibility(z);checks.append({'case':'exact_symbolic_scope_'+scope,'status':'PASS'})
 for name,key,value in [('unknown_scope','data_correctness_scope','NUMERIC_SASS_OUTPUT_VERIFIED'),('atomic_scope','application_input_scope','ATOMIC_ALLOWED')]:
  z=copy.deepcopy(q);z[key]=value
  try:native.require_scope_compatibility(z)
  except ValueError:checks.append({'case':name,'status':'REJECTED'})
  else:raise AssertionError(name+' unexpectedly accepted')
 row=pair['results'][0]
 for name,identity,raw in [('wrong_binary',{**row['identity'],'binary_sha256':'f'*64},row['raw_log_sha256']),('wrong_raw',row['identity'],'f'*64)]:
  try:api.require_current_result(identity,raw,row['summary']['cycles'],row['summary']['instructions'],state)
  except ValueError:checks.append({'case':name,'status':'REJECTED'})
  else:raise AssertionError(name+' unexpectedly accepted')
 return {'new_adapter_guard_checks':checks,'synthetic_cases_are_not_scientific_results':True,'old_test_suites_replayed':False}
