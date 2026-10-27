import pathlib,json,hashlib,sys,importlib.util,traceback,datetime
_d=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/supplemental_scan_m16_v2')
try:
 _r=_d.parents[2];_cfg=json.loads((_d/'INSTALL_CONFIG.json').read_bytes())
 def _sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
 for _key in ['module','route','plan']:assert _sha(_cfg[_key+'_path'])==_cfg[_key+'_sha256']
 _main=sys.modules['__main__'];assert not hasattr(_main,'DTC_L2_MLP_SUPPLEMENTAL_SCAN_TRIAL_V2');_frame=sys._current_frames()[_main.DTC_L2_MLP_ADDON_THREAD.ident]
 while _frame and not(_frame.f_code.co_name=='run_scheduler'and pathlib.Path(_frame.f_code.co_filename)==_r/'tools/l2_ops.py'):_frame=_frame.f_back
 assert _frame is not None;_e=_frame.f_locals['engine'];_e.assert_parent_lease();_journal=_main.DTC_L2_MLP_REGISTRY_JOURNAL_V1['guard'];_adaptive=_frame.f_locals['adaptive'];_prior_adaptive=_adaptive.recommend
 assert _prior_adaptive is _main.DTC_L2_MLP_TYPED_NEGATIVE_CONTEXT_TRANSPORT_V3['wrapper']
 _s=importlib.util.spec_from_file_location('actual_supplemental_trial_v2',_cfg['module_path']);_m=importlib.util.module_from_spec(_s);_s.loader.exec_module(_m)
 if 'supplemental_trial'in sys.modules:assert _sha(sys.modules['supplemental_trial'].__file__)==_cfg['module_sha256']
 else:sys.modules['supplemental_trial']=_m
 _s=importlib.util.spec_from_file_location('actual_supplemental_route_v2',_cfg['route_path']);_route=importlib.util.module_from_spec(_s);_s.loader.exec_module(_route)
 _plan=json.loads(pathlib.Path(_cfg['plan_path']).read_bytes());assert _m.digest(_plan)==_cfg['plan_sha256'];_approval=json.loads((_d/'MAIN_AUTHORIZATION.json').read_bytes());_store=_m.SupplementalRegistry(_r,_e,_journal.lock,_e.assert_parent_lease,lineage_verifier=_route.route_lineage_verifier)
 _before_budget=_e.registered()[2]['budget'];_matrix_sha=_sha(_r/'control/MATRIX_CURRENT.json');_registration=_store.register(_plan,_approval)
 _prior_read=_frame.f_globals['read'];_new_read=_m.make_ops_read(_prior_read,_store);_view=_new_read(_r/'control/MATRIX_CURRENT.json');assert _new_read.last_issue is None and len(_view['points'])==351 and _sha(_r/'control/MATRIX_CURRENT.json')==_matrix_sha
 _new_adaptive=_m.make_primary_adaptive(_prior_adaptive,_store,_journal);assert _new_adaptive.existing_journal is _journal
 _shadow=_new_adaptive(json.loads((_r/'analysis/AUTO_SUMMARY.json').read_bytes()),_view,json.loads((_r/'control/SEARCH_HISTORY.json').read_bytes()));assert not _shadow['proposals']and not _shadow['scientific_stage_complete']and not _shadow['adoption_ready']
 _frame.f_globals['read']=_new_read;_adaptive.recommend=_new_adaptive
 setattr(_main,'DTC_L2_MLP_SUPPLEMENTAL_SCAN_TRIAL_V2',dict(store=_store,module=_m,route=_route,adaptive=_adaptive,previous_recommend=_prior_adaptive,recommend_wrapper=_new_adaptive,ops_globals=_frame.f_globals,previous_ops_read=_prior_read,ops_read_wrapper=_new_read,journal=_journal,registration=_registration,cfg=_cfg))
 _q=_e.registered()[2];assert _q['budget']==_before_budget+1 and _q['consumed'][_m.OLD]['uuid']==_m.OLD_UUID and not _q['consumed'][_m.OLD].get('execution_receipt');assert len(json.loads((_r/'control/MATRIX_CURRENT.json').read_bytes())['points'])==350
 _ack=dict(status='SUPPLEMENTAL_ONE_FRESH_GRANT_AND_PRIVATE_DISPATCH_VIEW_ACTIVE',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=1498278,pool_object_id=id(_frame.f_locals['pool']),claims_object_id=id(_frame.f_locals['claims']),journal_object_id=id(_journal),old_cohort=_m.OLD,old_UUID=_m.OLD_UUID,new_cohort=_m.NEW,budget_before=_before_budget,budget_after=_q['budget'],new_grants=1,refunds=0,primary_matrix_cells=350,private_dispatch_view_cells=351,raw_primary_matrix_sha256=_matrix_sha,automatic_union=False,original_M16_inference_HOLD_preserved=True,registration=_registration,adaptive_shadow_state=_shadow.get('state'),publication_commit=_cfg['publication_commit'],model_starts_by_installer=0)
 with(_d/'ACK.json').open('x')as h:json.dump(_ack,h,indent=2)
 with(_d/'ACTUAL_ADAPTIVE_SHADOW.json').open('x')as h:json.dump(_shadow,h,indent=2)
except BaseException:
 with(_d/'ERROR.json').open('x')as h:json.dump({'traceback':traceback.format_exc()},h)
