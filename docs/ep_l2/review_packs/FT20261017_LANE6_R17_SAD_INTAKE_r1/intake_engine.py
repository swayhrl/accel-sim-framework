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
 try:legacy.read_native_packet(R,spec,context)
 except ValueError as error:
  assert 'Do not broaden data scope' in str(error),str(error);write('validation/OLD_NATIVE_SCOPE_MISMATCH.json',{'status':'EXPECTED_FAIL_CLOSED_SCHEMA_SPELLING','reason':str(error),'old_files_changed':False})
 else:write('validation/OLD_NATIVE_SCOPE_MISMATCH.json',{'status':'ORIGINAL_NATIVE_SCOPE_ALREADY_COMPATIBLE','old_files_changed':False})
 native=module('r17_native',P/'native_pair_intake_v2a.py');packet=native.read_native_packet(R,spec,context);summary=results.summarize(packet,context)
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

def finish():
 import csv,io
 assert (P/'SAD_NATIVE_INTAKE.json').exists(),'No numeric output before complete intake'
 evidence=json.loads((P/'SAD_NATIVE_INTAKE.json').read_text());metrics=json.loads((P/'SAD_RAW_METRICS.json').read_text());b,u=metrics
 ledger=json.loads((P/'APPLICATION_ACCEPTANCE.json').read_text());official=len({r['workload'] for r in ledger['rows'] if r['scientific_acceptance']=='CURRENT_ACCEPTED'});authority=evidence['current_authority']
 text=(P/'upstream_editorial/EP_L2_EN_v5.tex').read_text();changes=[]
 def replace(before,after):
  nonlocal text
  assert text.count(before)==1,before;text=text.replace(before,after);changes.append({'before':before,'after':after})
 replace('English working draft EN-v5','English working draft EN-v5 (SAD intake r1)')
 replace('Complete independent correctness qualification, application performance, and physical implementation costs remain open. This working draft therefore specifies the design and evaluation without reporting measured speedup or PPA benefits.','An initial independently accepted SAD control shows nearly unchanged execution time while eliminating measured staging copies. Evidence is limited to the qualified native nonatomic scope; broader performance conclusions and physical PPA benefits remain unestablished.')
 replace('This multi-cycle invariant is a design requirement whose production-path validation remains open; it is not a completed correctness claim.','The repaired release passes producer and independent directed qualification, including the tested cross-cycle boundary. Application qualification remains bounded by the native nonatomic scope below.')
 replace('The current official producer and its independent replay have each passed the original 21 directed invocations. Full independent qualification remains open, including the real multiway, cross-cycle replacement boundary discussed above. These passes are not application correctness or performance results. New measurements require qualification of the exact producing source, binary, and feature combination.','The repaired producer and its independent replay each pass 31 directed invocations, and Lane5 accepts the complete eleven-gate protocol. Per-spec complete-content proofs restrict application qualification to native nonatomic inputs. New results remain bound to the exact source, binary, configurations, and input content.')
 old='No independently accepted application pair or physical implementation measurement is available in this editorial snapshot. Figures~\\ref{fig:mainresults}--\\ref{fig:controls} reserve space for those results. The following analysis specifies the claims each measurement can support; accepted findings must replace this planning text.'
 new=(f'Lane5 ledger generation {authority["generation"]} accepts {official}/5 prescribed pairs; this revision independently ingests only SAD (1/5). '
      'SAD takes 110,773/110,749 cycles for B16/U-WB16, with 3,975/0 copy transfers and 483,611/475,661 logical bank operations. Both report zero WB-data-full events. The 24-cycle difference is a near tie; the operation reduction is consistent with copy removal, without establishing capacity benefit or behavior of other applications. No group mean or physical PPA result is reported. Figures~\\ref{fig:mainresults}--\\ref{fig:controls} retain their reservations for later consolidated results.')
 replace(old,new)
 write('EP_L2_EN_v5_SAD.tex',text);write('MANUSCRIPT_CHANGES.json',changes)
 write('validation/EN_V5_SAD_DIFF.patch',''.join(difflib.unified_diff((P/'upstream_editorial/EP_L2_EN_v5.tex').read_text().splitlines(True),text.splitlines(True),fromfile='upstream_EN_v5.tex',tofile='EN_v5_SAD.tex',n=0)))
 out=io.StringIO();writer=csv.DictWriter(out,fieldnames=list(b));writer.writeheader();writer.writerows(metrics);write('SAD_RESULTS.csv',out.getvalue())
 rows=[('Native cumulative cycles','cycles'),('Instructions','instructions'),('Completed copy transfers','copy_lines'),('Logical bank operations','bank_logical_ops'),('Successful send-read grants','staging_reads'),('WB completed','wb_completed'),('WB-data-full events','wbuf_full'),('Pool/eligible-landing failures','pool_full'),('Cumulative bank wait','bank_wait_cycles'),('WAD-full events','c7d_wad_full_events'),('WAD-hazard events','c7d_wad_hazard_events'),('DRAM write bytes','c7e_dram_successful_write_bytes')]
 table='| Metric | B16_BANKED | U_WB16 |\n|---|---:|---:|\n'+''.join(f'| {label} | {b[key]} | {u[key]} |\n' for label,key in rows)
 write('SAD_RESULT_AND_CAUSAL_ANALYSIS.md',f'''# Independently ingested SAD negative control\n\n{table}\nCoverage: Lane6 independently ingested **1/5**, paper numerical coverage **1/5**; live Lane5 authority at intake accepts **{official}/5**, generation{authority['generation']}, commit `{authority['publication_commit']}`. Historical first SAD acceptance0677446/generation4 is retained as provenance, never substituted for current authority. No five-workload chart or group geomean.\n\nBoth arms have identical157583646 instructions and identical repaired release/input scope. Cycles decrease by{b['cycles']-u['cycles']} ({100*(b['cycles']-u['cycles'])/b['cycles']:.6f}% relative cycle reduction), B/U={b['cycles']/u['cycles']:.12f}. This single observed near tie has no statistical-significance or equivalence claim. Copy3975→0 and logical operations decrease7950=2×3975, consistent with removing copy read/write work; it is not a unique end-to-end causal proof or a prediction of bank-cycle/energy savings.\n\nZero WB-data-full/pool/WAD counters and no observed capacity_above_C16 establish no capacity benefit for this pair. They do not prove that all possible capacity pressure is absent or that other applications cannot benefit. C1 legacy resident-headroom observations are excluded. The qualified correctness scope is symbolic32B sector versions/requester/WB/64-slice lifecycle under complete native nonatomic input, not numerical SASS payload outputs, atomic accesses, TVD/RO or Ideal.\n\nAll values above are independently summed/reparsed from hash-bound raw logs after the existing native adapter and current V2 checks. `SAD_IDENTITY_AND_CLOSURE.json` binds full release/config/trace/raw identities; `SAD_64_SLICE_EVIDENCE.json` preserves per-slice evidence. Runtime totals are native GPU cumulative values, never sums of per-slice cycles. Application bank counters use actual `scope=application` and `interval=application_cumulative`.\n''')
 write('EN_V5_ADOPTION_AND_REMAINING_GAPS.md',f'''# Editorial basis and remaining evidence\n\nExact EN-v5 editorial source `{json.loads((P/'SOURCE_MANIFEST.json').read_text())['editorial_commit']}` is retained under upstream_editorial. Its old088146/861a snapshot and open-qualification prose are historical; the SAD text uses repaired7b8e6ac7/9bd17f9d/binary23094a9d,31 producer+31 independent cases and complete eleven-gate qualification. Only five targeted textual replacements were made; no whole-paper rewrite, bibliography change or new experimental plot. The 4 technical+1 reference-page budget is verified by local typesetting.\n\nThe current ledger accepts{official}/5 but only SAD has passed this Lane6 intake. Remaining four workloads stay outside this revision's numerical results. Metadata-only discovery is not independent paper intake. Each future adapter must bind an exact currently accepted native pair and run the same gates; full trace/body/config/binary/raw hashes, source-bound parser64-slice reparse, exact scope proof and current withdrawal check are mandatory. New/unknown trace proof or producer schema fails closed; no input trimming or placeholder metric0. FWT or any still-unaccepted row cannot be filled from roster hashes.\n\nNo group geomean until all five pairs have also passed the paper intake. Fixed-total static repartition, WBUF8, Ideal and TVD/RO require their own scientific contracts/source/binary/config/qualification; this revision launches none. Original EN-v4 and all old packs are unchanged. PPA remains a source-level design representation, with no new RTL/synthesis/STA/area/power evidence; the old c948 field ledger is not silently promoted to a measured7b8 repair cost.\n''')
 write('INCREMENTAL_INTAKE.md','''# Event-driven incremental intake\n\nNo polling. Supply a new exact native adapter for one later pair, current qualification/producer publications and immutable pair path. Run the included receive_incremental.py with --repo, --adapter and a new --output-dir. It retains the original native identity/qualification/raw/config/drain checks, current V2 supersession/withdrawal and exact branch freshness, plus full trace-body/proof and frozen-parser checks. Unknown proof/schema/mode is rejected, not guessed. Only1168-slot B16/U_WB16 nonatomic scope is supported. Numerical output remains one pair; no automatic five-workload plot/mean.\n\nThe first publication9aad3338 did not yet list its pack in its Lane5 receipt; the adapter therefore uses the current Lane5 publication, with PAIR_RECEIPT/RESULTS bytes proven identical to the first publication. The old native adapter also refused the current certificate's exact scope spelling without AND. A new version allows only the two exact symbolic-scope strings, additionally requiring FULL_NATIVE_NONATOMIC_ONLY and per-spec complete input proofs; all other old native checks remain. No old file or Lane5 ledger is edited.\n\nFuture ingestion should use a new revision and rebind current authority before publication; if any consumed row is withdrawn, exclude it from the new manuscript while preserving historical artifacts. The three other already-accepted pairs are ready for their own intake event, not included as received numerical evidence here.\n''')
 # Export the exact engine used for this receipt, with a wrapper selecting a new output directory.
 engine=Path(__file__).read_text().replace("assert b['cycles']>0 and u['cycles']>0", "assert b['cycles']>0 and u['cycles']>0")
 engine=engine.replace("# No universal copy-to-application-operation identity is assumed for later workloads.", "# No universal copy-to-application-operation identity is assumed for later workloads.")
 write('intake_engine.py',engine)
 write('receive_incremental.py','''import argparse,importlib.util,json\nfrom pathlib import Path\np=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--adapter',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();assert not a.output_dir.exists();a.output_dir.mkdir(parents=True);s=importlib.util.spec_from_file_location('engine',Path(__file__).with_name('intake_engine.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.R=a.repo.resolve();m.OLD=m.R/'docs/ep_l2/review_packs/FT20261016_LANE6_PAPER_PPA_r3';m.P=a.output_dir.resolve();m.write('NATIVE_ADAPTER_SAD.json',json.loads(a.adapter.read_text()));m.write('native_pair_intake_v2a.py',Path(__file__).with_name('native_pair_intake_v2a.py').read_bytes());m.receive()\n''')
 # Typeset only, with the already-present isolated macro/font tree.
 render=Path('/tmp/epl2_lane6_r17_render');render.mkdir(exist_ok=True);(render/'build.tex').write_text('\\pdfmapfile{+newtx.map}\n\\input{'+str(P/'EP_L2_EN_v5_SAD.tex')+'}\n');env=dict(os.environ,TEXINPUTS='/tmp/ep-l2-lane6-r5-texdeps//:'+str(P)+'//:')
 for k in ['TFMFONTS','VFFONTS','T1FONTS','ENCFONTS','TEXFONTMAPS']:env[k]='/tmp/ep-l2-lane6-r5-texdeps//:'
 for n in [1,2]:
  with (render/f'pass{n}.log').open('w') as log:subprocess.run(['timeout','45','nice','-n','10','pdflatex','-interaction=nonstopmode','-halt-on-error','-no-shell-escape','-no-mktex=pk','-no-mktex=tfm','-jobname=EP_L2_EN_v5_SAD','build.tex'],cwd=render,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 pdf=(render/'EP_L2_EN_v5_SAD.pdf').read_bytes();write('EP_L2_EN_v5_SAD.pdf',pdf);write('validation/LATEX_FINAL.log',(render/'pass2.log').read_text());info=subprocess.check_output(['pdfinfo',str(render/'EP_L2_EN_v5_SAD.pdf')],text=True);fonts=subprocess.check_output(['pdffonts',str(render/'EP_L2_EN_v5_SAD.pdf')],text=True);extracted=subprocess.check_output(['pdftotext',str(render/'EP_L2_EN_v5_SAD.pdf'),'-'],text=True);pages=[x for x in extracted.split('\f') if x.strip()];assert len(pages)==5 and 'references' in pages[4].lower();assert 'Type 3' not in fonts;assert not any(t in (render/'pass2.log').read_text() for t in ['Overfull','undefined','Warning:']);write('validation/PDF_INFO.txt','\n'.join(x.rstrip() for x in info.splitlines())+'\n');write('validation/PDF_FONTS.txt',fonts);write('validation/LAYOUT.json',{'pages':5,'technical_pages':4,'reference_only_pages':1,'PDF_bytes':len(pdf),'PDF_sha256':sha(pdf),'Type3':False,'overfull_undefined':False,'new_performance_plots':False})
 write('README.md',f'''# Lane6 r17 SAD intake and EN-v5 update\n\nSAD independently received through current V2/native/identity/full trace/raw64-slice checks. Lane6 numerical coverage1/5; current official coverage{official}/5. No group geomean or five-workload figure. See SAD_RESULT_AND_CAUSAL_ANALYSIS.md and SAD_RESULTS.csv; source is raw evidence, not copied coordination numbers.\n\nEN-v5 exact editorial basis retained; EN-v5-SAD makes only qualification/status/first-negative-control updates. Architecture, figure reservations, ten references and4+1 budget preserved. Old EN-v4 and all prior review packs unchanged. No simulator/build/registry claim or mutation, no other process changes, no persistent polling.\n\nThe namespace sandbox could not start; task-specific approved read/ingest commands were used. Compatibility failures (publication listing, certificate spelling, actual scope/interval raw tag) were resolved in the new consumer without weakening gates or editing upstream assets.\n''')
 # Integrity and provenance include all source bindings from the successful native packet.
 manifest=json.loads((P/'SOURCE_MANIFEST.json').read_text());manifest['native_source_bindings']=evidence['packet']['source_bindings'];manifest['accepted_runtime_identity']=evidence['packet']['runs'][0]['identity'];manifest['current_authority']=authority;write('SOURCE_MANIFEST.json',manifest)
 oldnames=git('ls-tree','-r','--name-only','113eb6accb520db409b40193fba901089a723d20','--','docs/ep_l2/review_packs').decode().splitlines();ownold=[x for x in oldnames if any(t in x for t in ['LANE6_PAPER_PPA_r','LANE6_R14_REVIEW_r1'])]
 for name in ownold:assert (R/name).read_bytes()==git('show','113eb6accb520db409b40193fba901089a723d20:'+name)
 write('validation/PRESERVATION.json',{'old_files_unchanged':len(ownold),'base':'113eb6accb520db409b40193fba901089a723d20','simulators_builds_ledger_writes':0})
 files=sorted(f for f in P.rglob('*') if f.is_file() and f.name!='SHA256SUMS');write('SHA256SUMS',''.join(sha(f.read_bytes())+'  '+str(f.relative_to(P))+'\n' for f in files))
 handoff=R/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane6';identity=evidence['packet']['runs'][0]['identity'];receipt={'schema_version':'EP_L2_FT_LANE_RECEIPT_V1','lane_id':6,'task_id':'EP_L2_FT20261016_LANE6_PAPER_PPA_V1','status':'R17_SAD_INDEPENDENTLY_INGESTED_EN_V5_UPDATED','coordination_commit':'3e3920a42a865c90af37330ffe95b6bbb9d61537','framework_branch':'hrl/ep-l2-ft20261016-lane6-v1','lane6_start_HEAD':'113eb6accb520db409b40193fba901089a723d20','core_source_commit':identity['core_source_commit'],'framework_source_commit':identity['framework_source_commit'],'framework_source_role':'Accepted simulator producer; Lane6 publication identified by containing Git commit','binary_sha256':identity['binary_sha256'],'config_sha256':{x['mode']:x['identity']['runtime_config_sha256'] for x in json.loads((P/'SAD_IDENTITY_AND_CLOSURE.json').read_text())},'trace_identity':identity['trace_content_sha256'],'scientific_acceptance':{'authority':authority,'Lane6_received_pairs':1,'paper_numerical_pairs':1,'official_accepted_pairs_at_intake':official,'group_geomean':None,'old_withdrawals_preserved':True,'numeric_SASS_output_verified':False},'review_pack':str(P.relative_to(R)),'editorial_basis':manifest['editorial_commit'],'paper':'EP_L2_EN_v5_SAD','validation':{'native_scope_checks':6,'source_bound_terminal_reparse_arms':2,'slices_each_arm':64,'full_trace_bodies_rehashed':True,'binary_config_raw_rehashed':True,'production_builds':0,'simulator_runs':0,'registry_lease_writes':0,'raw_scientific_CSV_edits':0,'persistent_poller':False,'four_technical_plus_one_reference_pages':True,'old_files_preserved':len(ownold)},'pending':['Remaining four Lane6 native intakes; official acceptance and paper intake are distinct','No group mean until all five independently ingested','Separate contracts/qualification for static repartition, WBUF8, TVD/RO and Ideal','Physical RTL/macros/STA/power evidence absent'],'artifacts':[{'path':str(f.relative_to(R)),'sha256':sha(f.read_bytes())} for f in sorted(P.rglob('*')) if f.is_file()]};(handoff/'RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 (handoff/'STATUS.md').write_text(f'''# Lane6 r17 — SAD received, EN-v5 minimally updated\n\nOriginal branch/worktree retained. Current V2 generation{authority['generation']} at `{authority['publication_commit']}` independently consulted; two SAD rows remain CURRENT_ACCEPTED. Native producer/qualification/config/binary/trace/raw identities verified; full trace bodies rehashed; original source-bound parser reproduces both64-slice hardware terminals. RuntimeCore `{identity['core_source_commit']}`, Framework `{identity['framework_source_commit']}`, binary `{identity['binary_sha256']}`.\n\nSAD cycles110773/110749, copy3975/0, logical bank ops483611/475661; WB-data-full0/0. Near tie, no capacity-benefit or across-application conclusion, no statistical-significance/physical-energy claim. Full table and causal limits are in `{P.relative_to(R)}/SAD_RESULT_AND_CAUSAL_ANALYSIS.md`.\n\nThis Lane6 revision consumes1/5; official current ledger already accepts{official}/5. Others are metadata-discovered, not numerical paper intake. No five-workload chart/group geomean. Exact independent EN-v5 preserved as basis, outdated21/open-qualification/zero-result prose minimally updated to31+11gate and scoped SAD evidence. Architecture, pending Fig2–4, ten references and4+1 PDF budget retained. Old EN-v4 and all prior packs unchanged. PPA remains unmeasured.\n\nNew native adapter preserves original checks; current publication pack bytes equal original9aad3338, exact two symbolic-scope spellings accepted only with full-native-nonatomic/per-spec proof. Actual raw application tag uses scope/interval, not window. Six new narrow guards pass. Event-driven incremental entry prepared; unknown schema fails closed. No simulator/build/new experiment/ledger/process mutation or persistent poller. Reports and exact artifacts committed/pushed on original branch, final HEAD established by remote readback.\n''')
 print(json.dumps({'ready_for_commit':True,'files':len(receipt['artifacts']),'received_pairs':1,'official_pairs':official,'PDF_bytes':len(pdf)}))

if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='receive':receive()
 elif sys.argv[1]=='finish':finish()
 elif sys.argv[1]=='scope':
  c=git('rev-parse','origin/hrl/ep-l2-ft20261016-lane5-v1').decode().strip();source=git('show',c+':util/ep_l2/ft_lane5/run.py').decode();lines=source.splitlines()
  for i,line in enumerate(lines):
   if 'atomic_input_scope' in line or 'proof_identity' in line or 'validate_nonatomic' in line:print('\n'.join(lines[max(0,i-8):i+25]))
 elif sys.argv[1]=='debug':
  raw=Path('/workspace/results/ep_l2_ft20261016/734ba20d8648a25fb5930c4b8f2c207f658eca924a2d4c52ed0f24d19edbd533/raw.log')
  for line in raw.open():
   if 'bank_logical_ops=' in line and ('application' in line or 'cumulative' in line):print(line[:1200]);break
  print('LAST TAGS',[(x[:250]) for x in raw.read_text().splitlines() if x.startswith('EPL2')][-8:])
 else:raise ValueError('Unknown action')
