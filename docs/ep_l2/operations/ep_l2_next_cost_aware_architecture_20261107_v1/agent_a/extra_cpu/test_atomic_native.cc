#define main source_fixture_main
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1/agent_a/core/tests/ep_l2/test_optional128.cc"
#undef main
int main(int argc,char**argv) {
 setvbuf(stdout,nullptr,_IONBF,0);assert(argc==4);
 scenario f(argv[1],argv[2],true,true,false,1,2,1,16,false,std::stoul(argv[3]));
 puts("NATIVE_ATOMIC_MISS_BEGIN");auto u=f.push_atomic(777*128ULL);f.await(u);
 puts("NATIVE_ATOMIC_MISS_COMPLETE");f.drain();
}
