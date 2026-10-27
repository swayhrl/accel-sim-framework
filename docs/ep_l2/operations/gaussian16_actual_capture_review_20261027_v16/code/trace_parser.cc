#include "../shared/gaussian_scope_v1.h"
// developed by Mahmoud Khairy, Purdue Univ
// abdallm@purdue.edu

#include <bits/stdc++.h>
#include <regex>
#include <math.h>
#include <stdio.h>
#include <time.h>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include <errno.h>
#include <signal.h>
#include <unistd.h>

#include "trace_parser.h"

bool is_number(const std::string &s) {
  std::string::const_iterator it = s.begin();
  while (it != s.end() && std::isdigit(*it)) ++it;
  return !s.empty() && it == s.end();
}

void split(const std::string &str, std::vector<std::string> &cont,
           char delimi = ' ') {
  std::stringstream ss(str);
  std::string token;
  while (std::getline(ss, token, delimi)) {
    cont.push_back(token);
  }
}

inst_trace_t::inst_trace_t() {
  memadd_info = NULL;
  imm = 0;
}

inst_trace_t::~inst_trace_t() {
  if (memadd_info != NULL) delete memadd_info;
}

inst_trace_t::inst_trace_t(const inst_trace_t &b) {
  *this=b;
  memadd_info=b.memadd_info?new inst_memadd_info_t(*b.memadd_info):nullptr;
}

bool inst_trace_t::check_opcode_contain(const std::vector<std::string> &opcode,
                                        std::string param) const {
  for (unsigned i = 0; i < opcode.size(); ++i)
    if (opcode[i] == param) return true;

  return false;
}

std::vector<std::string> inst_trace_t::get_opcode_tokens() const {
  std::istringstream iss(opcode);
  std::vector<std::string> opcode_tokens;
  std::string token;
  while (std::getline(iss, token, '.')) {
    if (!token.empty()) opcode_tokens.push_back(token);
  }
  return opcode_tokens;
}

unsigned inst_trace_t::get_datawidth_from_opcode(
    const std::vector<std::string> &opcode) const {
  for (unsigned i = 0; i < opcode.size(); ++i) {
    if (is_number(opcode[i])) {
      return (std::stoi(opcode[i], NULL) / 8);
    } else if (opcode[i][0] == 'U' && is_number(opcode[i].substr(1))) {
      // handle the U* case
      unsigned bits;
      sscanf(opcode[i].c_str(), "U%u", &bits);
      return bits / 8;
    }
  }

  return 4;  // default is 4 bytes
}

kernel_trace_t::kernel_trace_t(const std::string &filePath)
    : pipeReader(filePath) {
  kernel_name = filePath;
  shmem_base_addr = 0;
  local_base_addr = 0;
  binary_verion = 0;
  trace_verion = 0;
}

void inst_memadd_info_t::base_stride_decompress(
    unsigned long long base_address, int stride,
    const std::bitset<WARP_SIZE> &mask) {
  bool first_bit1_found = false;
  bool last_bit1_found = false;
  unsigned long long addra = base_address;
  for (int s = 0; s < WARP_SIZE; s++) {
    if (mask.test(s) && !first_bit1_found) {
      first_bit1_found = true;
      addrs[s] = base_address;
    } else if (first_bit1_found && !last_bit1_found) {
      if (mask.test(s)) {
        addra += stride;
        addrs[s] = addra;
      } else
        last_bit1_found = true;
    } else
      addrs[s] = 0;
  }
}

void inst_memadd_info_t::base_delta_decompress(
    unsigned long long base_address, const std::vector<long long> &deltas,
    const std::bitset<WARP_SIZE> &mask) {
  bool first_bit1_found = false;
  long long last_address = 0;
  unsigned delta_index = 0;
  for (int s = 0; s < 32; s++) {
    if (mask.test(s) && !first_bit1_found) {
      addrs[s] = base_address;
      first_bit1_found = true;
      last_address = base_address;
    } else if (mask.test(s) && first_bit1_found) {
      assert(delta_index < deltas.size());
      addrs[s] = last_address + deltas[delta_index++];
      last_address = addrs[s];
    } else
      addrs[s] = 0;
  }
}

