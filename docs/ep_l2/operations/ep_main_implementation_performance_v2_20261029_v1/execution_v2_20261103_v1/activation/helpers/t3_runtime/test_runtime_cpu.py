"""TEST_ONLY small artifact controls, not application NI or scientific acceptance."""
import ast,copy,hashlib,importlib.util,json,pathlib,sys,tarfile
P=pathlib.Path;H=P(__file__).resolve().parent;E=H.parents[1];R=E/'runtime_t';sys.path.insert(0,str(R))
import ep_perf_common_v2 as c
import ep_perf_native_wv_modes_draft as e
import ep_perf_archive as a
import t3_application_ni as ni
import mode_aware_terminal as parser
import t3_counter_audit as audit
results=[]
def test(name,fn,reject=False):
 try:fn();ok=not reject;err=None
 except Exception as ex:ok=reject;err=repr(ex)
 results.append(dict(label=name,PASS=ok,error=err,TEST_ONLY=True));assert ok,results[-1]
def need(v):assert v
for p in sorted(R.rglob('*.py')):ast.parse(p.read_text())
test('all_python_AST',lambda:need(True))
test('exact_new_ROOT',lambda:need(c.ROOT==E/'t3'))
test('exact_fresh_request',lambda:need(c.GOAL=='EP_L2_T_THREE_ARM_CAUSAL_CONV16X8_V1'and c.FRONTEND_GOAL!=c.GOAL))
test('exact_6_cohorts_3_primary',lambda:need(len(e.EXACT_COHORTS)==6 and len(e.PRIMARY_OFF)==3))
test('foreign_cohort_rejected',lambda:e.spec_path('EP_PERF_CONV_F_G16_W8_V1'),True)
test('parser_freeze_allpins',parser.verify)
test('archive_scope_is_new_true164',lambda:need(str(a.ARCHIVE_ROOT).endswith('/ep_l2_execution_v2_20261103_v1/T3_CONV16X8')))
test('postprocess_new_common_import',lambda:need('from ep_perf_common_v2 import *'in(R/'ep_perf_postprocess.py').read_text()))
test('consume_before_Popen_text_control',lambda:need((R/'ep_perf_native_wv_modes_draft.py').read_text().index("transaction('CONSUME_EXACT_ONE_BEFORE_FORK_NO_REFUND'")<(R/'ep_perf_native_wv_modes_draft.py').read_text().index('p = subprocess.Popen(')))
fixture=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/implementation_performance_v2_20261029_v1/agent_c_formal_closure/synthetic_parser_fixtures')
model={'mechanism_metrics':{'full_mechanism_records':{'readonly':{i:{'resource':dict(query_count=0,query_wait_cycles=0,query_port_wait_attempts=0)}for i in range(64)}}}}
for mode in ['F_MINUS_T','LEGACY_F','CORRECTED_F']:
 for on in [False,True]:
  s=dict(T=mode!='F_MINUS_T',ordinary_ro_tag_relief=mode=='CORRECTED_F',observer_profile='T3_DIAG_ON'if on else'T3_PRIMARY_OFF')
  path=fixture/(('ON_'+mode+'_TEST_ONLY.log')if on else(mode+'_TEST_ONLY_SYNTHETIC.log'))
  test('preserved_P1_TP_full_audit_'+mode+str(on),lambda path=path,s=s:audit.audit(path,s,model))
base=dict(cycles=100,instructions=200,CTA=1,kernel_count=1,hardware_drained=True,model=dict(raw_log_sha256='a',x=[1,2]),application=dict(actual_options={'a':'1'},ordered_kernel_catalog=[1],application_scopes={'s':1}))
other=copy.deepcopy(base);other['model']['raw_log_sha256']='b'
test('NI_excludes_only_raw_identity',lambda:need(ni.projection(base)==ni.projection(other)))
other['model']['x']=[1,3]
test('NI_detects_semantic_difference',lambda:need(ni.projection(base)!=ni.projection(other)))
scratch=H/'cpu_scratch';scratch.mkdir(exist_ok=True);origin=scratch/'origin';origin.mkdir(exist_ok=True);(origin/'TEST_ONLY.txt').write_text('TEST_ONLY_SMALL_ARTIFACT_NOT_SCIENCE\n');members=a.inventory(origin);archive=scratch/'TEST_ONLY.tar'
with tarfile.open(archive,'w')as stream:
 for row in members:stream.add(origin/row['member'],arcname=row['member'])
manifest=scratch/'MANIFEST_TEST_ONLY.json';manifest.write_text(json.dumps(dict(archive_sha256=c.sha(archive),members=members)))
for name in ['FIRST','INDEPENDENT']:
 target=scratch/('RESTORED_TEST_ONLY_'+name)
 test('tiny_native_restore_'+name,lambda target=target:a.restore(archive,manifest,target,1024))
report=dict(schema='EP_T3_RUNTIME_SCOPE_CONTROL_TEST_ONLY_V1',status='PASS_CPU_ONLY_NOT_APPLICATION_NI_OR_MAIN_APPROVAL',controls=results,count=len(results),model_starts=0,registry_writes=0,real_native_route_writes=0,archive_tests='TINY_LOCAL_TEST_ONLY_NOT_TRUE164_SCIENTIFIC_ARCHIVE')
(H/'CPU_CONTROLS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],count=len(results))))
