"""Run exactly one E2-qualified Conv S/F queue through original bounded controller."""
from pathlib import Path
import sys,json,subprocess,time,importlib.util
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c
from controller import step
TAKE=P.parent/'MS20261020_E2_TAKEOVER_r1'
def main():
 coord=c.Coordinator();receipt=json.loads((P/'QUALIFICATION_RECEIPT.json').read_text());queue=receipt['queue'];assert c.digest(queue['path'])==queue['sha256']
 snap=coord.snapshot();assert snap['final_source_identity']==receipt['source_identity'] and snap['actual_starts']==8 and snap['controller']['state']=='STOPPED'
 assert snap['official_producer_current']['E_independent_qualification']
 binding=json.loads((P/'QUALIFICATION_REMOTE_READBACK.json').read_text());pub=binding['remote_commit']
 for name in ['convolutionSeparable_QUEUE.json','convolutionSeparable_QUALIFICATION.json','convolutionSeparable_S_SPEC.json','convolutionSeparable_F_SPEC.json','run_conv_pair.py']:
  f=P/name;assert subprocess.check_output(['git','-C',str(ROOT),'show',pub+':'+f.relative_to(ROOT).as_posix()])==f.read_bytes()
 result=step(coord,queue['path'])
 c.write_json(P/'CONTROLLER_RESULT.json',result)
 snap=coord.snapshot();paths=[P/'CONTROLLER_RESULT.json']
 for a in snap['attempts']:
  if a['identity']['binary_sha256']==receipt['source_identity']['binary_sha256'] and a.get('receipt_path'):
   assert c.digest(a['receipt_path'])==a['receipt_sha256'];f=P/(a['attempt_id']+'_RUN_STATUS.json');c.write_json(f,json.loads(Path(a['receipt_path']).read_text()));paths.append(f)
 pair=snap['accepted_pairs'].get('V2_MAIN_convolutionSeparable_S_F_MAIN61')
 status='FIRST_MAIN61_CONV_S_F_PAIR_CURRENT_ACCEPTED' if pair and pair['status']=='CURRENT_ACCEPTED' else 'CONV_S_F_NOT_ACCEPTED_EVIDENCE_REVIEW_REQUIRED'
 c.write_json(P/'PAIR_DECISION.json',dict(status=status,pair=pair,at_unix=time.time(),next_dispatch=False,reason='First-pair decision boundary: no FWT/main matrix automatically queued. Original contingency8 now accounted; later execution must use original remaining scientific conditions and budget. Preserve negative/zero/failed outcomes without selection.'))
 paths.append(P/'PAIR_DECISION.json')
 subprocess.run([sys.executable,'-B',str(TAKE/'checkpoint.py'),'CONV_PAIR_TERMINAL',status],cwd=ROOT,check=True)
 e=ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/e';paths += [TAKE/'CONV_PAIR_TERMINAL.json',e/'RECEIPT.json',e/'STATUS.md']
 module=importlib.util.spec_from_file_location('epublish',TAKE/'publish.py');m=importlib.util.module_from_spec(module);module.loader.exec_module(m)
 readback=m.publish('docs(ep-l2-e2): publish main61 Conv S/F terminal decision and complete evidence',paths)
 c.write_json(P/'PAIR_RESULT_REMOTE_READBACK.json',readback)
 c.write_json(c.HANDOFF/'events/E2_MAIN61_CONV_S_F_REMOTE_RESULT.json',dict(status=status,**readback))
 print(json.dumps(dict(status=status,pair=pair,remote_readback=readback)),flush=True)
if __name__=='__main__':main()
