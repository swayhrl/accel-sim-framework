"""Main-only immutable mixed-four replay capture; no simulation or authority writes."""
from pathlib import Path
import json,hashlib,sys,threading,os,importlib.util
P=Path
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def apply(config_path):
 cfg=json.loads(P(config_path).read_bytes())
 assert cfg['schema']=='DTC_MAIN_ACTUAL_MIXED_FOUR_CAPTURE_CONFIG_V1'
 assert os.getpid()==1498278 and threading.current_thread()is threading.main_thread()
 assert int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 for p,h in cfg['source_pins'].items():assert sha(p)==h
 main=sys.modules['__main__'];state=main.DTC_MAIN_CPU_SHARED_STAGE2_HANDOFF_V1
 assert state['phase']=='ARMED_ACKED'and sha(state['config_path'])==cfg['stage2_configuration_sha256']
 frame=state['frame'];engine=state['engine'];assert frame.f_locals['engine']is engine
 engine.assert_parent_lease()
 spec=importlib.util.spec_from_file_location('main_actual_mixed_four_capture_extra',cfg['gate_source_path']);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.capture_mixed_four_gate(frame,main,cfg['output_path'])
 assert result['gate']['accepted_real_count']==4 and result['gate']['four_point_qualified']is True
 return dict(status='CAPTURED_ACTUAL_MAIN_MIXED_FOUR_GATE',gate_path=result['path'],gate_sha256=result['sha256'],models_started=0,new_grants=0)
