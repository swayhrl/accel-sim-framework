from pathlib import Path
import json,hashlib,sys,importlib.util,copy,ast,types,gzip,datetime,subprocess
sys.dont_write_bytecode=True
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');D=A/'publication_service_v1';O=A/'agents/C_publication_review_v1';F=O/'CPU_PUBLISH_FIXTURES';F.mkdir(exist_ok=True);src=D/'report_only_publisher.py';rd=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();expected='acbb284231abf5c0d3dfe53a588e2101bdf778d7729d9fe38736b82a3f4c9f1f';assert sha(src)==expected;sp=importlib.util.spec_from_file_location('C_publisher_final_readonly',src);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);checks=[]
def ck(name,b,detail=None):checks.append({'check':name,'PASS':bool(b),'detail':detail});assert b,name

def reject(name,fn):
 try:fn()
 except(AssertionError,KeyError,ValueError,FileNotFoundError,RuntimeError)as err:ck(name,True,{'expected_rejection':type(err).__name__});return
 raise AssertionError('EXPECTED_REJECTION '+name)
actual=rd(m.BP);m.checked_provider(actual);ck('Actualsourcequalified Bprovider accepted exact48/32/192/144refs',True,{'provider_path':str(m.BP),'provider_sha256':sha(m.BP),'snapshot_manifest':actual['manifest'],'summary':actual['summary']})
for key,val in [('source_qualified',False),('new_model_starts',1),('native_scientific_writes',1),('request','UNAUTHORIZED'),('sole_publisher','AGENT')]:
 b=copy.deepcopy(actual);b[key]=val;reject('Reject provider '+key,lambda b=b:m.checked_provider(b))
for name,change in [('wrong_adapter_manifest',lambda d:d.update(qualification_manifest={'path':'/UNQUALIFIED','sha256':'0'*64})),('wrong_budget',lambda d:d['summary'].update(registered_remaining=49)),('fake_terminal',lambda d:(d.update(all_registered48_terminal_verified=True),d['summary'].update(all_registered48_terminal_verified=True,accepted_CH=48,archived_negative_CH=0,verification_hold=0,await_result=0,accepted_six_source_slots=192,registered_consumed=1,registered_remaining=47))),('modified_summary_not_snapshot',lambda d:d['summary'].update(core32_common_both_F_n=max(0,d['summary']['core32_common_both_F_n']-1))),('wrong192',lambda d:d['summary'].update(expected_six_source_slots=350))]:
 b=copy.deepcopy(actual);change(b);reject(name,lambda b=b:m.checked_provider(b))
