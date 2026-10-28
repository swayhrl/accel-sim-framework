"""Registered alternate native entry. Old native46/fa3/IO/CPU2 bytes unchanged."""
import pathlib,json,hashlib,importlib.util,sys,os
P=pathlib.Path
D=P('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/strace_bpf_future_entry_v3')
CFG=D/'ACTIVE_ENTRY.json'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def parse(argv):
 assert len(argv)==5 and argv[0]=='experiment'and argv[1]in ['prepare','inspect','run-native']and argv[2].startswith('E2-DTCL2MLP-')and argv[3:]==['--project','DTC_L1'];return argv
def private_native(cfg,c,native_module=None,hooks=None,memory_cfg_override=None):
 producer=load('BPF_future_qualified_producer',cfg['source_paths']['producer']);assert sha(producer.__file__)==cfg['qualified_sources']['producer']
 native=native_module or load('BPF_future_old_native',cfg['native_source_path']);assert sha(native.__file__)==cfg['expected_pins'][cfg['native_source_path']];producer.validate(cfg,native.registered()[2]);mode=producer.select_mode(cfg,c,native.registered()[2]);assert mode is not None
 if hooks is not None:assert cfg['qualification_only']and native.registered()[2].get('qualification_only')is True
 memory=load('BPF_private_unchanged_fa3',cfg['memory_frontend_path']);assert sha(memory.__file__)==cfg['memory_frontend_sha256'];io_path=memory.R/'control/operational_amendments/shared_json_io_v1/io_frontend.py';assert sha(io_path)==memory.IO_FRONT_SHA;io=load('BPF_private_unchanged_IO',io_path)
 if memory_cfg_override is not None:assert cfg['qualification_only']and native.registered()[2].get('qualification_only')is True
 memcfg=memory_cfg_override or read(memory.CFG);assert c in memcfg['allowed_cohorts'],'OFFICIAL_MEMORY_SCOPE_SYNC_REQUIRED'
 io=memory.adapt_io(io,memcfg)
 if hooks and hooks.get('memory_lib'):
  for cell in io.private_engine.__closure__ or []:
   value=cell.cell_contents
   if hasattr(value,'__file__')and P(value.__file__)==P(memcfg['library_path']):hooks['memory_lib'](value)
 native,overlay=io.private_engine(read(io.CFG),False,native_module=native)
 return producer.configure_native(native,cfg,c,mode,hooks),producer
def main(argv,cfg=None,native_module=None,hooks=None,memory_cfg_override=None,delegate=None):
 argv=parse(list(argv));cfg=cfg or read(CFG);native=native_module or load('BPF_front_authority_native',cfg['native_source_path']);producer=load('BPF_front_scope',cfg['source_paths']['producer']);assert sha(producer.__file__)==cfg['qualified_sources']['producer'];c=argv[2];q=native.registered()[2]
 if not producer.candidate_scope(cfg,c,q):
  engineering=c in producer.read(cfg['exclusion_contract_path'])['scope_cohorts'];path=cfg['v2_entry_path']if engineering else cfg['default_native_entry'];tail=argv[1:]if engineering else argv
  expected=cfg['v2_entry_sha256']if engineering else cfg['expected_pins'][path];assert sha(path)==expected
  if delegate is not None:
   assert cfg['qualification_only']and q.get('qualification_only')is True;return delegate(path,tail)
  os.execv(path,[path,*tail]);raise AssertionError('exec returned')
 producer.validate(cfg,q);mode=producer.select_mode(cfg,c,q);assert mode=='BPF_REQUIRED'
 assert producer.unused(native.registered()[2],c),'SPENT_OR_SEALED_NO_RESUBMIT'
 previous=sys.argv;sys.argv=[str(cfg['source_paths']['frontend']),*argv]
 try:
  native,producer=private_native(cfg,c,native,hooks,memory_cfg_override)
  return native.prepare(c)if argv[1]in ['prepare','inspect']else native.run_native(c)
 finally:sys.argv=previous
if __name__=='__main__':
 try:
  args=sys.argv[1:];assert len(args)==7 and args[:1]==['--config'];cfg=read(args[1]);print(json.dumps(main(args[2:],cfg)))
 except Exception as error:print(json.dumps(dict(status='HOLD',reason=repr(error),science_retry=False)),file=sys.stderr);sys.exit(2)
