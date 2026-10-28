"""Actual immutable transport9a certificate + primary/R2 wrapper shadow only."""
import copy,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path;H=P(__file__).resolve().parent;sys.path.insert(0,str(H));import owner_adapter as owner
import resource_qualifier as rq
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
cfg=read(R/'control/operational_amendments/typed_negative_transport_v3/INSTALL_CONFIG.json')
folder=R/'control/operational_amendments/typed_negative_full35_v2'
gate=load('terminal_gate',folder/'terminal_gate.py');view=load('typed_analysis_view',folder/'typed_analysis_view.py')
oldadapter=load('actual_old_owner_adapter',folder/'owner_recommend_adapter.py')
raw_path=R/'analysis/AUTO_SUMMARY.json';rawbytes=raw_path.read_bytes();raw=json.loads(rawbytes)
matrix_path=R/'control/MATRIX_CURRENT.json';matrixbytes=matrix_path.read_bytes();matrix=json.loads(matrixbytes)
history=read(R/'control/SEARCH_HISTORY.json')
class Journal:
 def guard_decision(self,d):return dict(d,registry_journal_status=dict(safe_for_scientific_completion=True),CPU_final_journal_object=id(self))
j=Journal();base=gate.private_module(cfg['source_paths']['base'],cfg['source_pins']['base'])
typed=oldadapter.make_owner_recommend(base.recommend,j,cfg['source_paths'],cfg['source_pins'],cfg['bindings'],cfg['verifier']['path'],cfg['verifier']['sha256'])
supp_path=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/supplemental_scan_m16_v2/supplemental_trial.py')
supp=load('actual_supplemental_adapter',supp_path)
registry=type('PrimaryProvider',(),dict(primary=lambda self:copy.deepcopy(matrix)))()
previous=supp.make_primary_adaptive(typed,registry,j)
project=owner.make_projector(view,cfg)
pins=read(H/'CPU_QUALIFICATION.json')['source_pins']+project.source_pins+rq.pins(R)+[
 dict(path=str(folder/'owner_recommend_adapter.py'),sha256=sha(folder/'owner_recommend_adapter.py')),
 dict(path=str(supp_path),sha256=sha(supp_path)),
 dict(path=str(R/'control/operational_amendments/registry_journal_v1/l2_registry_journal.py'),sha256=sha(R/'control/operational_amendments/registry_journal_v1/l2_registry_journal.py')),
 dict(path=str(R/'tools/l2_registry.py'),sha256=sha(R/'tools/l2_registry.py')),
 dict(path=str(R/'control/operational_amendments/typed_negative_transport_v3/INSTALL_CONFIG.json'),sha256=sha(R/'control/operational_amendments/typed_negative_transport_v3/INSTALL_CONFIG.json'))]
contract=owner.build_contract(R,pins);owner.check_contract(contract)
wrapper=owner.make_owner_recommend(previous,j,registry.primary,project,contract)
# The real supplemental dispatch view point, if known, is not part of inference.
dispatch=copy.deepcopy(matrix)
dispatch['points'].append(dict(input_digest=cfg['bindings'][0]['input_digest'],cohort=supp.NEW,scientific_role=owner.ROLE,cell='DH',profile='M16'))
dispatch['supplemental_dispatch_view']=dict(supplemental_cohorts=[supp.NEW])
before=copy.deepcopy(raw);result=wrapper(raw,dispatch,history)
assert wrapper.last_issue is None,wrapper.last_issue
assert result['interaction_phase_gate']['status']=='PASS_EXPLICIT_V3_PHASES_FULL35_PARENTS'
assert raw==before and matrix_path.read_bytes()==matrixbytes
assert result['requires_engineering_review']and not result['adoption_ready']and not result['scientific_stage_complete']
assert len(result['verified_typed_engineering_negatives'])==1
assert not any(p.get('supplementary_policy')=='DTC_L2_MLP_INTERACTION_POLICY_V3'for p in result['proposals']),'Initial350 still incomplete'
assert result['CPU_final_journal_object']==id(j)
out=dict(status='PASS_READONLY_ACTUAL_PRIMARY_R2_TRANSPORT9A_F21_A7_V3_CHAIN',raw_snapshot_sha256=hashlib.sha256(rawbytes).hexdigest(),
 primary_matrix_sha256=hashlib.sha256(matrixbytes).hexdigest(),primary_input_count=35,primary_cell_count=len(matrix['points']),
 verified_typed_negative_count=1,original_M16_performance_accepted=False,R2_performance_union=False,
 interaction_state=result['interaction_search']['phase'],new_V3_proposals=0,model_starts=0,production_grants=0,
 source_pins=pins,contract_sha256=owner.digest(contract),summary_unmodified=True,production_matrix_unmodified=True,
 caveat='Independent readonly recommendation with fake final-journal metadata only; no actual owner install or authority mutation')
(H/'ACTUAL_READONLY_COUPLING.json').write_text(json.dumps(out,indent=2)+'\n')
(H/'SCIENTIFIC_CONTRACT.json').write_text(json.dumps(contract,indent=2)+'\n')
print(json.dumps(out))
