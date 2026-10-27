"""Main-only existing owner instance IO publication and strict adapter."""
import pathlib,json,hashlib,importlib.util,sys,threading,os
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');MARKER='DTC_L2_MLP_SHARED_JSON_IO_OUTER_V1'
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def install_on_frame(frame,cfg,fixture=False):
 assert threading.current_thread()is threading.main_thread();main=sys.modules['__main__'];assert not hasattr(main,MARKER);front=load('owner_io_front',cfg['frontend_path']);front.validate(cfg,frame.f_locals['engine'].registered()[2]);helper=load('owner_io_helper',cfg['source_path']);res=frame.f_locals['res'];consumer=frame.f_locals['consumer'];helper.install_private_module(res,cfg['expected_pins'],1.0);helper.install_private_module(consumer,cfg['expected_pins'],1.0);oldload=consumer.load
 def consumer_load(name,file):
  module=oldload(name,file)
  if P(file).name=='l2_strict.py':
   original=module.terminal
   def terminal(c):
    oldproof=original(c);extra=load('owner_io_extra_strict',cfg['extra_strict_path']);return extra.terminal(c,oldproof)
   module.terminal=terminal
  return module
 consumer.load=consumer_load;state=dict(res=res,consumer=consumer,oldload=oldload,wrapper=consumer_load,cfg=cfg);setattr(main,MARKER,state)
 return dict(status='EXISTING_OWNER_SHARED_JSON_IO_INSTANCES_INSTALLED',owner_pid=os.getpid(),pool_object_id=id(frame.f_locals['pool']),claims_object_id=id(frame.f_locals['claims']),source_sha256=hashlib.sha256(P(__file__).read_bytes()).hexdigest(),no_running_supervisor_mutations=True,no_signals=True)
def apply_in_owner(config_path):
 plan=json.loads((R/'control/EXECUTION_PLAN.json').read_bytes());assert os.getpid()==plan['parent_pid']==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks']==977758783
 thread=sys.modules['__main__'].DTC_L2_MLP_ADDON_THREAD;frame=sys._current_frames()[thread.ident]
 while frame is not None and not(frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/l2_ops.py'):frame=frame.f_back
 assert frame is not None;return install_on_frame(frame,json.loads(P(config_path).read_bytes()))
