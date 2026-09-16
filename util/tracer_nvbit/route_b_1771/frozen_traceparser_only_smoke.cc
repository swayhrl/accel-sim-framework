#include <bitset>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <vector>

#include "trace_parser.h"

int main(int argc, char** argv) {
  if (argc != 2) return 2;
  trace_parser parser;
  kernel_trace_t* info = nullptr;
  try {
    info = parser.parse_kernel_info(argv[1]);
    if (!info || !info->trace_verion || !info->grid_dim_x || !info->tb_dim_x)
      throw std::runtime_error("missing kernel header");
    const unsigned threads = info->tb_dim_x * info->tb_dim_y * info->tb_dim_z;
    const unsigned warps = (threads + WARP_SIZE - 1) / WARP_SIZE;
    const unsigned long long blocks = static_cast<unsigned long long>(info->grid_dim_x) *
                                      info->grid_dim_y * info->grid_dim_z;
    std::vector<std::unique_ptr<std::vector<inst_trace_t>>> storage;
    std::vector<std::vector<inst_trace_t>*> views;
    for (unsigned i = 0; i < warps; ++i) {
      storage.emplace_back(new std::vector<inst_trace_t>());
      views.push_back(storage.back().get());
    }
    unsigned long long count = 0, ldgdepbar = 0;
    for (unsigned long long block = 0; block < blocks; ++block) {
      parser.get_next_threadblock_traces(views, info->trace_verion,
                                         info->enable_lineinfo, info->pipeReader);
      for (const auto* warp : views) {
        for (const auto& instruction : *warp) {
          ++count;
          if (instruction.opcode == "LDGDEPBAR") ++ldgdepbar;
        }
      }
    }
    parser.kernel_finalizer(info);
    std::cout << "FROZEN_TRACEPARSER_ONLY_PASS instructions=" << count
              << " ldgdepbar=" << ldgdepbar << '\n';
    return 0;
  } catch (const std::exception& error) {
    if (info) parser.kernel_finalizer(info);
    std::cerr << "FROZEN_TRACEPARSER_ONLY_REJECT " << error.what() << '\n';
    return 1;
  }
}
