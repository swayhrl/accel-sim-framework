"""Real existing full-forecast chain qualifier. Read-only, no invented RSS model."""
import copy,hashlib,importlib.util,json,pathlib
P=pathlib.Path
TARGET=('-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def pins(root):
 root=P(root)
 paths=[P(__file__),root/'tools/l2_registry.py',root/'tools/l2_config_generator.py',root/'tools/l2_resources.py',root/'tools/l2_ops.py',root/'control/RESOURCE_POLICY.json']
 return [dict(path=str(p),sha256=sha(p))for p in paths]

def make_host_qualifier(root,pinned_sources):
 root=P(root);pinned_sources=copy.deepcopy(pinned_sources)
 assert {p['path']for p in pinned_sources}=={p['path']for p in pins(root)}
 def qualifier(proposal):
  for pin in pinned_sources:assert sha(pin['path'])==pin['sha256'],'Resource qualification source changed'
  gen=load('qualified_original_generator',root/'tools/l2_config_generator.py')
  res=load('qualified_original_forecast',root/'tools/l2_resources.py')
  registry_source=(root/'tools/l2_registry.py').read_text();ops_source=(root/'tools/l2_ops.py').read_text()
  # These actual source paths were CPU integration-tested, not inferred from a
  # proof-shaped fixture. Source-pin changes require new chain qualification.
  assert "f=load('l2_resource_amend_prediction','l2_resources.py').forecast(s,history)"in registry_source
  refresh=ops_source.index('registry.refresh_pending_resource_spec(c,history);spec=engine.canonical(c)')
  bind=ops_source.index("db=R/'control/dispatch_bindings'/(c+'.json')",refresh)
  claim=ops_source.index("claims[c]=dict(host_cpu=",bind)
  assert refresh<bind<claim
  resource_policy=read(root/'control/RESOURCE_POLICY.json')
  # Dispatch choice may explicitly pass RESOURCE_POLICY; real registry refresh
  # calls forecast without it. Refuse divergence in actual forecast fields.
  fields=['minimum_prediction_bytes','minimum_unobserved_bytes','history_multiplier','history_additive_bytes',
   'candidate_l2_metadata_margin_bytes','hard_limit_multiplier','hard_limit_additive_bytes']
  assert all(resource_policy.get(k,res.DEFAULT_POLICY[k])==res.DEFAULT_POLICY[k]for k in fields)
  raw=(root/'control/HISTORICAL_RSS.json').read_bytes();history=json.loads(raw)
  matrix=read(root/'control/MATRIX_CURRENT.json');ids=sorted({p['input_digest']for p in matrix['points']})
  assert len(ids)==35 and len(proposal['new_cells'])==35
  assert len({(r['input_digest'],r['cell'])for r in proposal['new_cells']})==35
  assert sorted(r['input_digest']for r in proposal['new_cells'])==ids
  rows=[];adjustments=[]
  for want in proposal['new_cells']:
   d=want['input_digest'];cell=want['cell'];assert cell in('CH','DH')
   p=next(p for p in matrix['points']if p['input_digest']==d and p['cell']==cell and p['profile']=='P0')
   path=root/'control/specs'/(p['cohort']+'.json');base=read(path)
   texts=[]
   for config in base['configs']:assert sha(config['path'])==config['sha256'];texts.append(P(config['path']).read_text())
   after,transform=gen.generate(texts,proposal['parameters']);options=gen.effective_options(after)
   spec=copy.deepcopy(base);spec['profile']=spec['downstream_profile']=proposal['profile']
   spec['cohort']='E2-DTCL2MLP-'+d[:16]+'-'+cell+'-'+proposal['profile']+'-V1'
   # Exactly the registry's inherited canonical270 options, not a new default dump.
   for key in TARGET:spec['expected_options'][key]=[options[key]]
   assert len(spec['expected_options'])==270
   assert all(v==base['expected_options'][k]for k,v in spec['expected_options'].items()if k not in TARGET)
   f=res.forecast(spec,history) # exact function/default args consumed by real refresh
   oldcap=base['limits']['max_process_tree_rss_bytes'];cap=f['proposed_process_tree_rss_cap_bytes']
   # Original ratified refresh may change all three RAM fields after complete
   # history appears. This callback neither reduces nor overrides its output.
   lower=cap<oldcap
   if lower:adjustments.append(dict(input_digest=d,reason='RATIFIED_ORIGINAL_REFRESH_REPLACES_UNKNOWN_ENVELOPE_WITH_HISTORY',old=oldcap,new=cap))
   rows.append(dict(input_digest=d,cell=cell,program=base['program'],cohort=spec['cohort'],base_spec_path=str(path),base_spec_sha256=sha(path),
    full_reserved_peak_bytes=f['predicted_peak_RAM_bytes'],proposed_process_tree_rss_cap_bytes=cap,
    proposed_process_tree_vms_cap_bytes=max(2*cap,cap+8*1024**3),base_process_tree_rss_cap_bytes=oldcap,
    candidate_full_forecast_retained=True,new_qualifier_reduces_forecast_or_limits=False,ratified_refresh_rss_cap_decreased=lower,forecast=f,
    resource_fields_before=dict(estimated_peak_model_RAM_bytes=base['estimated_peak_model_RAM_bytes'],max_process_tree_rss_bytes=oldcap,max_process_tree_vms_bytes=base['limits']['max_process_tree_vms_bytes']),
    resource_fields_after_original_refresh=dict(estimated_peak_model_RAM_bytes=f['predicted_peak_RAM_bytes'],max_process_tree_rss_bytes=cap,max_process_tree_vms_bytes=max(2*cap,cap+8*1024**3)),
    unchanged_timeout_seconds=base['limits']['timeout_seconds'],unchanged_result_cap=base['limits']['max_result_directory_bytes']))
  proof=dict(status='PASS_SEPARATE_COMBINATION_RESOURCE_QUALIFICATION',
   proposal_id=proposal['proposal_id'],parameters=copy.deepcopy(proposal['parameters']),source_pins=copy.deepcopy(pinned_sources),
   initial_profile_padding_discount_applied=False,invented_fixed_margin_used=False,existing_dynamic_admission_retained=True,
   cell_forecasts=rows,ratified_original_cap_adjustments=adjustments,history_snapshot_sha256=hashlib.sha256(raw).hexdigest(),
   new_qualifier_reduces_forecast_or_limits=False,ratified_original_refresh_may_adjust_resource_caps=True,
   forecast_formula_source='EXACT_ORIGINAL_l2_resources.forecast; no argument or multiplier overrides',
   inherited_original_metadata_margin_bytes=res.DEFAULT_POLICY['candidate_l2_metadata_margin_bytes'],
   inherited_margin_is_not_new_sizeof_bound=True,exact_peak_RSS_guaranteed=False,
   qualification_scope='Actual source/config/full-forecast-consumption compatibility; not a measured new-profile RSS or a structural allocation bound',
   actual_consumption_chain='registry.extend clones P0 -> ops choose -> registry.refresh_pending_resource_spec(actual history) -> canonical -> binding/claim -> native fresh gates',
   subsequent_history_refresh='Recomputed from then-current real history by existing ratified registry; no stale proof overwrite',
   combinations_initial_eight_discount_ineligible='Only full candidate forecasts; no padding overlay invoked by qualifier')
  qualifier.last_proof=proof;return proof
 qualifier.last_proof=None;qualifier.source_pins=copy.deepcopy(pinned_sources);return qualifier
