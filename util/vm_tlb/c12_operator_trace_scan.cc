// Exact, read-only fast path for C12 operator-aware trace aggregation.
//
// NVBit trace records often encode all 32 warp lanes as a base/stride pair.
// Expanding every lane in Python would require billions of interpreter-level
// iterations.  This scanner keeps the full-lane contract, but counts an
// arithmetic progression against exact SimVA intervals analytically.  It only
// enumerates a progression when its stride is wider than one 64 KiB page.

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstdint>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Interval { int64_t begin, end; std::string tag; };
struct Totals {
  uint64_t refs[3] = {0, 0, 0};
  std::set<uint64_t> pages[3];
  std::set<std::string> parameters;
};

static void skip_space(const char*& text) { while (*text == ' ' || *text == '\t') ++text; }
static void skip_token(const char*& text) { skip_space(text); while (*text && *text != ' ' && *text != '\t' && *text != '\n' && *text != '\r') ++text; }
static int64_t parse_fast(const char*& text, int base) {
  skip_space(text); bool negative = false;
  if (*text == '-') { negative = true; ++text; }
  if (base == 16 && text[0] == '0' && (text[1] == 'x' || text[1] == 'X')) text += 2;
  int64_t value = 0; bool any = false;
  while (*text && *text != ' ' && *text != '\t' && *text != '\n' && *text != '\r') {
    char ch = *text++; int digit = (ch >= '0' && ch <= '9') ? ch-'0' :
                 (ch >= 'a' && ch <= 'f') ? ch-'a'+10 : (ch >= 'A' && ch <= 'F') ? ch-'A'+10 : -1;
    if (digit < 0 || digit >= base) throw std::runtime_error("invalid numeric trace token");
    value = value * base + digit; any = true;
  }
  if (!any) throw std::runtime_error("missing numeric trace token");
  return negative ? -value : value;
}
static int64_t integer(const std::string& text, int base = 0) {
  size_t used = 0; long long value = std::stoll(text, &used, base);
  if (used != text.size()) throw std::runtime_error("invalid integer: " + text);
  return value;
}
static bool trace_record(const std::string& line) {
  if (line.empty() || line[0] == '#' || line[0] == '-') return false;
  const char* text = line.c_str(); skip_space(text); if (!std::isxdigit(static_cast<unsigned char>(*text))) return false;
  char* end = nullptr; errno = 0; std::strtoull(text, &end, 16);
  return errno == 0 && end && (end > text) && (*end == ' ' || *end == '\t');
}
static int kind_index(const std::string& kind) {
  if (kind == "WEIGHT") return 0;
  if (kind == "KV_CACHE") return 1;
  return 2;
}
static int64_t floor_div(int64_t numerator, int64_t denominator) {
  // denominator is strictly positive.
  int64_t quotient = numerator / denominator, remainder = numerator % denominator;
  return remainder < 0 ? quotient - 1 : quotient;
}
static int64_t ceil_div(int64_t numerator, int64_t denominator) {
  return -floor_div(-numerator, denominator);
}
static size_t first_end_after(const std::vector<Interval>& rows, int64_t address) {
  size_t low = 0, high = rows.size();
  while (low < high) { size_t middle = low + (high-low)/2; if (rows[middle].end <= address) low = middle+1; else high = middle; }
  return low;
}
static std::vector<Interval> read_intervals(const std::string& path) {
  std::ifstream input(path); if (!input) throw std::runtime_error("cannot read " + path);
  std::vector<Interval> rows; std::string line;
  while (std::getline(input, line)) {
    if (line.empty()) continue;
    std::istringstream data(line); std::string a,b,tag;
    if (!(data >> a >> b >> tag)) throw std::runtime_error("bad range line in " + path);
    rows.push_back({integer(a), integer(b), tag});
  }
  std::sort(rows.begin(), rows.end(), [](const Interval& a, const Interval& b) { return a.begin < b.begin; });
  for (size_t i = 1; i < rows.size(); ++i) if (rows[i-1].end > rows[i].begin)
    throw std::runtime_error("overlapping intervals in " + path);
  return rows;
}

