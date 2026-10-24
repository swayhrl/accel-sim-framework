import pathlib
R=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1/producer')
p=R/'tracer_tool.cu';s=p.read_text()
s=s.replace('#define TRACER_VERSION "5"','#define TRACER_VERSION "6"\n#include "ada_semantics.h"')
s=s.replace('      int opcode_id = opcode_to_id_map[instr->getOpcode()];','      int opcode_id = ada_register(instr, nvbit_get_func_name(ctx, f));')
s=s.replace('      do {\n        /* insert call', '''      int cb_id=-1, cb_offset=0, cb_reg=-1;
      for(int oi=0;oi<instr->getNumOperands();++oi) {
        auto co=instr->getOperand(oi);
        if(co->type==InstrType::OperandType::CBANK) {
          if(cb_id>=0) { fprintf(stderr,"ADA multiple CBANK unsupported\\n"); abort(); }
          cb_id=co->u.cbank.id; cb_offset=co->u.cbank.has_imm_offset?co->u.cbank.imm_offset:0;
          cb_reg=co->u.cbank.has_reg_offset?co->u.cbank.reg_offset:-1;
        }
      }
      do {
        /* insert call''')
needle='        /* reg info */'
s=s.replace(needle,'''        nvbit_add_call_arg_const_val32(instr, cb_id);
        nvbit_add_call_arg_const_val32(instr, cb_offset);
        if(cb_reg>=0) nvbit_add_call_arg_reg_val(instr,cb_reg);
        else nvbit_add_call_arg_const_val32(instr,0);
        /* reg info */''')
start=s.index('        if (ma->GPRDst >= 0) {')
end=s.index('        // print addresses',start)
s=s[:start]+'''        const auto &sem=ada_meta.at(ma->opcode_id);
        fprintf(ctx_resultsFile[ctx], "%zu ",sem.dst.size());
        for(int r:sem.dst) fprintf(ctx_resultsFile[ctx],"R%d ",r);
        fprintf(ctx_resultsFile[ctx],"%s %zu ",sem.opcode.c_str(),sem.src.size());
        for(int r:sem.src) fprintf(ctx_resultsFile[ctx],"R%d ",r);
''' +s[end:]
s=s.replace('id_to_opcode_map[ma->opcode_id]', 'ada_meta.at(ma->opcode_id).opcode')
s=s.replace('fprintf(ctx_resultsFile[ctx], "%d ", ma->imm);','''fprintf(ctx_resultsFile[ctx], "%llu ",(unsigned long long)ma->imm);
        fprintf(ctx_resultsFile[ctx], "ADA6 %08x %08x %d %d %u %d ", ma->active_mask,ma->predicate_mask,ma->constant_bank,ma->constant_offset,ma->constant_regoffset,sem.qualified?1:0);''')
p.write_text(s)
p=R/'common.h';s=p.read_text().replace('  uint64_t imm;','  uint64_t imm;\n  int constant_bank;\n  int constant_offset;\n  uint32_t constant_regoffset;');p.write_text(s)
p=R/'inject_funcs.cu';s=p.read_text().replace('uint64_t addr, int32_t width, int32_t desReg','uint64_t addr, int32_t width, int32_t constant_bank, int32_t constant_offset, uint32_t constant_regoffset, int32_t desReg');s=s.replace('  ma.imm = immediate;','  ma.imm = immediate;\n  ma.constant_bank=constant_bank; ma.constant_offset=constant_offset; ma.constant_regoffset=constant_regoffset;');p.write_text(s)
p=R/'Makefile';s=p.read_text().replace('NVBIT_PATH=../nvbit_release/core','NVBIT_PATH=/data/c16/env/nvbit-1.7.5/core').replace('ARCH?=all','ARCH?=sm_89');p.write_text(s)
