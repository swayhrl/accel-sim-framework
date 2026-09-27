#include <cassert>
#include <cstring>
#include <iostream>
#include <map>

#define __managed__
#include "common.h"
#include "route_b_raw_formatter.hpp"

static inst_trace_t blank() {
  inst_trace_t p{};
  p.cta_id_x = 0; p.cta_id_y = 0; p.cta_id_z = 0; p.warpid_tb = 0;
  p.vpc = 0x80; p.active_mask = 0x3; p.predicate_mask = 0x3;
  p.GPRDst = -1;
  for (int i = 0; i < MAX_SRC; ++i) p.GPRSrcs[i] = -1;
  return p;
}

int main(int argc, char** argv) {
  std::map<int, std::string> ops{{0, "IMAD.MOV.U32"}, {1, "LDG.E.32"},
                                  {2, "STG.E.32"}, {3, "ULDC.64"}};
  inst_trace_t p = blank();
  p.opcode_id = 0; p.GPRDst = 9; p.GPRSrcs[0] = 4; p.imm = 7;
  const std::string nonmem = route_b_raw::format(p, ops).value();
  assert(nonmem == "0 0 0 0 0080 00000003 1 R9 IMAD.MOV.U32 1 R4 0 7\n");
  p = blank(); p.opcode_id = 3; p.imm = 0;
  const std::string uldc = route_b_raw::format(p, ops).value();
  assert(uldc == "0 0 0 0 0080 00000003 0 ULDC.64 0 0 0\n");
  p = blank(); p.opcode_id = 1; p.is_mem = true; p.addrs[0] = 0x100; p.addrs[1] = 0x104;
  p.imm = 17;
  const std::string stride = route_b_raw::format(p, ops).value();
  assert(stride == "0 0 0 0 0080 00000003 0 LDG.E.32 0 4 1 0x100 4 17\n");
  p = blank(); p.opcode_id = 2; p.is_mem = true; p.active_mask = 0x5; p.predicate_mask = 0x5;
  p.addrs[0] = 0x100; p.addrs[2] = 0x140;
  const std::string irregular_two = route_b_raw::format(p, ops).value();
  assert(irregular_two ==
         "0 0 0 0 0080 00000005 0 STG.E.32 0 4 0 0x100 0x140 0\n");
  p = blank(); p.opcode_id = 1; p.is_mem = true; p.active_mask = 0xb; p.predicate_mask = 0xb;
  p.addrs[0] = 0x200; p.addrs[1] = 0x208; p.addrs[3] = 0x250; p.imm = static_cast<uint64_t>(-7);
  const std::string irregular_many = route_b_raw::format(p, ops).value();
  assert(irregular_many ==
         "0 0 0 0 0080 0000000b 0 LDG.E.32 0 4 0 0x200 0x208 0x250 -7\n");
  assert(irregular_two.find(" 2 ") == std::string::npos);
  assert(irregular_many.find(" 2 ") == std::string::npos);
  if (argc == 2 && std::string(argv[1]) == "--emit-raw") {
    std::cout << nonmem << uldc << stride << irregular_two << irregular_many;
    return 0;
  }
  std::cout << "ROUTE_B_FORMATTER_SELFTEST_PASS\n";
}
