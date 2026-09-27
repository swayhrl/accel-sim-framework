#include "gpgpu-sim/oracle_elastic_residency.h"
#include "abstract_hardware_model.h"

#include <stdint.h>

#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>

int main(int argc, char **argv) {
  if (argc < 5 || ((argc - 4) % 5) != 0) {
    std::cerr << "usage: probe SIDECAR SHA OUTPUT label,address,type,is_write,expected ...\n";
    return 2;
  }
  try {
    oracle_elastic_residency::oracle_config config;
    config.configure(true, 0, 131072, 128, 16, argv[1], argv[2], false,
                     true);
    std::ofstream out(argv[3]);
    if (!out) return 2;
    out << "label\taddress_dec\taddress_hex\taccess_type\tis_write\t"
           "interval_match\toracle_target\ttarget_class\t"
           "region_relative_line_index\tselection_hash_hex\t"
           "protection_eligible\tselection_filtered\texpected_target\n";
    for (int i = 4; i < argc; i += 5) {
      const std::string label(argv[i]);
      const uint64_t address = strtoull(argv[i + 1], NULL, 0);
      const unsigned access_type =
          static_cast<unsigned>(strtoul(argv[i + 2], NULL, 0));
      const bool is_write = strtoul(argv[i + 3], NULL, 0) != 0;
      const bool expected = strtoul(argv[i + 4], NULL, 0) != 0;
      unsigned target_class = 0;
      const bool interval_match = config.lookup(address, &target_class);
      const bool request_eligible =
          oracle_elastic_residency::target_request_eligible(
              access_type, is_write, static_cast<unsigned>(GLOBAL_ACC_R));
      const bool oracle_target = interval_match && request_eligible;
      uint64_t line_index = 0;
      uint64_t hash = 0;
      const bool protection_eligible =
          oracle_target && config.protection_eligible(
                               address, &target_class, &line_index, &hash);
      const bool selection_filtered = oracle_target && !protection_eligible;
      out << label << '\t' << address << "\t0x" << std::hex << address
          << std::dec << '\t' << access_type << '\t' << (is_write ? 1 : 0)
          << '\t' << (interval_match ? 1 : 0) << '\t'
          << (oracle_target ? 1 : 0) << '\t' << target_class << '\t'
          << line_index << "\t0x" << std::hex << std::setw(16)
          << std::setfill('0') << hash << std::setfill(' ') << std::dec
          << '\t' << (protection_eligible ? 1 : 0) << '\t'
          << (selection_filtered ? 1 : 0) << '\t' << (expected ? 1 : 0)
          << '\n';
      if (oracle_target != expected) {
        std::cerr << "target expectation mismatch: " << label << "\n";
        return 1;
      }
      if (!oracle_target && protection_eligible) {
        std::cerr << "non-target became protection eligible: " << label
                  << "\n";
        return 1;
      }
    }
    std::cout << "M1F_REAL_TRACE_ACTIVATION_PROBE_PASS\n";
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "M1F_REAL_TRACE_ACTIVATION_PROBE_FAIL: " << error.what()
              << "\n";
    return 1;
  }
}
