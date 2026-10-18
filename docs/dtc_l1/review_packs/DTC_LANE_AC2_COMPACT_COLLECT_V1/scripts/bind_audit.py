"""Bind final CPU artifacts, exact source allowlist and all source identities."""
import datetime,hashlib,json,os,re,socket,subprocess
from pathlib import Path
PACK=Path(__file__).resolve().parents[1]
FRAME=PACK.parents[3]
RAW=Path('/workspace/dtc-lane-ac2-compact-collect-174-v1')
RUN=RAW/'final-cpu'
CORE=Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-lane-ac2-compact-collect-core-174-v1')
BASE='83aca449135703c176cfab29ae43e1245d00a557'
X2='e32afdcf44be3374ff36d22568ed01a075459b6f'
EXPECTED='835417b37627e46eaaf215f3ff697263c94a18cc'
def git(p,*args): return subprocess.check_output(['git','-C',str(p),*args])
def sha(data): return hashlib.sha256(data).hexdigest()
def filehash(p): return sha(Path(p).read_bytes())
def write(name,data): (PACK/name).write_text(json.dumps(data,indent=2)+'\n')
head=git(CORE,'rev-parse','HEAD').decode().strip();assert head==EXPECTED
assert not git(CORE,'status','--porcelain').strip()
assert git(CORE,'rev-parse',X2+'^').decode().strip()=='c0a5e2c31e407c57e3a4af3ce529c921e8059a05'
git(CORE,'merge-base','--is-ancestor',X2,BASE);git(CORE,'merge-base','--is-ancestor',BASE,head)
paths=git(CORE,'diff','--name-only',BASE,head).decode().splitlines()
assert paths==['CMakeLists.txt','tests/dtc_l1_ac2_capacity_probe.cc']
cm=(CORE/'CMakeLists.txt').read_text();start=cm.index('    # AC2 feasibility evidence only:');end=cm.index('    add_executable(dtc_l1_collect_wb_resource_test',start)
assert (cm[:start]+cm[end:]).encode()==git(CORE,'show',BASE+':CMakeLists.txt')
source=[]
for label,path in [('AC2',CORE),('AC',Path('/workspace/worktrees/gpgpu-sim-dtc-lane-ac2-parent-source-174-v1')),('X2',Path('/workspace/worktrees/gpgpu-sim-dtc-lane-ac2-x2-source-174-v1'))]:
 commit=git(path,'rev-parse','HEAD').decode().strip()
 for entry in git(path,'ls-tree','-rz','HEAD').split(b'\0'):
  if not entry: continue
  metadata,name=entry.split(b'\t',1);mode,kind,blob=metadata.decode().split();name=name.decode()
  if kind!='blob': continue
  data=(path/name).read_bytes();source.append((label,commit,name,blob,sha(data)))
(PACK/'SOURCE_SHA256.tsv').write_text('scope\tcommit\tpath\tblob\tsha256\n'+''.join('\t'.join(row)+'\n' for row in source))
(PACK/'SOURCE_DELTA.patch').write_bytes(git(CORE,'diff','--binary',BASE,head))
write('SOURCE_DELTA.json',{'status':'PASS_TEST_ONLY_ALLOWLIST_ALL_PRODUCTION_BYTE_IDENTICAL_TO_AC','base':BASE,'head':head,'tree':git(CORE,'rev-parse','HEAD^{tree}').decode().strip(),'changed_files':[{'path':p,'sha256':filehash(CORE/p),'blob':git(CORE,'rev-parse',head+':'+p).decode().strip()} for p in paths],'CMake_exact_recovery':True,'all_production_unchanged':True,'original_tests_unchanged':True,'compact_parser_registered':False,'source_X2_OFF_recovery_receipt':'PARENT_SOURCE_RECOVERY.json'})
# Verify complete source identities after final build/tests, including all comparison sources.
before=json.loads((RAW/'IDENTITY_BEFORE.json').read_text())
for label,record in before['cores'].items():
 path=Path(record['path'])
 assert git(path,'rev-parse','HEAD').decode().strip()==record['HEAD']
 assert not git(path,'status','--porcelain').strip()
 for name,digest in record['files'].items(): assert filehash(path/name)==digest,(label,name)
(RAW/'IDENTITY_AFTER.json').write_text(json.dumps(before,indent=2)+'\n')
# Normal parser/CPU result belongs to this final round only.
qual=json.loads((RUN/'QUALIFICATION.json').read_text());assert len(qual['capacity_cases'])==45
executions=json.loads((RUN/'EXECUTIONS.json').read_text())
matrix=json.loads((RUN/'fresh-parent-matrix/CPU_TEST_RECEIPTS.json').read_text())
assert matrix['core']==head and len(matrix['OFF_state_equivalence'])==17
libraries={
 'AC2':Path('/workspace/builds/dtc-lane-ac2-final-release-174-v1/libcudart.so'),
 'AC':Path('/workspace/builds/dtc-lane-ac2-parent-174-v1/libcudart.so'),
 'X2':Path('/workspace/builds/dtc-lane-ac2-x2-174-v1/libcudart.so')}
binaries={label+'_library':p for label,p in libraries.items()}
for label in ['dtc_l1_ac2_capacity_probe','dtc_l1_collect_wb_pipeline_probe','dtc_l1_normal_export_probe']:
 binaries['AC2_'+label]=libraries['AC2'].parent/label
