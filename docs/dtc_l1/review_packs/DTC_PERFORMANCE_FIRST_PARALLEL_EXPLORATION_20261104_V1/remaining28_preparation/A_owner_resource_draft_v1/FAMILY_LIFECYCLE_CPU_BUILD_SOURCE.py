from pathlib import Path
import os,subprocess,json,hashlib
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');O=A/'agents/A_remaining28_owner_resource_v1';cpp=(A/'agents/A_structure_config_v1/oo_structure_cpu_fixture.cpp').read_text();idx=cpp.index('int main()')
extra=r'''
void inflight_pool1024_lifecycle(){
 auto c=base_cfg(64,8,1024);oo_frontend f(c);uint64_t cycle=1;std::vector<physical_identity> refs;
 for(unsigned u=0;u<128;++u){assert(f.admit(u+1));for(unsigned j=0;j<8;++j){f.advance_service(cycle);uint64_t addr=uint64_t(u*8+j)*128;assert(f.try_serve_tag(cycle,addr));auto r=f.access(cycle,u+1,addr);assert(r.kind==io_access_kind::NEW_MISS);refs.push_back(r.physical);++cycle;}}
 assert(f.occupancy()==128);assert(f.allocated_lines()==1024);assert(!f.admit(10000));
 for(auto r:refs)f.complete(r);
 for(unsigned j=0;j<1100;++j)f.advance_service(cycle++);
 for(unsigned j=0;j<128;++j){assert(f.retire_one_ready(cycle));assert(!f.retire_one_ready(cycle));++cycle;}
 assert(f.occupancy()==0);assert(f.allocated_lines()==512);assert(f.retires()==128);
 std::cout<<"{\"case\":\"PHYS1024_INFLIGHT_128x8_FULLPOOL_COMPLETE_RETIRE\",\"physical_allocated_before\":1024,\"after_refcount_release\":512,\"retired\":128,\"residual_valid_tags_not_freed\":512,\"PASS\":true}\n";
}
void pib192_merged_reference_lifecycle(){
 auto c=base_cfg();c.oo_pib_entries=192;oo_frontend f(c);physical_identity physical;uint64_t cycle=1;
 for(unsigned u=0;u<192;++u){f.advance_service(cycle);assert(f.admit(u+1));assert(f.try_serve_tag(cycle,0));auto r=f.access(cycle,u+1,0);assert(r.kind==(u?io_access_kind::PENDING_HIT:io_access_kind::NEW_MISS));if(!u)physical=r.physical;++cycle;}
 assert(f.occupancy()==192);assert(!f.admit(10000));assert(f.allocated_lines()==1);f.complete(physical);
 for(unsigned j=0;j<200;++j)f.advance_service(cycle++);
 for(unsigned u=0;u<192;++u){assert(f.retire_one_ready(cycle));assert(!f.retire_one_ready(cycle));++cycle;}
 assert(f.occupancy()==0);assert(f.allocated_lines()==1);assert(f.retires()==192);
 std::cout<<"{\"case\":\"PIB192_MERGED_REFERENCE_COMPLETE_RETIRE\",\"instructions\":192,\"shared_inflight_physical_line\":1,\"retired\":192,\"finite_retirement1_preserved\":true,\"PASS\":true}\n";
}
'''
extra+=r"""
void ports8_allocation4_boundary(){
 auto c=base_cfg();c.tag_requests_per_bank_per_cycle=2;c.tag_requests_per_cycle=8;oo_frontend f(c);f.advance_service(1);
 for(unsigned u=0;u<8;++u){assert(f.admit(u+1));assert(f.try_serve_tag(1,u*128));auto r=f.access(1,u+1,u*128);assert(r.kind==(u<4?io_access_kind::NEW_MISS:io_access_kind::NO_FREE_LINE));}
 assert(f.allocated_lines()==4);assert(f.new_misses()==4);f.advance_service(2);
 for(unsigned u=4;u<8;++u){assert(f.try_serve_tag(2,u*128));auto r=f.access(2,u+1,u*128);assert(r.kind==io_access_kind::NEW_MISS);}
 assert(f.allocated_lines()==8);
 std::cout<<"{\"case\":\"TAG_GRANTS8_ALLOCATION4_RETAINED\",\"cycle1_tag_grants\":8,\"cycle1_new_allocations\":4,\"nextcycle_remaining_allocations\":4,\"PASS\":true}\n";
}
"""
cpp=cpp[:idx]+extra+cpp[idx:];cpp=cpp.replace('pib_case();ports_case();}', 'pib_case();ports_case();inflight_pool1024_lifecycle();pib192_merged_reference_lifecycle();ports8_allocation4_boundary();}')
p=O/'family_lifecycle_cpu.cpp';p.write_text(cpp);(O/'tmp').mkdir(exist_ok=True);env=dict(os.environ,TMPDIR=str(O/'tmp'),TMP=str(O/'tmp'),TEMP=str(O/'tmp'));cmd=['g++','-std=c++17','-O2','-Wall','-Wextra','-I/root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim',str(p),'-o',str(O/'family_lifecycle_cpu')];r=subprocess.run(cmd,capture_output=True,text=True,env=env);(O/'CPU_COMPILE.stdout.log').write_text(r.stdout);(O/'CPU_COMPILE.stderr.log').write_text(r.stderr);print('COMPILE',r.returncode,r.stderr[-2000:]);assert r.returncode==0
r=subprocess.run([str(O/'family_lifecycle_cpu')],capture_output=True,text=True,env=env);(O/'FAMILY_LIFECYCLE_CPU.stdout.jsonl').write_text(r.stdout);(O/'FAMILY_LIFECYCLE_CPU.stderr.log').write_text(r.stderr);print('RUN',r.returncode,r.stdout[-2800:],r.stderr);assert r.returncode==0
(O/'FAMILY_LIFECYCLE_CPU_RESULT.json').write_text(json.dumps(dict(status='PASS_EXPECTED_TAG_HOLD_AND_NON_TAG_LIFECYCLE_CONTROLS',cases=[json.loads(x)for x in r.stdout.splitlines()],header_path='/root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/dtc-l1-common.h',header_sha256=hashlib.sha256(Path('/root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/dtc-l1-common.h').read_bytes()).hexdigest(),model_starts=0,trace_body_reads=0,GPU_tasks=0),indent=2)+'\n')

