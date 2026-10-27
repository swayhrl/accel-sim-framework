"""Real read-only coupling test of E's pinned typed view and this V2 verifier."""
import sys
sys.dont_write_bytecode=True
import pathlib,hashlib,json,importlib.util,copy,datetime
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');D=P(__file__).parent;S=D/'scan_m16_terminal_verifier_v2.py'
E=A/'agents/E/engineering_terminal_gate_v1';T=E/'typed_analysis_view.py';G=E/'terminal_gate.py';TPIN='b0376692609927f922589163e41b6b218caabe6756b2763ddbf8864e5f06daaa'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
pin=sha(S);assert sha(T)==TPIN;gatepin=sha(G);sys.path.insert(0,str(E));view=load('actual_E_typedview_V2_coupling',T)
import terminal_gate
assert P(terminal_gate.__file__).resolve()==G.resolve()
v=load('actual_V2_contract_check',S);assert v.PROD==v.EXPECTED_BUNDLE.parent
rawpath=P('/root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/AUTO_SUMMARY.json');rawbytes=rawpath.read_bytes();raw=json.loads(rawbytes);before=copy.deepcopy(raw)
cohort='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1';uid='19105d9d-7522-498e-bf1d-73fbf7aba766';digest=next(d for d,profiles in raw['table'].items()if profiles.get('M16',{}).get('DH',{}).get('cohort')==cohort)
binding=dict(cohort=cohort,uuid=uid,input_digest=digest,cell='DH',profile='M16',bundle_path=str(v.EXPECTED_BUNDLE),certificate_sha256='37842f4191c6a0f293a01d22834c28794c3e23a477b1d657976d01bdb055c9e7')
projected,proofs=view.project(raw,[binding],S,pin)
assert raw==before,'Original raw summary object mutated'
assert projected['aggregates']==raw['aggregates']and projected['state_counts']==raw['state_counts']
row=projected['table'][digest]['M16']['DH'];assert row['state']=='ENGINEERING_TERMINAL_NEGATIVE_ARCHIVED_NO_RETRY'and row['accepted']is False and row['cycles']is None and row['uuid']==uid
assert row['typed_engineering_original_row']==raw['table'][digest]['M16']['DH']
assert proofs[cohort]['verified']is True and proofs[cohort]['verifier_sha256']==pin
assert sha(T)==TPIN and sha(G)==gatepin and sha(S)==pin
result=dict(schema='REAL_TYPEDVIEW_TO_VERIFIER_V2_READONLY_INTEGRATION',status='PASS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),verifier_path=str(S),verifier_sha256=pin,typedview_path=str(T),typedview_sha256=TPIN,terminal_gate_path=str(G),terminal_gate_sha256=gatepin,PROD_export_verified=True,actual_project_called=True,actual_load_verified_certificate_called=True,raw_summary_snapshot_sha256=hashlib.sha256(rawbytes).hexdigest(),raw_summary_object_unmodified=True,original_aggregates_and_state_counts_unmodified=True,binding=binding,original_row=raw['table'][digest]['M16']['DH'],projected_row=row,proof=proofs[cohort],analysis_view=projected['typed_engineering_analysis_view'],production_writes=0,authority_writes=0,models=0,signals=0)
print(json.dumps(result,indent=2,sort_keys=True))
