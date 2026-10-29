from pathlib import Path
import json,hashlib,copy,csv,ast,datetime
R=Path(__file__).resolve().parents[2]
O=Path(__file__).resolve().parent
J=R.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):p=Path(p);return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def put(n,j):(O/n).write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
j=json.loads((R/'agent_c/MT_OPPORTUNITY_AND_GAPS.json').read_text())
parent=next(x for x in j['rows'] if x['cohort']=='EP_PERF_CONV_F_G16_W8_V1')
s=json.loads(Path(parent['spec_ref']['path']).read_text());assert sha(parent['spec_ref']['path'])==parent['spec_ref']['sha256']
opt=copy.deepcopy(s['expected_effective_options']);assert len(opt)==282
assert opt['-gpgpu_ep_l2_ro_tag_detach']=='1' and opt['-gpgpu_ep_l2_ro_line_mshr_bypass']=='1'
opt['-gpgpu_ep_l2_ro_tag_detach']='0'
(O/'CONV16X8_F_MINUS_T_CANDIDATE.config').write_text('-gpgpu_ep_l2_ro_tag_detach 0\n')
delta={k:dict(F=s['expected_effective_options'][k],F_MINUS_T=v) for k,v in opt.items() if v!=s['expected_effective_options'][k]}
assert set(delta)=={'-gpgpu_ep_l2_ro_tag_detach'}
q=json.loads(Path(s['ro_qualification_ref']['path']).read_text());assert q['input_identity_sha256']==s['input_identity_sha256'] and q['source_identity']==s['source_identity']
for k in ['manifest_ref','ranges_ref']:assert sha(q[k]['path'])==q[k]['sha256']
put('CONV16X8_F_MINUS_T_EXACT_DRAFT.json',dict(schema='EP_L2_MT_ENGINEERING_SPEC_NOT_REGISTERED_V2',status='HOLD_MAIN_MODE_AND_P1_REVIEW',new_start_authorization=0,requested_conditional_starts=1,mode='F_MINUS_T',M=True,T=False,parent_F=parent,parent_spec_ref=ref(parent['spec_ref']['path']),source_identity=s['source_identity'],input_identity_sha256=s['input_identity_sha256'],geometry=s['geometry'],expected_effective_options=opt,exact_option_delta=delta,observer_env=s['observer_env'],candidate_ordered_configs=s['ordered_configs']+[ref(O/'CONV16X8_F_MINUS_T_CANDIDATE.config')],ro_qualification_ref=s['ro_qualification_ref'],input_binding_ref=s['input_binding_ref'],scientific_scope=s['scientific_scope'],control='same ELF/input/config and background except T. NOT WV.',native_ready=False,current_native_mode_allowlist=['S','F','WV_ZERO_RO'],gates=['Main P1 audit disposition: Source78 result means implemented legacy T, not corrected intended ordinary-request coverage','new exact mode allowlist + RO binding/capsule + validators + input eligibility + mode-specific Host/CPU/native qualification','fresh exact authorization/scoped budget/sole entry; no old epoch or227 budget reuse','fresh resource admission, actual config echo282, complete drain/identity/true164 archive'],alternate_new_Source=dict(condition='if Main integrates D correction or a production collector',F_reusable=False,minimum_fresh_causal_starts=2,optional_S_additional_start_only_for_full_EP_claim=1,authorization=0),old_F_wall_estimate_seconds=s['estimated_wall_seconds'],old_F_RAM_estimate_bytes=s['estimated_peak_RAM_bytes'],new_mode_wall_seconds='UNKNOWN: old F estimate is planning anchor, not prediction',Trace_copy_bytes=0))
rows=[]
for x in j['rows']:
 if x['profile']!='REF32x8_L100' or x['mode']!='F' or x['cohort'] not in ['EP_PERF_VECTOR6M_F_REF_V1','EP_PERF_SGEMM_F_REF_V1','EP_PERF_CONV_F_REF_V1']:continue
 a=x['RO'];m=x['ordinary_MSHR'];n=a['accepted_ro'];tx=a['transactions'];cand=a['accepted_oracle_candidates']
 rows.append(dict(cohort=x['cohort'],input_sha256=x['input_identity_sha256'],cycles=x['cycles'],accepted_ro_requesters=n,admitted_ro_transactions=tx,accepted_live_merge=a['merges'],live_merge_fraction=a['merges']/n,accepted_RO_per_admitted_transaction=n/tx,RO_runtime_entry_among_certified_FT_accepted_reads=n/cand,ordinary_line_peak=m['line_max_over_slices'],RO_issued_not_ready_distinct_line_peak_over_slices=a['max_over_slice_pending_unique_lines'],RO_live_transaction_peak_over_slices=a['max_over_slice_live_transactions'],descriptor_peak_over_slices=m['descriptor_max_over_slices'],WAD_peak_over_slices=m['WAD_max_over_slices'],ordinary_line_full_head_observations=m['line_full_head_observations_sum'],actual_detach=a['detached'],strict_required_sector_before_ready='UNKNOWN_NOT_COLLECTED',normal_RO_same_time_line_union='UNKNOWN_NOT_COLLECTED',full_NEW_structural_joint='UNKNOWN_NOT_COLLECTED',source_identity=x['source_identity'],evidence_refs={k:x[k] for k in ['bundle_ref','point_ref','spec_ref']}))
