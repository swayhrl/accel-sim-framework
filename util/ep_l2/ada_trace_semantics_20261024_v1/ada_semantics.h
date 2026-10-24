#include <cstdlib>
#include <sstream>
struct AdaMeta { std::string opcode,sass,function; unsigned pc; std::vector<int> dst,src; bool qualified; };
static std::vector<AdaMeta> ada_meta;
static std::map<std::pair<std::string,unsigned>,AdaMeta> ada_map;
static bool ada_loaded=false;
static std::vector<int> ada_regs(const std::string &s) {
  std::vector<int> r; if(s=="-") return r; std::istringstream ss(s);std::string x;
  while(std::getline(ss,x,',')) {int v=std::stoi(x); if(v<0||v>334) abort();r.push_back(v);}return r;
}
static int ada_register(Instr *instr,const char *fn) {
  if(!ada_loaded) {
    const char* path=getenv("ADA_SEMANTIC_MAP"); if(!path) {fprintf(stderr,"ADA_SEMANTIC_MAP required\n");abort();}
    std::ifstream in(path);if(!in) abort(); std::string line;
    while(std::getline(in,line)) { std::istringstream ss(line);std::string f,p,d,s,a;
      std::getline(ss,f,'\t');std::getline(ss,p,'\t');std::getline(ss,d,'\t');std::getline(ss,s,'\t');std::getline(ss,a);
      AdaMeta m; m.function=f;m.pc=std::stoul(p,nullptr,16);m.dst=ada_regs(d);m.src=ada_regs(s);m.sass=a;m.qualified=true;
      if(m.dst.size()>8||m.src.size()>24) abort();
      if(!ada_map.emplace(std::make_pair(f,m.pc),m).second) abort();
    } ada_loaded=true;
  }
  auto it=ada_map.find(std::make_pair(std::string(fn),instr->getOffset()));
  AdaMeta m;if(it!=ada_map.end())m=it->second;else {m.function=fn;m.pc=instr->getOffset();m.qualified=false;}
  m.opcode=instr->getOpcode();
  if(m.qualified) { // Compare opcode spelling independently of disassembler formatting.
    std::string op=m.sass; if(op[0]=='@') op=op.substr(op.find(' ')+1);op=op.substr(0,op.find(' '));
    if(op!=m.opcode) {fprintf(stderr,"ADA opcode mismatch %s != %s\n",op.c_str(),m.opcode.c_str());abort();}
  }
  int id=ada_meta.size();ada_meta.push_back(m);return id;
}
