#include <cstdlib>
#include <sstream>
struct AdaMeta { std::string opcode,sass,function; unsigned pc; std::vector<int> dst,src; bool qualified; int cb=-1,co=0,cw=0; uint64_t code_base=0,ctrl_static=0; int ctrl_kind=0,ctrl_reg=-1; bool ctrl_ureg=false; std::vector<int> call_summary_src,call_summary_dst; };
static std::vector<AdaMeta> ada_meta;
static std::map<std::pair<std::string,unsigned>,AdaMeta> ada_map;
static bool ada_loaded=false;
static std::vector<int> ada_regs(const std::string &s) {
  std::vector<int> r; if(s=="-") return r; std::istringstream ss(s);std::string x;
  while(std::getline(ss,x,',')) {int v=std::stoi(x); if(v<0||v>334) abort();r.push_back(v);}return r;
}
static int ada_register(Instr *instr,const char *fn,uint64_t code_base) {
  if(!ada_loaded) {
    const char* path=getenv("ADA_SEMANTIC_MAP"); if(!path) {fprintf(stderr,"ADA_SEMANTIC_MAP required\n");abort();}
    std::ifstream in(path);if(!in) abort(); std::string line;
    while(std::getline(in,line)) { std::istringstream ss(line);std::string f,p,d,s,a;
      std::getline(ss,f,'\t');std::getline(ss,p,'\t');std::getline(ss,d,'\t');std::getline(ss,s,'\t');std::getline(ss,a);
      AdaMeta m; m.function=f;m.pc=std::stoul(p,nullptr,16);m.dst=ada_regs(d);m.src=ada_regs(s);m.sass=a;m.qualified=true;
      // CALL summaries may exceed physical operand slots; validate only after separating summaries below.
      if(!ada_map.emplace(std::make_pair(f,m.pc),m).second) abort();
    } ada_loaded=true;
  }
  auto it=ada_map.find(std::make_pair(std::string(fn),instr->getOffset()));
  AdaMeta m;if(it!=ada_map.end())m=it->second;else {m.function=fn;m.pc=instr->getOffset();m.qualified=false;}
  fprintf(stderr,"ADA_STATIC function=%s pc=%x sass=%s qualified=%d\n",fn,instr->getOffset(),instr->getSass(),m.qualified?1:0); m.code_base=code_base;m.opcode=instr->getOpcode();
  if(m.qualified) { // Compare opcode spelling independently of disassembler formatting.
    std::string op=m.sass; if(op[0]=='@') op=op.substr(op.find(' ')+1);op=op.substr(0,op.find(' '));
    if(op!=m.opcode) {fprintf(stderr,"ADA opcode mismatch %s != %s\n",op.c_str(),m.opcode.c_str());abort();}
  }

  auto canon=[](std::string x){x.erase(std::remove_if(x.begin(),x.end(),[](unsigned char c){return std::isspace(c)||c==';';}),x.end());return x;};
  if(m.qualified&&canon(m.sass)!=canon(instr->getSass())) {fprintf(stderr,"ADA full SASS mismatch\n");abort();}
  for(int i=0;i<instr->getNumOperands();++i) {
    auto o=instr->getOperand(i);if(o->type==InstrType::OperandType::CBANK){
      if(m.cb>=0)m.qualified=false;
      m.cb=o->u.cbank.id;m.co=o->u.cbank.has_imm_offset?o->u.cbank.imm_offset:0;m.cw=o->nbytes; if(m.opcode.find("IMAD.WIDE")==0||m.opcode.find("DADD")==0||m.opcode.find("DMUL")==0||m.opcode.find("DFMA")==0||m.opcode.find("DSETP")==0)m.cw=8;
    }
  }
  auto ms=instr->getMemorySpace();int mrefs=0,cbanks=0;
  for(int oi=0;oi<instr->getNumOperands();oi++){auto o=instr->getOperand(oi);mrefs+=o->type==InstrType::OperandType::MREF;cbanks+=o->type==InstrType::OperandType::CBANK;}
  if(ms==InstrType::MemorySpace::TEXTURE || ms==InstrType::MemorySpace::SURFACE || mrefs>1)m.qualified=false;
  if((ms==InstrType::MemorySpace::GLOBAL || ms==InstrType::MemorySpace::LOCAL || ms==InstrType::MemorySpace::SHARED || ms==InstrType::MemorySpace::GENERIC) && mrefs!=1)m.qualified=false;
  if(ms==InstrType::MemorySpace::CONSTANT && cbanks!=1)m.qualified=false;
  if(m.opcode=="CALL.REL.NOINC") {
    m.ctrl_kind=1;
    std::smatch match;std::string actual=instr->getSass();
    if(!std::regex_search(actual,match,std::regex("0x([0-9a-fA-F]+)")))m.qualified=false;
    else m.ctrl_static=std::stoull(match[1],nullptr,16);
    // nvdisasm CALL marks transitive callee/ABI clobber summaries; not physical RF writes by CALL.
    m.call_summary_src=m.src;m.call_summary_dst=m.dst;m.src.clear();m.dst.clear();
  } else if(m.opcode=="RET.REL.NODEC") {
    m.ctrl_kind=2;
    for(int oi=0;oi<instr->getNumOperands();oi++){auto o=instr->getOperand(oi);if(o->type==InstrType::OperandType::REG){m.ctrl_reg=o->u.reg.num;break;}}
    if(m.ctrl_reg<0)m.qualified=false;
  } else if(m.opcode.find("WARPSYNC")==0 || m.opcode.find("BAR.WARP")==0) {
    m.ctrl_kind=3;bool found=false;
    for(int oi=0;oi<instr->getNumOperands();oi++){
      auto o=instr->getOperand(oi);
      if(o->type==InstrType::OperandType::REG||o->type==InstrType::OperandType::UREG){m.ctrl_reg=o->u.reg.num;m.ctrl_ureg=o->type==InstrType::OperandType::UREG;found=true;break;}
      if(o->type==InstrType::OperandType::IMM_UINT64){m.ctrl_static=o->u.imm_uint64.value;found=true;break;}
    }
    if(!found)m.qualified=false;
  } else if(m.opcode.find("CALL")==0 || m.opcode.find("RET")==0 || m.opcode.find("BRX")==0 || m.opcode.find("JMX")==0)m.qualified=false;
  if(m.dst.size()>8||m.src.size()>24)m.qualified=false;
  int id=ada_meta.size();
  std::ofstream out(std::string(getcwd(NULL,0))+"/traces/ada-static.tsv",std::ios::app);
  out<<std::hex<<(m.code_base+m.pc)<<"	"<<m.pc<<"	"<<m.function<<"	"<<m.sass<<"	"<<std::dec<<m.cb<<"	"<<m.co<<"	"<<m.cw<<"	"<<m.qualified<<"\t"<<m.ctrl_kind<<"\t"<<m.ctrl_static<<"\t";
  for(int x:m.call_summary_src)out<<x<<",";out<<"\t";for(int x:m.call_summary_dst)out<<x<<",";out<<"\n";
  ada_meta.push_back(m);return id;
}
