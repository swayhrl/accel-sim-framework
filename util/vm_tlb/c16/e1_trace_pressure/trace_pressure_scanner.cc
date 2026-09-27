// Exact, read-only streaming scanner for C16 E1 postprocessed traceg inputs.
//
// The output is a trace-address reference proxy.  It is not actual L2 traffic,
// hit/miss behavior, or timing.  Address decompression and global-space
// classification intentionally mirror the accepted Accel-Sim trace frontend.

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>

namespace {

constexpr uint64_t kLineBytes = 128;
constexpr uint64_t kLocalMemSizeMax = 1ULL << 14;
constexpr unsigned kTargetClasses = 28;

struct Args {
  std::string trace;
  std::string sidecar;
  std::string output;
  std::string semantic_identity;
  std::string exact_function;
  uint64_t kernel_id = 0;
  int decode = -1;
  int semantic_layer = -1;
};

[[noreturn]] void fail(const std::string &message) {
  throw std::runtime_error(message);
}

uint64_t parse_u64(const std::string &text, int base, const char *label) {
  if (text.empty()) fail(std::string("empty ") + label);
  size_t used = 0;
  uint64_t value = 0;
  try {
    value = std::stoull(text, &used, base);
  } catch (const std::exception &) {
    fail(std::string("invalid ") + label + ": " + text);
  }
  if (used != text.size()) fail(std::string("invalid ") + label + ": " + text);
  return value;
}

int64_t parse_i64(const std::string &text, int base, const char *label) {
  if (text.empty()) fail(std::string("empty ") + label);
  size_t used = 0;
  int64_t value = 0;
  try {
    value = std::stoll(text, &used, base);
  } catch (const std::exception &) {
    fail(std::string("invalid ") + label + ": " + text);
  }
  if (used != text.size()) fail(std::string("invalid ") + label + ": " + text);
  return value;
}

std::string json_escape(const std::string &value) {
  std::ostringstream out;
  for (unsigned char c : value) {
    switch (c) {
      case '\\': out << "\\\\"; break;
      case '"': out << "\\\""; break;
      case '\n': out << "\\n"; break;
      case '\r': out << "\\r"; break;
      case '\t': out << "\\t"; break;
      default:
        if (c < 0x20) {
          out << "\\u" << std::hex << std::setw(4) << std::setfill('0')
              << static_cast<unsigned>(c) << std::dec;
        } else {
          out << c;
        }
    }
  }
  return out.str();
}

std::string shell_quote(const std::string &value) {
  std::string result = "'";
  for (char c : value) {
    if (c == '\'') result += "'\\''";
    else result += c;
  }
  result += "'";
  return result;
}

bool ends_with(const std::string &value, const std::string &suffix) {
  return value.size() >= suffix.size() &&
         value.compare(value.size() - suffix.size(), suffix.size(), suffix) == 0;
}

class LineReader {
 public:
  explicit LineReader(const std::string &path) : path_(path) {
    if (ends_with(path, ".xz")) {
      command_ = "xz -dc -- " + shell_quote(path);
      pipe_ = popen(command_.c_str(), "r");
      if (!pipe_) fail("cannot start xz for " + path);
    } else {
      file_.open(path);
      if (!file_) fail("cannot open trace " + path);
    }
  }

  ~LineReader() {
    if (pipe_) pclose(pipe_);
  }

  bool getline(std::string *line) {
    if (!pipe_) return static_cast<bool>(std::getline(file_, *line));
    char *buffer = nullptr;
    size_t capacity = 0;
    ssize_t count = ::getline(&buffer, &capacity, pipe_);
    if (count < 0) {
      free(buffer);
      int status = pclose(pipe_);
      pipe_ = nullptr;
      if (status == -1 || !WIFEXITED(status) || WEXITSTATUS(status) != 0)
        fail("xz failed for " + path_);
      return false;
    }
    line->assign(buffer, static_cast<size_t>(count));
    free(buffer);
    if (!line->empty() && line->back() == '\n') line->pop_back();
    if (!line->empty() && line->back() == '\r') line->pop_back();
    return true;
  }