// Inclusive j interval whose base+j*stride is wholly inside [begin,end).
static bool j_interval(int64_t base, int64_t stride, int count, int64_t begin, int64_t end,
                       int width, int& low, int& high) {
  if (count <= 0 || end - begin < width) return false;
  int64_t top = end - width;
  if (stride == 0) {
    if (base < begin || base > top) return false;
    low = 0; high = count - 1; return true;
  }
  if (stride > 0) {
    low = static_cast<int>(ceil_div(begin-base, stride));
    high = static_cast<int>(floor_div(top-base, stride));
  } else {
    int64_t step = -stride;
    low = static_cast<int>(ceil_div(base-top, step));
    high = static_cast<int>(floor_div(base-begin, step));
  }
  low = std::max(low, 0); high = std::min(high, count-1);
  return low <= high;
}

static void add_pages_for_run(Totals& totals, int kind, int64_t base, int64_t stride, int low, int high, int width) {
  if (low > high) return;
  auto value = [=](int j) { return base + static_cast<int64_t>(j) * stride; };
  int64_t first = value(low), last = value(high);
  int64_t minimum = std::min(first, last), maximum = std::max(first, last) + width - 1;
  if (std::llabs(stride) <= 65536) {
    for (uint64_t page = static_cast<uint64_t>(minimum) / 65536; page <= static_cast<uint64_t>(maximum) / 65536; ++page)
      totals.pages[kind].insert(page);
    return;
  }
  for (int j=low; j<=high; ++j) for (uint64_t page = static_cast<uint64_t>(value(j)) / 65536;
       page <= static_cast<uint64_t>(value(j) + width - 1) / 65536; ++page) totals.pages[kind].insert(page);
}

static void add_explicit(Totals& totals, const std::vector<int64_t>& addresses, int width,
                         const std::vector<Interval>& objects, const std::vector<Interval>& parameters) {
  for (int64_t address : addresses) {
    int kind = 2;
    size_t object = first_end_after(objects, address);
    // Intervals are non-overlapping, hence at most the predecessor/successor
    // can intersect a non-zero-width address operand.
    for (size_t candidate = object; candidate < objects.size() && candidate <= object + 1; ++candidate)
      if (address >= objects[candidate].begin && address + width <= objects[candidate].end) { kind = kind_index(objects[candidate].tag); break; }
    totals.refs[kind]++;
    for (uint64_t page = static_cast<uint64_t>(address) / 65536; page <= static_cast<uint64_t>(address + width - 1) / 65536; ++page) totals.pages[kind].insert(page);
    size_t parameter = first_end_after(parameters, address);
    for (size_t candidate = parameter; candidate < parameters.size() && candidate <= parameter + 1; ++candidate)
      if (address < parameters[candidate].end && address + width > parameters[candidate].begin) totals.parameters.insert(parameters[candidate].tag);
  }
}

static void add_stride(Totals& totals, int64_t base, int64_t stride, int count, int width,
                       const std::vector<Interval>& objects, const std::vector<Interval>& parameters) {
  int64_t endpoint = base + static_cast<int64_t>(count-1) * stride;
  int64_t minimum = std::min(base, endpoint), maximum = std::max(base, endpoint) + width;
  std::vector<std::pair<int,int>> known;
  for (size_t cursor = first_end_after(objects, minimum); cursor < objects.size() && objects[cursor].begin < maximum; ++cursor) {
    const auto& range = objects[cursor];
    int low, high;
    if (j_interval(base, stride, count, range.begin, range.end, width, low, high)) {
      int kind = kind_index(range.tag); totals.refs[kind] += high - low + 1;
      add_pages_for_run(totals, kind, base, stride, low, high, width); known.push_back({low,high});
    }
  }
  std::sort(known.begin(), known.end()); int cursor = 0;
  for (const auto& run : known) { if (cursor < run.first) { totals.refs[2] += run.first-cursor; add_pages_for_run(totals,2,base,stride,cursor,run.first-1,width); } cursor = run.second+1; }
  if (cursor < count) { totals.refs[2] += count-cursor; add_pages_for_run(totals,2,base,stride,cursor,count-1,width); }
  for (size_t cursor = first_end_after(parameters, minimum); cursor < parameters.size() && parameters[cursor].begin < maximum; ++cursor) {
    const auto& range = parameters[cursor];
    int low, high;
    if (j_interval(base, stride, count, range.begin, range.end, width, low, high)) totals.parameters.insert(range.tag);
  }
}

