// developed by Mahmoud Khairy, Purdue Univ

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <vector>
#include <unordered_map>
#ifndef TRACE_PARSER_H
#define TRACE_PARSER_H

#define WARP_SIZE 32
#define MAX_DST 8
#define MAX_SRC 24

enum command_type {
  kernel_launch = 1,
  cpu_gpu_mem_copy,
  gpu_cpu_mem_copy,
};

enum address_space { GLOBAL_MEM = 1, SHARED_MEM, LOCAL_MEM, TEX_MEM };

enum address_scope {
  L1_CACHE = 1,
  L2_CACHE,
  SYS_MEM,
};

enum address_format { list_all = 0, base_stride = 1, base_delta = 2 };

struct trace_command {
  std::string command_string;
  command_type m_type;
};

struct inst_memadd_info_t {
  uint64_t addrs[WARP_SIZE];
  int32_t width;

  void base_stride_decompress(unsigned long long base_address, int stride,
                              const std::bitset<WARP_SIZE> &mask);
  void base_delta_decompress(unsigned long long base_address,
                             const std::vector<long long> &deltas,
                             const std::bitset<WARP_SIZE> &mask);
};

struct inst_trace_t {
  inst_trace_t();
  inst_trace_t(const inst_trace_t &b);

  unsigned line_num;
  uint64_t m_pc;
  unsigned mask;
  unsigned reg_dsts_num;
  unsigned reg_dest[MAX_DST];
  std::string opcode;
  unsigned reg_srcs_num;
  unsigned reg_src[MAX_SRC];
  uint64_t imm;
  bool ada_typed=false;
  unsigned ada_active=0,ada_predicate=0;
  int ada_bank=-1,ada_offset=0;
  unsigned ada_regoffset=0;
  int ada_qualified=0;
  unsigned ada_constwidth=0;
  bool ada_aux=false;
  unsigned ada_capture_version=0,ada_control_kind=0;
  uint64_t ada_control_targets[32]={};
  uint64_t ada_constant_offsets[32]={};
  unsigned constant_context_ordinal=0;

  inst_memadd_info_t *memadd_info;

  bool parse_from_string(std::string trace, unsigned tracer_version,
                         unsigned enable_lineinfo);

  bool check_opcode_contain(const std::vector<std::string> &opcode,
                            std::string param) const;

  unsigned get_datawidth_from_opcode(
      const std::vector<std::string> &opcode) const;

  std::vector<std::string> get_opcode_tokens() const;

  ~inst_trace_t();
};

class PipeReader {
 public:
  PipeReader(const std::string &filePath);

  // Destructor to close the pipe
  ~PipeReader() {
    if (pipe) {
      pclose(pipe);  // Close the pipe when done
    }
  }

  // It does not make sense to implement copy semantics for PipeReader,
  // because each instance should hold a unique Linux pipe handle
  PipeReader(const PipeReader &) = delete;
  PipeReader &operator=(const PipeReader &) = delete;

  // Move semantics can be supported
  PipeReader(PipeReader &&) noexcept;
  PipeReader &operator=(PipeReader &&) noexcept;

  // Read one line
  bool readLine(std::string &line);
  void close_checked();

 private:
  FILE *pipe = NULL;    // Store the pipe
  std::string command;  // Store the shell command to be executed

  // Helper function to check if a string ends with a specific suffix (file
  // extension)
  bool hasEnding(const std::string &fullString, const std::string &ending);

  void OpenFile(const std::string &filePath);
};

struct kernel_trace_t {
  kernel_trace_t(const std::string &filePath);

  std::string kernel_name;
  unsigned kernel_id;
  unsigned grid_dim_x;
  unsigned grid_dim_y;
  unsigned grid_dim_z;
  unsigned tb_dim_x;
  unsigned tb_dim_y;
  unsigned tb_dim_z;
  unsigned shmem;
  unsigned nregs;
  unsigned long long cuda_stream_id;
  unsigned binary_verion;
  unsigned constant_context_ordinal=0;
  unsigned enable_lineinfo;
  unsigned trace_verion;
  std::string nvbit_verion;
  unsigned long long shmem_base_addr;
  unsigned long long local_base_addr;
  PipeReader pipeReader;
};

class trace_parser {
 public:
  struct BlockResult { bool present=false; unsigned x=0,y=0,z=0; uint64_t raw_records=0,call_issues=0,ret_issues=0,call_lanes=0,ret_lanes=0,exit_lanes=0; };
  BlockResult last_block;
  trace_parser() {}
  trace_parser(const char *kernellist_filepath);

  std::vector<trace_command> parse_commandlist_file();

  kernel_trace_t *parse_kernel_info(const std::string &kerneltraces_filepath);

  void parse_memcpy_info(const std::string &memcpy_command, size_t &add,
                         size_t &count);

  void get_next_threadblock_traces(
      std::vector<std::vector<inst_trace_t> *> threadblock_traces,
      unsigned trace_version, unsigned enable_lineinfo,
      class PipeReader &pipeReader, unsigned block_threads=0);

  void kernel_finalizer(kernel_trace_t *trace_info);

 private:
  std::string kernellist_filename;
  std::unordered_map<uint64_t,uint64_t> ada_function_bases;
  std::unordered_map<uint64_t,std::string> gaussian_owners;
  std::unordered_map<uint64_t,std::string> gaussian_opcodes;
};

#endif
