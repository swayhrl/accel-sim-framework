"""Incremental exact-base audit only; no compiler, fixture or application."""
from pathlib import Path
import hashlib,json,re,subprocess

CORE=Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane2-repair-r3')
OUT=Path('/workspace/results/ep_l2_ft20261016/lane2/review_r5_exact62')
BASE='62dc1d179b5516e68b21b695c7a9c5d0667e9671'
PUB='c93d900e1f968a3b69990dc29b78d50fc18f35ac'
SOURCE='cbdf145314dbe5dcd9006a5de4e94f7b19fbbb71'
def git(*args):return subprocess.check_output(['git',*args],cwd=CORE,text=True)
def old(path):return git('show',BASE+':'+path)
def new(path):return (CORE/path).read_text()
def body(text,sig):
 a=text.index('{',text.index(sig));i=a+1;n=1
 while n:
  if text[i]=='{':n+=1
  if text[i]=='}':n-=1
  i+=1
 return text[a+1:i-1]
checks=[]
def check(name,ok,evidence):
 assert ok,name
 checks.append({'boundary':name,'result':'SOURCE_CHECK_ONLY_PASS','evidence':evidence})
assert git('rev-parse','HEAD').strip()==SOURCE
ft=new('src/gpgpu-sim/ep-l2-ft-cache.inc');tvd=new('src/gpgpu-sim/ep-l2-tvd-cache.inc')
host=body(ft,'bool l2_cache::ft_try_force_tag_access(')
commit=host.index('// Commit starts here:')
check('exact_Lane1_candidate_tree',git('rev-parse',BASE+'^{tree}')==git('rev-parse',PUB+'^{tree}'),{'candidate':BASE,'publication':PUB,'tree':git('rev-parse',BASE+'^{tree}').strip()})
method='unsigned long long l2_cache::ft_physical_cycle()'
check('canonical_physical_clock',body(ft,method)==body(old('src/gpgpu-sim/ep-l2-ft-cache.inc'),method) and 'return ft_physical_cycle();' in body(tvd,'unsigned long long l2_cache::m_gpu_cycle_for_tvd()'),'Lane1 helper preserved verbatim; TVD helper delegates to it')
sp='src/gpgpu-sim/l2cache.cc'
check('enclosing_try_wrapper_retained',all(body(new(sp),s)==body(old(sp),s) for s in ['bool memory_sub_partition::ft_try_force_l2_tag_update(','void memory_sub_partition::force_l2_tag_update(']),'exact Lane1 closure/offset-on-success and abort wrapper retained')
check('full_address_GPU_memcpy_retained',body(new('src/gpgpu-sim/gpu-sim.cc'),'void gpgpu_sim::perf_memcpy_to_gpu(')==body(old('src/gpgpu-sim/gpu-sim.cc'),'void gpgpu_sim::perf_memcpy_to_gpu('),'full-width address and nonaligned endpoint code unchanged from62dc1d')
check('shared_WAD_and_lease_guard','ep_l2_wad_occupancy() || m_tvd_lookup || m_tvd_read' in host[:commit] and 'm_ep_l2_wad_entries_live' not in host,'mandatory TVD/WAD queried through sole shared authority, no unused old-set guard')
check('refusal_before_commit','return false;' in host[:commit] and 'return false;' not in host[commit:] and not re.search(r'm_ep_l2_payload\.(release|reserve)\(|m_tvd->reclaim\(',host[:commit]),'all false returns, masks/dirty/pin/pending/generation/landing checks precede first metadata mutation')
check('exact_optional_alias_guard',all(t in host[:commit] for t in ['status != MISS','entry.reclaimable()','entry.incarnation == std::numeric_limits<std::uint64_t>::max()','slot.allocation_role != ep_l2_payload_store::TVD','slot.pins','slot.pending_sector_mask.any()','alias_payload.generation']) and 'm_tvd->reclaim(alias, released, ft_physical_cycle())' in host[commit:],'exact address/ticket and actual role/owner/pin/generation checked before reclaim; physical lifetime clock')
check('Tag_commit_same_reserved_index','actual_index == index && "host prefill must commit the pre-reserved Tag index"' in host and 'baseline_cache::force_tag_access(addr, time, mask)' in host,'native Tag time and actual chosen-index assertion retained')
header='src/gpgpu-sim/l2cache.h';pattern='unsigned long long ft_bank_grants_for_test(unsigned bank) const'
check('upstream_duplicate_definition_removed',old(header).count(pattern)==2 and new(header).count(pattern)==1,{'upstream_definition_lines':[i for i,l in enumerate(old(header).splitlines(),1) if pattern in l],'candidate_count':1,'compiler_invoked':False})
fixture=new('tests/ep_l2/test_tvd_production.cc')
check('new_try_gate_prepared',all(s in fixture for s in ['--candidate62-gates','const new_addr_type a=0x100000000ULL','assert(!f.try_warm(a))','assert(f.try_warm(a))','dir->live(unrelated)','offset+(accepted?1:0)']),'one new uncompiled actual-producer gate; high address/held-response/dirty refusal/exact alias after WB')
for p in ['CMakeLists.txt','src/gpgpu-sim/ep-l2-ft-cache.inc','src/gpgpu-sim/l2cache.h']:
 assert not re.search(r'^(<<<<<<<|=======|>>>>>>>)',new(p),re.M)
result={'core_source_commit':SOURCE,'base_candidate':BASE,'base_publication':PUB,'kind':'incremental exact-base source audit; NOT compilation/runtime/independent qualification','previous_13_checks':'not rerun; retained in immutable preadapt r1','new_source_checks':checks,'compiler_invoked':False,'runtime_tests_executed':0}
(OUT/'EXACT_BASE_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'source':SOURCE,'incremental_source_checks':len(checks),'runtime_tests_executed':0}))
