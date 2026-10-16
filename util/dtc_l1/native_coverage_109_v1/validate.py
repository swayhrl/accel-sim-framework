#!/usr/bin/env python3
import csv,hashlib,json,pathlib,subprocess
repo=pathlib.Path(__file__).resolve().parents[3];pack=repo/'docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1';root=pathlib.Path('/data/c16/dtc_native_coverage_109_v1');checks=[]
def check(name,predicate):assert predicate,name;checks.append(name)
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
r=json.loads((pack/'PREREGISTRATION.json').read_text());fixed=list(csv.DictReader((pack/'R0_FIXED_COHORT.tsv').open(),delimiter='\t'))
check('fixed_cohort_12_programs_629_ordered_members',len(fixed)==12 and sum(int(x['recorded_members']) for x in fixed)==629)
check('preregistration_unchanged_since_before_measurement',subprocess.check_output(['git','show','c24ffbb9:docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/PREREGISTRATION.json'],cwd=repo)==(pack/'PREREGISTRATION.json').read_bytes())
for n in ['diagnostic.cu','layernorm.py']:
 check(n+'_measurement_source_unchanged',subprocess.check_output(['git','show','57aa1b80:util/dtc_l1/native_coverage_109_v1/'+n],cwd=repo)==(repo/'util/dtc_l1/native_coverage_109_v1'/n).read_bytes())
ss=json.loads((pack/'TIMING_SAMPLES.json').read_text());names=r['diagnostic_conditions']+['SpMV','LayerNorm_1024','LayerNorm_8192']
check('15_cases_7_independent_batches_10_samples',len(ss)==105 and all(sum(x['case']==n for x in ss)==7 for n in names) and all(len(x['samples_ms'])==10 for x in ss))
check('all_recorded_native_commands_exit_zero',all(json.loads(l)['returncode']==0 for l in (root/'raw/COMMANDS.jsonl').read_text().splitlines()))
prof=list(csv.DictReader((pack/'PROFILE_METRICS.tsv').open(),delimiter='\t'));check('15_complete_roi_profiles',len(prof)==15 and {x['case'] for x in prof}==set(names))
trace=json.loads((pack/'TRACE_AUDIT.json').read_text());check('10_complete_trace_members',len(trace)==10 and all(x['coverage']=='PASS_ALL_DECLARED_WARPS_IN_ALL_CTAS' for x in trace))
check('actual_cubin_versions_not_device_inferred',all(x['header']['binary version']==('89' if x['case']=='SpMV' else '86') for x in trace))
check('layernorm_trace_not_admitted',all(x['simulator_admission'].startswith('NOT_ADMITTED') for x in trace if x['case']=='LayerNorm_1024'))
for x in trace:check('trace_sha_'+x['case']+'_'+str(x['order']),sha(root/x['path'])==x['sha256'])
ids=json.loads((pack/'BINARY_FRAMEWORK_INPUT_IDENTITY.json').read_text())
for x in ids:check('binary_input_identity_'+x['path'],sha(x['path'])==x['sha256'])
capture=(root/'traces_env_ready/LayerNorm_1024/capture.log').read_text();cp=json.loads(next(l for l in capture.splitlines() if l.startswith('{"family"')));baseline=next(x for x in ss if x['case']=='LayerNorm_1024')
check('capture_and_native_same_input_output',cp['input_sha256']==baseline['input_sha256'] and cp['output_sha256']==baseline['output_sha256'])
store=json.loads((pack/'DURABLE_STORE_RECEIPT.json').read_text());idx=json.loads((pack/'RAW_PAYLOAD_INDEX.json').read_text());check('independent_destination_all_payload_files_verified',store['status'].startswith('PASS_') and store['verified_files']==len(idx)==285)
result=dict(status='PASS',checks=len(checks),results=checks,scope='Native/producer evidence validation only; no DTC simulator/opcode admission')
(pack/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