for s in ['/absolute','../escape','valid/../../escape']:reject('Pathreject '+s,lambda s=s:m.rel(s))
ck('Safe simple relative artifactpath accepted',m.rel('safe/REPORT.json')==Path('safe/REPORT.json'))
inside=F/'source';inside.mkdir(exist_ok=True);outside=F/'outside.txt';outside.write_text('CPU_ONLY_NOT_SCIENCE');link=inside/'escape'
if not link.exists():link.symlink_to(outside)
reject('Source symlinkescape rejected beforeexport',lambda:m.verified(link,sha(outside),inside))
branch=m.git('branch','--show-current');ck('Read-onlyGitcheck isolatednewbranch/base only',branch==m.BRANCH=='hrl/dtc-stage-iia-remaining48-execution-20261104-v1'and m.git('merge-base',m.BASE,'HEAD')==m.BASE and m.REL=='docs/dtc_l1/review_packs/DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'and m.W.resolve().is_relative_to(A.resolve()))
contract=rd(D/'SERVICE_CONTRACT.json');cpu=rd(D/'CPU_CHECKS.json');approval=rd(D/'FIGURE_VISUAL_APPROVAL.json');fixedfig=rd(D/'APPROVED_FIGURE_PROVIDER.fixed.json');ck('Servicecontract/selfcheck binds exactsource andschedule/no scienceclosure',contract['source_sha256']==cpu['source_sha256']==expected and contract['interval_seconds']==1800 and contract['exact_scientific_budget']==48 and contract['fixed_core_inputs']==32 and contract['expected_six_source_slots']==192 and not contract['terminal_publish_is_final_scientific_review']and contract['model_launches']==contract['native_writes']==0)
ck('Onlyfixed approveddated076figure independentofmovingFP',m.FP==D/'APPROVED_FIGURE_PROVIDER.fixed.json'and fixedfig['manifest']==approval['approved_manifest']==contract['approved_figure_manifest']and fixedfig['manifest']['sha256']=='076136470ec6c047f59d6e293d08c69df16512d6880b855e315173c5f7ba857f'and sha(fixedfig['manifest']['path'])==fixedfig['manifest']['sha256']and all(sha(x['path'])==x['sha256']for x in fixedfig['files'])and fixedfig['common_both_F_n']==11 and fixedfig['accepted_new48']==11)
# Call actualfigureexport with allwrites intercepted, no worktree mutations.
oldwrite,oldput=m.write,m.put;writes=[];m.write=lambda p,b:writes.append(str(p));m.put=lambda p,v:writes.append(str(p));fig=m.export_figures();ck('Productionfigureexport usesfixedapprovedbytes only no replot',fig==fixedfig and len(writes)>0);m.write,m.put=oldwrite,oldput
source=src.read_text();tree=ast.parse(source);imports=[ast.unparse(n)for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))];ck('Publisher imports no model/native/controller modules',not any(any(s in n for s in ['stage2_native','stage2_ops','stage2_results','importlib','ctypes','signal'])for n in imports))
ck('Only subprocess API is gitwrapper no launch/queue/signal',len([n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='subprocess'])==1 and "cmd=['git'"in source and all(s not in source for s in ['run-native','Py_AddPendingCall','kill(','os.kill','gdb','run_scheduler(','reset --hard','--force']))
ck('ExplicitnewREL staging guard and nonforce exactbranchpush',"git('add','-f','--',*paths)"in source and "all(x.startswith(REL+'/')for x in changed)"in source and "git('push','origin',v['commit']+':refs/heads/'+BRANCH"in source and "git('branch','--show-current')==BRANCH"in source)
ck('SnapshotRESULTsha export no liveanalysisglob/asof substitution',"for row in observed['observations']"in source and "row['RESULT_sha256']"in source and "glob('*.RESULT.json')"not in source)
ck('Timerterminal closure explicitnonfinal andnosimulation',"time.monotonic()-last>=1800 or terminal"in source and "time.sleep(30)"in source and "'TERMINAL_PROGRESS_PUBLICATION_COMPLETE.json'"in source and 'final_scientific_closure=False'in source and 'automatic_next_phase=False'in source)
# Inspectcurrentstaticexport sources/manifests without performing export.
plan=rd(m.R/'control/EXECUTION_PLAN.json');publicpins=[]
for z in plan['source_pins']:
 p=Path(z['path']);assert sha(p)==z['sha256'];public=not(p.is_relative_to(m.R)and'input_bindings'in p.parts)
 if public:
  b=p.read_bytes();assert not b.startswith(b'\x7fELF')and p.suffix not in ['.traceg','.part','.out'];publicpins.append(str(p))
ck('122sourcepins only metadata/code/config public noELF/trace/raw',len(plan['source_pins'])==122 and len(publicpins)==98)
static=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='static_export');packnode=next(n for n in static.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='packs'for t in n.targets));packs=ast.literal_eval(packnode.value);nfiles=0
for relpath,pin in packs:
 p=A/'agents'/relpath;assert sha(p)==pin;manifest=rd(p)
 for z in manifest['files']:
  rel=m.rel(z['path']);b=m.verified(p.parent/rel,z['sha256'],p.parent);assert len(b)<8*1024**2 and not b.startswith(b'\x7fELF')and not str(rel).endswith(('.traceg','.log.gz','.part'));nfiles+=1
