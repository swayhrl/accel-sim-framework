from pathlib import Path
import hashlib,json,os,sys,threading,importlib.util
P=Path
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):
 with P(p).open('xb')as f:f.write((json.dumps(v,sort_keys=True,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
def apply(config_path):
 cfg=json.loads(P(config_path).read_bytes());directory=P(config_path).parent
 assert threading.current_thread()is threading.main_thread()and os.getpid()==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 for p,h in cfg['source_pins'].items():assert sha(p)==h
 assert cfg['source_path']==str(P(__file__))and sha(__file__)==cfg['source_sha256']
 main=sys.modules['__main__'];gate=main.DTC_REGISTERED_TAIL_ONLY_USER_SCOPE_HOLD_V1
 assert gate['phase']=='ACKED'and gate['frame'].f_locals['adaptive'].recommend is gate['wrapper']
 try:
  s=importlib.util.spec_from_file_location('root_actual_negative_archive_component_v3',cfg['component_path']);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  value=m.apply(cfg['component_configuration_path'],cfg['component_approval_path'])
  value.update(configuration_sha256=sha(cfg['component_configuration_path']),approval_sha256=sha(cfg['component_approval_path']),root_wrapper_source_sha256=sha(__file__))
  put(directory/'ACK.json',value);return value
 except BaseException as error:
  value=dict(status='NEGATIVE_ARCHIVE_INSTALL_PRESERVE_NO_REQUEUE',error=repr(error),models_started=0,new_grants=0)
  try:put(directory/'ERROR.json',value)
  except BaseException:pass
  return value
