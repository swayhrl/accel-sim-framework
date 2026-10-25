"""Replay actual natural DONE evidence; mutate only private in-memory negatives."""
import pathlib,json,hashlib,importlib.util,gzip,copy,types,io,ast,datetime,re
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1/validation');ROOT=R.parent/'ops';WRAPPER=ROOT/'repair_strict_postprocess_v2.py';OUT=R/'analysis/postprocess_v2';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
v2=load('qualified_strict_postprocess_v2',WRAPPER);before=sha(v2.BASE);positive=[];negative=[];samples={}
for mode in ['LEGACY','BASE','IO','OO','SECTOR']:
 cell='E2-AEREPAIR-SENT-a24dde1bad963516-'+mode+'-V1';spec=read(R/'control/specs'/(cell+'.json'));binding=read(spec['input_binding_path']);intent=read(R/'control/qualification_ledger'/(cell+'.INTENT.json'));out=P(intent['output']);done=read(out/'NATIVE_EXIT.json');raw=gzip.decompress((out/'raw.log.gz').read_bytes()).decode();base=v2.adapted();old=base.load('postprocess_legacy_population',base.T/'tools/sweep_strict_cap1m.py');legacy=old.legacy();domain=binding['qualification']
 # Unmodified v1 callback really rejects this historical expectation defect.
 pure=load('unmodified_registered_strict_for_negative_'+mode,v2.BASE)
 try:pure.sentinel_population(raw,spec,domain,legacy);raise RuntimeError('unmodified v1 unexpectedly accepted')
 except AssertionError:pass
 proof=v2.terminal(cell);assert proof['correctness_validation_passed'] and proof['accepted_cycles'] is None and proof['performance_accepted'] is False and proof['instructions']==288 and proof['CTA']==1 and proof['kernel_count']==1 and proof['strict_overlay_sha256']==v2.BASE_SHA256 and proof['registered_v1_sentinel_population_unmodified_PASS'] is False
 assert done['stop_reason'] is None and done['launcher_wait_returncode']==0 and done['uuid']==proof['uuid']
 path=OUT/(cell+'.TRACE_AND_COUNTER_POSTPROCESS_V2_PROOF_CANDIDATE.json')
 with path.open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
 positive.append({'cohort':cell,'uuid':done['uuid'],'mode':mode,'result':'FULL_UNCHANGED_V1_TERMINAL_BODY_PLUS_EXACT_TRACE_CORRECTION_PASS','proof_candidate_path':str(path),'proof_sha256':sha(path),'raw_compressed_sha256':sha(out/'raw.log.gz'),'raw_uncompressed_sha256':done['raw_uncompressed_sha256'],'base_unmodified_sentinel_callback_rejected':True,'instructions':288,'CTA':1,'kernels':1})
 samples[mode]=(cell,spec,domain,raw,legacy,out)
def reject(name,fn):
 try:fn();raise RuntimeError('negative unexpectedly accepted: '+name)
 except (AssertionError,KeyError,ValueError):negative.append({'case':name,'rejected':True})
cell,spec,domain,raw,legacy,out=samples['IO']
pop=v2.adapted().sentinel_population
reject('wrong_trace_in_actual_raw_echo',lambda:pop(raw.replace(domain['trace_entry'],'/wrong/input/kernelslist.g'),spec,domain,legacy))
wrong=copy.deepcopy(spec);wrong['expected_options']['-gpgpu_dtc_l1_oo_pib_entries']=['127'];reject('one_of_other269_option_expectations_wrong',lambda:pop(raw,wrong,domain,legacy))
reject('wrong_M4_atomic_admission_counter',lambda:pop(raw.replace('DTC_L1_m4_atomic_admits = 2','DTC_L1_m4_atomic_admits = 3'),spec,domain,legacy))
reject('unequal_actual_lower_credit_counters',lambda:pop(raw.replace('DTC_L1_lower_credit_released = 2','DTC_L1_lower_credit_released = 1'),spec,domain,legacy))
reject('wrong_population_instructions',lambda:pop(raw.replace('gpu_sim_insn = 288','gpu_sim_insn = 289'),spec,domain,legacy))
reject('wrong_CTA_population',lambda:pop(raw.replace('gpu_tot_issued_cta = 1','gpu_tot_issued_cta = 2'),spec,domain,legacy))
reject('wrong_mode',lambda:pop(raw.replace('DTC_L1_mode = PAPER_IO','DTC_L1_mode = PAPER_OO'),spec,domain,legacy))
reject('forbidden_deadlock_signature',lambda:pop(raw+'\ndeadlock detected\n',spec,domain,legacy))
wrongdom=copy.deepcopy(domain);wrongdom['trace_entry']='/other/input';reject('frozen_argv_domain_trace_disagreement',lambda:pop(raw,spec,wrongdom,legacy))
wrong=copy.deepcopy(spec);wrong['native_simulator_argv']+=['-trace',domain['trace_entry']];reject('duplicate_trace_argument',lambda:pop(raw,wrong,domain,legacy))
wrong=copy.deepcopy(spec);wrong['input_digest']='0'*64;reject('non_allowlisted_input_cannot_use_sentinel_correction',lambda:pop(raw,wrong,domain,legacy))
wrong=copy.deepcopy(spec);wrong['expected_options']['-trace']=['/arbitrary/stale/path'];reject('arbitrary_trace_mismatch_is_not_this_exact_copy_defect',lambda:pop(raw,wrong,domain,legacy))
def terminal_with_engine_mutation(change_spec=None,change_q=None):
 base=v2.adapted();original_load=base.load
 def altered_load(name,path):
  engine=original_load(name,path)
  if name=='repair_independent_engine':
   real_registered=engine.registered;real_spec=engine.spec_for
   def registered():
    reg,epoch,q,p=real_registered();q=copy.deepcopy(q)
    if change_q:change_q(q)
    return reg,epoch,q,p
   def spec_for(c):
    value=copy.deepcopy(real_spec(c))
    if change_spec:change_spec(value)
    return value
   return types.SimpleNamespace(registered=registered,spec_for=spec_for,check_input=engine.check_input,output_cap=engine.output_cap)
  return engine
 base.load=altered_load;return base.terminal(cell)
