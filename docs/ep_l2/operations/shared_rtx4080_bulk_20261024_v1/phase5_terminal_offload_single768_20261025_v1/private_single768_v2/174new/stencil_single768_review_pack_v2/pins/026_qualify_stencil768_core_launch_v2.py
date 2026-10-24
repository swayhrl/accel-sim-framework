"""Private launch protocol tests with fake CPU adapters, not real grouping."""
import pathlib,json,hashlib,sys,os,shutil,importlib.util
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');N=C.parent
Q=N/'stencil768_core_launch_qualification_A2';assert not Q.exists();Q.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();controller=C/'resume_stencil_single768_epoch4_v2.py'
g=Q/'GRANT_FOR_FUNCTION_EXTRACTION_ONLY.json';g.write_text(json.dumps({'status':'APPROVED_EXACT_STENCIL_LAST2_SINGLE768_EPOCH4','controller_sha256':sha(controller),'common_sha256':sha(C/'stencil768_common_v2.py')}))
oldargs=sys.argv;sys.argv=[str(controller),str(g)];ns={'__file__':str(controller)}
try:exec(compile(controller.read_text().split('\ndef main():',1)[0],str(controller),'exec'),ns)
finally:sys.argv=oldargs
u=ns['u'];proc=u.module(C/'validate_app_hot_resume_v4r3.py','proc','85ff5d68408632a4f15634bfa6a6d7a504429821ed8067f1ab8f39ce1b9a6909')
rows=[]
for index,case in enumerate(['normal_exit0','PASS_then_exit23','startup_receipt_failure']):
 base=Q/case;ctl=base/'control';ctl.mkdir(parents=True);work=base/'private_WORK';work.mkdir();kdir=work/'kernel';kdir.mkdir()
 shutil.copyfile(C/'stencil768_common_v2.py',ctl/'stencil768_common_v2.py')
 adapter=ctl/'stencil768_kernel_adapter_v2.py';adapter.write_text("import pathlib,json,sys\nj=json.loads(pathlib.Path(sys.argv[1]).read_text());pathlib.Path(j['marker']).write_text('ran');print(json.dumps({'status':'GROUPED_ALL_SHARDS_CRC_PASS','fixture_only':True}));raise SystemExit(j['exit'])\n")
 job={'common_sha256':sha(ctl/'stencil768_common_v2.py'),'adapter_sha256':sha(adapter),'marker':str(base/'ADAPTER_EXECUTED'),'exit':23 if case=='PASS_then_exit23'else 0}
 ns['C']=ctl;u.WORK=work;original_save=u.save
 if case=='startup_receipt_failure':
  def injected(p,o):
   if pathlib.Path(p).name.startswith('CORE_PROCESS_START_'):raise PermissionError('private durable child identity failure')
   return original_save(p,o)
  u.save=injected
 before={(r['pid'],r['ticks'])for r in proc.descendants(os.getpid())};error=None
 try:result=ns['run_core'](job,index,kdir)
 except BaseException as e:error=repr(e)
 finally:u.save=original_save
 after={(r['pid'],r['ticks'])for r in proc.descendants(os.getpid())};assert before==after,'launched own child not reaped'
 observed=(kdir/'CORE_OBSERVED_EXIT0.json').exists();marker=(base/'ADAPTER_EXECUTED').exists()
 if case=='normal_exit0':assert error is None and observed and marker
 elif case=='PASS_then_exit23':assert error and not observed and marker
 else:assert error and not observed and not marker
 rows.append({'case':case,'PASS':True,'error':error,'observed_exit0_receipt':observed,'CPU_adapter_marker':marker,'own_descendant_set_restored':True})
out=Q/'QUALIFICATION.json';out.write_text(json.dumps({'status':'ACTUAL_CONTROLLER_RUN_CORE_GATED_LAUNCH_AND_EXIT0_PUBLICATION_BOUNDARY_PASS','controller_sha256':sha(controller),'cases':rows,'scope':'Executes actual run_core/BOOT with private fake CPU adapters; no frozen grouping or scientific validator executes','production_Work_created':False,'GPU_SIM_109_or_registry_writes':0},indent=2)+'\n');print(json.dumps({'path':str(out),'sha256':sha(out),'status':'PASS'}))
