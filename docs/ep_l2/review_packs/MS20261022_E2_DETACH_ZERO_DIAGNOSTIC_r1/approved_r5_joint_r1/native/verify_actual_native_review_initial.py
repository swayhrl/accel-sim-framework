import sys,json,hashlib,importlib.util
from pathlib import Path
sys.path.insert(0,'/tmp/e2_r5_parser_candidate');import decoder
D=Path('/tmp/e2_r5_native_independent_review_r1');D.mkdir(exist_ok=True)
N=Path('/workspace/ep_l2_ms20261019_e_results/E2_R5_NATIVE_1093_r1/native_steps');B=Path('/workspace/ep_l2_ms20261019_e_results/E2_R5_BUILD_1093_r1/build_steps/BUILD_ARTIFACTS.json')
P=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1');F=P/'parser_recovery/decoder_samecycle_close.py';assert hashlib.sha256(F.read_bytes()).hexdigest()==decoder.FIXED_R4_SHA256
sp=importlib.util.spec_from_file_location('r4fixed_actual',F);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
r=json.loads((N/'RECEIPT.json').read_text());build=json.loads(B.read_text());binding={**build['source_identity'],'binary_sha256':build['artifacts']['main']['sha256'],'archive_sha256':build['artifacts']['archive']['sha256']};schema=json.loads((P/'runtime_r4/SOURCE_BOUND_SCHEMA_r4.json').read_text());fields=schema['counter_fields'];rows=[];allbytes=0
for t in r['tests']:
 raw=Path(t['raw_path']).read_bytes();allbytes+=len(raw);assert len(raw)==t['raw_bytes'];assert hashlib.sha256(raw).hexdigest()==t['raw_sha256'];assert t['actual_native_wait_exit']==0 and not t['timeout'] and not t['output_limit_exceeded']
 frames=[];current=None
 for ln,line in enumerate(raw.splitlines(keepends=True),1):
  if line.startswith(b'DETACH_NATIVE_FRAME_BEGIN|'):
   assert current is None;current={'name':line.decode().strip().split('|',1)[1],'lines':[],'start_line':ln};continue
  if line.startswith(b'DETACH_NATIVE_FRAME_END|'):
   assert current and current['name']==line.decode().strip().split('|',1)[1];current['end_line']=ln;frames.append(current);current=None;continue
  if current is not None:current['lines'].append((ln,line))
 assert current is None
 out={'id':t['id'],'variant':t.get('variant'),'raw_ref':{'path':t['raw_path'],'sha256':t['raw_sha256'],'bytes':len(raw)},'actual_native_exit':0,'frame_count':len(frames),'frames':[]}
 for fr in frames:
  old=[];invalid=[];normal=[]
  for ln,line in fr['lines']:
   if line.startswith(decoder.OLD):old.append(json.loads(line[len(decoder.OLD):]))
   if line.startswith(decoder.PREFIX):
    v=json.loads(line[len(decoder.PREFIX):]);(invalid if v.get('record')=='OUTPUT_INVALID' else normal).append({'line':ln,'record':v})
  record={'name':fr['name'],'source_lines':[fr['start_line'],fr['end_line']],'old212_record_count':len(old),'r5_normal_record_count':len(normal),'invalid_markers':invalid}
  if old:
   slices=[x for x in old if x['record']=='SLICE'];glob=[x for x in old if x['record']=='GLOBAL'];assert len(glob)==1;g=glob[0];checks=0
   for x in old:
    if x['record'] not in ('SLICE','PHASE','GLOBAL'):continue
    assert set(x['counters'])==set(fields)
    for k,v in x['counters'].items():assert type(v) is int and 0<=v<2**64
    m.partitions(x['counters']);m.r3_partitions(x['counters'],x['M']);checks+=1
   for s in slices:
    phases=[x for x in old if x['record']=='PHASE' and x['slice']==s['slice']]
    for k in fields:assert sum(x['counters'][k] for x in phases)==s['counters'][k];checks+=1
   for k in fields:assert sum(x['counters'][k] for x in slices)==g['counters'][k];checks+=1
   record['old212_math']={'status':'PASS_SCOPE_SELECTED_EQUATIONS_AND_EXACT_GLOBAL_NUMERIC_ROLLUP_ONLY','checks':checks,'selected_slices':[s['slice']for s in slices],'registered_count':g['slice'],'global_epoch_closed':g['epoch_closed'],'global_closure_ok':g['closure_ok'],'head_absent_cycles':g['counters']['head_absent_cycles'],'full64_qualification':False}
   if t.get('variant')=='R5_ON':
    flags={k:slices[0][k] for k in ('T','M','ro_runtime')};feed=decoder.Feed(expected_slices=[s['slice']for s in slices],registered_slice_count=g['slice'],expected_kernels=[],expected_flags=flags,source_binding=binding,old212_decoder_sha256=decoder.FIXED_R4_SHA256,full_application=False,allow_incomplete_native_global=True)
    for _,line in fr['lines']:feed.feed(line)
    record['independent_r5_decoder']={'status':'REJECTED' if feed.error else 'NOT_CLOSED','sticky_error':feed.error,'observed_r5_records':feed.records,'snapshots':feed.snapshots,'source_binding':binding}
    assert not normal and feed.snapshots==0
    if invalid:assert feed.error=='source OUTPUT_INVALID marker'
    else:assert feed.records==0
  out['frames'].append(record)
 rows.append(out)
result={'schema':'E2_R5_REAL_NATIVE_POSTERIOR_INDEPENDENT_REVIEW_V1','status':'R5_REJECTED_OUTPUT_INVALID_NO_OBSERVER_QUALIFICATION','source_identity':binding,'native_binary':build['artifacts']['native'],'native_receipt_ref':{'path':str(N/'RECEIPT.json'),'sha256':hashlib.sha256((N/'RECEIPT.json').read_bytes()).hexdigest()},'build_ref':{'path':str(B),'sha256':hashlib.sha256(B.read_bytes()).hexdigest()},'native_invocations':len(rows),'actual_native_exit0':len(rows),'raw_bytes_verified':allbytes,'r5_on_cases':sum(x['variant']=='R5_ON' for x in rows),'r5_invalid_frames':sum(bool(f['invalid_markers']) for x in rows for f in x['frames']),'r5_normal_frames':sum(f['r5_normal_record_count'] for x in rows for f in x['frames']),'counter_equations':'Old212 fixed647 partitions/r3 and PHASE→selected SLICE→GLOBAL numeric sums checked independently per actual FRAME, never concatenated fixture epochs','scope_boundary':'Native exit0 / original semantic assertions do not grant r5 wire/math PASS; registered2/open GLOBAL preserved; no full64 qualification','rows':rows,'parser_ref':{'path':'/tmp/e2_r5_parser_candidate/decoder.py','sha256':hashlib.sha256(Path('/tmp/e2_r5_parser_candidate/decoder.py').read_bytes()).hexdigest()},'actual_actions':{'native_runs':0,'builds':0,'apps':0,'production_mutations':0}}
(D/'REVIEW.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ('status','native_invocations','r5_on_cases','r5_invalid_frames','r5_normal_frames','raw_bytes_verified')},indent=2));print('reviewsha',hashlib.sha256((D/'REVIEW.json').read_bytes()).hexdigest())