bool inst_trace_t::parse_from_string(std::string trace, unsigned trace_version,
                                     unsigned enable_lineinfo) {
  static const std::regex gaussian_reg_token("R[0-9]+");
  std::stringstream ss;
  ss.str(trace);

  std::string temp;

  // Start Parsing

  if (trace_version < 3) {
    // for older trace version, read the tb ids and ignore
    unsigned threadblock_x = 0, threadblock_y = 0, threadblock_z = 0,
             warpid_tb = 0;

    ss >> std::dec >> threadblock_x >> threadblock_y >> threadblock_z >>
        warpid_tb;
  }
  if (enable_lineinfo) {
    ss >> std::dec >> line_num;
  }

  ss >> std::hex >> m_pc;
  ss >> std::hex >> mask;

  std::bitset<WARP_SIZE> mask_bits(mask);

  ss >> std::dec >> reg_dsts_num;
  assert(reg_dsts_num <= MAX_DST);
  for (unsigned i = 0; i < reg_dsts_num; ++i) {
    ss >> temp;
    if(!std::regex_match(temp,gaussian_reg_token))throw std::runtime_error("exact destination register token");
    auto value=std::stoul(temp.substr(1));if(value>334)throw std::runtime_error("destination register range");reg_dest[i]=value;
  }

  ss >> opcode;

  ss >> reg_srcs_num;
  assert(reg_srcs_num <= MAX_SRC);
  for (unsigned i = 0; i < reg_srcs_num; ++i) {
    ss >> temp;
    if(!std::regex_match(temp,gaussian_reg_token))throw std::runtime_error("exact source register token");
    auto value=std::stoul(temp.substr(1));if(value>334)throw std::runtime_error("source register range");reg_src[i]=value;
  }

  // parse mem info
  unsigned address_mode = 0;
  unsigned mem_width = 0;

  ss >> mem_width;
  ada_record_mem_width=mem_width;

  if (mem_width > 0)  // then it is a memory inst
  {
    memadd_info = new inst_memadd_info_t();

    // read the memory width from the opcode, as nvbit can report it incorrectly
    std::vector<std::string> opcode_tokens = get_opcode_tokens();
    memadd_info->width = get_datawidth_from_opcode(opcode_tokens);

    ss >> std::dec >> address_mode;
    if(!ss||address_mode>address_format::base_delta)throw std::runtime_error("unknown memory address mode");
    ada_address_mode=address_mode;
    if (address_mode == address_format::list_all) {
      // read addresses one by one from the file
      for (int s = 0; s < WARP_SIZE; s++) {
        if (mask_bits.test(s))
          ss >> std::hex >> memadd_info->addrs[s];
        else
          memadd_info->addrs[s] = 0;
      }
    } else if (address_mode == address_format::base_stride) {
      // read addresses as base address and stride
      unsigned long long base_address = 0;
      int stride = 0;
      ss >> std::hex >> base_address;
      ss >> std::dec >> stride;
      memadd_info->base_stride_decompress(base_address, stride, mask_bits);
    } else if (address_mode == address_format::base_delta) {
      unsigned long long base_address = 0;
      std::vector<long long> deltas;
      // read addresses as base address and deltas
      ss >> std::hex >> base_address;
      for (int s = 0, seen=0; s < WARP_SIZE; s++) {
        if (mask_bits.test(s) && seen++ > 0) {
          long long delta = 0;
          ss >> std::dec >> delta;
          deltas.push_back(delta);
        }
      }
      memadd_info->base_delta_decompress(base_address, deltas, mask_bits);
    }
  }

  ss >> std::dec >> imm;
  if(trace_version==6 || trace_version==7 || trace_version==8) {
    std::string tag,extra;unsigned mode=0;
    ss>>tag>>std::hex>>ada_active>>ada_predicate>>std::dec>>ada_bank>>ada_offset;
    if(trace_version==6)ss>>ada_regoffset>>ada_qualified>>ada_constwidth;
    else ss>>ada_qualified>>ada_constwidth>>mode;
    if(!ss || tag!=(trace_version==6?"ADA6":trace_version==7?"ADA7":"ADA8") || mask!=(ada_active&ada_predicate) || ada_qualified!=1)
      throw std::runtime_error("invalid or incomplete Ada semantic record");
    if(ada_bank < -1 || ada_bank>31 || ada_offset<0 || ada_regoffset)
      throw std::runtime_error("unsupported Ada constant bank/address");
    for(unsigned i=0;i<reg_dsts_num;i++)if(reg_dest[i]>334)throw std::runtime_error("Ada destination namespace");
    for(unsigned i=0;i<reg_srcs_num;i++)if(reg_src[i]>334)throw std::runtime_error("Ada source namespace");
    if((ada_bank<0)!=(ada_constwidth==0) || ada_constwidth>16)throw std::runtime_error("invalid Ada constant width");
    if(trace_version==7 || trace_version==8) {
      if(mode!=unsigned(ada_bank>=0))throw std::runtime_error("invalid ADA7 constant address mode");
      if(ada_bank>=0)for(unsigned lane=0;lane<32;lane++)if(mask&(1u<<lane)){
        ss>>ada_constant_offsets[lane];if(!ss||ada_constant_offsets[lane]>0xffffffffULL)throw std::runtime_error("ADA7 constant offset missing/range");
      }
    } else if(ada_bank>=0)for(unsigned lane=0;lane<32;lane++)if(mask&(1u<<lane))ada_constant_offsets[lane]=ada_offset;
    if(trace_version==8) {
      ss>>ada_control_kind;
      if(!ss||ada_control_kind>3)throw std::runtime_error("ADA8 missing control mode");
      if(ada_control_kind)for(unsigned lane=0;lane<32;lane++)if(mask&(1u<<lane)){
        ss>>ada_control_targets[lane];if(!ss)throw std::runtime_error("ADA8 missing control target/mask");
      }
      if((opcode=="CALL.REL.NOINC")!=(ada_control_kind==1) || (opcode=="RET.REL.NODEC")!=(ada_control_kind==2))
        throw std::runtime_error("ADA8 control opcode/type mismatch");
      if(ada_control_kind==1 && (reg_srcs_num||reg_dsts_num))throw std::runtime_error("CALL summary misrepresented as RF operations");
    }
    if(ss>>extra)throw std::runtime_error("Ada unexpected trailing field");
    ada_capture_version=trace_version;
    ada_typed=true;
  } else if(trace_version>8)throw std::runtime_error("unsupported future tracer version");


  // Finish Parsing

  return true;
}

