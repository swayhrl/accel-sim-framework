#include <bits/stdc++.h>
#include "trace_parser.h"
#include "cuda-sim/cuda-sim.h"
#include "cuda-sim/ptx_ir.h"
#include "gpgpu-sim/gpu-sim.h"
#include "gpgpu_context.h"
#include "trace_driven.h"
#include "../ISA_Def/ampere_opcode.h"
#include "option_parser.h"
class ProbeConfig:public core_config{public:ProbeConfig(gpgpu_context*c):core_config(c){warp_size=32;gpgpu_cache_texl1_linesize=128;gpgpu_cache_constl1_linesize=64;gpgpu_coalesce_arch=80;}void init()override{}};
int main(int argc,char**argv){
 assert(argc==2);trace_parser parser(argv[1]);auto commands=parser.parse_commandlist_file();
 gpgpu_context ctx;ProbeConfig cfg(&ctx);trace_config tc;option_parser_t opp=option_parser_create();tc.reg_options(opp);tc.parse_config();
 unsigned source=0,aux=0,source_lanes=0,aux_lanes=0,const_lanes=0,tex_lanes=0,global_load=0,global_store=0,exit_lanes=0,tex_requests=0,const8records=0,const4records=0,ctas=0;
 for(auto&command:commands)if(command.m_type==kernel_launch){
  auto*k=parser.parse_kernel_info(command.command_string);assert(k->binary_verion==89&&k->trace_verion==9&&k->tb_dim_x==37&&k->grid_dim_x==1);k->constant_context_ordinal=1;
  std::vector<std::vector<inst_trace_t>> warps(2);std::vector<std::vector<inst_trace_t>*> refs;for(auto&w:warps)refs.push_back(&w);
  parser.get_next_threadblock_traces(refs,9,0,k->pipeReader,37);ctas++;
  for(unsigned wid=0;wid<warps.size();wid++){
   unsigned expectedmask=wid?0x1f:0xffffffff;
   for(auto&raw:warps[wid]){
    unsigned lanes=__builtin_popcount(raw.mask);assert(raw.mask==expectedmask);
    if(raw.ada_aux){aux++;aux_lanes+=lanes;}else{source++;source_lanes+=lanes;}
    trace_warp_inst_t inst(&cfg);inst.parse_from_trace_struct(raw,&Ampere_OpcodeMap,&tc,k);
    if(raw.opcode=="EXIT")exit_lanes+=lanes;
    if(inst.space.get_type()==global_space){
     if(inst.is_load())global_load+=lanes;else if(inst.is_store())global_store+=lanes;
    }
    if(inst.is_load()&&(inst.space.get_type()==tex_space||inst.space.get_type()==const_space)){
     active_mask_t active=raw.mask;inst.issue(active,wid,0,wid,0,k->cuda_stream_id);inst.generate_mem_accesses();assert(!inst.accessq_empty());
     if(inst.space.get_type()==tex_space){
      assert(raw.ada_texture_kind==1&&inst.data_size==4);tex_lanes+=lanes;tex_requests+=inst.accessq_count();
      for(const auto&req:inst.accessq_entries())assert(req.get_type()==TEXTURE_ACC_R&&req.get_size()==128);
     }else{
      const_lanes+=lanes;assert(inst.accessq_count()==1);
      for(const auto&req:inst.accessq_entries()){assert(req.get_type()==CONST_ACC_R&&req.get_size()==64);assert(req.get_byte_mask().count()==inst.data_size);}
      if(inst.data_size==8)const8records++;else{assert(inst.data_size==4);const4records++;}
     }
     std::cout<<"CPU_ACTUAL_MEMORY pc="<<std::hex<<raw.m_pc<<std::dec<<" warp="<<wid<<" aux="<<raw.ada_aux<<" lanes="<<lanes<<" space="<<unsigned(inst.space.get_type())<<" width="<<inst.data_size<<" requests="<<inst.accessq_count()<<" byte_mask_bits="<<inst.accessq_back().get_byte_mask().count()<<"\n";
    }
   }
  }parser.kernel_finalizer(k);
 }
 assert(ctas==1&&source==26&&aux==10&&source_lanes==481&&aux_lanes==185&&const_lanes==222&&tex_lanes==37&&global_load==74&&global_store==37&&exit_lanes==37&&tex_requests==6&&const8records==6&&const4records==6);
 std::cout<<"ACTUAL_ADA9_CORE_PARSER_DECODE_COALESCER_PASS source_records="<<source<<" aux_records="<<aux<<" source_lanes="<<source_lanes<<" aux_lanes="<<aux_lanes<<" total_model_lane_uops="<<source_lanes+aux_lanes<<" const_lanes="<<const_lanes<<" const_width8_records="<<const8records<<" const_width4_records="<<const4records<<" tex_lanes="<<tex_lanes<<" tex_requests="<<tex_requests<<" global_load_lanes="<<global_load<<" global_store_lanes="<<global_store<<" EXIT_lanes="<<exit_lanes<<" tex_enum="<<unsigned(tex_space)<<" const_enum="<<unsigned(const_space)<<" no_application_simulation_started=1\n";
}
