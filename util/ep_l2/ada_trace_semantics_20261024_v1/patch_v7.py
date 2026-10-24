import pathlib
R=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1/producer')
p=R/'tracer_tool.cu';s=p.read_text().replace('#define TRACER_VERSION "6"','#define TRACER_VERSION "7"')
a=s.index('      /* check all operands.');b=s.index('      do {',a)
s=s[:a]+'''      int src_oprd[MAX_SRC]; std::fill(src_oprd,src_oprd+MAX_SRC,-1);
      int srcNum=0,dst_oprd=-1,mem_oper_idx=-1,num_mref=0;
      uint64_t imm_value=0;int cb_id=-1,cb_offset=0,cb_reg=-1;
      for(int oi=0;oi<instr->getNumOperands();++oi) {
        auto co=instr->getOperand(oi);
        if(co->type==InstrType::OperandType::MREF){mem_oper_idx++;num_mref++;}
        if(co->type==InstrType::OperandType::IMM_UINT64)imm_value=co->u.imm_uint64.value;
        if(co->type==InstrType::OperandType::CBANK){
          if(cb_id>=0){fprintf(stderr,"ADA_MULTIPLE_CBANK_UNSUPPORTED\\n");abort();}
          cb_id=co->u.cbank.id;cb_offset=co->u.cbank.has_imm_offset?co->u.cbank.imm_offset:0;
          cb_reg=co->u.cbank.has_reg_offset?co->u.cbank.reg_offset:-1;
        }
      }
      if(cb_id>=0&&num_mref){fprintf(stderr,"ADA_MREF_PLUS_CBANK_UNSUPPORTED\\n");abort();}
''' +s[b:]
s=s.replace('        if (mem_oper_idx >= 0) {','''        if(cb_id>=0) {
          nvbit_add_call_arg_const_val32(instr,2);
          nvbit_add_call_arg_const_val64(instr,uint64_t(uint32_t(cb_offset)));
          nvbit_add_call_arg_const_val32(instr,ada_meta.at(opcode_id).cw);
        } else if (mem_oper_idx >= 0) {''')
s=s.replace('        nvbit_add_call_arg_const_val32(instr, dst_oprd);','''        if(cb_reg>=0)nvbit_add_call_arg_reg_val(instr,cb_reg);
        else nvbit_add_call_arg_const_val32(instr,cb_id>=0?0:dst_oprd);''')
a=s.index('        fprintf(ctx_resultsFile[ctx], "ADA6 ');b=s.index('\n\n        fprintf(ctx_resultsFile[ctx], "\\n");',a)
s=s[:a]+'''        fprintf(ctx_resultsFile[ctx], "ADA7 %08x %08x %d %d %d %d %d ",ma->active_mask,ma->predicate_mask,sem.cb,sem.co,sem.qualified?1:0,sem.cw,sem.cb>=0?1:0);
        if(sem.cb>=0)for(unsigned lane=0;lane<32;lane++)if((ma->active_mask&ma->predicate_mask)&(1u<<lane))fprintf(ctx_resultsFile[ctx],"%llu ",(unsigned long long)ma->addrs[lane]);
''' +s[b:]
p.write_text(s)
p=R/'inject_funcs.cu';s=p.read_text().replace('int32_t vpc, bool is_mem,','int32_t vpc, int32_t is_mem,').replace('  inst_trace_t ma;','  inst_trace_t ma;\n  if(is_mem==2)addr+=uint32_t(desReg);').replace('    ma.is_mem = true;','    ma.is_mem = (is_mem==1);');p.write_text(s)
p=R/'ada_semantics.h';s=p.read_text().replace('if(m.cb>=0||o->u.cbank.has_reg_offset)m.qualified=false;','if(m.cb>=0)m.qualified=false;');p.write_text(s)
