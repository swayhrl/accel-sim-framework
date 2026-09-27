#include "accepted_l2_mapper_build_config.h"

#include "gpgpu-sim/addrdec.h"
#include "gpgpu-sim/gpu-cache.h"
#include "option_parser.h"
#include "tr1_hash_map.h"

#include <errno.h>
#include <stdint.h>
#include <unistd.h>

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

// addrdec.cc references this Core-owned table even though the accepted config
// selects CONSECUTIVE indexing and never enters the RANDOM case. The full
// simulator defines it in gpu-sim.cc; this focused source-direct executable
// provides the same linkage object without pulling in the simulator runtime.
tr1_hash_map<new_addr_type, unsigned> address_random_interleaving;

namespace {

struct mapped_address {
  uint64_t address;
  unsigned subpartition;
  unsigned set;
};

class accepted_l2_mapper {
 public:
  accepted_l2_mapper()
      : l2_config_string_(C16_ACCEPTED_L2_CONFIG,
                          C16_ACCEPTED_L2_CONFIG +
                              std::strlen(C16_ACCEPTED_L2_CONFIG) + 1) {
    option_parser_t parser = option_parser_create();
    address_mapping_.addrdec_setoption(parser);

    const char *arguments[] = {
        "accepted_l2_mapper_cli",
        "-gpgpu_mem_address_mask",
        C16_ACCEPTED_MEM_ADDRESS_MASK,
        "-gpgpu_memory_partition_indexing",
        C16_ACCEPTED_PARTITION_INDEXING,
        "-gpgpu_mem_addr_mapping",
        C16_ACCEPTED_MEM_ADDR_MAPPING,
    };
    option_parser_cmdline(parser, sizeof(arguments) / sizeof(arguments[0]),
                          arguments);
    // Core initialization reports decoded masks on stdout. Preserve those
    // diagnostics on stderr so stdout remains a strict TSV data stream.
    std::fflush(stdout);
    const int saved_stdout = dup(STDOUT_FILENO);
    if (saved_stdout < 0 || dup2(STDERR_FILENO, STDOUT_FILENO) < 0) {
      if (saved_stdout >= 0) close(saved_stdout);
      option_parser_destroy(parser);
      throw std::runtime_error("cannot redirect Core initialization output");
    }
    address_mapping_.init(C16_ACCEPTED_N_MEM,
                          C16_ACCEPTED_N_SUBPARTITIONS_PER_CHANNEL);
    std::fflush(stdout);
    if (dup2(saved_stdout, STDOUT_FILENO) < 0) {
      close(saved_stdout);
      option_parser_destroy(parser);
      throw std::runtime_error("cannot restore mapper stdout");
    }
    close(saved_stdout);
    option_parser_destroy(parser);

    l2_config_.m_config_string = l2_config_string_.data();
    l2_config_.init(&address_mapping_);
  }

  mapped_address map(uint64_t address) const {
    addrdec_t decoded;
    address_mapping_.addrdec_tlx(address, &decoded);
    mapped_address result = {address, decoded.sub_partition,
                             l2_config_.set_index(address)};
    return result;
  }