reject('wrong_framework_source_identity',lambda:terminal_with_engine_mutation(lambda s:s.update(framework_commit='0'*40)))
reject('wrong_registered_original_v1_strict_hash',lambda:terminal_with_engine_mutation(change_q=lambda q:q.update(strict_sha256='0'*64)))
reject('wrong_runtime_file_SHA',lambda:terminal_with_engine_mutation(lambda s:s['runtime_files'][0].update(sha256='0'*64)))
reject('wrong_input_binding_SHA',lambda:terminal_with_engine_mutation(lambda s:s.update(input_binding_sha256='0'*64)))
def terminal_with_stream_mutation(filename,mutate):
 base=v2.adapted();actual=gzip.open
 def opened(path,mode='rb',*args,**kwargs):
  if P(path).name!=filename:return actual(path,mode,*args,**kwargs)
  text=actual(path,'rt').read();data=mutate(text)
  return io.StringIO(data) if 't' in mode else io.BytesIO(data.encode())
 base.gzip=types.SimpleNamespace(open=opened);return base.terminal(cell)
def bad_end(text):
 rows=[json.loads(l) for l in text.splitlines()];rows[-1]['end']='NONE';return ''.join(json.dumps(r)+'\n' for r in rows)
def bad_BA(text):
 rows=[json.loads(l) for l in text.splitlines()];changed=0
 for row in rows:
  if 'DTC_exact_original_policy' in row:row['DTC_exact_original_policy']['decision']['decision']='STOP';changed+=1
 assert changed;return ''.join(json.dumps(r)+'\n' for r in rows)
reject('NATURAL_progress_terminal_missing',lambda:terminal_with_stream_mutation('progress.jsonl.gz',bad_end))
reject('original_BA_STOP_rejected',lambda:terminal_with_stream_mutation('RESOURCE_SAMPLES.jsonl.gz',bad_BA))
assert sha(v2.BASE)==before==v2.BASE_SHA256
source=ast.parse(WRAPPER.read_text());assignments=[ast.unparse(n) for n in ast.walk(source) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id=='base' for t in n.targets)];assert assignments==['base.sentinel_population = sentinel_population'],assignments
result={'schema':'DTC_EXACT_SENTINEL_TRACE_AND_COUNTER_NAME_METADATA_POSTPROCESS_V2_CPU_QUALIFICATION','status':'PASS','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'postprocess_reviewer_path':str(WRAPPER),'postprocess_reviewer_sha256':sha(WRAPPER),'registered_base_strict_path':str(v2.BASE),'registered_base_strict_sha256':before,'qualification_driver_path':str(P(__file__)),'qualification_driver_sha256':sha(__file__),'positive_cases':positive,'positive_count':len(positive),'negative_cases':negative,'negative_count':len(negative),'private_module_attribute_assignments':assignments,'frozen_files_modified':0,'authority_mutations':0,'native_INTENT_or_DONE_mutations':0,'scientific_model_starts':0,'original288_touched':False,'all_registered_terminal_checks_preserved':'Original v1 terminal body and its __file__ remain unchanged. Only sentinel_population receives a local spec copy correcting the precisely diagnosed expected-trace field and for IO/OO/SECTOR one counter-name pair. Both names call the identical Core lower-request counters and the same equality predicate remains mandatory. All other269 options, raw/source/runtime/launch/authority/BA/NATURAL/population/counter checks execute unchanged.','correction_scope':'Only two specifically allowlisted engineering sentinel inputs x five modes; no alias mapping for BASE/LEGACY. This is postprocess review, not a claim of unmodified registered v1 PASS or native numerical correctness.'}
path=ROOT/'POSTPROCESS_V2_CPU_QUALIFICATION.json'
with path.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'status':'PASS','source_sha256':sha(WRAPPER),'qualification_path':str(path),'qualification_sha256':sha(path),'positive_cases':len(positive),'negative_cases':len(negative),'scientific_model_starts':0},indent=2))
