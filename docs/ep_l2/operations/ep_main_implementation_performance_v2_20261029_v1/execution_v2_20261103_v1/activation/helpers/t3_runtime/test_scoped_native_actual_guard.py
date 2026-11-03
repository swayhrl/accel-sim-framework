"""TEST_ONLY actual AST guard controls in private files; no real authority or launch."""
import ast,copy,hashlib,json,pathlib,types
P=pathlib.Path;H=P(__file__).resolve().parent;E=H.parents[1];B=H/'scoped_guard_test_only';B.mkdir(exist_ok=True)
results=[]
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def test(label,fn,reject=False):
 try:fn();ok=not reject;err=None
 except Exception as e:err=repr(e);ok=reject
 results.append(dict(label=label,PASS=ok,error=err,TEST_ONLY=True));need(ok,repr(results[-1]))
for group in ['w','t']:
 src=E/('runtime_'+group)/'ep_perf_native_wv_modes_draft.py';tree=ast.parse(src.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='prepare');body=[]
 for n in fn.body:
  if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='s'for x in n.targets):break
  body.append(copy.deepcopy(n))
 fn=copy.deepcopy(fn);fn.name='guard_only';fn.body=body;module=ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[]));guard_source=ast.unparse(module);(B/('EXTRACTED_ACTUAL_'+group+'_GUARD.py')).write_text(guard_source+'\n')
 root=B/group/'E/t3';native=B/group/'shared';(root/'control').mkdir(parents=True,exist_ok=True);(root.parent/'bin').mkdir(parents=True,exist_ok=True);(native/'bin').mkdir(parents=True,exist_ok=True)
 prior=b'#!/bin/sh\n# TEST_ONLY_PRIOR_NOT_REAL_NATIVE\nexit 2\n';pre='#!/bin/sh\n# TEST_ONLY_OWN_PRELUDE\n';priorfile=root/'control/prior.bin';entry=root.parent/'bin/native';priorfile.write_bytes(prior);entry.write_bytes(pre.encode()+prior);(native/'bin/native').write_bytes(prior)
 route=dict(goal='TEST_ONLY_REQUEST',status='MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE',prior_entry_ref=dict(path=str(priorfile),sha256=sha(priorfile)),entry_ref=dict(path=str(entry),sha256=sha(entry)),own_prelude=pre)
 reg={'registered_future_requests':{'TEST_ONLY_REQUEST':{'native_entry_ref':route['entry_ref']}}}
 def invoke(r=None,q=None,shared=None,entrybytes=None):
  # Every case resets only owned TEST_ONLY files. Mock rows are never installed.
  rr=copy.deepcopy(route if r is None else r);qq=copy.deepcopy(reg if q is None else q);(native/'bin/native').write_bytes(prior if shared is None else shared);entry.write_bytes(pre.encode()+prior if entrybytes is None else entrybytes);(root/'control/NATIVE_ENTRY_ROUTE.json').write_text(json.dumps(rr));ns=dict(ROOT=root,NATIVE=native,GOAL='TEST_ONLY_REQUEST',os=types.SimpleNamespace(environ={'EP_FULL_PERF_NATIVE_ENTRY':'1'}),need=need,read=read,sha=sha,P=P,authority=lambda:(qq,{'TEST_ONLY':True}));exec(compile(module,str(src),'exec'),ns);return ns['guard_only']('TEST_ONLY_CASE')
 test(group+'_valid_registered_scoped_guard',invoke)
 bad=copy.deepcopy(reg);bad['registered_future_requests']={};test(group+'_unregistered_request_rejected',lambda:invoke(q=bad),True)
 bad=copy.deepcopy(reg);bad['registered_future_requests']['TEST_ONLY_REQUEST']['native_entry_ref']=dict(route['entry_ref'],sha256='0'*64);test(group+'_unregistered_entry_SHA_rejected',lambda:invoke(q=bad),True)
 test(group+'_actual_entry_SHA_drift_rejected',lambda:invoke(entrybytes=b'CORRUPT'),True)
 test(group+'_foreign_global_prior_change_rejected',lambda:invoke(shared=prior+b'CHANGED'),True)
 bad=copy.deepcopy(route);bad['prior_entry_ref']['sha256']='0'*64;test(group+'_prior_evidence_SHA_drift_rejected',lambda:invoke(r=bad),True)
 bad=copy.deepcopy(route);bad['own_prelude']='MISSING';test(group+'_missing_own_prelude_rejected',lambda:invoke(r=bad),True)
 bad=copy.deepcopy(route);bad['entry_ref']['path']=str(root/'wrong_native');badq=copy.deepcopy(reg);badq['registered_future_requests']['TEST_ONLY_REQUEST']['native_entry_ref']=bad['entry_ref'];test(group+'_wrong_scoped_entry_path_rejected',lambda:invoke(r=bad,q=badq),True)
 # SHA refreshed by hypothetical Main is still not enough if the prior suffix is absent.
 badbytes=pre.encode()+b'NO_PRIOR_SUFFIX';bad=copy.deepcopy(route);bad['entry_ref']['sha256']=hashlib.sha256(badbytes).hexdigest();badq=copy.deepcopy(reg);badq['registered_future_requests']['TEST_ONLY_REQUEST']['native_entry_ref']=bad['entry_ref'];test(group+'_missing_prior_suffix_rejected_even_with_registered_SHA',lambda:invoke(r=bad,q=badq,entrybytes=badbytes),True)
report=dict(schema='EP_MAIN_INDEPENDENT_SCOPED_NATIVE_ACTUAL_GUARD_CPU_V1',status='PASS_TEST_ONLY_ACTUAL_AST_GUARDS_NOT_AUTHORITY_OR_APPLICATION',checks=results,count=len(results),model_starts=0,real_registry_reads='NONE_IN_TEST_MOCK_AUTHORITY',real_registry_writes=0,shared_native_writes=0,Source_changes=0,guard_scope='actual prepare AST prefix before spec_for; not complete prepare/parser or appNI',source_refs=[dict(path=str(E/('runtime_'+x)/'ep_perf_native_wv_modes_draft.py'),sha256=sha(E/('runtime_'+x)/'ep_perf_native_wv_modes_draft.py'))for x in ['w','t']])
(H/'SCOPED_NATIVE_INDEPENDENT_GUARD_CPU.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],count=report['count'])))
