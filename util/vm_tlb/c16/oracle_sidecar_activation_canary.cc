#include "gpgpu-sim/oracle_elastic_residency.h"
#include "abstract_hardware_model.h"

#include <stdint.h>

#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

int main(int argc, char **argv) {
  if (argc < 5 || ((argc - 4) % 5) != 0) {
    std::cerr << "usage: canary SIDECAR SHA OUTPUT label,address,type,is_write,expected ...\n";
    return 2;
  }
  const char *sidecar = argv[1];
  const char *accepted_sha = argv[2];
  std::ofstream out(argv[3]);
  if (!out) return 2;
  oracle_elastic_residency::oracle_config config;
  config.configure(true, 0, 1, 128, 1, sidecar, accepted_sha, false);
  out << "label\taddress_dec\taddress_hex\taccess_type\tis_write\t"
         "interval_match\ttarget\ttarget_class\texpected\n";
  for (int i = 4; i < argc; i += 5) {
    std::string label(argv[i]);
    uint64_t address = strtoull(argv[i + 1], NULL, 0);
    unsigned access_type = static_cast<unsigned>(strtoul(argv[i + 2], NULL, 0));
    bool is_write = strtoul(argv[i + 3], NULL, 0) != 0;
    bool expected = strtoul(argv[i + 4], NULL, 0) != 0;
    unsigned target_class = 0;
    bool interval_match = config.lookup(address, &target_class);
    bool eligible = oracle_elastic_residency::target_request_eligible(
        access_type, is_write, static_cast<unsigned>(GLOBAL_ACC_R));
    bool target = interval_match && eligible;
    out << label << '\t' << address << "\t0x" << std::hex << address
        << std::dec << '\t' << access_type << '\t' << (is_write ? 1 : 0)
        << '\t' << (interval_match ? 1 : 0) << '\t' << (target ? 1 : 0)
        << '\t' << target_class << '\t' << (expected ? 1 : 0) << '\n';
    if (target != expected) {
      std::cerr << "target expectation mismatch: " << label << "\n";
      return 1;
    }
  }
  out.close();
  std::cout << "ORACLE_TAG_ACTIVATION_CANARY_PASS\n";
  return 0;
}
