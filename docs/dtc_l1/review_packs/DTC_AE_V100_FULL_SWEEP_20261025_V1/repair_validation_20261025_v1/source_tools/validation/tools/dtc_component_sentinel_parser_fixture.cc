#include "trace_parser.h"
#include <fstream>
#include <cassert>
#include <iostream>
#include <bitset>
#include <string>
static void parse(const char *path, unsigned version, bool mixed) {
  std::ifstream input(path); assert(input); std::string line;
  unsigned records=0, active=0, cacheable=0, bypass=0, stores=0, atoms=0, zero_dest=0;
  while(std::getline(input,line)) {
    if(!mixed && records && line.rfind("warp = ",0)==0) break;
    if(line.empty() || line[0]=='-' || line[0]=='#' || !std::isxdigit(line[0])) continue;
    if(line.rfind("thread",0)==0 || line.rfind("insts",0)==0) continue;
    inst_trace_t t;
    assert(t.parse_from_string(line,version,0,dim3(0,0,0),dim3(0,0,0),dim3(0,0,0),0));
    ++records; active+=std::bitset<32>(t.mask).count();
    if(t.opcode.rfind("LDG",0)==0) {
      if(t.opcode.find("STRONG.GPU")!=std::string::npos) ++bypass; else ++cacheable;
      assert(t.reg_dsts_num==1 && t.memadd_info && t.memadd_info->width==4);
      for(unsigned i=1;i<32;++i) assert(t.memadd_info->addrs[i]==t.memadd_info->addrs[0]+4*i);
    }
    if(t.opcode.rfind("STG",0)==0) {++stores; assert(t.reg_dsts_num==0);}
    if(t.opcode.rfind("ATOMG",0)==0 || t.opcode.rfind("RED",0)==0) {
      ++atoms; if(!t.reg_dsts_num) ++zero_dest;
      assert(t.memadd_info && t.memadd_info->width==4);
      for(unsigned i=1;i<32;++i) assert(t.memadd_info->addrs[i]==t.memadd_info->addrs[0]);
    }
  }
  if(mixed) assert(records==9 && active==288 && cacheable==2 && bypass==1 && stores==1 && atoms==2 && zero_dest==1);
  else assert(records==16 && active==448 && cacheable==2 && bypass==0 && stores==1 && atoms==0);
}
int main(int argc,char **argv) {
  assert(argc==3); parse(argv[1],3,true); parse(argv[2],0,false);
  std::cout<<"PASS actual frozen FW parser: authored mixed full9 records/288 thread-instructions; returning ATOMG and zero-dest RED decoded address payloads; original4M first complete warp16 records/448 thread-instructions; no simulator or kernel executed\n";
}