static void scan(const std::string& trace, Totals& totals, const std::vector<Interval>& objects, const std::vector<Interval>& parameters) {
  // Trace names have already been obtained from an immutable kernelslist and
  // contain no shell metacharacters; still quote every single quote defensively.
  std::string quoted = "'";
  for (char ch : trace) quoted += (ch == '\'') ? "'\\''" : std::string(1, ch);
  quoted += "'";
  FILE* source = popen(("xz -dc -- " + quoted).c_str(), "r");
  if (!source) throw std::runtime_error("cannot launch xz for " + trace);
  std::array<char, 65536> buffer{};
  while (fgets(buffer.data(), static_cast<int>(buffer.size()), source)) {
    std::string line(buffer.data()); if (!trace_record(line)) continue;
    try {
      const char* text = line.c_str(); skip_token(text); // PC
      int lanes = __builtin_popcountll(static_cast<uint64_t>(parse_fast(text,16)));
      int dst = static_cast<int>(parse_fast(text,10)); for (int j=0; j<dst; ++j) skip_token(text);
      skip_token(text); // opcode
      int src = static_cast<int>(parse_fast(text,10)); for (int j=0; j<src; ++j) skip_token(text);
      int width = static_cast<int>(parse_fast(text,10));
      if (width == 0) continue;
      int format = static_cast<int>(parse_fast(text,10));
      std::vector<int64_t> addresses;
      if (format == 0) { addresses.reserve(lanes); for (int j=0;j<lanes;++j) addresses.push_back(parse_fast(text,16)); add_explicit(totals,addresses,width,objects,parameters); }
      else if (format == 1) { int64_t base = parse_fast(text,16); int64_t stride = parse_fast(text,10); add_stride(totals, base, stride, lanes, width, objects, parameters); }
      else if (format == 2) { addresses.reserve(lanes); int64_t address=parse_fast(text,16); addresses.push_back(address); for(int j=1;j<lanes;++j){ address += parse_fast(text,10); addresses.push_back(address); } add_explicit(totals,addresses,width,objects,parameters); }
      else throw std::runtime_error("unknown address format");
    } catch (const std::exception& error) { pclose(source); throw std::runtime_error(trace + ": " + error.what() + " line=" + line.substr(0, 300)); }
  }
  if (pclose(source) != 0) throw std::runtime_error("xz failed for " + trace);
}

static std::string join_pages(const std::set<uint64_t>& pages) { std::ostringstream out; bool first=true; for(auto page:pages){ if(!first)out<<","; out<<page; first=false;} return out.str(); }
static std::string join_names(const std::set<std::string>& names) { if (names.empty()) return "NONE"; std::ostringstream out; bool first=true; for(const auto& name:names){ if(!first)out<<";"; out<<name; first=false;} return out.str(); }

int main(int argc, char** argv) {
  if (argc != 6) { std::cerr << "usage: scanner TRACE_LIST TRACE_DIR OBJECT_RANGES PARAMETER_RANGES OUTPUT\n"; return 2; }
  try {
    auto objects=read_intervals(argv[3]), parameters=read_intervals(argv[4]); std::ifstream list(argv[1]); if(!list)throw std::runtime_error("cannot read trace list"); std::ofstream output(argv[5]); if(!output)throw std::runtime_error("cannot create output");
    output << "compute_index\ttrace_filename\tweight_refs\tkv_refs\tunknown_refs\tweight_pages\tkv_pages\tunknown_pages\tparameter_names\n";
    std::string name; int index=0;
    while(std::getline(list,name)) { if(name.empty())continue; Totals totals; scan(std::string(argv[2])+"/"+name,totals,objects,parameters); output<<index<<"\t"<<name<<"\t"<<totals.refs[0]<<"\t"<<totals.refs[1]<<"\t"<<totals.refs[2]<<"\t"<<join_pages(totals.pages[0])<<"\t"<<join_pages(totals.pages[1])<<"\t"<<join_pages(totals.pages[2])<<"\t"<<join_names(totals.parameters)<<"\n"; ++index; }
  } catch(const std::exception& error) { std::cerr << "FAIL: " << error.what() << "\n"; return 1; }
  return 0;
}
