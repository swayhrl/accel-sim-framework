import pathlib,json,hashlib,subprocess,datetime,os
D=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_cpu_preparation_20261105_v1/agents/D_independent_review_v1')
A3=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1')
CORE=pathlib.Path('/root/data/dtc_failure_repair_20261025_v1/core')
D.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(n,o):
 p=D/n
 if p.exists():raise RuntimeError('Refuse overwrite '+str(p))
 p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
checks=[]
def check(n,x,e=None):checks.append({'check':n,'pass':bool(x),'evidence':e});assert x,n
cost=A3/'agents/A_hardware_cost_v1'
check('Frozen cost manifest bytes',sha(cost/'MANIFEST.json')=='a554120cbc7c68153c4f557233cf05b0e2df7b994da4b0b3f0c6958b3bf93812')
for f in json.loads((cost/'MANIFEST.json').read_text())['files']:
 p=cost/f['relative_path'];check('Cost file '+p.name,sha(p)==f['sha256'])
src=[]
for rel in ['src/gpgpu-sim/dtc-l1-common.h','src/gpgpu-sim/shader.cc','src/gpgpu-sim/gpu-cache.h']:
 p=CORE/rel;b=p.read_bytes();g=subprocess.run(['git','-C',str(CORE),'show','9eedb3131937748f0492fa83aad37d3691118d70:'+rel],capture_output=True,check=True).stdout
 check('Fixed Git source '+rel,b==g,sha(p));src.append({'path':str(p),'git_commit':'9eedb3131937748f0492fa83aad37d3691118d70','sha256':sha(p)})
h=(CORE/'src/gpgpu-sim/dtc-l1-common.h').read_text();shader=(CORE/'src/gpgpu-sim/shader.cc').read_text()
facts=[('128B model identity','constexpr uint64_t kLogicalLineBytes = 128;' in h),('Physical structure holds metadata without payload array','std::vector<waiter> waiters;' in h[h.index('  struct physical_line {',h.index('class oo_frontend')):h.index('  struct tag_entry {',h.index('class oo_frontend'))]),('LRU invalid slot chosen before victim','if (!tag.valid) return &tag;' in h),('Free scan requires unallocated','if (!m_phys[id].allocated)' in h),('Reclaim target victim reference guard','victim->valid && m_phys[victim->physical.id].ref_count == 0' in h),('Physical generation increment','++physical.generation' in h),('Fill identity checked','assert(fill_identity_matches(identity)' in h),('Single retirement cycle bound','if (cycle == m_retire_cycle) return false;' in h),('LDST full reference registration guard','candidate->next_reference != candidate->references.size()' in shader),('OO lower-create PIB coupling','m_dtc_l1_oo_lower_create_queue.size() +' in shader and 'm_config->dtc_l1_oo_pib_entries)' in shader)]
for n,x in facts:check(n,x)
fixture=A3/'agents/A_structure_config_v1/oo_structure_cpu_fixture.cpp'
local=D/'original_header_reproduction.cpp';local.write_bytes(fixture.read_bytes())
exe=D/'original_header_reproduction'
compile=subprocess.run(['nice','-n','15','g++','-std=c++14','-O0','-I'+str(CORE/'src/gpgpu-sim'),str(local),'-o',str(exe)],capture_output=True,text=True)
check('Original-header CPU compilation',compile.returncode==0,compile.stderr)
run=subprocess.run(['nice','-n','15',str(exe)],capture_output=True,text=True)
check('Original-header fixture execution',run.returncode==0,run.stderr)
rows=[json.loads(l) for l in run.stdout.splitlines() if l.strip()]
check('Both unsafe larger Tag organizations blocked at 641st allocation',sum(r.get('expected_structural_HOLD',False) and r.get('repeated_NO_FREE_LINE')==16 for r in rows)==2)
save('INITIAL_INDEPENDENT_CPU_AND_SOURCE_CHECKS.json',{'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'CPU-only fixed original header independent reproduction; no models, requests, production edits or active raw','checks':checks,'source_pins':src,'fixture':{'path':str(local),'sha256':sha(local),'copied_from':str(fixture),'binary_sha256':sha(exe),'compile_argv':['nice','-n','15','g++','-std=c++14','-O0','-I'+str(CORE/'src/gpgpu-sim'),str(local),'-o',str(exe)]},'results':rows,'limitations':['Repeated NO_FREE_LINE structural witness is not general liveness proof.','Standalone frontend empty PIB retirement test does not certify integrated LDST retirement; next_reference guard must hold.','Existing original-header fixture tests do not authorize new scientific runs.']})
print(json.dumps({'checks':len(checks),'all_PASS':all(x['pass'] for x in checks),'report':str(D/'INITIAL_INDEPENDENT_CPU_AND_SOURCE_CHECKS.json'),'sha256':sha(D/'INITIAL_INDEPENDENT_CPU_AND_SOURCE_CHECKS.json')}))
