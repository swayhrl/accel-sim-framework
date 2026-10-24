#include <bits/stdc++.h>
#include "trace_parser.h"
int main(int argc,char**argv){
 trace_parser parser(argv[1]);auto commands=parser.parse_commandlist_file();unsigned records=0,aux=0,calls=0,returns=0,ctas=0;uint64_t maxpc=0;
 for(auto&command:commands)if(command.m_type==kernel_launch){auto k=parser.parse_kernel_info(command.command_string);assert(k->binary_verion==89&&k->trace_verion==8);unsigned threads=k->tb_dim_x*k->tb_dim_y*k->tb_dim_z;
  for(unsigned c=0;c<k->grid_dim_x*k->grid_dim_y*k->grid_dim_z;c++){
   std::vector<std::vector<inst_trace_t>> warps((threads+31)/32);std::vector<std::vector<inst_trace_t>*> refs;for(auto&w:warps)refs.push_back(&w);
   parser.get_next_threadblock_traces(refs,8,0,k->pipeReader,threads);ctas++;
   for(auto&w:warps)for(auto&i:w){records++;aux+=i.ada_aux;calls+=i.ada_control_kind==1;returns+=i.ada_control_kind==2;maxpc=std::max(maxpc,i.m_pc);if(i.ada_control_kind==1)assert(i.reg_srcs_num==0&&i.reg_dsts_num==0);}
  }parser.kernel_finalizer(k);
 }
 assert(ctas==2&&records==75&&aux==15&&calls==3&&returns==3&&maxpc>0xffffffffULL);
 std::cout<<"ADA8_CPU_PARSER_PASS ctas="<<ctas<<" internal_uops="<<records<<" aux="<<aux<<" call_records="<<calls<<" return_records="<<returns<<" full64_pc="<<std::hex<<maxpc<<std::endl;
}