 private:
  std::string path_;
  std::string command_;
  FILE *pipe_ = nullptr;
  std::ifstream file_;
};

std::vector<std::string> split_ws(const std::string &line) {
  std::istringstream stream(line);
  std::vector<std::string> fields;
  for (std::string field; stream >> field;) fields.push_back(field);
  return fields;
}

std::vector<std::string> split(const std::string &value, char delimiter) {
  std::vector<std::string> result;
  std::stringstream stream(value);
  for (std::string item; std::getline(stream, item, delimiter);)
    if (!item.empty()) result.push_back(item);
  return result;
}

bool decimal_digits(const std::string &value) {
  return !value.empty() &&
         std::all_of(value.begin(), value.end(), [](unsigned char c) {
           return c >= '0' && c <= '9';
         });
}

unsigned opcode_width(const std::string &opcode) {
  for (const std::string &token : split(opcode, '.')) {
    if (decimal_digits(token)) return static_cast<unsigned>(parse_u64(token, 10, "opcode width")) / 8;
    if (token.size() > 1 && token[0] == 'U' && decimal_digits(token.substr(1)))
      return static_cast<unsigned>(parse_u64(token.substr(1), 10, "opcode width")) / 8;
  }
  return 4;
}

std::string opcode_base(const std::string &opcode) {
  size_t dot = opcode.find('.');
  return opcode.substr(0, dot);
}

struct Interval {
  uint64_t begin;
  uint64_t end;
  unsigned target_class;
};

std::vector<Interval> read_sidecar(const std::string &path) {
  std::ifstream source(path);
  if (!source) fail("cannot open sidecar " + path);
  std::string line;
  if (!std::getline(source, line) ||
      line != "ORACLE_ELASTIC_QWEIGHT_RESIDENCY_V1\t1\tMODELED_L2_GET_ADDR")
    fail("sidecar header drift");
  std::vector<Interval> intervals;
  while (std::getline(source, line)) {
    if (line.empty()) continue;
    std::vector<std::string> fields = split(line, '\t');
    if (fields.size() != 4) fail("malformed sidecar row");
    Interval item{parse_u64(fields[0], 0, "sidecar begin"),
                  parse_u64(fields[1], 0, "sidecar end"),
                  static_cast<unsigned>(parse_u64(fields[3], 10, "target class"))};
    if (item.begin >= item.end || item.begin % kLineBytes || item.end % kLineBytes ||
        item.target_class < 1 || item.target_class > kTargetClasses)
      fail("invalid sidecar interval");
    intervals.push_back(item);
  }
  std::sort(intervals.begin(), intervals.end(), [](const Interval &a, const Interval &b) {
    return a.begin < b.begin;
  });
  if (intervals.size() != kTargetClasses) fail("sidecar must contain exact 28 intervals");
  std::array<bool, kTargetClasses + 1> classes{};
  for (size_t i = 0; i < intervals.size(); ++i) {
    if (i && intervals[i - 1].end > intervals[i].begin) fail("overlapping sidecar intervals");
    if (classes[intervals[i].target_class]) fail("duplicate target class");
    classes[intervals[i].target_class] = true;
  }
  return intervals;
}

unsigned classify_target(uint64_t address, unsigned width,
                         const std::vector<Interval> &intervals,
                         bool *boundary_overlap) {
  *boundary_overlap = false;
  if (!width || address > std::numeric_limits<uint64_t>::max() - width) return 0;
  uint64_t end = address + width;
  auto it = std::upper_bound(intervals.begin(), intervals.end(), address,
      [](uint64_t value, const Interval &item) { return value < item.begin; });
  if (it != intervals.begin()) {
    const Interval &candidate = *std::prev(it);
    if (candidate.begin <= address && end <= candidate.end) return candidate.target_class;
    if (std::max(address, candidate.begin) < std::min(end, candidate.end)) *boundary_overlap = true;
  }
  if (it != intervals.end() && std::max(address, it->begin) < std::min(end, it->end))
    *boundary_overlap = true;
  return 0;
}

struct Collector {
  std::unordered_map<uint64_t, uint64_t> non_target_refs;
  std::unordered_map<uint64_t, uint64_t> target_refs;
  std::array<std::unordered_set<uint64_t>, kTargetClasses> target_lines_by_class;
  uint64_t address_refs = 0;
  uint64_t line_refs = 0;
  uint64_t target_line_refs = 0;
  uint64_t non_target_line_refs = 0;
  uint64_t non_target_address_refs = 0;
  uint64_t target_address_refs = 0;

  void clear() {
    non_target_refs.clear();
    target_refs.clear();
    for (auto &lines : target_lines_by_class) lines.clear();
    address_refs = line_refs = target_line_refs = non_target_line_refs = 0;
    non_target_address_refs = target_address_refs = 0;
  }

