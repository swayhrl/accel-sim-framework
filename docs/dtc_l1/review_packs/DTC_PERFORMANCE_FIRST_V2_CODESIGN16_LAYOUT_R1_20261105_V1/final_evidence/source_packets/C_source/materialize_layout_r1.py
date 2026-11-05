"""Complete new layout-R1 CPU materialization, never registry/owner/model actions."""
from pathlib import Path
import argparse,copy,hashlib,json,types,ast
D=Path(__file__).resolve().parent;R=Path('/root/data/dtc_perf_first_v2_codesign16_layout_r1_20261105_v1');A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_layout_r1_execution_20261105_v1');OLD=Path('/root/data/dtc_perf_first_v2_codesign16_20261105_v1');REQ='DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1';AUTH='425ff55a5b57eb28d968bfc8f79eb5f5060e6ebe';AUTH_SHA='5814765fb0b8301d68c0af1ce61a62a3db68a0d8d21f69f79b48816e41c8c48f'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_bytes())
def load(p):
 m=types.ModuleType('R1_CPU_MATERIALIZER_PRIVATE');m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m

def materialize(output_root,fields,fields_sha,policy):
 assert Path(output_root).resolve()==R;assert sha(A/'control/PROJECT_AUTHORITY.fixed.json')==AUTH_SHA;authority=rd(A/'control/PROJECT_AUTHORITY.fixed.json');assert authority['authority_commit']==AUTH and authority['new_request']==REQ and authority['budget']==16
 assert sha(fields)==fields_sha;resource=rd(fields);records=resource.get('records',resource.get('points'));assert resource['request']==REQ and len(records)==16
 dep=rd(D/'DEPENDENCY_PINS.json');matrix=rd(dep['candidate_matrix_path']);u=load(dep['utility_path']);R.mkdir(exist_ok=True)
 for directory in ['tools','analysis','logs','control/specs','control/input_bindings','control/dispatch_bindings','control/qualification_ledger','DTC/control','DTC/run/results','DTC/run/recovery']:(R/directory).mkdir(parents=True,exist_ok=True)
 # Fresh canonical runtime links and four frozen configuration files exist before
 # the complete loader→strace→private-loader→true probes. No simulator invoked.
 for d in dep['selected']:
  base=rd(d['baseline_spec_path'])
  for record in base['runtime_files']:u.runtime_link(R,record)
 for row in matrix['candidates']:
  for i,x in enumerate(row['configs']):assert sha(x['path'])==x['sha256'];u.write_exact(R/'DTC/env'/('DH_'+row['profile'])/('config-'+str(i)+'.config'),Path(x['path']).read_bytes(),R)
 for p in (D/'runtime').glob('*.py'):
  ast.parse(p.read_bytes())
  for target in [R/'tools'/p.name,A/'tools'/p.name]:
   target.parent.mkdir(exist_ok=True);u.write_exact(target,p.read_bytes(),target.parent)
 # Exact pinned recovery metadata is initialized up front, not first discovered
 # missing during successful or negative result archiving.
 pin=Path('/root/data/dtc_perf_first_remaining28_20261104_v1/control/RESULT_ENGINE_PIN.json');assert sha(pin)=='b93dcc20e07082c688f58704a65fd533109d35b01b64180f9f23eaedd3a0e14b';u.write_exact(R/'control/RESULT_ENGINE_PIN.json',pin.read_bytes(),R)
 specs=[]
 for row in matrix['candidates']:
  b=rd(next(d['baseline_spec_path']for d in dep['selected']if d['program']==row['program']));rp=next(x for x in records if x['cohort']==row['proposed_native_cohort']);s=copy.deepcopy(b);s.update(cohort=row['proposed_native_cohort'],program=row['program'],profile=row['profile'],limits=dict(b['limits'],**rp['limits']));argv=list(s['native_simulator_argv']);pos=[i+1 for i,t in enumerate(argv)if t=='-config'];assert len(pos)==4
  for i,j in enumerate(pos):argv[j]=str(R/'DTC/env'/('DH_'+row['profile'])/('config-'+str(i)+'.config'))
  s['native_simulator_argv']=argv;specs.append(s)
 layout=load(D/'runtime/perf16r1_layout.py');ref=layout.initialize(specs,D/'launcher_CPU_evidence')
 builder=load(D/'build_layout_r1_specs.py');receipt=builder.build(R,fields,fields_sha,R);m=rd(R/'control/MATRIX.fixed.json');assert len(m['points'])==16
 # Preserve established contract key schemas; new identities/authority/host
 # layout are explicit. These files themselves do not create registry credits.
 profile=rd(OLD/'control/BUILD_PROFILE.json');profile.update(schema='DTC_PERFV2_CODESIGN16_LAYOUT_R1_BUILD_PROFILE_V1',authority_commit=AUTH,performance_scope='PERFV2_CODESIGN16_LAYOUT_R1_DH_ONLY_NEVER_ORIGINAL_OR_IR_R2',resource_policy_sha256=sha(policy),host_launcher_layout=ref,source_contract='Authorized new layout-R1 sixteen combinations. Same fixed Core/FW/binary/cudart/input/options/configs. No old UUID or refunded credit. First vectorAdd PHYS768 real PID/ROI gate before fifteen.')
 approval=rd(OLD/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json');approval.update(schema='DTC_PERFV2_CODESIGN16_LAYOUT_R1_EXPLICIT_APPROVAL_REQUEST_V1',request=REQ,approved_contract_commit=AUTH,project_authority_sha256=AUTH_SHA,fresh_user_authorization_sha256=authority['user_authorization_sha256'],source_candidate_matrix_sha256=authority['frozen_proposed_matrix_sha256'],source_goal_sha256=authority['execution_goal_sha256'],host_launcher_layout=ref,specs=[{'cohort':p['cohort'],'path':p['canonical_spec_path'],'sha256':p['canonical_spec_sha256']}for p in m['points']],input_digests=sorted({p['input_digest']for p in m['points']}),source_policy='New request16, no old identity reset/refund/reuse. Complete launcher CPU closure plus source qualification, fixed first real vectorAdd PHYS768 with PID/maps+ROI progress and qualified closure before15. Positive and closed-negative full SOURCE_KEEP/true164/native restore, no duplicate models.')
 for name,value in [('BUILD_PROFILE.json',profile),('SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',approval)]:u.write_exact(R/'control'/name,u.encoded(value),R)
 auth=rd(OLD/'control/SCIENCE_AUTHORIZATION.json');auth.update(schema='DTC_PERFV2_CODESIGN16_LAYOUT_R1_EXPLICIT_USER_AUTHORIZATION_V1',approved_contract_commit=AUTH,approval_request_sha256=sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),budgets={p['cohort']:1 for p in m['points']},approval='New explicit user recovery authorization425ff55a. Contract metadata only, not native registration; sole owner and independent qualification still required. Fixed first actualpoint before fifteen; no old credit reuse.')
 u.write_exact(R/'control/SCIENCE_AUTHORIZATION.json',u.encoded(auth),R);u.write_exact(R/'control/RESOURCE_POLICY.json',Path(policy).read_bytes(),R)
 for p in (R/'control').iterdir():
  if p.is_file()and(p.name in ['MATRIX.fixed.json','BUILD_PROFILE.json','SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','SCIENCE_AUTHORIZATION.json','RESOURCE_POLICY.json','RESULT_ENGINE_PIN.json','LAUNCHER_LAYOUT.fixed.json','P0_REFERENCE_INDEX.json','SPEC_BUILD_REFERENCE_TABLE.json']):u.write_exact(A/'control'/p.name,p.read_bytes(),A)
 out=dict(schema='DTC_CODESIGN16_LAYOUT_R1_CPU_MATERIALIZATION_RECEIPT_V1',status='ALL_NAMESPACE_LAYOUT_SPEC_CONTROLS_CPU_READY_NOT_REGISTERED',request=REQ,source_code_sha256=sha(__file__),resource_fields_sha256=fields_sha,resource_policy_sha256=sha(policy),host_launcher_layout=ref,CPU_true_passes=16,new_science_registrations=0,new_simulator_processes=0,new_science_UUIDs_allocated=0,builder_receipt=receipt,control_files=[{'path':str(R/'control'/n),'sha256':sha(R/'control'/n)}for n in ['MATRIX.fixed.json','BUILD_PROFILE.json','SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','SCIENCE_AUTHORIZATION.json','RESOURCE_POLICY.json','RESULT_ENGINE_PIN.json','LAUNCHER_LAYOUT.fixed.json']]);(D/'MATERIALIZATION_RECEIPT.json').write_text(json.dumps(out,indent=2)+'\n');return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output-root',default=R,type=Path);p.add_argument('--resource-fields',required=True,type=Path);p.add_argument('--resource-fields-sha256',required=True);p.add_argument('--resource-policy',required=True,type=Path);a=p.parse_args();print(json.dumps(materialize(a.output_root,a.resource_fields,a.resource_fields_sha256,a.resource_policy),indent=2))