ck('Frozen8reviewpack members qualified and privatefixtures/raw excluded',len(packs)==8 and nfiles==66)
# Exercisependingpush branch of actualpublish in a C-owned sandbox. No realgit,
# network, staticexport, model/native writes or service/main invocation.
S=F/'PENDING_PUSH_SANDBOX';S.mkdir(exist_ok=True);(S/'service').mkdir(exist_ok=True);(S/'work').mkdir(exist_ok=True);commit='c'*40;pending={'commit':commit,'branch':m.BRANCH,'UTC':'CPU_ONLY','all48_terminal_verified':False,'final_scientific_closure':False,'manifest_sha256':'CPU_ONLY','summary':{'CPU_ONLY_NOT_SCIENTIFIC_RESULT':True}};m.A=S;m.D=S/'service';m.O=S/'work';m.put(m.D/'PENDING_PUSH.json',pending)
for name in ['MANIFEST.json','LATEST_STATUS.json','analysis/STAGEIIA_REMAINING48_CORE32_RESULTS.md','analysis/STAGEIIA_REMAINING48_SUMMARY.json.gz']:
 p=m.O/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(('CPU_ONLY '+name).encode())
commands=[];failure={'first':True}
def gitmock(*args,**kwargs):
 commands.append(list(args))
 if args==('rev-parse','HEAD'):return commit
 if args[0]=='push':
  if failure['first']:failure['first']=False;raise RuntimeError('CPU_ONLY_TRANSPORT_FAILURE')
  return ''
 if args[0]=='ls-remote':return commit+'\trefs/heads/'+m.BRANCH
 raise AssertionError('UNEXPECTED_GIT_MUTATION '+str(args))
m.git=gitmock;m.urllib=types.SimpleNamespace(request=types.SimpleNamespace(ProxyHandler=lambda p:None,build_opener=lambda *a:types.SimpleNamespace(open=lambda url,timeout:types.SimpleNamespace(read=lambda:(m.O/url.split('/'+m.REL+'/')[-1]).read_bytes()))));before=m.sha(m.D/'PENDING_PUSH.json');reject('Actualpublish transportfail preserves samependingcommit',m.publish);ck('Pendingrecord unmodified after failedpush',m.sha(m.D/'PENDING_PUSH.json')==before);result=m.publish();pushes=[c for c in commands if c[0]=='push'];ck('Actualpublish retry exactlysamecommit no rebuild/add/commit',len(pushes)==2 and pushes[0]==pushes[1]==['push','origin',commit+':refs/heads/'+m.BRANCH]and not(m.D/'PENDING_PUSH.json').exists()and result['status']=='PUSH_LSREMOTE_HTTPS_VERIFIED'and result['final_scientific_closure']is False)
ck('FinalRootsource unaffected byCPU sandbox',sha(src)==expected)
report={'schema':'C_REMAINING48_REPORT_ONLY_PUBLICATION_REVIEW_V1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_REPORT_ONLY_PUBLICATION_BOUNDARIES','source_sha256':expected,'source_path':str(src),'checks':checks,'actual_provider_at_review':actual,'approved_figure_manifest':approval['approved_manifest'],'sandbox_git_commands':commands,'scientific_models_started':0,'native_registration_owner_queue_or_control_actions':0,'real_Git_mutations_or_pushes_by_C':0,'service_started_by_C':False,'limits':['Thisqualifiespublication service boundaries,notactualremotecommit/readback andnotfull48scientificterminalreview.','Figures remainapproved01:35snapshot11/32 whiletablesadvance withtheirownsourceasof.','Pendingcommit transportretry ismocked insideC-ownedfixture;freshpublishing stillrequiresqualifiedBprovider.','Initialreview identifiedproviderqualification/summarybinding gapandmovingfigureavailabilitycoupling;RootfixedbothbeforethisPASS.']};(O/'PUBLICATION_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':len(checks),'sha256':sha(O/'PUBLICATION_REVIEW.json'),'public_sourcepins':len(publicpins),'review_members':nfiles}))
