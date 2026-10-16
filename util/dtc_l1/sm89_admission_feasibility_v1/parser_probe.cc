// Host-only probe of unmodified frozen parser. No architecture dispatch/simulator.
#include "trace_parser.h"
#include <iostream>
#include <sstream>
#include <string>
int main(){
 std::string line;
 while(std::getline(std::cin,line)){
  inst_trace_t i;if(!i.parse_from_string(line,5,0))return 2;
  std::cout<<i.m_pc<<'\t'<<i.mask<<'\t'<<i.opcode<<'\t';
  for(unsigned k=0;k<i.reg_dsts_num;k++){if(k)std::cout<<',';std::cout<<int(i.reg_dest[k].type)<<':'<<i.reg_dest[k].num;}
  std::cout<<'\t';for(unsigned k=0;k<i.reg_srcs_num;k++){if(k)std::cout<<',';std::cout<<int(i.reg_src[k].type)<<':'<<i.reg_src[k].num;}
  std::cout<<'\t'<<(i.memadd_info?i.memadd_info->width:0)<<'\t';
  if(i.memadd_info)for(unsigned k=0;k<32;k++)if(i.mask&(1u<<k))std::cout<<k<<':'<<i.memadd_info->addrs[k]<<',';
  std::cout<<'\t'<<i.imm<<'\t';
  #include "frozen_register_conversion.h"
  for(unsigned k=0;k<i.reg_dsts_num;k++){if(k)std::cout<<',';std::cout<<convert_reg_num(i.reg_dest[k]);}
  std::cout<<'\t';for(unsigned k=0;k<i.reg_srcs_num;k++){if(k)std::cout<<',';std::cout<<convert_reg_num(i.reg_src[k]);}
  std::cout<<'\n';
 }
}
