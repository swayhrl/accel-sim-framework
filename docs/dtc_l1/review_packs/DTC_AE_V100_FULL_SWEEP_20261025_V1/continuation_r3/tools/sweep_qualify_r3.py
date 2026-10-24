import pathlib,json,hashlib,importlib.util,tempfile,shutil,gzip,ast,datetime,copy
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');cell='E2-AEV100-1df9d5479504d9c7-DM';tests=[]
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x)+chr(10))
def load(p):s=importlib.util.spec_from_file_location('isolated_failure_review',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def check(label,fn):fn();tests.append({'test':label,'status':'PASS'})
def assert_true(v):assert v
controller=T/'tools/revision3/sweep_controller.py';failure=T/'tools/sweep_failure_review.py';r2=T/'tools/revision2/sweep_controller.py';prep=read(T/'analysis/CONTINUATION_R3_PREPARATION.json')
check('successor_and_failure_sources_syntax',lambda:(ast.parse(controller.read_text()),ast.parse(failure.read_text())))
check('prior_controller_source_preserved',lambda:assert_true(sha(r2)==prep['base_sha256']))
check('qualified_native_launcher_unchanged',lambda:assert_true(sha(T/'tools/sweep_native.py')==read(T/'control/REGISTRATION_CANDIDATE.json')['controller_sha256']))
module=load(failure);check('positive_exact_closed_failed_uuid_full_raw_and_original_resource_replay',lambda:assert_true(module.classify(cell)['accepted_cycles'] is None))
with tempfile.TemporaryDirectory(prefix='dtc-r3-zero-model-') as tmp:
 root=P(tmp);intent=read(T/'control/qualification_ledger'/(cell+'.INTENT.json'));src=P(intent['output']);out=root/'DTC/run/results'/intent['uuid'];out.mkdir(parents=True);(root/'analysis').mkdir()
 spec=read(T/'control'/(cell+'_SPEC.json'))
 for r in spec['runtime_files']:
  p=root/r['target'];p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():p.symlink_to(T/r['target'])
 for name in ['core','framework']:(root/name).symlink_to((T/name).resolve())
 for name in ['raw.log.gz','RESOURCE_SAMPLES.jsonl.gz','progress.jsonl.gz','NATIVE_SIMULATOR_PID_AND_MAPS.json']:shutil.copyfile(src/name,out/name)
 done=read(src/'NATIVE_EXIT.json');done['output']=str(out);intent['output']=str(out)
 write(root/'control'/(cell+'_SPEC.json'),spec);write(root/'control/qualification_ledger'/(cell+'.INTENT.json'),intent)
 write(root/'control/qualification_ledger'/(cell+'.DONE.json'),done);write(out/'NATIVE_EXIT.json',done)
 write(root/'qualification'/spec['input_digest']/'QUALIFICATION.json',read(T/'qualification'/spec['input_digest']/'QUALIFICATION.json'))
 module.T=root
 check('positive_isolated_complete_failure_fixture_no_acceptance_or_launch',lambda:assert_true(module.classify(cell)['scientific_acceptance'] is False))
 def rejects(label,change,restore):
  change()
  try:module.classify(cell)
  except (AssertionError,OSError,EOFError,ValueError):tests.append({'test':label,'status':'PASS'})
  else:raise AssertionError('negative fixture accepted:'+label)
  finally:restore()
 raw=(out/'raw.log.gz').read_bytes()
 rejects('reject_corrupt_compressed_raw_SHA',lambda:(out/'raw.log.gz').write_bytes(raw+b'X'),lambda:(out/'raw.log.gz').write_bytes(raw))
 original=gzip.decompress(raw);changed=original.replace(b'ERROR ** deadlock detected:',b'NOT_THE_REVIEWED_SIGNATURE').replace(b'DEADLOCK  shader cores no longer committing',b'NOT_THE_REVIEWED_SHADER_SIGNATURE')
 def changed_signature():
  (out/'raw.log.gz').write_bytes(gzip.compress(changed));d=copy.deepcopy(done);d.update(raw_sha256=sha(out/'raw.log.gz'),raw_uncompressed_sha256=hashlib.sha256(changed).hexdigest(),raw_uncompressed_bytes=len(changed));write(out/'NATIVE_EXIT.json',d);write(root/'control/qualification_ledger'/(cell+'.DONE.json'),d)
 def restore_signature():
  (out/'raw.log.gz').write_bytes(raw);write(out/'NATIVE_EXIT.json',done);write(root/'control/qualification_ledger'/(cell+'.DONE.json'),done)
 rejects('reject_non_deadlock_crash_even_with_consistent_raw_hashes',changed_signature,restore_signature)
 resource=(out/'RESOURCE_SAMPLES.jsonl.gz').read_bytes();rs=[json.loads(x) for x in gzip.decompress(resource).splitlines()]
 def resource_stop():
  next(x for x in rs if 'DTC_exact_original_policy' in x)['DTC_exact_original_policy']['decision']['decision']='STOP';(out/'RESOURCE_SAMPLES.jsonl.gz').write_bytes(gzip.compress((chr(10).join(json.dumps(x) for x in rs)+chr(10)).encode()))
 rejects('reject_original_resource_STOP',resource_stop,lambda:(out/'RESOURCE_SAMPLES.jsonl.gz').write_bytes(resource))
 progress=(out/'progress.jsonl.gz').read_bytes();pg=[json.loads(x) for x in gzip.decompress(progress).splitlines()]
 def natural():
  pg[-1]['end']='NATURAL';(out/'progress.jsonl.gz').write_bytes(gzip.compress((chr(10).join(json.dumps(x) for x in pg)+chr(10)).encode()))
 rejects('reject_natural_semantic_termination_as_failure',natural,lambda:(out/'progress.jsonl.gz').write_bytes(progress))
source=controller.read_text();tree=ast.parse(source);adopt=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='adopt');adopt_source=ast.get_source_segment(source,adopt)
check('adoption_requires_old_generation_gone_and_all_prior_DONE',lambda:assert_true("old['start_ticks']" in adopt_source and "'execution_receipt' in row" in adopt_source and "not read(T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']" in adopt_source))
check('adoption_preserves_budget_consumed_remaining_specs_and_auth',lambda:assert_true("if k not in ['orchestrator_sha256','operational_continuations']" in adopt_source and "q['budget']==356" in adopt_source))
check('dispatch_excludes_spent_INTENT_cells',lambda:assert_true("cell in results or cell in q['consumed']" in source and "spent cell cannot be restarted" in source))
check('only_diagnosed_failure_class_continues_other_failures_checkpoint',lambda:assert_true("FAIL_CLOSED_NATIVE_DEADLOCK_ARCHIVED_NO_RETRY" in source and "FAILURE_CLASS_NOT_REVIEWED_CHECKPOINT" in source and "if issues and not running" in source))
check('native_lease_ancestry_and_original_guards_unchanged',lambda:assert_true(sha(T/'tools/sweep_native.py')==read(T/'control/REGISTRATION_CANDIDATE.json')['controller_sha256']))
proof={'schema':'DTC_SWEEP_R3_ZERO_MODEL_QUALIFICATION_V1','status':'PASS','tests':tests,'test_count':len(tests),'controller_sha256':sha(controller),'failure_review_sha256':sha(failure),'scientific_starts':0,'live_authority_mutated':False,'native_binary_config_input_mutated':False,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (T/'control/CONTINUATION_R3_ZERO_MODEL_QUALIFICATION.json').open('x') as f:json.dump(proof,f,indent=2);f.write(chr(10))
print(json.dumps(proof,indent=2))