trace_parser::trace_parser(const char *kernellist_filepath) {
  kernellist_filename = kernellist_filepath;
}

std::vector<trace_command> trace_parser::parse_commandlist_file() {
  std::ifstream fs;
  fs.open(kernellist_filename);

  if (!fs.is_open()) {
    std::cout << "Unable to open file: " << kernellist_filename << std::endl;
    exit(1);
  }

  std::string directory(kernellist_filename);
  const size_t last_slash_idx = directory.rfind('/');
  if (std::string::npos != last_slash_idx) {
    directory = directory.substr(0, last_slash_idx);
  }

  std::string line, filepath;
  std::vector<trace_command> commandlist;
  while (!fs.eof()) {
    getline(fs, line);
    if (line.empty())
      continue;
    else if (line.substr(0, 10) == "MemcpyHtoD") {
      trace_command command;
      command.command_string = line;
      command.m_type = command_type::cpu_gpu_mem_copy;
      commandlist.push_back(command);
    } else if (line.substr(0, 6) == "kernel") {
      trace_command command;
      command.m_type = command_type::kernel_launch;
      filepath = directory + "/" + line;
      command.command_string = filepath;
      commandlist.push_back(command);
    }
    // ignore gpu_to_cpu_memory_cpy
  }

  fs.close();
  return commandlist;
}

void trace_parser::parse_memcpy_info(const std::string &memcpy_command,
                                     size_t &address, size_t &count) {
  std::vector<std::string> params;
  split(memcpy_command, params, ',');
  assert(params.size() == 3);
  std::stringstream ss;
  ss.str(params[1]);
  ss >> std::hex >> address;
  ss.clear();
  ss.str(params[2]);
  ss >> std::dec >> count;
}

