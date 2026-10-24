import pathlib
R=pathlib.Path('/root/data/ada_trace_semantics_20261024_v1/consumer')
p=R/'trace-parser'/'trace_parser.h';s=p.read_text().replace('  int ada_qualified=0;','  int ada_qualified=0;\n  unsigned ada_constwidth=0;\n  bool ada_aux=false;');p.write_text(s)
p=R/'trace-parser'/'trace_parser.cc';s=p.read_text();a=s.index('inst_trace_t::inst_trace_t(const inst_trace_t &b) {');b=s.index('\nbool inst_trace_t::check_opcode_contain',a)
s=s[:a]+'''inst_trace_t::inst_trace_t(const inst_trace_t &b) {
  *this=b;
  memadd_info=b.memadd_info?new inst_memadd_info_t(*b.memadd_info):nullptr;
}
''' +s[b:]
s=s.replace('>>ada_regoffset>>ada_qualified;', '>>ada_regoffset>>ada_qualified>>ada_constwidth;')
s=s.replace('    ada_typed=true;', '''    if((ada_bank<0)!=(ada_constwidth==0) || ada_constwidth>16)throw std::runtime_error("invalid ADA6 constant width");
    ada_typed=true;''')
s=s.replace('        break;  // end of TB stream','''        if(trace_version==6) {
          for(auto warp:threadblock_traces) {
            std::vector<inst_trace_t> expanded;expanded.reserve(warp->size()*2);
            for(const auto &inst:*warp) {
              auto op=inst.opcode.substr(0,inst.opcode.find('.'));
              bool split=inst.ada_bank>=0 && op!="LDC" && op!="ULDC";
              if(split) {
                if(inst.reg_srcs_num>=MAX_SRC)throw std::runtime_error("ADA6 aux dependency overflow");
                inst_trace_t aux(inst);aux.ada_aux=true;aux.opcode="LDC";
                aux.m_pc=inst.m_pc*2;aux.reg_srcs_num=0;aux.reg_dsts_num=1;aux.reg_dest[0]=384;
                if(aux.memadd_info)throw std::runtime_error("ADA6 dual explicit/implicit memory unsupported");
                expanded.push_back(aux);
              }
              inst_trace_t primary(inst);primary.m_pc=inst.m_pc*2+16;
              if(split)primary.reg_src[primary.reg_srcs_num++]=384;
              expanded.push_back(primary);
            }
            warp->swap(expanded);
          }
        }
        break;  // end of TB stream''')
p.write_text(s)
p=R/'trace-driven'/'trace_driven.cc';s=p.read_text().replace('data_size=trace.get_datawidth_from_opcode(opcode_tokens);','data_size=trace.ada_constwidth;');p.write_text(s)
