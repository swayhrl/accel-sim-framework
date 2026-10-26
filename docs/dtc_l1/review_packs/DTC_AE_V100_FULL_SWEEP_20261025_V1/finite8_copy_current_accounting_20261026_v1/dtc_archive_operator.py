"""Finite8 archive operation using the already-published truthful R19 COPY gate.
Only private module namespace is adapted; frozen source/manifest/COPY primitives
and all original evidence and native-device restoration checks stay unchanged.
"""
import pathlib,json,hashlib,importlib.util,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');D=F/'ops/finite8_archive_current_gate_v1';O=F/'ops';QUALIFIED_GATE=F/'validation_remaining_failure_v1/tools/remaining_outbox_v1.py';GATE_SHA='e285ea59eea863e52cd9bc482ae9d9cf20e76555c2824577383dc5981781a00b'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def install(base,gate):
 original_root=base.ROOT;original_nas=base.NAS;original_cohorts=dict(base.COHORTS);base.gate=gate;assert base.ROOT==original_root and base.NAS==original_nas and base.COHORTS==original_cohorts;return base
def adapted_loader(original,gate):
 def loader(path,name):
  module=original(path,name)
  return install(module,gate)if P(path)==T/'tools/sweep_outbox.py'else module
 return loader
def actual_gate():
 assert sha(QUALIFIED_GATE)==GATE_SHA;overlay=load('published_R19_current_COPY_resource_gate',QUALIFIED_GATE);private=overlay.adapted();gate=private.gate;sample=gate(16*1024**2);assert sample['schema']=='R19_FIVE_SCOPE_EXACT_FUTURE_WRITES_ACTUAL_RAM_V1'and sample['copy_overlay_sha256']==GATE_SHA and sample['local_safety_floor_bytes']==5*1024**3;return gate,sample
def apply():
 pub=read(D/'PUBLICATION_READBACK.json');qual=read(D/'CPU_QUALIFICATION.json');assert pub['verified']and pub['operator_sha256']==qual['operator_sha256']==sha(__file__)and pub['qualification_sha256']==sha(D/'CPU_QUALIFICATION.json')and qual['status']=='PASS';assert not(D/'ACTUAL_ARCHIVE_BINDING.json').exists();gate,before=actual_gate();review=load('frozen_exact8_negative_reviewer',O/'review_eight_original_expected_growth_v1.py');original_loader=review.load;review.load=adapted_loader(original_loader,gate);results=review.apply(O/'EIGHT_ORIGINAL_EXPECTED_GROWTH_READ_ONLY_PLAN_V1.json',O/'EIGHT_GROWTH_PUBLICATION_READBACK.json');assert len(results)==8 and all(x['state']=='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY'and x['accepted_cycles']is None for x in results)
 proof=dict(status='FINITE8_REAL_164_COPY_AND_NATIVE2128_RESTORE_VERIFIED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),operator_sha256=sha(__file__),publication_commit=pub['commit'],qualified_R19_gate_source_path=str(QUALIFIED_GATE),qualified_R19_gate_source_sha256=GATE_SHA,unchanged_original_outbox_source_sha256=sha(T/'tools/sweep_outbox.py'),frozen_review_tool_sha256=sha(O/'review_eight_original_expected_growth_v1.py'),resource_sample_before=before,negative_closures=[dict(cohort=r['cohort'],uuid=r['uuid'],old_RESULT_sha256=r['old_RESULT_sha256'],native_restore=r['archive']['receipt']['native_restore'],archive_sha256=r['archive']['receipt']['archive_sha256'],verified_entries=r['archive']['independently_verified_restored_entries'])for r in results],authority_or_old_RESULT_or_scientific_source_mutations=0,scientific_starts=0,scientific_model_signals=0,native_runtime_floor_bytes=5*1024**3)
 with(D/'ACTUAL_ARCHIVE_BINDING.json').open('x')as f:json.dump(proof,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in proof.items()if k not in['resource_sample_before','negative_closures']},indent=2))
if __name__=='__main__':apply()