kernel_trace_t *trace_parser::parse_kernel_info(
    const std::string &kerneltraces_filepath) {
  std::cout << "Processing kernel " << kerneltraces_filepath << std::endl;
  kernel_trace_t *kernel_info = new kernel_trace_t(kerneltraces_filepath);
  kernel_info->enable_lineinfo = 0;  // default disabled

  std::string line,gaussian_profile,gaussian_binary,gaussian_map,gaussian_cubin;unsigned gaussian_markers=0;
  while (kernel_info->pipeReader.readLine(line)) {
    if (line.length() == 0) {
      continue;
    } else if (line[0] == '#') {
      // the trace format, ignore this and assume fixed format for now
      break;  // the begin of the instruction stream
    } else if (line[0] == '-') {
      std::stringstream ss;
      std::string string1, string2;

      ss.str(line);
      ss.ignore();
      ss >> string1 >> string2;

      if(line.rfind("-ada gaussian contract = ",0)==0){gaussian_profile=line.substr(25);gaussian_markers++;}
      else if(line.rfind("-ada binary sha256 = ",0)==0){gaussian_binary=line.substr(21);gaussian_markers++;}
      else if(line.rfind("-ada map sha256 = ",0)==0){gaussian_map=line.substr(18);gaussian_markers++;}
      else if(line.rfind("-ada cubin sha256 = ",0)==0){gaussian_cubin=line.substr(20);gaussian_markers++;}
      else if (string1 == "kernel" && string2 == "name") {
        const size_t equal_idx = line.find('=');
        kernel_info->kernel_name = line.substr(equal_idx + 2);
      } else if (string1 == "kernel" && string2 == "id") {
        sscanf(line.c_str(), "-kernel id = %d", &kernel_info->kernel_id);
      } else if (string1 == "grid" && string2 == "dim") {
        sscanf(line.c_str(), "-grid dim = (%d,%d,%d)", &kernel_info->grid_dim_x,
               &kernel_info->grid_dim_y, &kernel_info->grid_dim_z);
      } else if (string1 == "block" && string2 == "dim") {
        sscanf(line.c_str(), "-block dim = (%d,%d,%d)", &kernel_info->tb_dim_x,
               &kernel_info->tb_dim_y, &kernel_info->tb_dim_z);
      } else if (string1 == "shmem" && string2 == "=") {
        sscanf(line.c_str(), "-shmem = %d", &kernel_info->shmem);
      } else if (string1 == "nregs") {
        sscanf(line.c_str(), "-nregs = %d", &kernel_info->nregs);
      } else if (string1 == "cuda" && string2 == "stream") {
        sscanf(line.c_str(), "-cuda stream id = %llu",
               &kernel_info->cuda_stream_id);
      } else if (string1 == "binary" && string2 == "version") {
        sscanf(line.c_str(), "-binary version = %d",
               &kernel_info->binary_verion);
      } else if (string1 == "enable" && string2 == "lineinfo") {
        sscanf(line.c_str(), "-enable lineinfo = %d",
               &kernel_info->enable_lineinfo);
      } else if (string1 == "nvbit" && string2 == "version") {
        const size_t equal_idx = line.find('=');
        kernel_info->nvbit_verion = line.substr(equal_idx + 1);

      } else if (string1 == "accelsim" && string2 == "tracer") {
        sscanf(line.c_str(), "-accelsim tracer version = %d",
               &kernel_info->trace_verion);

      } else if (string1 == "shmem" && string2 == "base_addr") {
        const size_t equal_idx = line.find('=');
        ss.str(line.substr(equal_idx + 1));
        ss >> std::hex >> kernel_info->shmem_base_addr;

      } else if (string1 == "local" && string2 == "mem") {
        const size_t equal_idx = line.find('=');
        ss.str(line.substr(equal_idx + 1));
        ss >> std::hex >> kernel_info->local_base_addr;
      }
      std::cout << line << std::endl;
      continue;
    }
  }

  gaussian16::require(gaussian16::owner_ok(kernel_info->kernel_name),"exact kernel owner");
  gaussian16::require(kernel_info->trace_verion==8&&kernel_info->binary_verion==89,"ADA8/SM89 required");
  gaussian16::require(gaussian_markers==4&&gaussian_profile==gaussian16::profile&&gaussian_binary==gaussian16::binary&&gaussian_map==gaussian16::mapsha&&gaussian_cubin==gaussian16::cubin,"explicit exact contract headers");
  auto slash=kerneltraces_filepath.find_last_of('/');std::string dir=kerneltraces_filepath.substr(0,slash+1);
  gaussian16::require(gaussian16::file_sha(dir+"semantic-map.tsv")==gaussian16::mapsha,"consumer semantic map SHA");
  struct M {std::string sass;std::vector<int>src,dst;};
  std::map<std::pair<std::string,uint64_t>,M> expected;
  auto regs=[](const std::string&s){std::vector<int>r;if(s=="-")return r;std::istringstream in(s);std::string x;while(std::getline(in,x,','))r.push_back(std::stoi(x));return r;};
  std::ifstream mapfile(dir+"semantic-map.tsv");std::string row;
  while(std::getline(mapfile,row)){
   std::istringstream in(row);std::string fn,pc,dst,src,sass;
   std::getline(in,fn,'\t');std::getline(in,pc,'\t');std::getline(in,dst,'\t');std::getline(in,src,'\t');std::getline(in,sass);
   gaussian16::require(gaussian16::owner_ok(fn),"map owner");
   gaussian16::require(expected.emplace(std::make_pair(fn,std::stoull(pc,nullptr,16)),M{sass,regs(src),regs(dst)}).second,"map duplicate key");
  }
  std::ifstream loaded(dir+"ada-loaded.tsv");gaussian16::require(bool(loaded),"loaded metadata missing");std::map<std::string,uint64_t>bases;std::set<std::string>contexts;
  while(std::getline(loaded,row)){
   std::istringstream in(row);std::string ctx,base,fn,sm,size,path;
   std::getline(in,ctx,'\t');std::getline(in,base,'\t');std::getline(in,fn,'\t');std::getline(in,sm,'\t');std::getline(in,size,'\t');std::getline(in,path);
   auto name=path.substr(path.find_last_of('/')+1);gaussian16::require(!name.empty()&&name!="."&&name!="..","loaded basename");
   gaussian16::loaded_identity(dir+name,fn,std::stoi(sm));std::ifstream sz(dir+name,std::ios::binary|std::ios::ate);gaussian16::require(sz&&uint64_t(sz.tellg())==std::stoull(size),"loaded declared size");contexts.insert(ctx);
   gaussian16::require(bases.emplace(fn,std::stoull(base,nullptr,16)).second,"duplicate function loaded lifetime");
  }
  gaussian16::require(contexts.size()==1&&bases.size()==2&&bases.count(gaussian16::fan1)&&bases.count(gaussian16::fan2),"exact single context/two owner closure");
  std::ifstream table(dir+"ada-static.tsv");gaussian16::require(bool(table),"static table missing");
  std::set<std::pair<std::string,uint64_t>>seen,padding_seen;ada_function_bases.clear();gaussian_owners.clear();gaussian_opcodes.clear();gaussian_record_sites.clear();
  while(std::getline(table,row)){
   std::istringstream in(row);std::string absolute,relative,fn,sass,cb,co,cw,qualified;
   std::getline(in,absolute,'\t');std::getline(in,relative,'\t');std::getline(in,fn,'\t');std::getline(in,sass,'\t');
   std::getline(in,cb,'\t');std::getline(in,co,'\t');std::getline(in,cw,'\t');std::getline(in,qualified,'\t');
   uint64_t pc=std::stoull(absolute,nullptr,16),offset=std::stoull(relative,nullptr,16);
   auto key=std::make_pair(fn,offset);auto it=expected.find(key);
   if(qualified=="0"&&sass.empty()){
    std::string rest;std::getline(in,rest);
    bool exact_padding=(fn==gaussian16::fan1&&offset>=0x980&&offset<=0x9f0)||(fn==gaussian16::fan2&&offset>=0x300&&offset<=0x370);
    gaussian16::require(exact_padding&&offset%16==0&&it==expected.end()&&cb=="-1"&&co=="0"&&cw=="0"&&rest=="0\t0\t\t","exact nonexecuted blank padding metadata");
    gaussian16::require(bases.count(fn)&&gaussian16::add(bases[fn],offset)==pc&&padding_seen.insert(key).second,"padding owner full64 PC/unique");
    // These nonexecuted metadata rows grant no record site. A dynamic record at
    // any padding PC remains unknown and is rejected by the normal record join.
    continue;
   }
   gaussian16::require(qualified=="1"&&it!=expected.end()&&gaussian16::compact(sass)==gaussian16::compact(it->second.sass)&&seen.insert(key).second,"static owner/PC/SASS closure");
   gaussian16::require(bases.count(fn)&&gaussian16::add(bases[fn],offset)==pc,"full64 loaded/static base");
   gaussian16::static_site(fn,offset,sass,it->second.src,it->second.dst);
   gaussian16::require(ada_function_bases.emplace(pc,bases[fn]).second,"overlapping absolute PC owners");
   gaussian_owners[pc]=fn;std::istringstream words(sass);std::string op;words>>op;if(op[0]=='@')words>>op;gaussian_opcodes[pc]=op;
    StaticRecordSite site;site.src=it->second.src;site.dst=it->second.dst;
    // The frozen CALL map carries ABI/callee summaries, not physical RF writes.
    if(op=="CALL.REL.NOINC"){site.src.clear();site.dst.clear();}
    site.declared_bank=std::stoi(cb);site.declared_offset=std::stoi(co);site.declared_const_width=std::stoul(cw);
    bool direct_constant=sass.find("c[")!=std::string::npos;
    if(direct_constant){
      std::smatch match;std::regex literal("c\\[0x([0-9a-fA-F]+)\\]\\[0x([0-9a-fA-F]+)\\]");
      gaussian16::require(std::regex_search(sass,match,literal),"only actual direct constant site");
      std::string after=match.suffix();gaussian16::require(!std::regex_search(after,literal),"one constant operand");
      auto bank=std::stoull(match[1],nullptr,16),offset=std::stoull(match[2],nullptr,16);
      gaussian16::require(bank<=31&&offset<=INT_MAX,"constant literal bounds");site.bank=bank;site.offset=offset;
      static const std::set<std::string> scalar={"MOV","IMAD.MOV.U32","ULDC","IMAD","IADD3","IADD3.X","LEA","LEA.HI.X"};
      if(op=="ULDC.64"||op=="IMAD.WIDE")site.const_width=8;
      else {gaussian16::require(scalar.count(op),"unknown actual constant width");site.const_width=4;}
    } else if(sass.find('[')!=std::string::npos){
      gaussian16::require(op=="LDG.E"||op=="STG.E","outside actual scalar global memory subset");site.mem_width=4;
    }
    gaussian16::require(gaussian_record_sites.emplace(pc,site).second,"duplicate record static site");

  }
  gaussian16::require(seen.size()==expected.size(),"complete all-owner static map set");
  // do not close the file ifs, the kernel_finalizer will close it
  return kernel_info;
}

