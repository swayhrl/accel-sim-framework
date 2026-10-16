// CPU-only harness linked to the exact frozen parser, not a replacement decoder.
#include "trace_parser.h"
#include <openssl/evp.h>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <sstream>

int main(int argc, char** argv) {
  if (argc != 2) return 2;
  std::ifstream input(argv[1]);
  if (!input) return 3;
  auto* ctx = EVP_MD_CTX_new();
  EVP_DigestInit_ex(ctx, EVP_sha256(), nullptr);
  uint64_t records=0, instructions=0, memory=0;
  std::string line;
  while (std::getline(input,line)) {
    if (line.empty() || !std::isxdigit(static_cast<unsigned char>(line[0]))) continue;
    // Fixed original member declares trace version zero and no line info.
    inst_trace_t t;
    if (!t.parse_from_string(line,0,0)) return 4;
    ++records; instructions += std::bitset<32>(t.mask).count();
    if (t.memadd_info) {
      ++memory;
      uint64_t fields[35] = {t.m_pc,t.mask,static_cast<uint64_t>(t.memadd_info->width)};
      for (int i=0;i<32;++i) fields[i+3]=(t.mask & (1u<<i)) ? t.memadd_info->addrs[i] : 0;
      // Host is little endian x86_64; audit schema is 35 little-endian u64.
      const uint16_t one=1;
      if (*reinterpret_cast<const uint8_t*>(&one)!=1) return 5;
      EVP_DigestUpdate(ctx,fields,sizeof(fields));
    }
  }
  unsigned char hash[32]; unsigned size=0;
  EVP_DigestFinal_ex(ctx,hash,&size); EVP_MD_CTX_free(ctx);
  std::ostringstream digest;
  for (unsigned i=0;i<size;++i) digest << std::hex << std::setw(2) << std::setfill('0') << unsigned(hash[i]);
  std::cout << "{\"warp_records\":" << records << ",\"active_thread_instructions\":" << instructions
            << ",\"memory_records\":" << memory << ",\"consumer_memory_sha256\":\"" << digest.str() << "\"}\n";
  return records==13169524 && instructions==377291004 ? 0 : 6;
}
