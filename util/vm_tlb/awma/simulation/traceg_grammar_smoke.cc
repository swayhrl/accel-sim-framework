// Strict smoke driver around Accel-Sim's authoritative trace parser.
#include <algorithm>
#include <bitset>
#include <cctype>
#include <iostream>
#include <map>
#include <memory>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "trace_parser.h"

namespace {

struct Receipt {
  unsigned trace_version = 0;
  unsigned lineinfo = 0;
  unsigned long long expected_thread_blocks = 0;
  unsigned long long thread_blocks = 0;
  unsigned long long instructions = 0;
  unsigned block_threads = 0;
  std::map<std::string, unsigned long long> opcode_counts;
};

std::vector<std::string> tokens(const std::string &line) {
  std::istringstream stream(line);
  std::vector<std::string> result;
  for (std::string token; stream >> token;) result.push_back(token);
  return result;
}

unsigned long long number(const std::string &text, int base,
                          const std::string &label) {
  size_t consumed = 0;
  unsigned long long value = 0;
  try {
    value = std::stoull(text, &consumed, base);
  } catch (const std::exception &) {
    throw std::runtime_error("invalid " + label + ": " + text);
  }
  if (consumed != text.size())
    throw std::runtime_error("invalid " + label + ": " + text);
  return value;
}

long long signed_number(const std::string &text, int base,
                        const std::string &label) {
  size_t consumed = 0;
  long long value = 0;
  try {
    value = std::stoll(text, &consumed, base);
  } catch (const std::exception &) {
    throw std::runtime_error("invalid " + label + ": " + text);
  }
  if (consumed != text.size())
    throw std::runtime_error("invalid " + label + ": " + text);
  return value;
}

std::string base_opcode(const std::string &opcode) {
  return opcode.substr(0, opcode.find('.'));
}

bool starts_with(const std::string &value, const std::string &prefix) {
  return value.rfind(prefix, 0) == 0;
}

// Ampere ISA defines LDGDEPBAR as ALU_OP. trace-driven uses it to group
// preceding LDGSTS operations, so its trace record has no memory payload.
bool addressless_control_opcode(const std::string &opcode) {
  return base_opcode(opcode) == "LDGDEPBAR";
}

// Accepted Ampere parsing classifies LDC as OP_LDC/ALU_OP and trace-driven
// supplies its pre-existing implicit constant-load approximation without a
// serialized dynamic address payload.  This exception is deliberately exact:
// it does not make other LD* opcodes, including ULDC, addressless.
bool implicit_constant_load_opcode(const std::string &opcode) {
  return base_opcode(opcode) == "LDC";
}

std::string access_kind(const std::string &opcode) {
  const std::string base = base_opcode(opcode);
  if (addressless_control_opcode(opcode)) return "";
  if (base.find("ATOM") != std::string::npos || starts_with(base, "RED"))
    return "ATOMIC";
  if (starts_with(base, "LD") || starts_with(base, "TEX") ||
      starts_with(base, "SULD"))
    return "READ";
  if (starts_with(base, "ST") || starts_with(base, "SUST"))
    return "WRITE";
  return "";
}

std::string memory_space(const std::string &opcode) {
  const std::string base = base_opcode(opcode);
  if (starts_with(base, "LDG") || starts_with(base, "STG") ||
      starts_with(base, "ATOMG") || starts_with(base, "REDG") ||
      starts_with(base, "LDGSTS"))
    return "GLOBAL";
  if (starts_with(base, "LDS") || starts_with(base, "STS") ||
      starts_with(base, "ATOMS") || starts_with(base, "REDS"))
    return "SHARED";
  if (starts_with(base, "LDL") || starts_with(base, "STL"))
    return "LOCAL";
  if (starts_with(base, "LDC") || starts_with(base, "ULDC"))
    return "CONSTANT";
  if (starts_with(base, "TEX")) return "TEXTURE";
  if (starts_with(base, "SULD") || starts_with(base, "SUST"))
    return "SURFACE";
  return "";
}

unsigned opcode_width(const std::string &opcode) {
  std::istringstream stream(opcode);
  for (std::string component; std::getline(stream, component, '.');) {
    std::string digits = component;
    if (digits.size() > 1 && digits[0] == 'U') digits.erase(0, 1);
    if (!digits.empty() &&
        std::all_of(digits.begin(), digits.end(),
                    [](unsigned char c) { return std::isdigit(c); })) {
      const unsigned bits = static_cast<unsigned>(number(digits, 10, "opcode width"));
      if (bits % 8 != 0) throw std::runtime_error("opcode width is not byte aligned");
      return bits / 8;
    }
  }
  return 0;
}

std::string take(const std::vector<std::string> &parts, size_t &index,
                 const std::string &label) {
  if (index >= parts.size()) throw std::runtime_error("missing " + label);
  return parts[index++];
}

void parse_instruction(const std::string &line, Receipt &receipt) {
  const std::vector<std::string> parts = tokens(line);
  size_t index = 0;
  if (receipt.trace_version < 3) {
    for (unsigned i = 0; i < 4; ++i)
      number(take(parts, index, "legacy CTA/warp field"), 10, "legacy CTA/warp field");
  }
  if (receipt.lineinfo)
    number(take(parts, index, "line number"), 10, "line number");
  number(take(parts, index, "PC"), 16, "PC");
  const unsigned mask = static_cast<unsigned>(number(take(parts, index, "active mask"), 16, "active mask"));
  const unsigned destinations = static_cast<unsigned>(number(take(parts, index, "destination count"), 10, "destination count"));
  if (destinations > MAX_DST) throw std::runtime_error("destination count exceeds grammar maximum");
  const std::regex reg("R[0-9]+");
  for (unsigned i = 0; i < destinations; ++i)
    if (!std::regex_match(take(parts, index, "destination register"), reg))
      throw std::runtime_error("invalid destination register");
  const std::string opcode = take(parts, index, "opcode");
  const unsigned sources = static_cast<unsigned>(number(take(parts, index, "source count"), 10, "source count"));
  if (sources > MAX_SRC) throw std::runtime_error("source count exceeds grammar maximum");
  for (unsigned i = 0; i < sources; ++i)
    if (!std::regex_match(take(parts, index, "source register"), reg))
      throw std::runtime_error("invalid source register");

  const unsigned width = static_cast<unsigned>(number(take(parts, index, "memory width"), 10, "memory width"));
  const std::string access = access_kind(opcode);
  if (width == 0 && !access.empty() && !implicit_constant_load_opcode(opcode))
    throw std::runtime_error("memory opcode has zero/missing width: " + opcode);
  if (width > 0) {
    if (access.empty()) throw std::runtime_error("memory width lacks access semantics: " + opcode);
    if (memory_space(opcode).empty()) throw std::runtime_error("memory opcode lacks space semantics: " + opcode);
    if (width > 64 || (width & (width - 1)) != 0)
      throw std::runtime_error("invalid memory width: " + std::to_string(width));
    const unsigned encoded_width = opcode_width(opcode);
    if (encoded_width && encoded_width != width)
      throw std::runtime_error("trace/opcode memory width mismatch: " + opcode);
    const unsigned mode = static_cast<unsigned>(number(take(parts, index, "address mode"), 10, "address mode"));
    const unsigned active = std::bitset<WARP_SIZE>(mask).count();
    if (mode == address_format::list_all) {
      for (unsigned i = 0; i < active; ++i)
        number(take(parts, index, "lane address"), 16, "lane address");
    } else if (mode == address_format::base_stride) {
      number(take(parts, index, "base address"), 16, "base address");
      signed_number(take(parts, index, "stride"), 10, "stride");
    } else if (mode == address_format::base_delta) {
      number(take(parts, index, "base address"), 16, "base address");
      for (unsigned i = 0; i < active; ++i)
        signed_number(take(parts, index, "address delta"), 10, "address delta");
    } else {
      throw std::runtime_error("invalid address mode");
    }
  }
  number(take(parts, index, "immediate"), 10, "immediate");
  if (index != parts.size()) throw std::runtime_error("trailing tokens in instruction record");
  ++receipt.instructions;
  ++receipt.opcode_counts[opcode];
}

Receipt strict_scan(const std::string &path) {
  Receipt receipt;
  PipeReader reader(path);
  std::string line;
  bool format_seen = false;
  bool in_tb = false;
  bool thread_block_seen = false;
  bool warp_open = false;
  unsigned declared_instructions = 0;
  unsigned seen_instructions = 0;
  unsigned grid_x = 0, grid_y = 0, grid_z = 0;
  unsigned block_x = 0, block_y = 0, block_z = 0;
  bool name_seen = false, id_seen = false, grid_seen = false, block_seen = false;

  while (reader.readLine(line)) {
    if (line.empty()) continue;
    if (!format_seen) {
      if (starts_with(line, "-kernel name = ")) name_seen = true;
      else if (starts_with(line, "-kernel id = ")) {
        unsigned kernel_id = 0;
        if (sscanf(line.c_str(), "-kernel id = %u", &kernel_id) != 1)
          throw std::runtime_error("malformed kernel id header");
        id_seen = true;
      }
      else if (sscanf(line.c_str(), "-grid dim = (%u,%u,%u)", &grid_x, &grid_y, &grid_z) == 3) grid_seen = true;
      else if (sscanf(line.c_str(), "-block dim = (%u,%u,%u)", &block_x, &block_y, &block_z) == 3) block_seen = true;
      else if (sscanf(line.c_str(), "-accelsim tracer version = %u", &receipt.trace_version) == 1) {}
      else if (sscanf(line.c_str(), "-enable lineinfo = %u", &receipt.lineinfo) == 1) {}
      else if (starts_with(line, "#traces format")) format_seen = true;
      continue;
    }
    if (line == "#BEGIN_TB") {
      if (in_tb) throw std::runtime_error("nested #BEGIN_TB");
      in_tb = true;
      thread_block_seen = false;
      warp_open = false;
      continue;
    }
    if (line == "#END_TB") {
      if (!in_tb || !thread_block_seen) throw std::runtime_error("orphan/incomplete #END_TB");
      if (warp_open && seen_instructions != declared_instructions)
        throw std::runtime_error("warp instruction count mismatch");
      in_tb = false;
      ++receipt.thread_blocks;
      continue;
    }
    if (!in_tb) throw std::runtime_error("record outside thread block");
    if (starts_with(line, "thread block = ")) {
      unsigned x = 0, y = 0, z = 0;
      if (sscanf(line.c_str(), "thread block = %u,%u,%u", &x, &y, &z) != 3)
        throw std::runtime_error("malformed thread block record");
      thread_block_seen = true;
      continue;
    }
    if (starts_with(line, "warp = ")) {
      if (!thread_block_seen) throw std::runtime_error("warp before thread block record");
      if (warp_open && seen_instructions != declared_instructions)
        throw std::runtime_error("warp instruction count mismatch");
      unsigned warp = 0;
      if (sscanf(line.c_str(), "warp = %u", &warp) != 1)
        throw std::runtime_error("malformed warp record");
      warp_open = true;
      declared_instructions = 0;
      seen_instructions = 0;
      continue;
    }
    if (starts_with(line, "insts = ")) {
      if (!warp_open || sscanf(line.c_str(), "insts = %u", &declared_instructions) != 1)
        throw std::runtime_error("malformed insts record");
      seen_instructions = 0;
      continue;
    }
    if (!warp_open) throw std::runtime_error("instruction before warp record");
    parse_instruction(line, receipt);
    ++seen_instructions;
    if (seen_instructions > declared_instructions)
      throw std::runtime_error("too many instructions in warp");
  }
  if (!format_seen || !name_seen || !id_seen || !grid_seen || !block_seen || receipt.trace_version == 0)
    throw std::runtime_error("required trace header is missing");
  if (in_tb) throw std::runtime_error("non-terminal thread block");
  if (warp_open && seen_instructions != declared_instructions)
    throw std::runtime_error("warp instruction count mismatch at EOF");
  if (!grid_x || !grid_y || !grid_z || !block_x || !block_y || !block_z)
    throw std::runtime_error("zero grid/block dimension");
  receipt.expected_thread_blocks = static_cast<unsigned long long>(grid_x) * grid_y * grid_z;
  receipt.block_threads = block_x * block_y * block_z;
  if (receipt.thread_blocks != receipt.expected_thread_blocks)
    throw std::runtime_error("thread block count does not match grid dimensions");
  if (!receipt.instructions) throw std::runtime_error("trace contains no instructions");
  return receipt;
}

void official_smoke(const std::string &path, const Receipt &strict) {
  std::ostringstream suppressed;
  std::streambuf *original = std::cout.rdbuf(suppressed.rdbuf());
  trace_parser parser;
  kernel_trace_t *info = nullptr;
  try {
    info = parser.parse_kernel_info(path);
    if (!info || !info->trace_verion || !info->grid_dim_x || !info->tb_dim_x)
      throw std::runtime_error("official parser did not recover required header fields");
    const unsigned warps = (strict.block_threads + WARP_SIZE - 1) / WARP_SIZE;
    std::vector<std::unique_ptr<std::vector<inst_trace_t>>> storage;
    std::vector<std::vector<inst_trace_t> *> views;
    for (unsigned i = 0; i < warps; ++i) {
      storage.emplace_back(new std::vector<inst_trace_t>());
      views.push_back(storage.back().get());
    }
    unsigned long long official_instructions = 0;
    for (unsigned long long block = 0; block < strict.expected_thread_blocks; ++block) {
      parser.get_next_threadblock_traces(views, info->trace_verion,
                                         info->enable_lineinfo, info->pipeReader);
      unsigned long long block_instructions = 0;
      for (const auto *warp : views) {
        block_instructions += warp->size();
        for (const auto &instruction : *warp) {
          if (instruction.opcode.empty())
            throw std::runtime_error("official parser produced empty opcode");
        }
      }
      if (!block_instructions)
        throw std::runtime_error("official parser produced empty thread block");
      official_instructions += block_instructions;
    }
    if (official_instructions != strict.instructions)
      throw std::runtime_error("official/strict instruction counts disagree");
    parser.kernel_finalizer(info);
    info = nullptr;
  } catch (...) {
    if (info) parser.kernel_finalizer(info);
    std::cout.rdbuf(original);
    throw;
  }
  std::cout.rdbuf(original);
}

void emit(const Receipt &receipt) {
  std::cout << "{\"status\":\"TRACEG_GRAMMAR_PASS\",\"trace_version\":"
            << receipt.trace_version << ",\"thread_blocks\":"
            << receipt.thread_blocks << ",\"instructions\":"
            << receipt.instructions << ",\"opcode_counts\":{";
  bool first = true;
  for (const auto &item : receipt.opcode_counts) {
    if (!first) std::cout << ',';
    first = false;
    std::cout << '\"' << item.first << "\":" << item.second;
  }
  std::cout << "}}\n";
}

}  // namespace

int main(int argc, char **argv) {
  if (argc != 2) {
    std::cerr << "usage: traceg_grammar_smoke TRACE.traceg.xz\n";
    return 2;
  }
  try {
    Receipt receipt = strict_scan(argv[1]);
    official_smoke(argv[1], receipt);
    emit(receipt);
    return 0;
  } catch (const std::exception &exc) {
    std::cerr << "TRACEG_GRAMMAR_REJECT: " << exc.what() << '\n';
    return 2;
  }
}