void trace_parser::kernel_finalizer(kernel_trace_t *trace_info) {
  assert(trace_info);

  // The pipe read/write end file descriptors held by the child process would
  // have been automatically closed when it terminated. But the parent
  // process may read an arbitrary amount of trace files, so it has to close
  // all file descriptors.
  delete trace_info;
}

void trace_parser::get_next_threadblock_traces(
    std::vector<std::vector<inst_trace_t> *> threadblock_traces,
    unsigned trace_version, unsigned enable_lineinfo,
    class PipeReader &pipeReader, unsigned block_threads) {
  for (unsigned i = 0; i < threadblock_traces.size(); ++i) {
    threadblock_traces[i]->clear();
  }

  last_block=BlockResult{};
  std::vector<unsigned>declared(threadblock_traces.size()),parsed(threadblock_traces.size());std::vector<bool>seen_warp(threadblock_traces.size()),seen_count(threadblock_traces.size());bool coordinates=false,in_warp=false;unsigned next_warp=0;
  unsigned block_id_x = 0, block_id_y = 0, block_id_z = 0;
  bool start_of_tb_stream_found = false;

  unsigned warp_id = 0;
  unsigned insts_num = 0;
  unsigned inst_count = 0;
  std::string line;
  while (pipeReader.readLine(line)) {
    std::stringstream ss;
    std::string string1, string2;

    if (line.length() == 0) {
      continue;
    } else {
      ss.str(line);
      ss >> string1 >> string2;
      if (string1 == "#BEGIN_TB") {
        if(line!="#BEGIN_TB")throw std::runtime_error("exact BEGIN_TB grammar");
        if (!start_of_tb_stream_found) {
          start_of_tb_stream_found = true;
        } else
          assert(0 &&
                 "Parsing error: thread block start before the previous one "
                 "finishes");
      } else if (string1 == "#END_TB") {
        if(line!="#END_TB")throw std::runtime_error("exact END_TB grammar");
        if(!start_of_tb_stream_found||!coordinates)throw std::runtime_error("missing TB start/coordinates");
        for(unsigned w=0;w<seen_warp.size();w++)if(!seen_warp[w]||!seen_count[w]||parsed[w]!=declared[w])throw std::runtime_error("missing/short/duplicate warp body");
        last_block.present=true;last_block.x=block_id_x;last_block.y=block_id_y;last_block.z=block_id_z;
        if(trace_version==8) {
          for(unsigned wi=0;wi<threadblock_traces.size();wi++) {
            auto warp=threadblock_traces[wi];unsigned lanes=std::min(32u,block_threads-wi*32);
            unsigned launched=lanes==32?0xffffffffu:(1u<<lanes)-1u,live=launched;
            std::vector<uint64_t> stack[32];uint64_t pending[32]={};
            for(const auto &inst:*warp){
              last_block.raw_records++;
              if(inst.opcode=="EXIT")last_block.exit_lanes+=__builtin_popcount(inst.mask);
              if(inst.ada_control_kind==1){last_block.call_issues++;last_block.call_lanes+=__builtin_popcount(inst.mask);}
              if(inst.ada_control_kind==2){last_block.ret_issues++;last_block.ret_lanes+=__builtin_popcount(inst.mask);}
              if((inst.ada_active&~live)||(inst.mask&~launched))throw std::runtime_error("ADA8 active lanes outside live/physical warp");
              for(unsigned lane=0;lane<32;lane++)if((inst.ada_active&(1u<<lane))&&pending[lane]){
                if(inst.m_pc!=pending[lane])throw std::runtime_error("ADA8 control successor PC mismatch");pending[lane]=0;
              }
              auto found=ada_function_bases.find(inst.m_pc);if(found==ada_function_bases.end())throw std::runtime_error("ADA8 missing loaded-function identity");
              gaussian16::require(gaussian_opcodes.at(inst.m_pc)==inst.opcode,"record opcode/static map mismatch");
              const auto&site=gaussian_record_sites.at(inst.m_pc);
              gaussian16::require(std::vector<int>(inst.reg_src,inst.reg_src+inst.reg_srcs_num)==site.src&&std::vector<int>(inst.reg_dest,inst.reg_dest+inst.reg_dsts_num)==site.dst,"executed static physical register operands");
              gaussian16::require(inst.ada_record_mem_width==site.mem_width&&bool(inst.memadd_info)==bool(site.mem_width),"executed static memory presence/width");
              if(site.mem_width)gaussian16::require(unsigned(inst.memadd_info->width)==site.mem_width,"decoded memory width");
              gaussian16::require(site.declared_bank==site.bank&&site.declared_offset==site.offset&&site.declared_const_width==site.const_width,"executed static constant declaration/SASS");
              gaussian16::require(inst.ada_bank==site.bank&&inst.ada_offset==site.offset&&inst.ada_constwidth==site.const_width,"executed dynamic/static constant bank/offset/width");
              if(site.bank>=0)for(unsigned lane=0;lane<32;lane++)if(inst.mask&(1u<<lane))
                gaussian16::require(inst.ada_constant_offsets[lane]==unsigned(site.offset),"direct constant per-lane offset");

              if(inst.ada_control_kind||inst.opcode.rfind("CALL",0)==0||inst.opcode.rfind("RET",0)==0){
                gaussian16::require(inst.mask==inst.ada_active,"predicated control outside subset");
                gaussian16::record(gaussian_owners.at(inst.m_pc),inst.m_pc-found->second,inst.ada_control_kind,inst.opcode,inst.reg_srcs_num,inst.reg_src,inst.reg_dsts_num,inst.ada_active,inst.mask,inst.ada_control_targets);
              }
              for(unsigned lane=0;lane<32;lane++)if(inst.mask&(1u<<lane)) {
                if(inst.ada_control_kind==1){stack[lane].push_back(gaussian16::add(inst.m_pc,16));pending[lane]=gaussian16::add(found->second,inst.ada_control_targets[lane]);}
                else if(inst.ada_control_kind==2){
                  uint64_t target=gaussian16::add(found->second,inst.ada_control_targets[lane]);
                  if(stack[lane].empty()||stack[lane].back()!=target)throw std::runtime_error("ADA8 return target/frame mismatch");
                  stack[lane].pop_back();pending[lane]=target;
                } else if(inst.ada_control_kind==3){
                  uint64_t participants=inst.ada_control_targets[lane];
                  if(participants>0xffffffffULL||(unsigned(participants)&live)!=inst.mask)throw std::runtime_error("Unsupported divergent WARPSYNC participant rendezvous");
                }
                if(inst.opcode=="EXIT") {if(!stack[lane].empty()||pending[lane])throw std::runtime_error("ADA8 EXIT in call frame");live&=~(1u<<lane);}
              }
            }
            if(live)throw std::runtime_error("ADA8 warp does not terminate all physical lanes");
          }
        }
        if(trace_version==6 || trace_version==7 || trace_version==8) {
          for(auto warp:threadblock_traces) {
            std::vector<inst_trace_t> expanded;expanded.reserve(warp->size()*2);
            for(const auto &inst:*warp) {
              auto op=inst.opcode.substr(0,inst.opcode.find('.'));
              bool split=inst.mask!=0 && inst.ada_bank>=0 && op!="LDC" && op!="ULDC";
              if(split) {
                if(inst.reg_srcs_num>=MAX_SRC)throw std::runtime_error("ADA6 aux dependency overflow");
                inst_trace_t aux(inst);aux.ada_aux=true;aux.opcode="LDC";
                aux.m_pc=inst.m_pc;aux.reg_srcs_num=0;aux.reg_dsts_num=1;aux.reg_dest[0]=384;
                if(aux.memadd_info)throw std::runtime_error("ADA6 dual explicit/implicit memory unsupported");
                expanded.push_back(aux);
              }
              inst_trace_t primary(inst);primary.m_pc=inst.m_pc;
              if(split)primary.reg_src[primary.reg_srcs_num++]=384;
              expanded.push_back(primary);
            }
            warp->swap(expanded);
          }
        }
        break;  // end of TB stream
      } else if (string1 == "thread" && string2 == "block") {
        if(!start_of_tb_stream_found||coordinates||in_warp)throw std::runtime_error("duplicate/outside TB coordinates");
        std::smatch match;
        if(!std::regex_match(line,match,std::regex("thread block = ([0-9]+),([0-9]+),([0-9]+)")))throw std::runtime_error("exact CTA coordinates grammar");
        uint64_t x=std::stoull(match[1]),y=std::stoull(match[2]),z=std::stoull(match[3]);
        if(x>UINT_MAX||y>UINT_MAX||z>UINT_MAX)throw std::runtime_error("CTA coordinate range");
        block_id_x=x;block_id_y=y;block_id_z=z;coordinates=true;
        std::cout << line << std::endl;
      } else if (string1 == "warp") {
        // the start of new warp stream
        if(!start_of_tb_stream_found||!coordinates)throw std::runtime_error("warp before CTA coordinates");
        if(in_warp&&(!seen_count[warp_id]||parsed[warp_id]!=declared[warp_id]))throw std::runtime_error("warp switch before complete body");
        std::smatch match;if(!std::regex_match(line,match,std::regex("warp = ([0-9]+)")))throw std::runtime_error("exact warp grammar");
        uint64_t id=std::stoull(match[1]);if(id>=seen_warp.size()||id!=next_warp||seen_warp[id])throw std::runtime_error("bad/duplicate/out-of-order warp id");
        warp_id=id;next_warp++;in_warp=true;seen_warp[warp_id]=true;
      } else if (string1 == "insts") {
        if(!start_of_tb_stream_found||!coordinates||!in_warp||seen_count[warp_id])throw std::runtime_error("single instruction count after warp required");
        std::smatch match;if(!std::regex_match(line,match,std::regex("insts = ([0-9]+)")))throw std::runtime_error("exact insts grammar");
        uint64_t count=std::stoull(match[1]);if(!count||count>10000000)throw std::runtime_error("bad warp instruction count");
        insts_num=count;seen_count[warp_id]=true;declared[warp_id]=insts_num;
        threadblock_traces[warp_id]->resize(
            insts_num);  // allocate all the space at once
        inst_count = 0;
      } else {
        if(!start_of_tb_stream_found||!coordinates||!in_warp)throw std::runtime_error("record before complete block/warp envelope");
        if(warp_id>=seen_warp.size()||!seen_warp[warp_id]||!seen_count[warp_id]||inst_count>=declared[warp_id])throw std::runtime_error("record outside declared warp");parsed[warp_id]++;
        threadblock_traces[warp_id]
            ->at(inst_count)
            .parse_from_string(line, trace_version, enable_lineinfo);
        inst_count++;
      }
    }
  }
  if(start_of_tb_stream_found&&!last_block.present)throw std::runtime_error("truncated TB missing END");
}

