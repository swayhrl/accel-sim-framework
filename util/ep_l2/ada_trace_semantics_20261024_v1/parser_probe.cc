#include <bits/stdc++.h>
#include "trace_parser.h"
int main(int argc,char**argv) {
  std::string good="10 15 0 LDG.E 0 4 2 0x100 8 7 0 ADA6 ffffffff 15 -1 0 0 1 0";
  {inst_trace_t x;x.parse_from_string(good,6,0);assert(x.memadd_info->addrs[0]==0x100&&x.memadd_info->addrs[2]==0x108&&x.memadd_info->addrs[4]==0x10f&&x.imm==0);inst_trace_t y(x);assert(y.memadd_info!=x.memadd_info&&y.memadd_info->addrs[4]==0x10f);}
  std::vector<std::string> bad={"10 15 0 LDG.E 0 4 2 0x100 8 7 0 ADA6 ffffffff 16 -1 0 0 1 0","10 15 0 LDG.E 0 4 2 0x100 8 7 0 ADA6 ffffffff 15 -1 0 0 0 0","10 15 0 LDG.E 0 4 2 0x100 8 7 0 ADA6 ffffffff 15 -1 0 0 1 0 extra","10 15 1 R900 MOV 0 0 0 ADA6 ffffffff 15 -1 0 0 1 0","10 15 0 LDC 0 0 0 ADA6 ffffffff 15 0 8 4 1 4"};
  for(const auto &line:bad){bool threw=false;try{inst_trace_t x;x.parse_from_string(line,6,0);}catch(const std::exception&){threw=true;}assert(threw);}
  trace_parser parser(argv[1]);auto commands=parser.parse_commandlist_file();unsigned ctas=0,uops=0,auxs=0,zero=0,constants=0;
  for(auto &command:commands)if(command.m_type==kernel_launch){auto info=parser.parse_kernel_info(command.command_string);assert(info->binary_verion==89&&info->trace_verion==6);
    for(unsigned c=0;c<info->grid_dim_x*info->grid_dim_y*info->grid_dim_z;c++){
      std::vector<std::vector<inst_trace_t>> values(2);std::vector<std::vector<inst_trace_t>*> refs;for(auto &v:values)refs.push_back(&v);
      parser.get_next_threadblock_traces(refs,6,0,info->pipeReader);ctas++;
      for(auto &warp:values)for(unsigned i=0;i<warp.size();i++){auto &x=warp[i];uops++;zero+=x.mask==0;constants+=x.ada_bank>=0;
        if(x.ada_aux){auxs++;assert(x.mask&&x.reg_dsts_num==1&&x.reg_dest[0]==384&&x.reg_srcs_num==0);assert(i+1<warp.size());auto &n=warp[i+1];assert(n.m_pc==x.m_pc&&n.reg_src[n.reg_srcs_num-1]==384);}
      }
    }parser.kernel_finalizer(info);
  }
  assert(ctas==2&&uops==78&&auxs==21&&zero==2);std::cout<<"PARSER_PROBE_PASS ctas="<<ctas<<" uops="<<uops<<" aux="<<auxs<<" zero_mask="<<zero<<" negative_fixtures="<<bad.size()<<std::endl;
}
