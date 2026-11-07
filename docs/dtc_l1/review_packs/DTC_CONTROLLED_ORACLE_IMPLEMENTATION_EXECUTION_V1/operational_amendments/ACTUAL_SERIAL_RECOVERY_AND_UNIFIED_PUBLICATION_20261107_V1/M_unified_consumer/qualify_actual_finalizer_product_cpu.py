"""Call the actual frozen finalizer only in a disposable CPU tree, then consume its output.
No production finalizer invocation; no lock, route installation or registration.
"""
from pathlib import Path
import hashlib,json,types
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1')
O=A/'agents/M_clean_successor_unified_consumer_v2'
S=A/'agents/S_clean_main_successor_preparation_v1'
src=S/'qualify_clean_finalizer_cpu.py'
t=src.read_text()
t=t[:t.index(" check('ACTUAL_FINALIZER_FULL_CALL_COMPLETES_ON_DISPOSABLE_TREE'")]
t=t.replace("HERE=Path(__file__).resolve().parent",'HERE=Path('+repr(str(S))+')')
t=t.replace("prefix='DTC_MOCK_NO_SCIENCE_COMPLETE_FINALIZER_'","prefix='DTC_M_CPU_ONLY_FINALIZER_CONSUMER_'")
t=t.replace("guard=t/'MOCK_ONLY_LIVE_PARENT_BACKEND.py'","guard=root/'tools/MOCK_ONLY_LIVE_PARENT_BACKEND.py'")
t=t.replace("controller=ref(HERE/'oracle_clean_main.py')","controller=ref(root/'tools/oracle_clean_main.py')")
t=t.replace("write(lp,dict(parent,MOCK_CPU_ONLY=True))", "write(lp,dict(parent,MOCK_CPU_ONLY=True,schema='DTC_ORACLE_CLEAN_MAIN_PRIVATE_LEASE_V1',budget=96,old32_new_starts=0,authority_commit='18b1ee9d339902e555fc2e04ef51c84f77dfe1b1',guard_sha256=sha(guard),locks=[dict(role=x)for x in ('governance','owner','qualification','shared')]))")
t=t.replace("plan['execution_root']=str(root)", "plan['execution_root']=str(root)\n # Explicit CPU path relocation of private references, not scientific source/config/input bytes.\n def relocate(v):\n  if isinstance(v,dict):return {k:relocate(x)for k,x in v.items()}\n  if isinstance(v,list):return [relocate(x)for x in v]\n  if isinstance(v,str):return v.replace(str(original),str(root))\n  return v\n plan=relocate(plan)")
t+='''
 # The real function produced this plan/receipt, not a handwritten substitute.
 import importlib.util
 spec=importlib.util.spec_from_file_location('CPU_CONSUMER_V2',OUT/'oracle_unified_roots_consumer.py')
 adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
 cfg=rd(OUT/'UNIFIED_BINDINGS.fixed.json');settings=rd(cfg['science_settings']['path'])
 fixed=rd(cfg['fixed_matrix']['path']);expected={p['plan_id']:p for p in fixed['rows']if not p['initial_fixed8']}
 plan_final=rd(root/'control/EXECUTION_PLAN.json')
 external=[x for x in plan_final['source_pins']if not Path(x['path']).resolve().is_relative_to(root)]
 cc=dict(cfg['remaining24_private'],root=str(root),expected_build_identity=settings['expected_build_identity'],
  expected_plan_rows=expected,matrix_fixed_sha256=sha(root/'control/MATRIX.fixed.json'),allowed_external_source_pins=external)
 proof=adapter.inspect_new_root(root,cc)
 assert proof.get('ready')is True,proof
 assert plan_final['clean_operational_generation']['no_same_PID_exec_continuation']is True
 assert 'same_PID_exec_or_legacy_frame_required'not in plan_final['clean_operational_generation']
 assert len(external)>0
 denied=dict(cc,allowed_external_source_pins=[])
 bad=adapter.inspect_new_root(root,denied);assert not bad.get('ready')and 'UNDECLARED_EXTERNAL_SOURCE_PIN'in bad['reason']
 drift=[dict(x)for x in external];drift[0]['sha256']='0'*64
 bad2=adapter.inspect_new_root(root,dict(cc,allowed_external_source_pins=drift));assert not bad2.get('ready')
 report=dict(status='PASS_ACTUAL_FINALIZER_PRODUCT_CPU_ONLY_CONSUMER',finalizer_source=ref(source),
  source_fixture=ref(SOURCE_FIXTURE),consumer_source=ref(OUT/'oracle_unified_roots_consumer.py'),
  actual_finalizer_function_called=True,explicit_MOCK_parent_and_guard=True,
  explicit_CPU_private_path_relocation_only=True,actual_production_finalizer_calls=0,
  registrations=0,models_started=0,owner_or_tracer_actions=0,production_route_writes=0,
  new_generation_schema=plan_final['clean_operational_generation'],
  external_pins_count=len(external),binding_ready=True,
  undeclared_external_rejected=True,external_wrong_SHA_rejected=True,
  receipt_does_not_establish_real_scientific_authority=True)
 (OUT/'ACTUAL_FINALIZER_PRODUCT_CPU_QUALIFICATION.fixed.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\\n')
 print(json.dumps(report,sort_keys=True))
'''
ns={'__file__':str(src),'OUT':O,'SOURCE_FIXTURE':src}
exec(compile(t,str(src)+'#CPU_consumer_product','exec'),ns)