 private:
  linear_to_raw_address_translation address_mapping_;
  l2_cache_config l2_config_;
  std::vector<char> l2_config_string_;
};

void print_provenance(std::ostream &out) {
  out << "accepted_mapper_schema=C16_E1_ACCEPTED_L2_MAPPER_V1\n"
      << "accepted_source_mode=SOURCE_DIRECT_CORE\n"
      << "accepted_core_sha=" << C16_ACCEPTED_CORE_SHA << "\n"
      << "accepted_config_sha256=" << C16_ACCEPTED_CONFIG_SHA256 << "\n"
      << "accepted_config_path=" << C16_ACCEPTED_CONFIG_PATH << "\n"
      << "accepted_address_namespace=MODELED_L2_GET_ADDR\n"
      << "accepted_address_transform=IDENTITY_NUMERIC_NO_ADDRESS_REWRITE\n";
}

bool parse_address(const std::string &token, uint64_t *value) {
  if (token.empty() || token[0] == '-') return false;
  int base = 10;
  const char *start = token.c_str();
  if (token.size() > 2 && token[0] == '0' &&
      (token[1] == 'x' || token[1] == 'X')) {
    base = 16;
    start += 2;
  }
  if (*start == '\0') return false;

  errno = 0;
  char *end = NULL;
  unsigned long long parsed = std::strtoull(start, &end, base);
  if (errno == ERANGE || end == start || *end != '\0') return false;
  *value = static_cast<uint64_t>(parsed);
  return true;
}

void print_row(std::ostream &out, const mapped_address &mapped) {
  out << "0x" << std::hex << mapped.address << std::dec << '\t'
      << mapped.subpartition << '\t' << mapped.set << '\n';
}

struct canary_case {
  const char *label;
  uint64_t address;
  unsigned expected_subpartition;
  unsigned expected_set;
};

int run_canary(const accepted_l2_mapper &mapper) {
  // These are fixed outputs from the accepted Core/config pair. The production
  // mapping remains the direct Core calls above; no mapping formula is copied.
  static const canary_case cases[] = {
      {"L0_START", 0x7ea94e000000ULL, 0, 1336},
      {"L0_MID", 0x7ea94f030000ULL, 0, 1372},
      {"L0_LAST_LINE", 0x7ea95005ff80ULL, 15, 1535},
      {"L14_START", 0x7ea906000000ULL, 0, 1048},
      {"L14_MID", 0x7ea907030000ULL, 0, 1148},
      {"L14_LAST_LINE", 0x7ea90805ff80ULL, 15, 1183},
      {"L27_START", 0x7ea7de000000ULL, 0, 1912},
      {"L27_MID", 0x7ea7df030000ULL, 0, 1820},
      {"L27_LAST_LINE", 0x7ea7e005ff80ULL, 15, 1855},
  };

  for (size_t i = 0; i < sizeof(cases) / sizeof(cases[0]); ++i) {
    mapped_address actual = mapper.map(cases[i].address);
    if (actual.subpartition != cases[i].expected_subpartition ||
        actual.set != cases[i].expected_set) {
      std::cerr << "CANARY_MISMATCH label=" << cases[i].label << " address=0x"
                << std::hex << cases[i].address << std::dec
                << " expected_subpartition=" << cases[i].expected_subpartition
                << " actual_subpartition=" << actual.subpartition
                << " expected_set=" << cases[i].expected_set
                << " actual_set=" << actual.set << "\n";
      return 1;
    }
  }

  std::cout << "ACCEPTED_L2_MAPPER_CANARY_PASS\t"
            << sizeof(cases) / sizeof(cases[0]) << "\n";
  return 0;
}

void usage(std::ostream &out) {
  out << "usage: accepted_l2_mapper_cli map [--no-header]\n"
      << "       accepted_l2_mapper_cli map --input-lines-u64 FILE "
         "--output-tsv FILE [--no-header]\n"
      << "       accepted_l2_mapper_cli --self-test\n"
      << "       accepted_l2_mapper_cli --provenance\n"
      << "Read decimal or 0x-prefixed addresses from stdin and emit TSV.\n";
}

int map_text_stream(const accepted_l2_mapper &mapper, std::istream &input,
                    std::ostream &output, bool print_header) {
  if (print_header)
    output << "line_address_hex\tsubpartition\tset_index\n";
  std::string line;
  size_t line_number = 0;
  while (std::getline(input, line)) {
    ++line_number;
    const size_t comment = line.find('#');
    if (comment != std::string::npos) line.erase(comment);
    std::istringstream tokens(line);
    std::string token;
    while (tokens >> token) {
      uint64_t address = 0;
      if (!parse_address(token, &address)) {
        std::cerr << "invalid address at input line " << line_number << ": "
                  << token << "\n";
        return 2;
      }
      print_row(output, mapper.map(address));
    }
  }
  if (!input.eof()) {
    std::cerr << "input read failure\n";
    return 2;
  }
  return 0;
}

int map_u64le_file(const accepted_l2_mapper &mapper,
                   const std::string &input_path,
                   const std::string &output_path, bool print_header) {
  if (input_path == output_path) {
    std::cerr << "input and output paths must differ\n";
    return 2;
  }
  std::ifstream input(input_path.c_str(), std::ios::in | std::ios::binary);
  if (!input) {
    std::cerr << "cannot open input-lines-u64 file: " << input_path << "\n";
    return 2;
  }
  std::ofstream output(output_path.c_str(),
                       std::ios::out | std::ios::binary | std::ios::trunc);
  if (!output) {
    std::cerr << "cannot open output-tsv file: " << output_path << "\n";
    return 2;
  }
  if (print_header)
    output << "line_address_hex\tsubpartition\tset_index\n";

  uint64_t previous = 0;
  bool have_previous = false;
  size_t record = 0;
  while (true) {
    unsigned char bytes[8] = {0};
    input.read(reinterpret_cast<char *>(bytes), sizeof(bytes));
    const std::streamsize count = input.gcount();
    if (count == 0 && input.eof()) break;
    if (count != static_cast<std::streamsize>(sizeof(bytes))) {
      std::cerr << "truncated input-lines-u64 record after " << record
                << " complete records\n";
      return 2;
    }
    uint64_t address = 0;
    for (unsigned i = 0; i < sizeof(bytes); ++i)
      address |= static_cast<uint64_t>(bytes[i]) << (8U * i);
    if ((address & 127ULL) != 0) {
      std::cerr << "unaligned 128B line address at record " << record
                << ": 0x" << std::hex << address << std::dec << "\n";
      return 2;
    }
    if (have_previous && address < previous) {
      std::cerr << "input-lines-u64 is not sorted at record " << record
                << "\n";
      return 2;
    }
    print_row(output, mapper.map(address));
    previous = address;
    have_previous = true;
    ++record;
  }
  if (!input.eof()) {
    std::cerr << "input-lines-u64 read failure\n";
    return 2;
  }
  if (!output) {
    std::cerr << "output-tsv write failure\n";
    return 2;
  }
  return 0;
}

}  // namespace