PipeReader::PipeReader(const std::string &filePath) { OpenFile(filePath); }

void PipeReader::OpenFile(const std::string &filePath) {
  if (hasEnding(filePath, ".xz")) {
    // Use xz command to decompress .xz files
    command = "xz -dc " + filePath;
  } else if (hasEnding(filePath, ".traceg")) {
    // Use cat command for regular trace files
    command = "cat " + filePath;
  } else {
    throw std::runtime_error("Unsupported file type!");
  }

  // Open the pipe
  pipe = popen(command.c_str(), "r");
  if (!pipe) {
    throw std::runtime_error("Failed to open pipe!");
  }
}

bool PipeReader::readLine(std::string &line) {
  char *buffer = nullptr;
  size_t len = 0;
  ssize_t nread;

  // Use getline() to read from the pipe
  if ((nread = getline(&buffer, &len, pipe)) != -1) {
    line.assign(buffer, nread);  // Assign the read line to the std::string
    assert(line.back() == '\n');
    line.pop_back();  // Remove the newline character
    free(buffer);     // Free the buffer allocated by getline
    return true;
  }

  free(buffer);  // Free the buffer if getline failed or reached EOF
  return false;  // End of pipe or error
}

// Helper function to check if a string ends with a specific suffix (file
// extension)
bool PipeReader::hasEnding(const std::string &fullString,
                           const std::string &ending) {
  if (fullString.length() >= ending.length()) {
    return (0 == fullString.compare(fullString.length() - ending.length(),
                                    ending.length(), ending));
  }
  return false;
}

PipeReader::PipeReader(PipeReader &&other) noexcept
    : pipe(other.pipe), command(other.command) {
  other.pipe = NULL;
  other.command = {};
}

PipeReader &PipeReader::operator=(PipeReader &&other) noexcept {
  if (this != &other) {
    pipe = other.pipe;
    command = other.command;

    other.pipe = NULL;
    other.command = {};
  }
  return *this;
}
void PipeReader::close_checked(){
 if(pipe){FILE*p=pipe;pipe=nullptr;int rc=pclose(p);if(rc!=0)throw std::runtime_error("trace decompressor/CRC nonzero");}
}
