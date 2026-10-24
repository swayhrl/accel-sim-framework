#include <bits/stdc++.h>
#include "trace_parser.h"
#include "cuda-sim/cuda-sim.h"
#include "cuda-sim/ptx_ir.h"
#include "gpgpu-sim/gpu-sim.h"
#include "gpgpu_context.h"
#include "trace_driven.h"
#include "../ISA_Def/ampere_opcode.h"
#include "gpgpu_context.h"
#include "option_parser.h"
using U=unsigned long long;
class ProbeConfig:public core_config{public:ProbeConfig(gpgpu_context*c):core_config(c){warp_size=32;gpgpu_cache_texl1_linesize=128;gpgpu_cache_constl1_linesize=64;gpgpu_coalesce_arch=80;}void init()override{}};
std::string line(unsigned mask=0x21,U base=4096,U bytes=512,U handle=1,U generation=1,unsigned kind=1,
                 std::vector<U> pairs={4294967299ULL,4294967304ULL},std::vector<U> addresses={4108,4128},unsigned width=4,
                 std::string opcode="TLD.SCR.B.LZ",int count=-1){
 std::ostringstream s;s<<"7900000090 "<<std::hex<<mask<<std::dec<<" 1 R9 "<<opcode<<" 2 R2 R5 "<<width<<" ";
 if(width){s<<"0 ";for(U a:addresses)s<<std::hex<<a<<" "<<std::dec;}
 s<<"0 ADA9 "<<std::hex<<mask<<" "<<mask<<std::dec<<" -1 0 1 0 0 0 "<<kind<<" ";
 if(kind){s<<base<<" "<<bytes<<" "<<handle<<" "<<generation<<" "<<(count<0?__builtin_popcount(mask):count)<<" ";for(U p:pairs)s<<p<<" ";}
 return s.str();
}
int main(){
 unsigned rejected=0;
 auto reject=[&](const std::string&s){bool bad=false;try{inst_trace_t x;x.parse_from_string(s,9,0);}catch(const std::exception&){bad=true;}if(!bad){fprintf(stderr,"MISSED_NEGATIVE %u line=%s\n",rejected,s.c_str());abort();}rejected++;};
 inst_trace_t x;x.parse_from_string(line(),9,0);assert(x.ada_texture_kind==1&&x.memadd_info->width==4&&x.memadd_info->addrs[5]==4128&&x.reg_srcs_num==2);
 reject(line(0x21,4096,512,1,1,0)); // TLD requires origin marker
 reject(line(0x21,4096,512,1,1,1,{4294967299ULL})); // missing lane pair
 reject(line(0x21,4096,512,1,1,1,{8589934595ULL,4294967304ULL})); // wrong handle
 reject(line(0x21,4096,512,4294967297ULL)); // API high half unsupported
 reject(line(0x21,4096,512,1,1,1,{8589934591ULL,4294967304ULL})); // signed -1
 reject(line(0x21,4096,512,1,1,1,{4294967424ULL,4294967304ULL})); // index128
 reject(line(0x21,4096,512,1,1,1,{4294967299ULL,4294967304ULL},{4109,4128})); // wrong resolved
 reject(line(0x21,4096,512,1,1,1,{4294967299ULL,4294967304ULL},{4108,4128},8)); // width
 reject(line(0x21,UINT64_MAX-127,512)); // extent overflow
 reject(line(0x21,4096,511)); // component size
 reject(line(0x21,4096,512,1,2)); // unknown generation
 reject(line(0x21,4096,512,1,1,1,{4294967299ULL,4294967304ULL},{4108,4128},4,"TEX")); // sampler
 reject(line(0x21,4096,512,1,1,1,{4294967299ULL,4294967304ULL},{4108,4128},4,"TLD.SCR.B.LZ",1));
 reject(line()+" extra");
 reject(line(0,4096,512,1,1,1,{}, {},4)); // predicated-off width side effect
 inst_trace_t z;z.parse_from_string(line(0,4096,512,1,1,1,{}, {},0),9,0);
 assert(z.ada_texture_base==4096&&z.ada_texture_handle==1&&!z.memadd_info&&z.mask==0);
 gpgpu_context ctx;ProbeConfig cfg(&ctx);trace_config tc;option_parser_t opp=option_parser_create();tc.reg_options(opp);tc.parse_config();
 trace_warp_inst_t inst(&cfg);inst.parse_from_trace_struct(x,&Ampere_OpcodeMap,&tc,nullptr);
 assert(inst.op==LOAD_OP&&inst.memory_op==memory_load&&inst.space.get_type()==tex_space&&inst.incount==2&&inst.outcount==1&&inst.data_size==4);
 active_mask_t mask=x.mask;inst.issue(mask,0,0,0,0,1);inst.generate_mem_accesses();
 assert(inst.accessq_count()==1);auto&a=inst.accessq_back();assert(a.get_type()==TEXTURE_ACC_R&&a.get_addr()==4096&&a.get_size()==128);
 trace_warp_inst_t zero(&cfg);zero.parse_from_trace_struct(z,&Ampere_OpcodeMap,&tc,nullptr);assert(zero.op==ALU_OP&&zero.outcount==0&&zero.num_regs==0);
 active_mask_t empty;zero.issue(empty,0,0,0,0,1);zero.generate_mem_accesses();assert(zero.accessq_empty());
 printf("ADA9_CPU_PARSER_DECODER_PASS negatives=%u texture_requests=1 cache_line=128 space=TEX zero_mask_requests=0 common_Core_unchanged=1 no_simulator_application_started=1\n",rejected);
}
