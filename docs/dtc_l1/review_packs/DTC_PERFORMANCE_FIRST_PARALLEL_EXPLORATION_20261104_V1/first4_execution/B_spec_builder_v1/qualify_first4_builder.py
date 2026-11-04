"""CPU-only source/spec/API qualification. No native API registration or prepare call."""
from pathlib import Path
import json,hashlib,ast,copy,importlib.util
D=Path(__file__).resolve().parent;O=D/'sandbox';R=Path('/root/data/dtc_perf_first_parallel_exploration_20261104_v1')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
checks=[]
def ck(n,v):assert v,n;checks.append({'check':n,'pass':True})
source=D/'build_first4_specs.py';tree=ast.parse(source.read_text());ck('builderimports_only_stdlib_no_nativeengine',all(not(isinstance(x,ast.ImportFrom)and x.module and x.module.startswith('perf'))for x in tree.body));deps=read(D/'DEPENDENCY_PINS.json')
for x in deps['files']:ck('source_pin_'+x['path'],sha(x['path'])==x['sha256'])
m=read(O/'control/MATRIX.json');ck('exact4PHYS768points',m['count']==len(m['points'])==4 and{p['program']for p in m['points']}=={'2DCONV','GEMM','MVT','BICG'}and not m['Tag_HOLD_or_other_variants_admitted']);
# Actual current canonical source is executed only with in-memory fake registered/read context;
# no native module import, registry files, lease, prepare or model path is called.
api=R/'tools/perf4_native.py';apibytes=api.read_bytes();mod=ast.parse(apibytes.decode());fn=next(x for x in mod.body if isinstance(x,ast.FunctionDef)and x.name=='canonical');pure=compile(ast.Module(body=[fn],type_ignores=[]),str(api),'exec');granted={'admitted_specs':{p['cohort']:p['spec_sha256']for p in m['points']}};auth=read(deps['authority_path'])
def fake_read(p):
 p=Path(p)
 if p==O/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json':return {'input_digests':[x['input_digest']for x in m['points']]}
 if p==O/'control/BUILD_PROFILE.json':return {'core_commit':auth['build']['core'],'framework_commit':auth['build']['framework']}
 return read(p)
g={'R':O,'REQ':deps['request'],'read':fake_read,'sha':sha,'registered':lambda:(None,None,granted,{})};exec(pure,g)
for p in m['points']:
 s=g['canonical'](p['cohort']);old=next(x for x in deps['selected']if x['program']==s['program']);b=read(old['baseline_spec_path']);ck(s['program']+'_exact_current_native_canonical_pure_context',s['cohort']==p['cohort']);ck(s['program']+'_complete270onlyphysical',len(s['expected_options'])==270 and{k for k in s['expected_options']if s['expected_options'][k]!=b['expected_options'][k]}=={'-gpgpu_dtc_l1_physical_lines'});ck(s['program']+'_runtime_environment_expected_unchanged',s['runtime_files']==b['runtime_files']and s['original_environment']==b['original_environment']and s['expected']==b['expected']);ck(s['program']+'_inputbinding_copy_exact',sha(O/'control/input_bindings'/(s['input_digest']+'.json'))==s['input_binding_sha256']);ck(s['program']+'_spec_alias_exact',sha(O/'control/specs'/(s['cohort']+'.json'))==sha(O/'control'/(s['cohort']+'_SPEC.json')));ck(s['program']+'_resources_exact_A',s['limits']==next(x for x in read(deps['resource_fields_path'])['points']if x['program']==s['program'])['limits'])
 for x in s['runtime_files']:ck(s['program']+'_runtime_link_'+x['target'],(O/x['target']).resolve()==Path(x['actual_realpath']).resolve()and sha(O/x['target'])==x['sha256'])
 for i,c in enumerate(s['configs']):ck(s['program']+'_activeconfig_'+str(i),sha(O/'DTC/env/DH_PHYS768_TAG64x8'/('config-'+str(i)+'.config'))==c['sha256'])
# Meaningful negative guards on the builder's own fixture files only.
sp=importlib.util.spec_from_file_location('first4_builder_CPU_only',source);b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);F=D/'cpu_only_negative_fixtures';F.mkdir(exist_ok=False);out=F/'output';out.mkdir();outside=F/'outside';outside.mkdir();(out/'link').symlink_to(outside);held=False
try:b.write_exact(out/'link/newchild/file',b'x',out)
except AssertionError:held=True
ck('symlink_parent_escape_refused_before_external_mkdir',held and not(outside/'newchild').exists());p=out/'existing';p.write_bytes(b'kept');held=False
try:b.write_exact(p,b'replace',out)
except AssertionError:held=True
ck('existing_different_output_not_overwritten',held and p.read_bytes()==b'kept');ck('no_native_intent_created_by_qualification',not(O/'control/qualification_ledger').exists());
(D/'API_COMPATIBILITY_REFS.json').write_text(json.dumps({'native_source':str(api),'native_source_sha256':hashlib.sha256(apibytes).hexdigest(),'tested_function':'canonical','test_mode':'ASTextracted exactfunction with in-memory fake registered/read fixtures; no actualgrant/registry/lease/nativeimport','strict_source':str(R/'tools/perf4_strict.py'),'strict_source_sha256':sha(R/'tools/perf4_strict.py'),'strict_terminal_invoked':False,'prepare_or_dispatch_invoked':False},indent=2)+'\n');(D/'CPU_QUALIFICATION.json').write_text(json.dumps({'schema':'DTC_PERFFIRST_FIRST4_SPEC_BUILDER_CPU_QUALIFICATION_V1','checks':checks,'count':len(checks),'all_pass':True,'actual4specs270options':True,'sandbox':str(O),'logicalroot':str(R),'new_models':0,'registrations':0,'R3_runtime_mutation':False,'inmemory_fixture_not_actual_authority':True},indent=2)+'\n');print(json.dumps({'status':'CPU_PASS_NO_START','checks':len(checks),'specs':4,'native_R3_writes':0,'registrations':0}))