put('MT_RESOURCE_NEED_AND_LIMITS.json',dict(source='Source78; exact same REF32x8L100/MSB0M0a111',rows=rows,boundaries=['RO runtime entry fraction is not a rejection fraction; certified cache hits may never create a RO transaction','accepted_RO/transaction is lifetime requester multiplicity, not simultaneous waiter occupancy','slice maxima are not global synchronous peaks and cannot be summed','MS full head checks are retry population, not unique requests or exclusive GPU stall cycles','merge fraction is not strict requested-sector-before-ready revisit']))
with (O/'MT_RESOURCE_NEED_AND_LIMITS.csv').open('w',newline='') as f:
 flat=[{k:v for k,v in x.items() if k not in ['source_identity','evidence_refs']} for x in rows];w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
# Read current mode-policy syntax only, never invoke spec_for/authority or model start.
engine=Path(s['host_engine_ref']['path']);assert sha(engine)==s['host_engine_ref']['sha256'];tree=ast.parse(engine.read_text());fun=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='spec_for');tests=[]
for node in fun.body:
 if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='need' and len(node.value.args)>1 and isinstance(node.value.args[1],ast.Constant) and node.value.args[1].value=='unreviewed mode':
  expr=ast.Expression(body=node.value.args[0]);code=compile(ast.fix_missing_locations(expr),str(engine),'eval')
  for mode in ['S','F','WV_ZERO_RO','F_MINUS_T']:
   tests.append(dict(mode=mode,current_native_mode_predicate=bool(eval(code,{},dict(s=dict(mode=mode))))))
assert len(tests)==4 and not tests[-1]['current_native_mode_predicate']
put('HOST_POLICY_READBACK.json',dict(engine_ref=ref(engine),tests=tests,method='isolated AST expression only; no controller import, authority, registry writes, spec_for or native call',unclosed=['mode allowlist','M1T0 expected flags','non-F cannot inherit RO permission must distinguish F_MINUS_T','RO certificate copy path currently F-only','eligibility includes F_MINUS_T','native mode qualification and fresh scoped budget'],not_host_qualification=True))
cpu=json.loads((O/'CPU_EXECUTION.json').read_text());g=json.loads((O/'GEOMETRY16_CPU_EXECUTION.json').read_text());assert all(x['rc']==0 for x in cpu['rows']+g['rows'])
pairs=[]
for T in ['T0','T1']:
 rr=[x for x in cpu['rows'] if x['name'].startswith(T+'_')];sem=[]
 for x in rr:
  sem.append([z.split('|semantic=',1)[1].split('|',1)[0] for z in x['lines'] if '|semantic=' in z])
 assert sem[0]==sem[1];pairs.append(dict(mode=T,semantic_equal=True,scope='module + reference port only'))
put('ROUND2_QA.json',dict(final_module_executions=4,total_module_executions_including_superseded_harness=8,module_OFF_ON_pairs=pairs,actual_geometry16_partition_executions=4,preserved_initial_fixture_failures=4,complete282=True,option_delta=delta,new_models=0,new_production_Core_ELF=False,app_NI='NOT_EXECUTED',counter_size_bytes=88,counter_64slice_bytes=5632,collector_max_output_contract_bytes=65536,production_hook='NOT_IMPLEMENTED'))
print('round2 derivation PASS')