int main(int argc, char **argv) {
  bool print_header = true;
  bool self_test = false;
  bool provenance_only = false;
  bool map_mode = false;
  std::string input_lines_u64;
  std::string output_tsv;

  for (int i = 1; i < argc; ++i) {
    const std::string argument(argv[i]);
    if (argument == "map") {
      if (map_mode) {
        std::cerr << "map mode specified more than once\n";
        return 2;
      }
      map_mode = true;
    } else if (argument == "--input-lines-u64") {
      if (++i >= argc) {
        std::cerr << "--input-lines-u64 requires a path\n";
        return 2;
      }
      input_lines_u64 = argv[i];
    } else if (argument == "--output-tsv") {
      if (++i >= argc) {
        std::cerr << "--output-tsv requires a path\n";
        return 2;
      }
      output_tsv = argv[i];
    } else if (argument == "--no-header") {
      print_header = false;
    } else if (argument == "--self-test") {
      self_test = true;
    } else if (argument == "--provenance") {
      provenance_only = true;
    } else if (argument == "--help" || argument == "-h") {
      usage(std::cout);
      return 0;
    } else {
      std::cerr << "unknown argument: " << argument << "\n";
      usage(std::cerr);
      return 2;
    }
  }

  if ((self_test ? 1 : 0) + (provenance_only ? 1 : 0) + (map_mode ? 1 : 0) >
      1) {
    std::cerr << "map, --self-test, and --provenance are mutually exclusive\n";
    return 2;
  }
  if (!map_mode && (!input_lines_u64.empty() || !output_tsv.empty())) {
    std::cerr << "file options require map mode\n";
    return 2;
  }
  if (input_lines_u64.empty() != output_tsv.empty()) {
    std::cerr << "--input-lines-u64 and --output-tsv must be used together\n";
    return 2;
  }
  if (provenance_only) {
    print_provenance(std::cout);
    return 0;
  }

  try {
    accepted_l2_mapper mapper;
    print_provenance(std::cerr);
    if (self_test) return run_canary(mapper);
    if (!input_lines_u64.empty())
      return map_u64le_file(mapper, input_lines_u64, output_tsv,
                            print_header);
    return map_text_stream(mapper, std::cin, std::cout, print_header);
  } catch (const std::exception &error) {
    std::cerr << "mapper initialization failed: " << error.what() << "\n";
    return 1;
  }
  return 0;
}
