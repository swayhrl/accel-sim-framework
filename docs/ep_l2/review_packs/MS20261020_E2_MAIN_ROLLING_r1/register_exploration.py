"""Register D's SGEMM proposal as separate, non-launchable exploration."""
from pathlib import Path
import json,sys,time
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'));import coordinator as c
D=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-d-analysis-v1/docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/input_suitability_20261020_r1')
def ref(p):return dict(path=str(p),sha256=c.digest(p))
p=json.loads((D/'SGEMM_PROPOSAL_TO_E.json').read_text());assert c.digest(D/'CANDIDATE_AUDIT.json')==p['input_proof_sha256'];assert p['selected_before_new_candidate_S_F_performance'] and not p['candidate_new_speedup_inspected']
reg=dict(schema='E2_INDEPENDENT_EXPLORATORY_INPUT_REGISTRATION_V1',registration_id='E2_EXP_SGEMM_MEDIUM_20261020_r1',at_unix=time.time(),campaign_id=c.CAMPAIGN,selected_by='D',registered_by='E2',status='REGISTERED_EXPLORATORY_HOLD_NOT_LAUNCHABLE',source_proposal=ref(D/'SGEMM_PROPOSAL_TO_E.json'),source_proof=ref(D/'CANDIDATE_AUDIT.json'),source_review=ref(D/'REPLAY_REPRODUCIBILITY_AND_COST_SCOPE.md'),source_D_publication='613d362b37f1b74b7ac7c1963bef850e43b9bb66',workload='sgemm',trace_content_sha256=p['trace_content_sha256'],trace_manifest=p['trace_content_manifest'],expected_full_instructions=p['expected_full_instructions'],complete_commandlist=p['full_commandlist'],selection_basis=p['independent_value'],selection_on_new_F_speedup=False,reviewed_semantics='D complete original-byte/native grammar/non-atomic proof inspected; E fresh complete content binding required before possible admission. No runtime/performance PASS inherited.',capture_source_scope=p['candidate_scope'],application_source_revision=p['app_original_source_revision'],capture_command=p['capture_run_sh_literal'],hold_reasons=['Original application revision and capture command UNKNOWN; provenance limits must stay explicit in any later input-scope approval.','Own RO certificate or explicitly reviewed zero-coverage fallback and E full runtime qualification still pending.','No original unstarted scientific condition has yet been reallocated to this separate exploratory set; no launch reservation.'],original_seven_input_main_set_unchanged=True,Btree='HOLD_NOT_REPLACED',budget=dict(maximum=40,new_starts=0,contingency_remaining=0),not_a_launch_authorization=True)
c.write_json(P/'EXPLORATORY_SGEMM_REGISTRATION.json',reg);coord=c.Coordinator()
with coord.locked() as (data,item):
 item.setdefault('exploratory_input_registrations',{})[reg['registration_id']]=dict(**ref(P/'EXPLORATORY_SGEMM_REGISTRATION.json'),status=reg['status'],main_roster_replacement=False,launch_authorized=False)
c.write_json(c.HANDOFF/'events/E2_TO_D_SGEMM_EXPLORATORY_REGISTERED_HOLD.json',reg)
print(reg['status'])
