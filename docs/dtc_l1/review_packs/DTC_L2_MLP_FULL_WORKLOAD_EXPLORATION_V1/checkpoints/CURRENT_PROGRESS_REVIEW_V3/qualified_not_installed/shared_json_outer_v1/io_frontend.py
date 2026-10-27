"""Future-only newREQ native CLI destination; import has no action."""
import pathlib,importlib.util,json,hashlib,sys,os,copy
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';ID='SHARED_JSON_IO_OUTER_V1';CFG=R/'control/operational_amendments/shared_json_io_v1/ACTIVE_IO.json'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
ROLES=['source','frontend','extra_strict','owner']
def validate(cfg,q):
 assert cfg['status']=='ACTIVE_FUTURE_ONLY'and cfg['request']==REQ and cfg['overlay_id']==ID
 for role in ROLES+['QA','readback']:assert sha(cfg[role+'_path'])==cfg[role+'_sha256']
 qualified={k:cfg[k+'_sha256']for k in ROLES};qa=read(cfg['QA_path']);back=read(cfg['readback_path']);assert qa['status']=='PASS'and qa['native_prefix_qualified']is True and qa['additional_strict_qualified']is True
 assert qa['qualified_sources']==back['qualified_sources']==qualified and back['verified']is True
 assert qa['expected_pins']==back['expected_pins']==cfg['expected_pins']
 for path,digest in cfg['expected_pins'].items():assert sha(path)==digest
 assert cfg['frontend_sha256']==sha(__file__)
 record=q['additional_operational_overlays'][ID]
 for key in['request','overlay_id','expected_pins',*[k+'_sha256'for k in ROLES+['QA','readback']]]:assert record[key]==cfg[key],key
 assert record['status']=='ACTIVE'
 return record
def configure_native(native,cfg,fixture=False):
 helper=load('io_outer_helper',cfg['source_path']);helper.install_private_module(native,cfg['expected_pins'],1.0)
 oldengine=native.engine
 def engine():
  n=oldengine();old=n.exclusive;binding=dict(schema=ID,request=REQ,qualified_sources={k:cfg[k+'_sha256']for k in ROLES},QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],config_sha256=hashlib.sha256(js(cfg)).hexdigest(),expected_pins=cfg['expected_pins'],padding_optin=bool(cfg.get('_padding_optin')),snapshot_sha256=None)
  def exclusive(path,obj):
   path=P(path)
   if path.name.endswith('.INTENT.json'):
    snapshot=dict(schema=ID,config={k:v for k,v in cfg.items()if not k.startswith('_')},operational_overlay_record=copy.deepcopy(native.registered()[2]['additional_operational_overlays'][ID]),source_snapshots={k:dict(path=cfg[k+'_path'],sha256=cfg[k+'_sha256'],utf8=P(cfg[k+'_path']).read_bytes().decode('utf-8'))for k in ROLES},QA=read(cfg['QA_path']),QA_raw_utf8=P(cfg['QA_path']).read_bytes().decode('utf-8'),readback=read(cfg['readback_path']),readback_raw_utf8=P(cfg['readback_path']).read_bytes().decode('utf-8'),padding_optin=bool(cfg.get('_padding_optin')))
    out=P(obj['output']);helper.atomic_exclusive(out/'SHARED_JSON_IO_SNAPSHOT.json',snapshot);binding['snapshot_sha256']=sha(out/'SHARED_JSON_IO_SNAPSHOT.json')
   if path.name.endswith('.INTENT.json')or path.name in['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:
    assert binding['snapshot_sha256'];obj=dict(obj,additional_shared_json_io_binding=copy.deepcopy(binding))
   return old(path,obj)
  n.exclusive=exclusive;return n
 native.engine=engine;return native
def parse(argv):
 assert argv.count('--padding-only-admission-v1')<=1
 padding='--padding-only-admission-v1'in argv;argv=[x for x in argv if x!='--padding-only-admission-v1']
 assert len(argv)==5 and argv[0]=='experiment'and argv[1]in['prepare','inspect','run-native']and argv[2].startswith('E2-DTCL2MLP-')and argv[3:]==['--project','DTC_L1']
 return argv,padding
def private_engine(cfg,padding=False,native_module=None):
 native=native_module or load('shared_io_original_native',R/'tools/l2_native.py');validate(cfg,native.registered()[2]);helper=load('shared_io_front_helper',cfg['source_path']);assert set(cfg['expected_pins'])=={str(p)for p in helper.ALLOWED};helper.install_private_module(native,cfg['expected_pins'],1.0)
 overlay=None
 if padding:
  pcfg=read(R/'control/operational_amendments/padding_only_v1/ACTIVE_FRONTEND.json');front=load('shared_io_unchanged_padding_front',pcfg['frontend_path']);assert sha(front.__file__)==pcfg['frontend_sha256'];native,overlay=front.private_engine(pcfg,native_module=native);core=load('shared_io_unchanged_padding_core',pcfg['source_path']);overlay.activation_context=dict(allowed_cohorts_sha256=core.jsonsha(pcfg['allowed_cohorts']),extra_strict_sha256=pcfg['extra_strict_sha256'],frontend_sha256=pcfg['frontend_sha256'],owner_sha256=pcfg['owner_sha256'],QA_sha256=pcfg['QA_sha256'],readback_sha256=pcfg['readback_sha256'])
 return configure_native(native,dict(cfg,_padding_optin=padding)),overlay
def main(argv):
 if len(argv)>=3 and argv[:2]==['result','archive']and argv[2].startswith('E2-DTCL2MLP-')and'--padding-only-admission-v1'not in argv:
  legacy=R/'tools/l2_frontend.py';plan=read(R/'control/EXECUTION_PLAN.json');pin=next(x['sha256']for x in plan['source_pins']if P(x['path'])==legacy);assert sha(legacy)==pin;return load('io_unchanged_archive_front',legacy).main(argv)
 a,padding=parse(argv);cfg=read(CFG);native,overlay=private_engine(cfg,padding);q=native.registered()[2];c=a[2];assert c in q['admitted_specs']and c not in q['consumed']
 if padding:assert c in overlay.activation_context.get('allowed_cohorts',read(R/'control/operational_amendments/padding_only_v1/ACTIVE_FRONTEND.json')['allowed_cohorts'])
 if a[1]in['prepare','inspect']:return native.prepare(c)
 return native.run_native(c)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:])))
 except Exception as e:print(json.dumps(dict(status='HOLD',reason=repr(e),science_retry=False)),file=sys.stderr);sys.exit(2)