for label in ['parent-dtc_l1_ac2_capacity_probe','x2-dtc_l1_ac2_capacity_probe','x2-dtc_l1_collect_wb_pipeline_probe']: binaries[label]=RUN/label
binaries['AC_pipeline_probe']=libraries['AC'].parent/'dtc_l1_collect_wb_pipeline_probe'
identities={}
for label,p in binaries.items():
 note=subprocess.check_output(['readelf','-n',str(p)],text=True)
 identities[label]={'path':str(p),'sha256':filehash(p),'bytes':p.stat().st_size,'build_id':re.search(r'Build ID: (\w+)',note).group(1),'dynamic_section':subprocess.check_output(['readelf','-d',str(p)],text=True)}
for label,p in libraries.items():
 strings=subprocess.check_output(['strings',str(p)],text=True)
 identity=next(s for s in strings.splitlines() if s.startswith('gpgpu-sim_git-commit-'))
 expected={'AC2':head[:8],'AC':BASE[:8],'X2':X2[:8]}[label]
 assert identity=='gpgpu-sim_git-commit-'+expected+'_modified_0.0.',identity
 identities[label+'_library']['embedded_source']=identity
# All executed probe/library hashes must remain fixed after each process.
for rec in executions+matrix['processes']:
 if 'executable_sha256' in rec: assert filehash(rec['argv'][0])==rec['executable_sha256']
 if 'library_sha256' in rec: assert filehash(rec['library'])==rec['library_sha256']
 if 'probe_sha256' in rec: assert filehash(rec['argv'][0])==rec['probe_sha256']
 if 'loaded_library_sha256' in rec: assert filehash(rec['loaded_library'])==rec['loaded_library_sha256']
# Compiler flags and actual dynamic loads are kept separately from source identity.
compiles=[]
for label,p in libraries.items():
 entries=json.loads((p.parent/'compile_commands.json').read_text())
 assert all('-DNDEBUG' not in e['command'] for e in entries)
 compiles.append({'label':label,'path':str(p.parent/'compile_commands.json'),'sha256':filehash(p.parent/'compile_commands.json'),'assertions_enabled':True,'commands':len(entries)})
ctests=[]
for tag,total in [('candidate',9),('parent',8),('x2',7)]:
 p=RUN/('ctest-'+tag+'.stdout');text=p.read_text()
 assert '100% tests passed, 0 tests failed out of '+str(total) in text
 ctests.append({'scope':tag,'passed':total,'total':total,'path':str(p),'sha256':filehash(p)})
write('7_PLUS_AC_PLUS_AC2_CTEST.json',{'status':'PASS_CPU_REGRESSION_AND_CAPACITY_BOUND_ONLY','tests':ctests,'compact_integration_PASS':False})
write('CPU_TEST_RECEIPTS.json',{'status':qual['status'],'qualification':qual,'inherited_parent_matrix':matrix,'executions':executions})
write('PARENT_SOURCE_RECOVERY.json',json.loads((RUN/'PARENT_SOURCE_RECOVERY.json').read_text()))
write('RESOURCE_MODEL.json',{'status':'SCIENTIFIC_STOP_RAW_RETENTION_CAPACITY','production_compact_implemented':False,'actual_new_data_bytes_relative_to_parent':0,'production_parent_data_bytes_per_SM':163840,'requested_compact_data_bytes_per_SM':8192,'requested_data_bytes_64SM':524288,'test_local_banks':2,'test_local_sectors_per_bank':128,'proven_source_API_capacity_witness_sectors':512,'raw_retention_lower_bound_for_witness_bytes':16384,'source_API_witness_is_real_trace_or_ISA':False,'manual_pool_witness_sectors':2560,'manual_pool_raw_bytes':81920,'retire_per_cycle_unchanged':1,'collect_sector_per_cycle_unchanged':4,'fallback_not_implemented':True})
write('SHA_BINDING.json',{'status':'PASS_FINAL_FRESH_SOURCE_ELF_LOAD_BINDING_CPU_STOP_ARTIFACT','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'uid':os.getuid(),'core':{'head':head,'tree':git(CORE,'rev-parse','HEAD^{tree}').decode().strip(),'parent':BASE,'x2_ancestor':X2,'branch':git(CORE,'branch','--show-current').decode().strip(),'source_before_after_unchanged':True},'framework_tools_source':git(FRAME,'rev-parse','HEAD').decode().strip(),'framework_input':'134a77798a2502a308c7f1e439a8f39dbc3ee043','binaries':identities,'compilations':compiles,'runtime_map_receipts':str(RUN/'EXECUTIONS.json'),'old_parent_matrix_abort_maps':'5 unsupported config aborts have no flushed runtime-map witness; not positive loads','trace_binary_built_or_executed':False,'full_canary_native_GPU_starts':0,'raw':str(RAW),'own_build_parallelism_max':2,'initial_and_final_source_manifest':{'before_sha256':filehash(RAW/'IDENTITY_BEFORE.json'),'after_sha256':filehash(RAW/'IDENTITY_AFTER.json')},'scope':'Final fresh immutable-source build only; earlier loader failure, insufficient test-budget and stale incremental build-string products are excluded and retained'})
print(json.dumps({'core':head,'status':qual['status'],'capacity_processes':45,'AC_ON_equivalence':len(qual['AC_ON_equivalence']),'ctests':[x['passed'] for x in ctests],'bound_source_files':len(source)}))
