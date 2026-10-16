// CPU driver only. Link the complete, unchanged frozen production trace_parser.cc.
// No Core, simulator, CUDA runtime call, or replacement runtime decoder.
#include "trace_parser.h"
#include <openssl/evp.h>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>

struct Hash {
  EVP_MD_CTX* c=EVP_MD_CTX_new();
  Hash(){EVP_DigestInit_ex(c,EVP_sha256(),nullptr);}
  void put(const void* p,size_t n){EVP_DigestUpdate(c,p,n);}
  void put(const std::string& s){put(s.data(),s.size());}
  std::string end(){unsigned char b[32];unsigned n;EVP_DigestFinal_ex(c,b,&n);std::ostringstream o;for(unsigned i=0;i<n;i++)o<<std::hex<<std::setw(2)<<std::setfill('0')<<unsigned(b[i]);return o.str();}
  ~Hash(){EVP_MD_CTX_free(c);}
};
static void need(bool b,const char* s){if(!b)throw std::runtime_error(s);}
static std::string reg(trace_reg_t r){return std::to_string(r.type)+":"+std::to_string(r.num);}
static std::string instruction(inst_trace_t& t,unsigned cta,unsigned warp){
  std::string s=std::to_string(cta)+"|"+std::to_string(warp)+"|"+std::to_string(t.m_pc)+"|"+std::to_string(t.mask)+"|"+t.opcode+"|";
  for(unsigned i=0;i<t.reg_dsts_num;i++)s+=reg(t.reg_dest[i])+",";
  s+="|";for(unsigned i=0;i<t.reg_srcs_num;i++)s+=reg(t.reg_src[i])+",";
  s+="|"+std::to_string(t.memadd_info?t.memadd_info->width:0);
  // LDG does not consume imm; old excess mode0 words may populate this unused field.
  if(!t.memadd_info)s+="|"+std::to_string(t.imm)+"|"+std::to_string(t.imm2);
  return s+"\n";
}
int main(int argc,char** argv){try{
  need(argc==3,"arguments: unit|full input");
  const uint16_t one=1;need(*reinterpret_cast<const uint8_t*>(&one)==1,"LE hash schema");
  if(std::string(argv[1])=="unit"){
    std::ifstream f(argv[2]);need(bool(f),"unit input");std::string l;unsigned n=0;
    while(std::getline(f,l)){inst_trace_t t;need(t.parse_from_string(l,0,0),"unit parse");
      unsigned lane=n;need(lane<32 && t.mask==(1u<<lane),"unit lane");
      need(t.m_pc==0x1c40 && t.opcode=="LDG.E.SYS" && t.memadd_info && t.memadd_info->width==4,"unit shape");
      for(unsigned i=0;i<32;i++)need(t.memadd_info->addrs[i]==(i==lane?0x1000+4*lane:0),"unit P-list address");++n;}
    need(n==32,"unit coverage");std::cerr<<"{\"status\":\"PASS\",\"single_lane_P_list_cases\":32}\n";return 0;
  }
  need(std::string(argv[1])=="full","mode");trace_parser p(argv[2]);auto cmds=p.parse_commandlist_file();unsigned ki=0;
  for(auto& cmd:cmds){if(cmd.m_type!=kernel_launch)continue;
    auto* k=p.parse_kernel_info(cmd.command_string);need(k->trace_verion==0 && k->enable_lineinfo==0 && k->binary_verion==70,"fixed kernel format");
    unsigned nw=(k->tb_dim_x*k->tb_dim_y*k->tb_dim_z+31)/32;
    unsigned nc=k->grid_dim_x*k->grid_dim_y*k->grid_dim_z;
    std::vector<std::vector<inst_trace_t>> owned(nw);std::vector<std::vector<inst_trace_t>*> warps;
    for(auto& v:owned)warps.push_back(&v);
    Hash memory,instructions;uint64_t records=0,active=0,mem=0;
    for(unsigned cta=0;cta<nc;cta++){
      p.get_next_threadblock_traces(warps,k->trace_verion,k->enable_lineinfo,k->pipeReader);
      for(unsigned w=0;w<nw;w++){need(!owned[w].empty() && owned[w].back().opcode=="EXIT","complete warp terminal");
        for(auto& t:owned[w]){records++;active+=std::bitset<32>(t.mask).count();instructions.put(instruction(t,cta,w));
          need(!t.tma_memadd_info,"no TMA");
          if(t.memadd_info){mem++;uint64_t data[35]={t.m_pc,t.mask,static_cast<uint64_t>(t.memadd_info->width)};
            for(unsigned i=0;i<32;i++)data[i+3]=(t.mask&(1u<<i))?t.memadd_info->addrs[i]:0;
            memory.put(data,sizeof(data));}
        }
      }
    }
    std::string tail;while(k->pipeReader.readLine(tail))need(tail.find_first_not_of(" \r\n\t")==std::string::npos,"unexpected extra TB/tail");
    std::cerr<<"{\"kernel_ordinal\":"<<++ki<<",\"warp_records\":"<<records<<",\"active_thread_instructions\":"<<active<<",\"memory_records\":"<<mem<<",\"complete_ctas\":"<<nc<<",\"complete_warps\":"<<uint64_t(nc)*nw<<",\"instruction_sha256\":\""<<instructions.end()<<"\",\"consumer_memory_sha256\":\""<<memory.end()<<"\"}\n";
    p.kernel_finalizer(k);
  }
  need(ki==2,"ordered two-kernel workload");return 0;
}catch(const std::exception& e){std::cerr<<"FAIL_STOP: "<<e.what()<<"\n";return 1;}}
