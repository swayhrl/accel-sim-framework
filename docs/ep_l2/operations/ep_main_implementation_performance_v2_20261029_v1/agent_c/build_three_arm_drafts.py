import copy,csv,hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'host_candidate'))
import three_arm_contract as c
P=pathlib.Path
parent=c.parent()
def ref(p):p=P(p);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def put(p,x):P(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
source={k:'NOT_FROZEN_PENDING_D_MAIN_REVIEW'for k in parent['source_identity']}
newq=ROOT.parent/'agent_d/NEW_SOURCE_IDENTITY.json'
source_evidence=None
if newq.exists():
 d=json.loads(newq.read_text());sid=d.get('source_identity',d)
 if set(sid)==c.SOURCE_KEYS and all(isinstance(v,str)and len(v)in[40,64]for v in sid.values()):source=sid;source_evidence=ref(newq)
points=[]
for arm,(mode,(t,fix))in zip('ABC',c.MODES.items()):
 s=copy.deepcopy(parent)
 s.update(schema='EP_L2_T3_ARM_ENGINEERING_DRAFT_NOT_REGISTERED_V1',goal='EP_L2_MAIN_OBSERVATION_GUIDED_OPTIMIZATION_V2',science_request_id='NOT_REGISTERED_EP_L2_T_THREE_ARM_CONV16X8_V1',cohort='DRAFT_ONLY_EP_T3_CONV16X8_'+arm+'_'+mode,mode=mode,M=True,T=t=='1',ordinary_ro_tag_relief=fix=='1',source_identity=source,old_application_acceptance_inherited=False,application_budget=1,authorization_status='NO_START_AUTHORIZATION',approved_starts=0)
 s['expected_effective_options'][c.T]=t;s['expected_effective_options'][c.CORRECTION]=fix
 s['source_worktrees']={'core':'NOT_FROZEN_NEW_SOURCE_CORE_PATH','framework':'NOT_FROZEN_NEW_SOURCE_FRAMEWORK_PATH'}
 s['binary_path']='NOT_FROZEN_NEW_ELF_PATH';s['static_library_path']='NOT_FROZEN_NEW_ARCHIVE_PATH'
 for k in list(s):
  if k.endswith('_ref')and k not in ['input_binding_ref','modeled_resource_cost_ref']:
   s[k]={'status':'NOT_QUALIFIED_REQUIRES_EXACT_NEW_SOURCE_MODE16X8_AND_HOST_BINDING','path':'NOT_FROZEN','sha256':'NOT_FROZEN'}
 s['pinned_files']={'status':'NOT_FROZEN_DO_NOT_INHERIT_OLD_HOST_LIBRARY_PINS'}
 s['ordered_configs']=[{'status':'NOT_FROZEN_RECONSTRUCT_PARENT_HARDWARE_PLUS_T_AND_CORRECTION_ONLY','parent_path':x['path'],'parent_sha256':x['sha256']}for x in parent['ordered_configs']]
 s['scientific_option_contract']={'legacy_option_count':282,'new_option_count':283,'correction_option':c.CORRECTION,'correction_default':'0','T0_correctionON':'INERT_NOT_PRIMARY_ARM','full_actual_echo':'REQUIRED_FROM_SAME_NEW_ELF_WITHOUT_APP_START','declared_arm_differences':[c.T,c.CORRECTION]}
 s['parent_F_background_only']={'spec_ref':ref('/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_CONV_F_G16_W8_V1/control/FROZEN_SPEC.json'),'old_cycles':367152,'old_detached':237,'reuse_as_new_ELF_performance':False}
 s['RO_certificate_contract']={'manifest_path':parent['expected_effective_options']['-gpgpu_ep_l2_ro_manifest'],'manifest_sha256':parent['expected_effective_options']['-gpgpu_ep_l2_ro_manifest_sha256'],'ranges_path':parent['expected_effective_options']['-gpgpu_ep_l2_ro_ranges'],'ranges_sha256':parent['expected_effective_options']['-gpgpu_ep_l2_ro_ranges_sha256'],'status':'OLD_BYTES_REUSABLE_NEW_SOURCE_LOADER_QUALIFICATION_REQUIRED'}
 s['collector_scope']={'primary':'Existing ordinary stats and RO aggregate; fourheavyOFF','T_independent_same_request_joint':'NOT_INSTRUMENTED_IN_PRIMARY_PROFILE','structural_state_vs_operational_detach':'MUST_DISTINGUISH','new_collector_NI':'NOT_QUALIFIED_NO_PRODUCTION_COLLECTOR'}
 s['main_required_gates']=['D fullSource build and wholeTU verification','Main newSource Source5 seal','16x8 newSource allthree modeCPU review','sameinput wholecommandlist ROloader qualification','16x8 allthree Host/parser/native qualification','fresh separate exactT request and user approval','fresh actual resources','complete accepted outputs true164 and independent restore']
 c.validate_background(s);points.append(s)
 put(ROOT/('DRAFT_'+arm+'_'+mode+'.json'),s)
c.validate_triplet(points)
put(ROOT/'T_THREE_ARM_EXACT_DRAFT_MATRIX.json',dict(schema='EP_T_THREE_ARM_DRAFT_MATRIX_V1',status='HOLD_NOT_FROZEN_OR_REGISTERED',approved_starts=0,requested_primary_points=3,source_evidence=source_evidence,points=points,contrasts={'B_over_A_speedup':'cycles_A/cycles_B','C_over_B_speedup':'cycles_B/cycles_C; includes charged query lookup latency and contention','C_over_A_speedup':'cycles_A/cycles_C'},optional_diagnostic_NI=dict(starts=3,condition='Only if existing heavy diagnostics are enabled for each primary mode; 3OFF arms may serve as OFF controls after exact NI qualification',new_observer_engineering='HOLD_16x8_geometry_and_stage_identity_gaps'),backup=dict(program='Vector4M',geometry=dict(slices=64,sets=32,ways=4,line_bytes=128),status='NOT_EXPANDED_NO_BUDGET_NO_AUTOMATIC_FALLBACK'),reuse_oldELF_F=False))
with(ROOT/'T_THREE_ARM_MODE_AND_OPTION_DIFF.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=['arm','mode','M','T','ordinary_correction','option_count','hardware_delta','newSource_frozen','approved_starts']);w.writeheader()
 for arm,s in zip('ABC',points):w.writerow(dict(arm=arm,mode=s['mode'],M=1,T=int(s['T']),ordinary_correction=int(s['ordinary_ro_tag_relief']),option_count=len(s['expected_effective_options']),hardware_delta='NONE',newSource_frozen=bool(source_evidence),approved_starts=0))
print(json.dumps(dict(points=3,option_count=283,source_bound=bool(source_evidence),approved_starts=0)))
