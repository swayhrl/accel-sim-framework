import pathlib,shutil
R=pathlib.Path('/data/c16/ada_trace_extensions_v8_20261024_v1/producer')
p=R/'ada_semantics.h';s=p.read_text()
s=s.replace('bool qualified; int cb=-1,co=0,cw=0;','bool qualified; int cb=-1,co=0,cw=0; uint64_t code_base=0,ctrl_static=0; int ctrl_kind=0,ctrl_reg=-1; bool ctrl_ureg=false; std::vector<int> call_summary_src,call_summary_dst;')
s=s.replace('static int ada_register(Instr *instr,const char *fn) {','static int ada_register(Instr *instr,const char *fn,uint64_t code_base) {')
s=s.replace('m.opcode=instr->getOpcode();','m.code_base=code_base;m.opcode=instr->getOpcode();')
needle='  int id=ada_meta.size();'
insert=r'''  if(m.opcode=="CALL.REL.NOINC") {
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
'''
s=s.replace(needle,insert+needle)
s=s.replace('out<<std::hex<<(id*16)','out<<std::hex<<(m.code_base+m.pc)')
s=s.replace('<<m.qualified<<"\\n";',r'''<<m.qualified<<"\t"<<m.ctrl_kind<<"\t"<<m.ctrl_static<<"\t";
  for(int x:m.call_summary_src)out<<x<<",";out<<"\t";for(int x:m.call_summary_dst)out<<x<<",";out<<"\n";'''.replace('\\"','"'))
p.write_text(s)
p=R/'tracer_tool.cu';s=p.read_text()
s=s.replace('ada_register(instr, nvbit_get_func_name(ctx, f, true))','ada_register(instr, nvbit_get_func_name(ctx, f, true),nvbit_get_func_addr(ctx,f))')
s=s.replace('        if(cb_id>=0) {',r'''        if(ada_meta.at(opcode_id).ctrl_kind) {
          nvbit_add_call_arg_const_val32(instr,3);
          nvbit_add_call_arg_const_val64(instr,ada_meta.at(opcode_id).ctrl_static);
          nvbit_add_call_arg_const_val32(instr,0);
        } else if(cb_id>=0) {''')
s=s.replace('        if(cb_reg>=0)nvbit_add_call_arg_reg_val(instr,cb_reg);',r'''        auto &control=ada_meta.at(opcode_id);
        if(control.ctrl_kind && control.ctrl_reg>=0) {
          if(control.ctrl_ureg)nvbit_add_call_arg_ureg_val(instr,control.ctrl_reg);
          else nvbit_add_call_arg_reg_val(instr,control.ctrl_reg);
        } else if(control.ctrl_kind)nvbit_add_call_arg_const_val32(instr,0);
        else if(cb_reg>=0)nvbit_add_call_arg_reg_val(instr,cb_reg);''')
s=s.replace('''        for (int i = srcNum; i < MAX_SRC; i++) {
          nvbit_add_call_arg_const_val32(instr, static_cast<uint32_t>(-1));
        }''',r'''        for (int i=srcNum;i<MAX_SRC;i++) {
          if(i==0 && control.ctrl_kind==2 && control.ctrl_reg>=0)nvbit_add_call_arg_reg_val(instr,control.ctrl_reg+1);
          else nvbit_add_call_arg_const_val32(instr,control.ctrl_kind?0:static_cast<uint32_t>(-1));
        }''')
s=s.replace('fprintf(ctx_resultsFile[ctx], "%04x ", ma->vpc);','fprintf(ctx_resultsFile[ctx], "%016llx ",(unsigned long long)(ada_meta.at(ma->opcode_id).code_base+ma->vpc));')
needle='''        if(sem.cb>=0)for(unsigned lane=0;lane<32;lane++)if((ma->active_mask&ma->predicate_mask)&(1u<<lane))fprintf(ctx_resultsFile[ctx],"%llu ",(unsigned long long)ma->addrs[lane]);'''
s=s.replace(needle,needle+r'''
        fprintf(ctx_resultsFile[ctx],"%d ",sem.ctrl_kind);
        if(sem.ctrl_kind)for(unsigned lane=0;lane<32;lane++)if((ma->active_mask&ma->predicate_mask)&(1u<<lane))fprintf(ctx_resultsFile[ctx],"%llu ",(unsigned long long)ma->addrs[lane]);''')
p.write_text(s)
p=R/'inject_funcs.cu';s=p.read_text().replace('  if(is_mem==2)addr+=uint32_t(desReg);','  if(is_mem==2)addr+=uint32_t(desReg);\n  if(is_mem==3)addr+=(uint64_t(uint32_t(srcReg1))<<32)|uint32_t(desReg);');p.write_text(s)
