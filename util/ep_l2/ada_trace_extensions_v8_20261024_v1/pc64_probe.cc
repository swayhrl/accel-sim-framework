#include <cassert>
#include <cstdio>
#include <cstdint>
#include <type_traits>
#include "abstract_hardware_model.h"
#include "cuda-sim/cuda-sim.h"
#include "cuda-sim/ptx_sim.h"
#include "gpgpu-sim/shader.h"
#include "gpgpu_context.h"
int main(){
 constexpr address_type a=0x000079c035285200ULL,b=0x00007ac035285200ULL;
 static_assert(sizeof(address_type)==8,"PC width");
 static_assert(sizeof(decltype(std::declval<ptx_thread_info>().get_pc()))==8,"thread PC return");
 static_assert(sizeof(decltype(std::declval<ptx_thread_info>().get_rpc()))==8,"RPC return");
 assert(uint32_t(a)==uint32_t(b)&&a!=b);
 simt_stack stack(0,32,nullptr);simt_mask_t mask;mask.set();stack.launch(a,mask);
 address_type pc=0,rpc=0;stack.get_pdom_stack_top_info(&pc,&rpc);assert(pc==a&&rpc==address_type(-1));
 stack.launch(b,mask);stack.get_pdom_stack_top_info(&pc,&rpc);assert(pc==b);
 ifetch_buffer_t fetch(a,16,0);assert(fetch.m_pc==a);
 stack_entry frame;frame.m_PC=a;frame.m_RPC=b;assert(frame.m_PC==a&&frame.m_RPC==b);
 insn_latency_info latency;latency.pc=a;assert(latency.pc==a);
 using Index=decltype(std::declval<gpgpu_context>().func_sim->g_pc_to_finfo);
 Index index;index[a]=nullptr;index[b]=nullptr;assert(index.size()==2);
 printf("PC64_PROBE_PASS same_low32_distinct=2 simt_pdom=%llx ifetch=%llx call_frame=%llx rpc=%llx index_entries=%zu no_simulator_application_started=1\n",pc,fetch.m_pc,frame.m_PC,frame.m_RPC,index.size());
}
