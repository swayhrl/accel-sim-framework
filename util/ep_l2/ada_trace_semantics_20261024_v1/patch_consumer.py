import pathlib
R=pathlib.Path('/root/data/ada_trace_semantics_20261024_v1/consumer')
p=R/'trace-parser'/'trace_parser.h';s=p.read_text().replace('#define MAX_DST 1','#define MAX_DST 8').replace('#define MAX_SRC 4','#define MAX_SRC 24')
s=s.replace('  uint64_t imm;','  uint64_t imm;\n  bool ada_typed=false;\n  unsigned ada_active=0,ada_predicate=0;\n  int ada_bank=-1,ada_offset=0;\n  unsigned ada_regoffset=0;\n  int ada_qualified=0;')
p.write_text(s)
p=R/'trace-parser'/'trace_parser.cc';s=p.read_text()
s=s.replace('for (int s = 0; s < WARP_SIZE; s++) {\n        if (mask_bits.test(s)) {\n          long long delta', 'for (int s = 0, seen=0; s < WARP_SIZE; s++) {\n        if (mask_bits.test(s) && seen++ > 0) {\n          long long delta')
s=s.replace('  ss >> imm;','''  ss >> std::dec >> imm;
  if(trace_version==6) {
    std::string tag,extra;
    ss>>tag>>std::hex>>ada_active>>ada_predicate>>std::dec>>ada_bank>>ada_offset>>ada_regoffset>>ada_qualified;
    if(!ss || tag!="ADA6" || mask!=(ada_active&ada_predicate) || ada_qualified!=1 || (ss>>extra))
      throw std::runtime_error("invalid or incomplete ADA6 semantic record");
    if(ada_bank < -1 || ada_bank>31 || ada_offset<0 || ada_regoffset)
      throw std::runtime_error("unsupported ADA6 constant bank/address");
    for(unsigned i=0;i<reg_dsts_num;i++)if(reg_dest[i]>334)throw std::runtime_error("ADA6 destination namespace");
    for(unsigned i=0;i<reg_srcs_num;i++)if(reg_src[i]>334)throw std::runtime_error("ADA6 source namespace");
    ada_typed=true;
  } else if(trace_version>6)throw std::runtime_error("unsupported future tracer version");''')
p.write_text(s)
p=R/'trace-driven'/'trace_driven.cc';s=p.read_text()
s=s.replace('arch_reg.dst[m] = trace.reg_dest[m] + 1;', 'arch_reg.dst[m] = (trace.ada_typed && trace.reg_dest[m]>=256)?-1:trace.reg_dest[m]+1;')
s=s.replace('arch_reg.src[m] = trace.reg_src[m] + 1;', 'arch_reg.src[m] = (trace.ada_typed && trace.reg_src[m]>=256)?-1:trace.reg_src[m]+1;')
s=s.replace('  // fill latency and initl','''  if(trace.ada_typed) {
    num_regs=0;
    for(unsigned i=0;i<trace.reg_dsts_num;i++)num_regs+=(trace.reg_dest[i]<256);
    for(unsigned i=0;i<trace.reg_srcs_num;i++)num_regs+=(trace.reg_src[i]<256);
    num_operands=num_regs;
  }
  // fill latency and initl''')
s=s.replace('    case OP_LDC:  // handle Load from Constant\n      data_size = 4;','''    case OP_ULDC:
    case OP_LDC:  // ADA6 symbolic constant-bank addressing; never a GPU physical VA.
      if(trace.ada_typed) {
        if(trace.ada_bank<0) throw std::runtime_error("ADA6 constant load missing address");
        data_size=trace.get_datawidth_from_opcode(opcode_tokens);
        for(unsigned i=0;i<warp_size();i++)set_addr(i, (uint64_t(trace.ada_bank)<<32)+unsigned(trace.ada_offset));
        op=LOAD_OP;
      } else data_size = 4;''')
p.write_text(s)