  void add(uint64_t address, unsigned width, unsigned target_class) {
    ++address_refs;
    if (target_class) ++target_address_refs;
    else ++non_target_address_refs;
    uint64_t first = address & ~(kLineBytes - 1);
    uint64_t last = (address + width - 1) & ~(kLineBytes - 1);
    for (uint64_t line = first;; line += kLineBytes) {
      ++line_refs;
      if (target_class) {
        ++target_line_refs;
        ++target_refs[line];
        target_lines_by_class.at(target_class - 1).insert(line);
      } else {
        ++non_target_line_refs;
        ++non_target_refs[line];
      }
      if (line == last) break;
    }
  }

  std::vector<uint64_t> non_target_unique() const {
    std::vector<uint64_t> values;
    values.reserve(non_target_refs.size());
    for (const auto &entry : non_target_refs) values.push_back(entry.first);
    std::sort(values.begin(), values.end());
    return values;
  }

  std::vector<uint64_t> all_unique() const {
    std::vector<uint64_t> values = non_target_unique();
    for (const auto &entry : target_refs) values.push_back(entry.first);
    std::sort(values.begin(), values.end());
    values.erase(std::unique(values.begin(), values.end()), values.end());
    return values;
  }

  std::vector<std::pair<uint64_t, uint64_t>> all_line_refs() const {
    std::unordered_map<uint64_t, uint64_t> merged = non_target_refs;
    for (const auto &entry : target_refs) merged[entry.first] += entry.second;
    std::vector<std::pair<uint64_t, uint64_t>> rows(merged.begin(), merged.end());
    std::sort(rows.begin(), rows.end());
    return rows;
  }

