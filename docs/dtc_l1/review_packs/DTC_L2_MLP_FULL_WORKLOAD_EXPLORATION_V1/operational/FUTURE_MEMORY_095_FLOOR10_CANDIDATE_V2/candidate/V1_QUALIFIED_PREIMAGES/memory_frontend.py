"""Future memory outer over unchanged existing IO outer. No import action."""
import pathlib,importlib.util,json,sys,hashlib
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');CFG=R/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json';IO_FRONT_SHA='01ba76be6b3f694ae077f21ceda1d108a4616ac54818028469d9afd262c43b7e'
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def adapt_io(io,cfg):
 lib=load('future_memory_native_library',cfg['library_path']);old=io.private_engine
 def private_engine(iocfg,padding=False,native_module=None):
  native,overlay=old(iocfg,padding,native_module);return lib.install_future_native(native,cfg,padding),overlay
 io.private_engine=private_engine;return io
def main(argv):
 io_path=R/'control/operational_amendments/shared_json_io_v1/io_frontend.py';assert hashlib.sha256(io_path.read_bytes()).hexdigest()==IO_FRONT_SHA;io=load('future_memory_original_IO_front',io_path)
 if argv[:2]==['result','archive']:return io.main(argv)
 try:cfg=json.loads(CFG.read_bytes())
 except(OSError,ValueError):return io.main(argv)
 if len(argv)<3 or argv[2]not in cfg.get('allowed_cohorts',[]):return io.main(argv)
 return adapt_io(io,cfg).main(argv)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:])))
 except Exception as e:print(json.dumps(dict(status='HOLD',reason=repr(e),science_retry=False)),file=sys.stderr);sys.exit(2)
