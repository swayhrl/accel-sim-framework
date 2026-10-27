import pathlib,json,hashlib,sys,importlib.util,traceback,datetime
_d=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/typed_negative_full35_v2')
try:
 def _load(n,p):
  s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 _r=_d.parents[2];_e=_load('typed_full35_main_lease',_r/'tools/l2_native.py');_e.assert_parent_lease();_main=sys.modules['__main__'];assert not hasattr(_main,'DTC_L2_MLP_TYPED_NEGATIVE_FULL35_V2')
 _manifest=json.loads((_d/'DELIVERY_MANIFEST_V2.json').read_bytes());_cfg=json.loads((_d/'INSTALL_CONFIG.json').read_bytes())
 for n in ['terminal_gate.py','typed_analysis_view.py','owner_recommend_adapter.py']:assert hashlib.sha256((_d/n).read_bytes()).hexdigest()==_manifest['files'][n]
 _jm=_main.DTC_L2_MLP_REGISTRY_JOURNAL_V1;_ad=_jm['adaptive'];_prior=_ad.recommend;_guard=_jm['guard'];_ext=_jm['registry'].extend;assert _prior is _main.DTC_L2_MLP_BOUNDARY_V2['wrapper']and _ext.__self__ is _guard
 _old={n:sys.modules.get(n)for n in ['terminal_gate','typed_analysis_view']}
 try:
  _gate=_load('dtc_actual_terminal_gate_v2',_d/'terminal_gate.py');sys.modules['terminal_gate']=_gate
  _view=_load('dtc_actual_typed_analysis_view_v2',_d/'typed_analysis_view.py');sys.modules['typed_analysis_view']=_view
  _owner=_load('dtc_actual_typed_owner_factory_v2',_d/'owner_recommend_adapter.py')
 finally:
  for n,m in _old.items():
   if m is None:sys.modules.pop(n,None)
   else:sys.modules[n]=m
 _new=_owner.make_owner_recommend(_prior,_guard,_cfg['source_paths'],_cfg['source_pins'],_cfg['bindings'],_cfg['verifier']['path'],_cfg['verifier']['sha256'])
 _raw=json.loads((_r/'analysis/AUTO_SUMMARY.json').read_bytes());_scope=json.loads((_r/'control/MATRIX_CURRENT.json').read_bytes());_hist=json.loads((_r/'control/SEARCH_HISTORY.json').read_bytes());_shadow=_new(_raw,_scope,_hist)
 assert _new.last_issue is None and not _shadow['proposals']and not _shadow['adoption_ready']and not _shadow['scientific_stage_complete']and _shadow['requires_engineering_review']
 assert len(_shadow['verified_typed_engineering_negatives'])==1 and _new.existing_journal is _guard
 with(_d/'ACTUAL_SHADOW.json').open('x')as h:json.dump(_shadow,h,indent=2)
 _ad.recommend=_new;assert _jm['registry'].extend is _ext
 _state=dict(adaptive=_ad,previous_recommend=_prior,wrapper=_new,journal=_guard,gate=_gate,view=_view,owner_module=_owner)
 setattr(_main,'DTC_L2_MLP_TYPED_NEGATIVE_FULL35_V2',_state)
 def _activate(reg):reg['registered_future_requests'][_e.REQ]['additional_operational_overlays']['DTC_L2_MLP_TYPED_NEGATIVE_FULL35_V2']['status']='ACTIVE_PRIVATE_RECOMMENDATION_TYPED_TERMINAL_FULL35_ONLY'
 _e.update_authority(_activate)
 _p=dict(status='ACTIVE_SAME_OWNER_TYPED_TERMINAL_FULL35_POLICY_V2',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=1498278,same_live_journal_object=True,journal_object_id=id(_guard),registry_extend_unchanged=True,actual_shadow_state=_shadow['state'],verified_negatives=1,proposals_on_install=0,old_raw_summary_and_RESULTS_unchanged=True,resource_provider_and_claims_unchanged=True,no_new_grants_or_model_signals=True,publication_commit='bf1a7050ec93b5dc1c67deef02bc1450d1b9670f')
 _state['proof']=_p
 with(_d/'ACK.json').open('x')as h:json.dump(_p,h,indent=2)
except BaseException:
 with(_d/'ERROR.json').open('x')as h:json.dump({'traceback':traceback.format_exc()},h)
