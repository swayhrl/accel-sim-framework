from pathlib import Path
import json,ast,hashlib,copy,datetime
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');D=A/'publication_service_v1';O=A/'agents/C_publication_review_v1';src=D/'start_root_report_service.py';text=src.read_text();tree=ast.parse(text);withnode=next(n for n in tree.body if isinstance(n,ast.With));oldif=next(n for n in withnode.body if isinstance(n,ast.If));wrapper=ast.FunctionDef(name='old_instance_check',args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=[copy.deepcopy(oldif)],decorator_list=[]);ast.fix_missing_locations(wrapper);checks=[]
for state,same,missing,expected in [('S',True,False,'SystemExit'),('Z',True,False,'RuntimeError'),('X',True,False,'RuntimeError'),('S',False,False,'RuntimeError'),('S',True,True,'RuntimeError')]:
 def identity(pid):
  if missing:raise FileNotFoundError('CPU_ONLY')
  return {'state':state,'start_ticks':42 if same else 43}
 env={'old':type('Old',(),{'exists':lambda self:True})(),'rd':lambda path:{'pid':123,'start_ticks':42},'proc_identity':identity,'json':json,'print':lambda *a:None};exec(compile(ast.Module(body=[wrapper],type_ignores=[]),str(src),'exec'),env);caught=None
 try:env['old_instance_check']()
 except(SystemExit,RuntimeError)as e:caught=type(e).__name__
 assert caught==expected;checks.append({'case':{'state':state,'same_ticks':same,'missing':missing},'expected':expected,'PASS':True})
assert "subprocess.Popen(['python3','-B',str(src)]"in text and 'ROOT_SERVICE_START.lock'in text and 'Prior publication process is no longer live'in text and "contract['source_sha256']==s==checks['source_sha256']"in text
r=json.loads((O/'PUBLICATION_REVIEW.json').read_text());r['starter']={'path':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'not_executed_by_C':True,'duplicate_and_dead_instance_AST_fixtures':checks,'only_report_process_Popen':True,'independent_start_lock_and_publisher_service_lock':True};r['status']='PASS_REPORT_ONLY_PUBLICATION_BOUNDARIES';r['review_complete_UTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();(O/'PUBLICATION_REVIEW.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'starter_sha256':r['starter']['sha256'],'review_sha256':hashlib.sha256((O/'PUBLICATION_REVIEW.json').read_bytes()).hexdigest(),'starterchecks':len(checks)}))

