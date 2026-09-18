#pragma once

#include <bitset>
#include <cstdint>
#include <map>
#include <optional>
#include <sstream>
#include <string>
#include <vector>

/*
 * Pure Route-B raw-line formatter.  This deliberately has no channel, thread,
 * writer, or NVBit lifecycle state: both the CPU differential test and the
 * live Route-B receiver call this one implementation.
 */
namespace route_b_raw {

inline std::vector<std::string> opcode_tokens(const std::string& opcode) {
  std::vector<std::string> result;
  std::stringstream stream(opcode);
  std::string token;
  while (std::getline(stream, token, '.')) {
    if (!token.empty()) result.push_back(token);
  }
  return result;
}

inline bool decimal(const std::string& value) {
  if (value.empty()) return false;
  for (char c : value) {
    if (c < '0' || c > '9') return false;
  }
  return true;
}

inline unsigned opcode_width_bytes(const std::string& opcode) {
  for (const std::string& token : opcode_tokens(opcode)) {
    if (decimal(token)) return static_cast<unsigned>(std::stoul(token) / 8);
    if (token.size() > 1 && token[0] == 'U' && decimal(token.substr(1))) {
      return static_cast<unsigned>(std::stoul(token.substr(1)) / 8);
    }
  }
  return 4;
}

inline bool base_stride(const uint64_t* addresses, const std::bitset<32>& mask,
                        uint64_t& base, int& stride) {
  bool constant = true;
  bool first_found = false;
  bool gap_seen = false;
  for (int lane = 0; lane < 32; ++lane) {
    if (mask.test(lane) && !first_found) {
      first_found = true;
      base = addresses[lane];
      if (lane < 31 && mask.test(lane + 1)) {
        stride = static_cast<int>(addresses[lane + 1] - addresses[lane]);
      } else {
        constant = false;
        break;
      }
    } else if (first_found && !gap_seen) {
      if (mask.test(lane)) {
        if (stride != static_cast<int>(addresses[lane] - addresses[lane - 1])) {
          constant = false;
          break;
        }
      } else {
        gap_seen = true;
      }
    } else if (gap_seen && mask.test(lane)) {
      constant = false;
      break;
    }
  }
  return constant;
}

inline std::optional<std::string> format(const inst_trace_t& packet,
                                         const std::map<int, std::string>& opcodes,
                                         bool lineinfo = false,
                                         bool compress = true) {
  auto found = opcodes.find(packet.opcode_id);
  if (found == opcodes.end()) return std::nullopt;
  const std::string& opcode = found->second;
  const uint32_t effective_mask = packet.active_mask & packet.predicate_mask;
  std::bitset<32> mask(effective_mask);
  std::ostringstream line;
  line << packet.cta_id_x << ' ' << packet.cta_id_y << ' ' << packet.cta_id_z
       << ' ' << packet.warpid_tb << ' ';
  if (lineinfo) line << packet.line_num << ' ';
  line << std::hex;
  line.width(4);
  line.fill('0');
  line << packet.vpc << ' ';
  line.width(8);
  line << effective_mask << std::dec << ' ';
  if (packet.GPRDst >= 0) {
    line << "1 R" << packet.GPRDst << ' ';
  } else {
    line << "0 ";
  }
  line << opcode << ' ';
  unsigned sources = 0;
  for (int i = 0; i < MAX_SRC; ++i) {
    if (packet.GPRSrcs[i] >= 0) ++sources;
  }
  line << sources << ' ';
  for (int i = 0; i < MAX_SRC; ++i) {
    if (packet.GPRSrcs[i] >= 0) line << "R" << packet.GPRSrcs[i] << ' ';
  }
  if (packet.is_mem) {
    line << opcode_width_bytes(opcode) << ' ';
    uint64_t base = 0;
    int stride = 0;
    if (compress && base_stride(packet.addrs, mask, base, stride)) {
      line << "1 0x" << std::hex << base << std::dec << ' ' << stride << ' ';
    } else {
      /* V2 producer compatibility policy: list every effective lane address
       * when base+stride cannot represent the packet.  Never emit legacy
       * base_delta mode 2, whose N-1 producer contract is incompatible with
       * the frozen consumer's N-delta reader. */
      line << "0 ";
      for (int lane = 0; lane < 32; ++lane) {
        if (mask.test(lane)) line << "0x" << std::hex << packet.addrs[lane] << std::dec << ' ';
      }
    }
  } else {
    line << "0 ";
  }
  /* Legacy v5 used fprintf(..., "%d", ma->imm); preserve its low signed word. */
  line << static_cast<int32_t>(packet.imm) << '\n';
  return line.str();
}

}  // namespace route_b_raw
