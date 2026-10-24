import pathlib
R=pathlib.Path('/root/data/ada_trace_extensions_v8_20261024_v1/consumer')
p=R/'trace-parser/trace_parser.h';s=p.read_text().replace('#include <vector>','#include <vector>\n#include <unordered_map>')
s=s.replace('  unsigned m_pc;','  uint64_t m_pc;')
s=s.replace('  bool ada_aux=false;','  bool ada_aux=false;\n  unsigned ada_capture_version=0,ada_control_kind=0;\n  uint64_t ada_control_targets[32]={};')
s=s.replace('class PipeReader &pipeReader);','class PipeReader &pipeReader, unsigned block_threads=0);')
s=s.replace('  std::string kernellist_filename;','  std::string kernellist_filename;\n  std::unordered_map<uint64_t,uint64_t> ada_function_bases;')
p.write_text(s)
p=R/'trace-parser/trace_parser.cc';s=p.read_text().replace('trace_version==6 || trace_version==7','trace_version==6 || trace_version==7 || trace_version==8')
s=s.replace('tag!=(trace_version==6?"ADA6":"ADA7")','tag!=(trace_version==6?"ADA6":trace_version==7?"ADA7":"ADA8")')
s=s.replace('    if(trace_version==7) {','    if(trace_version==7 || trace_version==8) {')
s=s.replace('    if(ss>>extra)throw std::runtime_error("Ada unexpected trailing field");',r'''    if(trace_version==8) {
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
    ada_capture_version=trace_version;'''.replace('\\"','"'))
s=s.replace('else if(trace_version>7)','else if(trace_version>8)')
s=s.replace('class PipeReader &pipeReader) {','class PipeReader &pipeReader, unsigned block_threads) {')
needle='''        if(trace_version==6 || trace_version==7 || trace_version==8) {
          for(auto warp:threadblock_traces) {'''
replacement=r'''        if(trace_version==8) {
          for(unsigned wi=0;wi<threadblock_traces.size();wi++) {
            auto warp=threadblock_traces[wi];unsigned lanes=std::min(32u,block_threads-wi*32);
            unsigned launched=lanes==32?0xffffffffu:(1u<<lanes)-1u,live=launched;
            std::vector<uint64_t> stack[32];uint64_t pending[32]={};
            for(const auto &inst:*warp){
              if((inst.ada_active&~live)||(inst.mask&~launched))throw std::runtime_error("ADA8 active lanes outside live/physical warp");
              for(unsigned lane=0;lane<32;lane++)if((inst.ada_active&(1u<<lane))&&pending[lane]){
                if(inst.m_pc!=pending[lane])throw std::runtime_error("ADA8 control successor PC mismatch");pending[lane]=0;
              }
              auto found=ada_function_bases.find(inst.m_pc);if(found==ada_function_bases.end())throw std::runtime_error("ADA8 missing loaded-function identity");
              for(unsigned lane=0;lane<32;lane++)if(inst.mask&(1u<<lane)) {
                if(inst.ada_control_kind==1){stack[lane].push_back(inst.m_pc+16);pending[lane]=found->second+inst.ada_control_targets[lane];}
                else if(inst.ada_control_kind==2){
                  uint64_t target=found->second+inst.ada_control_targets[lane];
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
          for(auto warp:threadblock_traces) {'''.replace('\\"','"')
assert needle in s;s=s.replace(needle,replacement)
s=s.replace('  // do not close the file ifs, the kernel_finalizer will close it',r'''  if(kernel_info->trace_verion==8) {
    auto slash=kerneltraces_filepath.find_last_of('/');std::ifstream table(kerneltraces_filepath.substr(0,slash+1)+"ada-static.tsv");
    if(!table)throw std::runtime_error("ADA8 loaded-code static table missing");std::string row;
    while(std::getline(table,row)){
      std::istringstream parts(row);std::string absolute,relative;
      std::getline(parts,absolute,'\t');std::getline(parts,relative,'\t');
      uint64_t pc=std::stoull(absolute,nullptr,16),offset=std::stoull(relative,nullptr,16);
      auto old=ada_function_bases.find(pc);if(old!=ada_function_bases.end()&&old->second!=pc-offset)throw std::runtime_error("ADA8 conflicting loaded-code identity");
      ada_function_bases[pc]=pc-offset;
    }
  }
  // do not close the file ifs, the kernel_finalizer will close it'''.replace('\\"','"'))
p.write_text(s)
p=R/'trace-driven/trace_driven.cc';s=p.read_text()
s=s.replace('m_kernel_trace_info->enable_lineinfo, m_kernel_trace_info->pipeReader);','m_kernel_trace_info->enable_lineinfo, m_kernel_trace_info->pipeReader, m_kernel_trace_info->tb_dim_x*m_kernel_trace_info->tb_dim_y*m_kernel_trace_info->tb_dim_z);')
s=s.replace('    case OP_BAR:',r'''    case OP_WARPSYNC:
      if(trace.ada_capture_version!=8 || trace.ada_control_kind!=3)throw std::runtime_error("WARPSYNC missing actual participant mask");
      op=BARRIER_OP;bar_id=0;bar_count=32;bar_type=SYNC;
      break;
    case OP_BAR:'''.replace('\\"','"'))
s=s.replace('ADA6_DECODE pc=%x','ADA8_DECODE pc=%llx').replace('trace.m_pc,trace.mask','(unsigned long long)trace.m_pc,trace.mask')
p.write_text(s)