  size_t target_unique_count() const { return target_refs.size(); }
};

void write_u64(std::ofstream *out, uint64_t value) {
  char bytes[8];
  for (unsigned i = 0; i < 8; ++i) bytes[i] = static_cast<char>((value >> (8 * i)) & 0xff);
  out->write(bytes, sizeof(bytes));
  if (!*out) fail("binary output write failed");
}

void write_values(const std::string &path, const std::vector<uint64_t> &values) {
  std::ofstream out(path, std::ios::binary);
  if (!out) fail("cannot create " + path);
  for (uint64_t value : values) write_u64(&out, value);
}

void write_pairs(const std::string &path,
                 const std::unordered_map<uint64_t, uint64_t> &values) {
  std::vector<std::pair<uint64_t, uint64_t>> rows(values.begin(), values.end());
  std::sort(rows.begin(), rows.end());
  std::ofstream out(path, std::ios::binary);
  if (!out) fail("cannot create " + path);
  for (const auto &row : rows) {
    write_u64(&out, row.first);
    write_u64(&out, row.second);
  }
}

void write_pairs(const std::string &path,
                 const std::vector<std::pair<uint64_t, uint64_t>> &rows) {
  std::ofstream out(path, std::ios::binary);
  if (!out) fail("cannot create " + path);
  for (const auto &row : rows) {
    write_u64(&out, row.first);
    write_u64(&out, row.second);
  }
}

void mkdir_fresh(const std::string &path) {
  struct stat info {};
  if (stat(path.c_str(), &info) == 0) fail("output directory already exists: " + path);
  if (mkdir(path.c_str(), 0775) != 0) fail("cannot create output directory: " + path);
}

void emit_collector(const std::string &root, const std::string &prefix,
                    const Collector &collector) {
  write_values(root + "/" + prefix + "all_unique_lines.u64", collector.all_unique());
  write_values(root + "/" + prefix + "non_target_unique_lines.u64", collector.non_target_unique());
  write_pairs(root + "/" + prefix + "all_line_refs.u64", collector.all_line_refs());
  write_pairs(root + "/" + prefix + "non_target_line_refs.u64", collector.non_target_refs);
}

void emit_segment_json(std::ostream &out, const Collector &collector,
                       uint64_t dynamic_instructions,
                       const std::string &prefix, const std::string &indent) {
  out << "{\n"
      << indent << "  \"dynamic_instructions\": " << dynamic_instructions << ",\n"
      << indent << "  \"global_address_references\": " << collector.address_refs << ",\n"
      << indent << "  \"non_target_address_references\": "
      << collector.non_target_address_refs << ",\n"
      << indent << "  \"line_references\": " << collector.line_refs << ",\n"
      << indent << "  \"non_target_line_references\": "
      << collector.non_target_line_refs << ",\n"
      << indent << "  \"artifacts\": {\n"
      << indent << "    \"all_unique_lines_u64le\": \"" << prefix
      << "all_unique_lines.u64\",\n"
      << indent << "    \"non_target_unique_lines_u64le\": \"" << prefix
      << "non_target_unique_lines.u64\",\n"
      << indent << "    \"all_line_refs_u64le\": \"" << prefix
      << "all_line_refs.u64\",\n"
      << indent << "    \"non_target_line_refs_u64le\": \"" << prefix
      << "non_target_line_refs.u64\",\n"
      << indent << "    \"all_set_refs_u64le\": \"" << prefix
      << "all_set_refs.u64\",\n"
      << indent << "    \"non_target_set_refs_u64le\": \"" << prefix
      << "non_target_set_refs.u64\"\n"
      << indent << "  }\n"
      << indent << "}";
}

struct Decoded {
  std::string opcode;
  unsigned width = 0;
  std::vector<uint64_t> addresses;
};

Decoded decode_record(const std::string &line, unsigned trace_version,
                      unsigned lineinfo) {
  std::vector<std::string> fields = split_ws(line);
  size_t i = 0;
  if (trace_version < 3) {
    if (fields.size() < 4) fail("truncated legacy trace prefix");
    i += 4;
  }
  if (lineinfo) ++i;
  if (i + 3 > fields.size()) fail("truncated trace record prefix");
  parse_u64(fields.at(i++), 16, "PC");
  uint64_t mask = parse_u64(fields.at(i++), 16, "active mask");
  unsigned destinations = static_cast<unsigned>(parse_u64(fields.at(i++), 10, "destination count"));
  if (destinations > 1 || i + destinations >= fields.size()) fail("invalid destination list");
  i += destinations;
  std::string opcode = fields.at(i++);
  unsigned sources = static_cast<unsigned>(parse_u64(fields.at(i++), 10, "source count"));
  if (sources > 4 || i + sources >= fields.size()) fail("invalid source list");
  i += sources;
  unsigned encoded_width = static_cast<unsigned>(parse_u64(fields.at(i++), 10, "memory width"));
  if (!encoded_width) return Decoded{opcode, 0, {}};
  unsigned width = opcode_width(opcode);
  if (!width) fail("zero opcode-derived memory width");
  if (i >= fields.size()) fail("missing address mode");
  unsigned mode = static_cast<unsigned>(parse_u64(fields.at(i++), 10, "address mode"));
  std::vector<unsigned> active;
  for (unsigned lane = 0; lane < 32; ++lane)
    if ((mask >> lane) & 1ULL) active.push_back(lane);
  if (active.empty()) return Decoded{opcode, width, {}};
  std::vector<uint64_t> addresses;
  addresses.reserve(active.size());
  if (mode == 0) {
    if (i + active.size() > fields.size()) fail("truncated list-all address payload");
    for (size_t n = 0; n < active.size(); ++n)
      addresses.push_back(parse_u64(fields.at(i++), 16, "lane address"));
  } else if (mode == 1) {
    if (i + 2 > fields.size()) fail("truncated base-stride address payload");
    uint64_t current = parse_u64(fields.at(i++), 16, "base address");
    int64_t stride = parse_i64(fields.at(i++), 10, "stride");
    for (size_t n = 1; n < active.size(); ++n)
      if (active[n] != active[n - 1] + 1)
        fail("base-stride active mask is non-contiguous; accepted parser result is undefined");
    addresses.push_back(current);
    for (size_t n = 1; n < active.size(); ++n) {
      current = static_cast<uint64_t>(static_cast<int64_t>(current) + stride);
      addresses.push_back(current);
    }
  } else if (mode == 2) {
    if (i >= fields.size()) fail("truncated base-delta address payload");
    uint64_t current = parse_u64(fields.at(i++), 16, "base address");
    addresses.push_back(current);
    // The accepted parser reads one delta per active lane, but consumes N-1.
    if (i + active.size() > fields.size()) fail("truncated base-delta payload");
    for (size_t n = 1; n < active.size(); ++n) {
      int64_t delta = parse_i64(fields.at(i++), 10, "address delta");
      current = static_cast<uint64_t>(static_cast<int64_t>(current) + delta);
      addresses.push_back(current);
    }
  } else {
    fail("unknown address mode " + std::to_string(mode));
  }
  return Decoded{opcode, width, addresses};
}

enum class Space { kGlobal, kNonGlobal };

Space classify_space(const Decoded &record, uint64_t shmem_base,
                     uint64_t local_base) {
  const std::string base = opcode_base(record.opcode);
  static const std::set<std::string> non_global = {
      "LDC", "LDL", "STL", "LDS", "STS", "ATOMS", "LDSM"};
  static const std::set<std::string> global = {
      "LDG", "LDGSTS", "STG", "ATOMG", "RED", "ATOM"};
  if (non_global.count(base)) return Space::kNonGlobal;
  if (global.count(base)) return Space::kGlobal;
  if (base == "LD" || base == "ST") {
    if (!shmem_base || !local_base || record.addresses.empty()) return Space::kNonGlobal;
    uint64_t address = record.addresses.front();
    if (shmem_base <= address && address < local_base) return Space::kNonGlobal;
    if (local_base <= address && address < local_base + kLocalMemSizeMax)
      return Space::kNonGlobal;
    return Space::kGlobal;
  }
  fail("unclassified memory opcode: " + record.opcode);
}

std::string value_after_equal(const std::string &line) {
  size_t equal = line.find('=');
  if (equal == std::string::npos) fail("missing '=' in trace header: " + line);
  size_t begin = equal + 1;
  while (begin < line.size() && line[begin] == ' ') ++begin;
  return line.substr(begin);
}

Args parse_args(int argc, char **argv) {
  Args args;
  std::map<std::string, std::string *> strings = {
      {"--trace", &args.trace}, {"--sidecar", &args.sidecar},
      {"--output", &args.output}, {"--semantic-identity", &args.semantic_identity},
      {"--exact-function", &args.exact_function}};
  for (int i = 1; i < argc; ++i) {
    std::string key = argv[i];
    if (i + 1 >= argc) fail("missing value for " + key);
    std::string value = argv[++i];
    auto found = strings.find(key);
    if (found != strings.end()) *found->second = value;
    else if (key == "--kernel-id") args.kernel_id = parse_u64(value, 10, "kernel ID");
    else if (key == "--decode") args.decode = static_cast<int>(parse_i64(value, 10, "decode"));
    else if (key == "--semantic-layer") args.semantic_layer = static_cast<int>(parse_i64(value, 10, "semantic layer"));
    else fail("unknown argument " + key);
  }
  if (args.trace.empty() || args.sidecar.empty() || args.output.empty() || !args.kernel_id)
    fail("required: --trace --sidecar --output --kernel-id");
  return args;
}

void scan(const Args &args) {
  std::vector<Interval> intervals = read_sidecar(args.sidecar);
  mkdir_fresh(args.output);
  LineReader source(args.trace);
  Collector all;
  Collector prefix;
  Collector suffix;
  std::array<uint64_t, kTargetClasses> target_refs{};
  uint64_t dynamic_instructions = 0;
  uint64_t cta_count = 0;
  uint64_t global_memory_instructions = 0;
  uint64_t target_boundary_crossings = 0;
  uint64_t first_target_instruction = 0;
  uint64_t last_target_instruction = 0;
  uint64_t first_target_reference = 0;
  uint64_t last_target_reference = 0;
  bool saw_expected_target = false;
  uint64_t trace_kernel_id = 0;
  uint64_t shmem_base = 0;
  uint64_t local_base = 0;
  unsigned trace_version = 0;
  unsigned lineinfo = 0;
  unsigned expected_class =
      args.semantic_identity == "up_proj" && args.semantic_layer >= 0 &&
              args.semantic_layer < static_cast<int>(kTargetClasses)
          ? static_cast<unsigned>(args.semantic_layer + 1)
          : 0;

  std::string line;
  while (source.getline(&line)) {
    if (line.rfind("-kernel id =", 0) == 0) {
      trace_kernel_id = parse_u64(value_after_equal(line), 10, "trace kernel ID");
      continue;
    }
    if (line.rfind("-shmem base_addr =", 0) == 0) {
      shmem_base = parse_u64(value_after_equal(line), 0, "shmem base");
      continue;
    }
    if (line.rfind("-local mem base_addr =", 0) == 0) {
      local_base = parse_u64(value_after_equal(line), 0, "local base");
      continue;
    }
    if (line.rfind("-accelsim tracer version =", 0) == 0) {
      trace_version = static_cast<unsigned>(parse_u64(value_after_equal(line), 10, "trace version"));
      continue;
    }
    if (line.rfind("-enable lineinfo =", 0) == 0) {
      lineinfo = static_cast<unsigned>(parse_u64(value_after_equal(line), 10, "lineinfo"));
      continue;
    }
    if (line.rfind("#BEGIN_TB", 0) == 0) {
      ++cta_count;
      continue;
    }
    if (line.empty() || line[0] == '#' || line[0] == '-' ||
        line.rfind("thread block", 0) == 0 || line.rfind("warp", 0) == 0 ||
        line.rfind("insts", 0) == 0)
      continue;
    std::vector<std::string> probe = split_ws(line);
    if (probe.empty()) continue;
    try {
      parse_u64(probe[0], 16, "PC");
    } catch (const std::exception &) {
      fail("unexpected trace line: " + line.substr(0, 160));
    }
    if (!trace_version) fail("instruction before trace-version header");
    ++dynamic_instructions;
    Decoded decoded = decode_record(line, trace_version, lineinfo);
    if (!decoded.width || decoded.addresses.empty()) continue;
    if (classify_space(decoded, shmem_base, local_base) != Space::kGlobal) continue;
    ++global_memory_instructions;
    for (uint64_t address : decoded.addresses) {
      bool boundary = false;
      unsigned target_class = classify_target(address, decoded.width, intervals, &boundary);
      if (boundary) ++target_boundary_crossings;
      if (target_class) ++target_refs.at(target_class - 1);
      uint64_t reference_ordinal = all.address_refs + 1;
      bool expected = expected_class && target_class == expected_class;
      if (!saw_expected_target) {
        if (expected) {
          saw_expected_target = true;
          first_target_instruction = dynamic_instructions;
          first_target_reference = reference_ordinal;
          suffix.clear();
        } else {
          prefix.add(address, decoded.width, target_class);
        }
      }
      if (expected) {
        last_target_instruction = dynamic_instructions;
        last_target_reference = reference_ordinal;
        suffix.clear();
      } else if (saw_expected_target) {
        suffix.add(address, decoded.width, target_class);
      }
      all.add(address, decoded.width, target_class);
    }
  }
  if (trace_kernel_id != args.kernel_id)
    fail("trace/header kernel ID mismatch");
  if (target_boundary_crossings)
    fail("target interval boundary-crossing reference observed");

  emit_collector(args.output, "", all);
  emit_collector(args.output, "prefix_", prefix);
  emit_collector(args.output, "suffix_", suffix);
  std::ofstream summary(args.output + "/summary.json");
  if (!summary) fail("cannot create summary.json");
  std::vector<uint64_t> all_unique = all.all_unique();
  std::vector<uint64_t> non_target_unique = all.non_target_unique();
  summary << "{\n"
          << "  \"schema\": \"C16_E1_TRACE_KERNEL_SUMMARY_V1\",\n"
          << "  \"scanner_schema\": \"C16_E1_TRACE_PRESSURE_KERNEL_SCANNER_V1\",\n"
          << "  \"status\": \"PASS\",\n"
          << "  \"claim_boundary\": \"TRACE_ADDRESS_REFERENCE_AND_128B_LINE_REFERENCE_PROXY_ONLY\",\n"
          << "  \"kernel_id\": " << args.kernel_id << ",\n"
          << "  \"decode_iteration\": " << args.decode << ",\n"
          << "  \"decode_index\": " << args.decode << ",\n"
          << "  \"semantic_layer\": " << args.semantic_layer << ",\n"
          << "  \"semantic_identity\": \"" << json_escape(args.semantic_identity) << "\",\n"
          << "  \"exact_function\": \"" << json_escape(args.exact_function) << "\",\n"
          << "  \"trace_version\": " << trace_version << ",\n"
          << "  \"dynamic_instructions\": " << dynamic_instructions << ",\n"
          << "  \"cta_count\": " << cta_count << ",\n"
          << "  \"global_memory_instructions\": " << global_memory_instructions << ",\n"
          << "  \"global_address_references\": " << all.address_refs << ",\n"
          << "  \"global_128b_line_references\": " << all.line_refs << ",\n"
          << "  \"target_128b_line_references\": " << all.target_line_refs << ",\n"
          << "  \"non_target_128b_line_references\": " << all.non_target_line_refs << ",\n"
          << "  \"target_address_references\": " << all.target_address_refs << ",\n"
          << "  \"non_target_address_references\": " << all.non_target_address_refs << ",\n"
          << "  \"unique_128b_lines\": " << all_unique.size() << ",\n"
          << "  \"target_unique_128b_lines\": " << all.target_unique_count() << ",\n"
          << "  \"non_target_unique_128b_lines\": " << non_target_unique.size() << ",\n"
          << "  \"target_refs_by_class\": [";
  for (unsigned i = 0; i < kTargetClasses; ++i) {
    if (i) summary << ", ";
    summary << target_refs[i];
  }
  summary << "],\n"
          << "  \"per_target_class_references\": {";
  for (unsigned i = 0; i < kTargetClasses; ++i) {
    if (i) summary << ", ";
    summary << "\"" << i + 1 << "\": " << target_refs[i];
  }
  summary << "},\n"
          << "  \"expected_target_class\": " << expected_class << ",\n"
          << "  \"expected_target_observed\": " << (saw_expected_target ? "true" : "false") << ",\n"
          << "  \"first_expected_target_instruction_ordinal\": " << first_target_instruction << ",\n"
          << "  \"last_expected_target_instruction_ordinal\": " << last_target_instruction << ",\n"
          << "  \"first_expected_target_reference_ordinal\": " << first_target_reference << ",\n"
          << "  \"last_expected_target_reference_ordinal\": " << last_target_reference << ",\n"
          << "  \"prefix\": {\"address_references\": " << prefix.address_refs
          << ", \"line_references\": " << prefix.line_refs
          << ", \"non_target_line_references\": " << prefix.non_target_line_refs
          << ", \"unique_128b_lines\": " << prefix.all_unique().size()
          << ", \"non_target_unique_128b_lines\": " << prefix.non_target_unique().size() << "},\n"
          << "  \"suffix\": {\"address_references\": " << suffix.address_refs
          << ", \"line_references\": " << suffix.line_refs
          << ", \"non_target_line_references\": " << suffix.non_target_line_refs
          << ", \"unique_128b_lines\": " << suffix.all_unique().size()
          << ", \"non_target_unique_128b_lines\": " << suffix.non_target_unique().size() << "},\n"
          << "  \"artifacts\": {\n"
          << "    \"all_unique_lines_u64le\": \"all_unique_lines.u64\",\n"
          << "    \"non_target_unique_lines_u64le\": \"non_target_unique_lines.u64\",\n"
          << "    \"all_line_refs_u64le\": \"all_line_refs.u64\",\n"
          << "    \"non_target_line_refs_u64le\": \"non_target_line_refs.u64\",\n"
          << "    \"all_set_refs_u64le\": \"all_set_refs.u64\",\n"
          << "    \"non_target_set_refs_u64le\": \"non_target_set_refs.u64\"\n"
          << "  },\n"
          << "  \"target_boundaries\": {";
  if (saw_expected_target) {
    summary << "\n    \"" << expected_class << "\": {\n"
            << "      \"referenced_target_unique_lines\": "
            << all.target_lines_by_class.at(expected_class - 1).size() << ",\n"
            << "      \"first_instruction_ordinal\": " << first_target_instruction << ",\n"
            << "      \"last_instruction_ordinal\": " << last_target_instruction << ",\n"
            << "      \"first_reference_ordinal\": " << first_target_reference << ",\n"
            << "      \"last_reference_ordinal\": " << last_target_reference << ",\n"
            << "      \"prefix\": ";
    emit_segment_json(summary, prefix, first_target_instruction - 1, "prefix_", "      ");
    summary << ",\n      \"suffix\": ";
    emit_segment_json(summary, suffix, dynamic_instructions - last_target_instruction,
                      "suffix_", "      ");
    summary << "\n    }\n  },\n";
  } else {
    summary << "},\n";
  }
  summary
          << "  \"binary_encoding\": \"LITTLE_ENDIAN_UINT64\",\n"
          << "  \"non_target_line_refs_encoding\": \"REPEATED_PAIR_LINE_ADDRESS_COUNT\",\n"
          << "  \"mapper\": {\"status\": \"UNMAPPED\"}\n"
          << "}\n";
}

}  // namespace

int main(int argc, char **argv) {
  try {
    scan(parse_args(argc, argv));
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "TRACE_PRESSURE_SCANNER_FAIL: " << error.what() << "\n";
    return 1;
  }
}
