#include <cassert>
#include <cstring>
#include <iostream>
#include <map>

#define __managed__
#include "common.h"
#include "route_b_raw_formatter.hpp"

static inst_trace_t blank() {
  inst_trace_t p{};
  p.cta_id_x = 1; p.cta_id_y = 2; p.cta_id_z = 3; p.warpid_tb = 4;
  p.vpc = 0x80; p.active_mask = 0x3; p.predicate_mask = 0x3;
  p.GPRDst = -1;
  for (int i = 0; i < MAX_SRC; ++i) p.GPRSrcs[i] = -1;
  return p;
}

int main() {
  std::map<int, std::string> ops{{0, "IMAD.MOV.U32"}, {1, "LDG.E.32"},
                                  {2, "STG.E.32"}};
  inst_trace_t p = blank();
  p.opcode_id = 0; p.GPRDst = 9; p.GPRSrcs[0] = 4; p.imm = 7;
  assert(route_b_raw::format(p, ops).value() ==
         "1 2 3 4 0080 00000003 1 R9 IMAD.MOV.U32 1 R4 0 7\n");
  p = blank(); p.opcode_id = 1; p.is_mem = true; p.addrs[0] = 0x100; p.addrs[1] = 0x104;
  assert(route_b_raw::format(p, ops).value() ==
         "1 2 3 4 0080 00000003 0 LDG.E.32 0 4 1 0x100 4 0\n");
  p = blank(); p.opcode_id = 2; p.is_mem = true; p.active_mask = 0x5; p.predicate_mask = 0x5;
  p.addrs[0] = 0x100; p.addrs[2] = 0x140;
  assert(route_b_raw::format(p, ops).value() ==
         "1 2 3 4 0080 00000005 0 STG.E.32 0 4 2 0x100 64 0\n");
  std::cout << "ROUTE_B_FORMATTER_SELFTEST_PASS\n";
}
