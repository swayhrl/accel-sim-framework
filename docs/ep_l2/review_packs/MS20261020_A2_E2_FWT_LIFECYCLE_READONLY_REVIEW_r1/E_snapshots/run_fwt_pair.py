"""One finite original-controller FWT pair after trusted Conv; no subsequent queue."""
from pathlib import Path
import sys,json,time,subprocess,importlib.util
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c
from controller import step
TAKE=P.parent/'MS20261020_E2_TAKEOVER_r1'
def main():
 coord=c.Coordinator();decision=json.loads((P/'DECISION.json').read_text());snap=coord.snapshot();assert snap['actual_starts']==10 and snap['controller']['state']=='STOPPED' and snap['accepted_pairs']['V2_MAIN_convolutionSeparable_S_F_MAIN61']['status']=='CURRENT_ACCEPTED'
 assert snap['final_source_identity']==decision['source_identity'] and c.digest(decision['queue']['path'])==decision['queue']['sha256']
 published=json.loads((P/'PRELAUNCH_REMOTE_READBACK.json').read_text())['remote_commit']
 for name in ['run_fwt_pair.py','DECISION.json','FWT_7_21_QUALIFICATION.json','FWT_7_21_S_SPEC.json','FWT_7_21_F_SPEC.json','FWT_7_21_QUEUE.json']:
  f=P/name;assert subprocess.check_output(['git','-C',str(ROOT),'show',published+':'+f.relative_to(ROOT).as_posix()])==f.read_bytes()
 result=step(coord,decision['queue']['path']);c.write_json(P/'CONTROLLER_RESULT.json',result);snap=coord.snapshot();paths=[P/'CONTROLLER_RESULT.json']
 for a in snap['attempts']:
  if a['identity']['workload']=='FWT_7_21' and a['identity']['binary_sha256']==decision['source_identity']['binary_sha256'] and a.get('receipt_path'):
   assert c.digest(a['receipt_path'])==a['receipt_sha256'];f=P/(a['attempt_id']+'_RUN_STATUS.json');c.write_json(f,json.loads(Path(a['receipt_path']).read_text()));paths.append(f)
 pair=snap['accepted_pairs'].get('V2_MAIN_FWT_7_21_S_F_MAIN61');status='FWT_MAIN61_PAIR_CURRENT_ACCEPTED' if pair and pair['status']=='CURRENT_ACCEPTED' else 'FWT_REQUIRES_RESULT_REVIEW_NO_NEXT_DISPATCH'
 c.write_json(P/'TERMINAL_DECISION.json',dict(status=status,at_unix=time.time(),pair=pair,next_dispatch=False,reason='One original planned FWT pair only. Later main-matrix scientific/profile/input qualification and live resource admission remain separate. No automatic retries, contingency increase, Btree/SGEMM substitution or extra joint-fixture promotion.'));paths.append(P/'TERMINAL_DECISION.json')
 subprocess.run([sys.executable,'-B',str(TAKE/'checkpoint.py'),'FWT_PAIR_TERMINAL',status],cwd=ROOT,check=True);e=ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/e';paths += [TAKE/'FWT_PAIR_TERMINAL.json',e/'STATUS.md',e/'RECEIPT.json']
 spec=importlib.util.spec_from_file_location('epublish',TAKE/'publish.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);readback=m.publish('docs(ep-l2-e2): publish original planned main61 FWT terminal results',paths)
 c.write_json(P/'TERMINAL_REMOTE_READBACK.json',readback);c.write_json(c.HANDOFF/'events/E2_MAIN61_FWT_S_F_REMOTE_RESULT.json',dict(status=status,**readback));print(json.dumps(dict(status=status,pair=pair,remote_readback=readback)),flush=True)
if __name__=='__main__':main()
