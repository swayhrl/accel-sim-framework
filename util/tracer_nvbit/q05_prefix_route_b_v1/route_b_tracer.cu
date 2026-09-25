/*
 * SPDX-FileCopyrightText: Copyright (c) 2019 NVIDIA CORPORATION & AFFILIATES.
 * All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <assert.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <map>
#include <regex>
#include <atomic>
#include <cerrno>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>

/* every tool needs to include this once */
#include "nvbit_tool.h"

/* nvbit interface file */
#include "nvbit.h"

// #define USE_ASYNC_STREAM
// NOTE: USE_ASYNC_STREAM version of channel.hpp can cause deadlock if two
// kernels have some dependency, since after each kernel launch, a device
// synchronization is needed for USE_ASYNC_STREAM version. Otherwise, the async
// copy in ChannelHost->recv() and a CUDA API call following a kernel launch
// can cause a deadlock, where the CUDA API call can take the CUDA context lock
// and waits for the kernel to finish, but the async copy in ChannelHost->recv()
// is waiting for the aforementioned CUDA context lock, thus stalling the kernel
// to finish (the instrumented kernel now needs to flush channel bufferto host
// side to finish by using the async copy).

/* for channel */
#include "utils/channel.hpp"

/* contains definition of the mem_access_t structure */
#include "common.h"
#include "route_b_raw_formatter.hpp"
#include "route_b_writer_state.hpp"

#define HEX(x)                                                            \
    "0x" << std::setfill('0') << std::setw(16) << std::hex << (uint64_t)x \
         << std::dec

#define CHANNEL_SIZE (1l << 20)

enum class RecvThreadState {
    INIT,
    WORKING,
    STOP,
    FINISHED,
};

struct CTXstate {
    /* context id */
    int id;

    /* Channel used to communicate from GPU to CPU receiving thread */
    ChannelDev* channel_dev;
    ChannelHost channel_host;

    /* tool module */
    CUmodule tool_module;

    /* flush channel function */
    CUfunction flush_channel_func;

    // Start with INIT, so that if no kernel is launched in the ctx, there is
    // no need to wait on the thread at the context termination.
    // After initialization, set it to WORKING to make recv thread get data,
    // parent thread sets it to STOP to make recv thread stop working.
    // recv thread sets it to FINISHED when it cleans up.
    // parent thread should wait until the state becomes FINISHED to clean up.
    volatile RecvThreadState recv_thread_done = RecvThreadState::INIT;
    // whether the context and the channel need a synchronization.
    bool need_sync = false;

    /* Route-B data-plane state only.  The official NVBit 1.7.7.1 channel,
     * receiver thread and STOP/FINISHED lifecycle above remain authoritative. */
    RouteBWriter raw_writer;
    std::string raw_dir;
    std::string raw_partial_path;
    std::string raw_final_path;
    std::string raw_kernelslist_path;
    std::string raw_kernelslist_member;
    uint64_t active_kernel_id = 0;
    CUfunction active_selected_function = nullptr;
    std::atomic<bool> raw_kernel_armed{false};
    bool device_finished = false;
    bool flush_finished = false;
    bool receiver_drained = false;
    bool terminal_complete = false;
    std::atomic<uint64_t> receiver_accepted{0};
    std::atomic<uint64_t> receiver_written{0};
    uint64_t device_reported = 0;
    uint64_t drop_count = 0;
    uint64_t overflow_count = 0;
};

#include "tool_func/flush_channel.c"

/* lock */
pthread_mutex_t mutex;
pthread_mutex_t cuda_event_mutex;

/* map to store context state */
std::unordered_map<CUcontext, CTXstate*> ctx_state_map;

/* skip flag used to avoid re-entry on the nvbit_callback when issuing
 * flush_channel kernel call */
bool skip_callback_flag = false;

/* global control variables for this tool */
uint32_t instr_begin_interval = 0;
uint32_t instr_end_interval = UINT32_MAX;
int verbose = 0;
int exact_root_function_only = 0;
int use_nvbit_static_index = 0;
int lineinfo = 0;
std::string route_b_raw_dir = "";
std::string route_b_selector_regex = ".*";
std::regex route_b_selector(".*");
int64_t route_b_selector_occurrence = -1;
uint64_t route_b_selector_seen = 0;
int64_t route_b_last_selector_ordinal = -1;
bool route_b_census_only = false;
std::atomic<bool> route_b_capture_terminal_complete{false};
/* Opt-in contiguous launch range.  Unset preserves accepted one-target mode. */
int64_t route_b_prefix_start = -1;
int64_t route_b_prefix_end = -1;

/* opcode to id map and reverse map  */
std::map<std::string, int> opcode_to_id_map;
std::map<int, std::string> id_to_opcode_map;

/* grid launch id, incremented at every launch */
uint64_t global_grid_launch_id = 0;

void* recv_thread_fun(void* args);

static bool route_b_select_function(const char* function_name) {
    if (!std::regex_search(function_name, route_b_selector)) {
        route_b_last_selector_ordinal = -1;
        return false;
    }
    const uint64_t occurrence = route_b_selector_seen++;
    route_b_last_selector_ordinal = static_cast<int64_t>(occurrence);
    if (route_b_census_only) return false;
    return route_b_selector_occurrence < 0 ||
           occurrence == static_cast<uint64_t>(route_b_selector_occurrence);
}

static std::string shell_quote(const std::string& value) {
    std::string quoted("'");
    for (char c : value) {
        if (c == '\'') quoted += "'\\\"'\\\"'";
        else quoted += c;
    }
    quoted += "'";
    return quoted;
}

static bool open_raw_writer(CUcontext ctx, CTXstate* state,
                            uint64_t kernel_id, const char* kernel_name,
                            unsigned grid_x, unsigned grid_y, unsigned grid_z,
                            unsigned block_x, unsigned block_y, unsigned block_z,
                            int nregs, int shmem, int binary_version,
                            uint64_t stream_id) {
    if (route_b_raw_dir.empty()) return true;
    if (state->raw_kernel_armed.load() ||
        (state->raw_writer.state != RouteBWriterState::UNOPENED &&
         state->raw_writer.state != RouteBWriterState::CLOSED)) {
        fprintf(stderr, "ROUTEB_RAW_WRITER_ERROR reason=multiple_active_kernel\n");
        return false;
    }
    try {
        std::filesystem::create_directories(route_b_raw_dir);
    } catch (const std::exception& error) {
        fprintf(stderr, "ROUTEB_RAW_WRITER_ERROR reason=mkdir detail=%s\n", error.what());
        return false;
    }
    char member[256];
    snprintf(member, sizeof(member), "kernel-%lu-ctx_0x%lx.trace.xz",
             kernel_id, (uint64_t)ctx);
    state->raw_dir = route_b_raw_dir;
    state->raw_kernelslist_path = state->raw_dir + "/kernelslist";
    state->raw_kernelslist_member = member;
    state->raw_final_path = state->raw_dir + "/" + member;
    state->raw_partial_path = state->raw_final_path + ".partial";
    std::string command = "xz -1 -T0 -c > " + shell_quote(state->raw_partial_path);
    state->raw_writer.handle = popen(command.c_str(), "w");
    if (state->raw_writer.handle == nullptr) {
        fprintf(stderr, "ROUTEB_RAW_WRITER_ERROR reason=popen errno=%d\n", errno);
        return false;
    }
    state->raw_writer.state = RouteBWriterState::OPEN;
    state->active_kernel_id = kernel_id;
    state->raw_kernel_armed.store(true, std::memory_order_release);
    state->device_finished = false;
    state->flush_finished = false;
    state->receiver_drained = false;
    state->terminal_complete = false;
    state->receiver_accepted.store(0);
    state->receiver_written.store(0);
    state->device_reported = 0;
    state->drop_count = 0;
    state->overflow_count = 0;
    fprintf(state->raw_writer.handle, "-kernel name = %s\n", kernel_name);
    fprintf(state->raw_writer.handle, "-kernel id = %lu\n", kernel_id);
    fprintf(state->raw_writer.handle, "-grid dim = (%u,%u,%u)\n", grid_x, grid_y, grid_z);
    fprintf(state->raw_writer.handle, "-block dim = (%u,%u,%u)\n", block_x, block_y, block_z);
    fprintf(state->raw_writer.handle, "-shmem = %d\n", shmem);
    fprintf(state->raw_writer.handle, "-nregs = %d\n", nregs);
    fprintf(state->raw_writer.handle, "-binary version = %d\n", binary_version);
    fprintf(state->raw_writer.handle, "-cuda stream id = %lu\n", stream_id);
    fprintf(state->raw_writer.handle, "-shmem base_addr = 0x%016lx\n", (uint64_t)nvbit_get_shmem_base_addr(ctx));
    fprintf(state->raw_writer.handle, "-local mem base_addr = 0x%016lx\n", (uint64_t)nvbit_get_local_mem_base_addr(ctx));
    fprintf(state->raw_writer.handle, "-nvbit version = %s\n", NVBIT_VERSION);
    fprintf(state->raw_writer.handle, "-accelsim tracer version = 5\n");
    fprintf(state->raw_writer.handle, "-enable lineinfo = %d\n\n", lineinfo);
    fprintf(state->raw_writer.handle,
            "#traces format = [line_num] PC mask dest_num [reg_dests] opcode src_num [reg_srcs] mem_width [adrrescompress?] [mem_addresses] immediate\n\n");
    return true;
}

static bool close_raw_writer_after_terminal(CTXstate* state) {
    if (!state->raw_kernel_armed.load(std::memory_order_acquire) || state->raw_writer.state != RouteBWriterState::TERMINAL_ACKED) return false;
    if (pclose(state->raw_writer.handle) != 0) {
        fprintf(stderr, "ROUTEB_RAW_WRITER_ERROR reason=xz_close\n");
        state->raw_writer.handle = nullptr;
        return false;
    }
    state->raw_writer.handle = nullptr;
    if (rename(state->raw_partial_path.c_str(), state->raw_final_path.c_str()) != 0) {
        fprintf(stderr, "ROUTEB_RAW_WRITER_ERROR reason=rename errno=%d\n", errno);
        return false;
    }
    std::ofstream kernels(state->raw_kernelslist_path, std::ios::app);
    if (!kernels) {
        fprintf(stderr, "ROUTEB_RAW_WRITER_ERROR reason=kernelslist_open\n");
        return false;
    }
    kernels << state->raw_kernelslist_member << '\n';
    kernels.close();
    state->raw_writer.state = RouteBWriterState::CLOSED;
    fprintf(stdout, "ROUTEB_LIFECYCLE trace_sink_closed kernel=%lu raw=%s\n",
            state->active_kernel_id, state->raw_final_path.c_str());
    fflush(stdout);
    state->terminal_complete = true;
    /* The sole selected target is terminally closed.  Subsequent workload
     * kernels are outside the capture selector and must execute unchanged,
     * but no longer need to re-enter the tracer callback. */
    const bool final_member = route_b_prefix_end < 0 ||
        state->active_kernel_id == static_cast<uint64_t>(route_b_prefix_end);
    if (final_member) route_b_capture_terminal_complete.store(true, std::memory_order_release);
    fprintf(stdout,
            "ROUTEB_TERMINAL_COMPLETE kernel=%lu device_reported=%lu receiver_accepted=%lu raw_records=%lu drop_count=%lu overflow_count=%lu raw=%s\n",
            state->active_kernel_id, state->device_reported,
            state->receiver_accepted.load(), state->receiver_written.load(),
            state->drop_count, state->overflow_count, state->raw_final_path.c_str());
    fflush(stdout);
    return true;
}

void nvbit_at_init() {
    GET_VAR_INT(
        instr_begin_interval, "INSTR_BEGIN", 0,
        "Beginning of the instruction interval where to apply instrumentation");
    GET_VAR_INT(
        instr_end_interval, "INSTR_END", UINT32_MAX,
        "End of the instruction interval where to apply instrumentation");
    GET_VAR_INT(verbose, "TOOL_VERBOSE", 0, "Enable verbosity inside the tool");
    const char* raw_dir = getenv("ROUTE_B_RAW_DIR");
    if (raw_dir != nullptr) route_b_raw_dir = raw_dir;
    const char* selector = getenv("ROUTE_B_FUNCTION_REGEX");
    if (selector != nullptr && *selector != '\0') route_b_selector_regex = selector;
    try {
        route_b_selector = std::regex(route_b_selector_regex);
    } catch (const std::regex_error& error) {
        fprintf(stderr, "ROUTEB_SELECTOR_ERROR regex=%s detail=%s\n",
                route_b_selector_regex.c_str(), error.what());
        abort();
    }
    const char* occurrence = getenv("ROUTE_B_FUNCTION_OCCURRENCE");
    if (occurrence != nullptr && *occurrence != '\0') {
        route_b_selector_occurrence = strtoll(occurrence, nullptr, 10);
        if (route_b_selector_occurrence < 0) abort();
    }
    const char* census = getenv("ROUTE_B_LAUNCH_CENSUS_ONLY");
    route_b_census_only = census != nullptr && std::string(census) == "1";
    const char* prefix_start = getenv("ROUTE_B_PREFIX_START");
    const char* prefix_end = getenv("ROUTE_B_PREFIX_END");
    if ((prefix_start == nullptr) != (prefix_end == nullptr)) abort();
    if (prefix_start != nullptr) {
        route_b_prefix_start = strtoll(prefix_start, nullptr, 10);
        route_b_prefix_end = strtoll(prefix_end, nullptr, 10);
        if (route_b_prefix_start < 0 || route_b_prefix_end < route_b_prefix_start) abort();
    }
    route_b_capture_terminal_complete.store(false, std::memory_order_release);
    if (!route_b_census_only) {
        setenv("CUDA_MANAGED_FORCE_DEVICE_ALLOC", "1", 1);
    }
    std::string pad(100, '-');
    printf("%s\n", pad.c_str());

    /* set mutex as recursive */
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_RECURSIVE);
    pthread_mutex_init(&mutex, &attr);

    pthread_mutex_init(&cuda_event_mutex, &attr);
}

/* Set used to avoid re-instrumenting the same functions multiple times */
std::unordered_set<CUfunction> already_instrumented;

void instrument_function_if_needed(CUcontext ctx, CUfunction func) {
  CTXstate* ctx_state = ctx_state_map.at(ctx);
  std::vector<CUfunction> related_functions;
  if (exact_root_function_only) {
    /* The Route-E static-map receipt names this root function, not callees. */
    related_functions.push_back(func);
  } else {
    related_functions = nvbit_get_related_functions(ctx, func);
    /* add kernel itself to the related function vector */
    related_functions.push_back(func);
  }

  /* iterate on function */
  for (auto f : related_functions) {
    /* "recording" function was instrumented, if set insertion failed
     * we have already encountered this function */
    if (!already_instrumented.insert(f).second) {
      continue;
    }

    const std::vector<Instr *> &instrs = nvbit_get_instrs(ctx, f);
    if (verbose >= 1) {
      printf("Inspecting function %s at address 0x%lx\n",
             nvbit_get_func_name(ctx, f), nvbit_get_func_addr(ctx, f));
    }

    uint32_t cnt = 0;
    /* iterate on all the static instructions in the function */
    for (auto instr : instrs) {
      uint32_t line_num = 0;
      // Temporary workaround for a bug in NVBit 1.7.4, which does not correctly
      // handle `call.rel`. Instrumenting this instruction leads to illegal
      // memory access. Refer to:
      // https://github.com/NVlabs/NVBit/issues/142#issue-2911561744
      if (!strcmp(instr->getOpcode(), "CALL.REL.NOINC")) {
        printf("Warning: Ignoring CALL.REL.NOINC (NVBit 1.7.4 bug)\n");
        continue;
      }

      uint32_t selection_index =
          use_nvbit_static_index ? (uint32_t)instr->getIdx() : cnt;
      if (selection_index < instr_begin_interval ||
          selection_index >= instr_end_interval) {
        cnt++;
        continue;
      }

      if (verbose >= 2) {
        instr->printDecoded();
      }

      if (lineinfo) {
        char *file_name, *dir_name;
        nvbit_get_line_info(ctx, func, instr->getOffset(), &file_name,
                            &dir_name, &line_num);
      }

      if (opcode_to_id_map.find(instr->getOpcode()) == opcode_to_id_map.end()) {
        int opcode_id = opcode_to_id_map.size();
        opcode_to_id_map[instr->getOpcode()] = opcode_id;
        id_to_opcode_map[opcode_id] = instr->getOpcode();
      }

      int opcode_id = opcode_to_id_map[instr->getOpcode()];

      /* check all operands. For now, we ignore constant, TEX, predicates and
       * unified registers. We only report vector regisers */
      int src_oprd[MAX_SRC];
      int srcNum = 0;
      int dst_oprd = -1;
      int mem_oper_idx = -1;
      int num_mref = 0;
      uint64_t imm_value = 0;

      for (int i = 0; i < instr->getNumOperands(); ++i) {
        const InstrType::operand_t *op = instr->getOperand(i);
        if (op->type == InstrType::OperandType::MREF) {
          assert(srcNum < MAX_SRC);
          src_oprd[srcNum] = instr->getOperand(i)->u.mref.ra_num;
          srcNum++;
          mem_oper_idx++;
          num_mref++;
          // if(mem_oper_idx == 0){
          //   mem_oper_idx = 1; // loop control
          // }
        } else if (op->type == InstrType::OperandType::REG) {
          if (i == 0) {
            // find dst reg
            dst_oprd = instr->getOperand(0)->u.reg.num;
          } else {
            // find src regs
            assert(srcNum < MAX_SRC);
            src_oprd[srcNum] = instr->getOperand(i)->u.reg.num;
            srcNum++;
          }
        }
        // Add immediate value for DEPBAR instruction
        else if (op->type == InstrType::OperandType::IMM_UINT64) {
          imm_value = instr->getOperand(i)->u.imm_uint64.value;
        }
      }

      do {
        /* insert call to the instrumentation function with its
         * arguments */
        nvbit_insert_call(instr, "instrument_inst", IPOINT_BEFORE);

        /* pass predicate value */
        nvbit_add_call_arg_guard_pred_val(instr);

        /* send opcode and pc */
        nvbit_add_call_arg_const_val32(instr, opcode_id);
        nvbit_add_call_arg_const_val32(instr, (int)instr->getOffset());

        /* mem addresses info */
        if (mem_oper_idx >= 0) {
          nvbit_add_call_arg_const_val32(instr, 1);
          assert(num_mref <= 2);
          if (num_mref == 2) { // LDGSTS
            nvbit_add_call_arg_mref_addr64(instr, 1 - mem_oper_idx);
          } else {
            nvbit_add_call_arg_mref_addr64(instr, mem_oper_idx);
          }
          nvbit_add_call_arg_const_val32(instr, (int)instr->getSize());
        } else {
          nvbit_add_call_arg_const_val32(instr, 0);
          nvbit_add_call_arg_const_val64(instr, static_cast<uint64_t>(-1));
          nvbit_add_call_arg_const_val32(instr, static_cast<uint32_t>(-1));
        }

        /* reg info */
        nvbit_add_call_arg_const_val32(instr, dst_oprd);
        for (int i = 0; i < srcNum; i++) {
          nvbit_add_call_arg_const_val32(instr, src_oprd[i]);
        }
        for (int i = srcNum; i < MAX_SRC; i++) {
          nvbit_add_call_arg_const_val32(instr, static_cast<uint32_t>(-1));
        }
        nvbit_add_call_arg_const_val32(instr, srcNum);

        /* immediate info */
        nvbit_add_call_arg_const_val64(instr, imm_value);

        /* add pointer to channel_dev and other counters*/
        nvbit_add_call_arg_const_val64(instr, (uint64_t)ctx_state->channel_dev);
        nvbit_add_call_arg_const_val64(instr,
                                       (uint64_t)&total_dynamic_instr_counter);
        nvbit_add_call_arg_const_val64(
            instr, (uint64_t)&reported_dynamic_instr_counter);
        nvbit_add_call_arg_const_val64(instr, (uint64_t)&stop_report);
        /* Add Source code line number for current instr */
        nvbit_add_call_arg_const_val32(instr, (int)line_num);
        /* Add instruction index for current instr (spinlock detection) */
        nvbit_add_call_arg_const_val32(instr, (uint32_t)instr->getIdx());

        mem_oper_idx--;
      } while (mem_oper_idx >= 0);

      cnt++;
    }
  }
}


void init_context_state(CUcontext ctx) {
    CTXstate* ctx_state = ctx_state_map[ctx];
    ctx_state->recv_thread_done = RecvThreadState::WORKING;
    cudaMallocManaged(&ctx_state->channel_dev, sizeof(ChannelDev));
    ctx_state->channel_host.init((int)ctx_state_map.size() - 1, CHANNEL_SIZE,
                                 ctx_state->channel_dev, recv_thread_fun, ctx);
    nvbit_set_tool_pthread(ctx_state->channel_host.get_thread());
}

static void enter_kernel_launch(CUcontext ctx, CUfunction func,
                uint64_t &grid_launch_id, nvbit_api_cuda_t cbid, void* params,
                bool stream_capture = false, bool build_graph = false) {
    /* Q05 launch census is intentionally payload-free: it needs only launch
     * geometry and exact root-name/occurrence binding.  Avoid CUDA/NVBit
     * static queries from inside the callback on the 1.7.7.1 runtime. */
    if (route_b_census_only) {
        const char* census_name = nvbit_get_func_name(ctx, func);
        const bool selected = route_b_select_function(census_name);
        unsigned grid_x = 0, grid_y = 0, grid_z = 0;
        unsigned block_x = 0, block_y = 0, block_z = 0;
        uint64_t stream_id = 0;
        if (cbid == API_CUDA_cuLaunchKernelEx_ptsz || cbid == API_CUDA_cuLaunchKernelEx) {
            cuLaunchKernelEx_params* p = (cuLaunchKernelEx_params*)params;
            grid_x = p->config->gridDimX; grid_y = p->config->gridDimY; grid_z = p->config->gridDimZ;
            block_x = p->config->blockDimX; block_y = p->config->blockDimY; block_z = p->config->blockDimZ;
            stream_id = (uint64_t)p->config->hStream;
        } else {
            cuLaunchKernel_params* p = (cuLaunchKernel_params*)params;
            grid_x = p->gridDimX; grid_y = p->gridDimY; grid_z = p->gridDimZ;
            block_x = p->blockDimX; block_y = p->blockDimY; block_z = p->blockDimZ;
            stream_id = (uint64_t)p->hStream;
        }
        if (!stream_capture && !build_graph) {
            printf("ROUTEB_CENSUS_LAUNCH grid_launch_id=%lu function=%s grid=%u,%u,%u block=%u,%u,%u stream=%lu\n",
                   grid_launch_id, census_name, grid_x, grid_y, grid_z,
                   block_x, block_y, block_z, stream_id);
            if (route_b_last_selector_ordinal >= 0) {
                printf("ROUTEB_SELECTOR_CANDIDATE grid_launch_id=%lu selector_occurrence=%ld selected=%d function=%s\n",
                       grid_launch_id, route_b_last_selector_ordinal,
                       selected ? 1 : 0, census_name);
            }
            fflush(stdout);
            grid_launch_id++;
        }
        stop_report = true;
        return;
    }

    /* Resolve the root selector before any static query.  Q05 has tens of
     * thousands of unselected launches; they must advance launch identity but
     * must not cause NVBit attribute/disassembly work or payload activity. */
    const char* func_name = nvbit_get_func_name(ctx, func);
    const bool prefix_mode = route_b_prefix_start >= 0;
    bool selected = prefix_mode
        ? (grid_launch_id >= static_cast<uint64_t>(route_b_prefix_start) &&
           grid_launch_id <= static_cast<uint64_t>(route_b_prefix_end))
        : route_b_select_function(func_name);
    if (prefix_mode) route_b_last_selector_ordinal = selected ? static_cast<int64_t>(grid_launch_id) : -1;
    if (!selected) {
        stop_report = true;
        if (!stream_capture && !build_graph) grid_launch_id++;
        return;
    }

    int nregs = 0;
    CUDA_SAFECALL(
        cuFuncGetAttribute(&nregs, CU_FUNC_ATTRIBUTE_NUM_REGS, func));

    int shmem_static_nbytes = 0;
    CUDA_SAFECALL(
        cuFuncGetAttribute(&shmem_static_nbytes,
                           CU_FUNC_ATTRIBUTE_SHARED_SIZE_BYTES, func));

    int binary_version = 0;
    CUDA_SAFECALL(
        cuFuncGetAttribute(&binary_version, CU_FUNC_ATTRIBUTE_BINARY_VERSION, func));

    /* Selected root only: obtain static instruction identity and metadata. */
    uint64_t pc = nvbit_get_func_addr(ctx, func);

    unsigned grid_x = 0, grid_y = 0, grid_z = 0;
    unsigned block_x = 0, block_y = 0, block_z = 0;
    unsigned shared_mem = 0;
    uint64_t stream_id = 0;
    if (cbid == API_CUDA_cuLaunchKernelEx_ptsz || cbid == API_CUDA_cuLaunchKernelEx) {
        cuLaunchKernelEx_params* p = (cuLaunchKernelEx_params*)params;
        grid_x = p->config->gridDimX; grid_y = p->config->gridDimY; grid_z = p->config->gridDimZ;
        block_x = p->config->blockDimX; block_y = p->config->blockDimY; block_z = p->config->blockDimZ;
        shared_mem = p->config->sharedMemBytes; stream_id = (uint64_t)p->config->hStream;
    } else {
        cuLaunchKernel_params* p = (cuLaunchKernel_params*)params;
        grid_x = p->gridDimX; grid_y = p->gridDimY; grid_z = p->gridDimZ;
        block_x = p->blockDimX; block_y = p->blockDimY; block_z = p->blockDimZ;
        shared_mem = p->sharedMemBytes; stream_id = (uint64_t)p->hStream;
    }

    // during stream capture or manual graph build, no kernel is launched, so
    // do not set launch argument, do not print kernel info, do not increase
    // grid_launch_id. All these should be done at graph node launch time.
    if (!stream_capture && !build_graph) {
        /* set grid launch id at launch time */
        if (selected) nvbit_set_at_launch(ctx, func, (uint64_t)grid_launch_id);

        if (selected && !route_b_raw_dir.empty()) {
            /* The device counter is passed to instrument_inst; after the
             * explicit flush it is the source-backed expected packet count. */
            CUDA_SAFECALL(cudaDeviceSynchronize());
            total_dynamic_instr_counter = 0;
            reported_dynamic_instr_counter = 0;
            stop_report = false;
            CTXstate* state = ctx_state_map.at(ctx);
            bool opened = open_raw_writer(ctx, state, grid_launch_id, func_name,
                                          grid_x, grid_y, grid_z,
                                          block_x, block_y, block_z, nregs,
                                          shmem_static_nbytes + shared_mem, binary_version,
                                          stream_id);
            if (!opened) {
                fprintf(stderr, "ROUTEB_RAW_WRITER_ERROR reason=open_failed\n");
                abort();
            }
            state->active_selected_function = func;
        }

        if (cbid == API_CUDA_cuLaunchKernelEx_ptsz ||
            cbid == API_CUDA_cuLaunchKernelEx) {
            cuLaunchKernelEx_params* p = (cuLaunchKernelEx_params*)params;
            printf(
                "MEMTRACE: CTX 0x%016lx - LAUNCH - Kernel pc 0x%016lx - "
                "Kernel name %s - grid launch id %ld - grid size %d,%d,%d "
                "- block size %d,%d,%d - nregs %d - shmem %d - cuda stream "
                "id %ld\n",
                (uint64_t)ctx, pc, func_name, grid_launch_id,
                p->config->gridDimX, p->config->gridDimY,
                p->config->gridDimZ, p->config->blockDimX,
                p->config->blockDimY, p->config->blockDimZ, nregs,
                shmem_static_nbytes + p->config->sharedMemBytes,
                (uint64_t)p->config->hStream);
        } else {
            cuLaunchKernel_params* p = (cuLaunchKernel_params*)params;
            printf(
                "MEMTRACE: CTX 0x%016lx - LAUNCH - Kernel pc 0x%016lx - "
                "Kernel name %s - grid launch id %ld - grid size %d,%d,%d "
                "- block size %d,%d,%d - nregs %d - shmem %d - cuda stream "
                "id %ld\n",
                (uint64_t)ctx, pc, func_name, grid_launch_id, p->gridDimX,
                p->gridDimY, p->gridDimZ, p->blockDimX, p->blockDimY,
                p->blockDimZ, nregs,
                shmem_static_nbytes + p->sharedMemBytes,
                (uint64_t)p->hStream);
        }
        fflush(stdout);

        // increment grid launch id for next launch
        // grid id can be changed here, since nvbit_set_at_launch() has copied
        // its value above.
        if (route_b_last_selector_ordinal >= 0) {
            printf("ROUTEB_SELECTOR_CANDIDATE grid_launch_id=%lu selector_occurrence=%ld selected=%d function=%s\n",
                   grid_launch_id, route_b_last_selector_ordinal, selected ? 1 : 0,
                   func_name);
        }
        grid_launch_id++;
    }

    /* Instrument only the selected root.  This is intentionally after the
     * selector decision so Q05 re-resolution does not create a broad packet
     * stream merely to enumerate launches. */
    instrument_function_if_needed(ctx, func);

    /* enable instrumented code to run */
    stop_report = false;
    nvbit_enable_instrumented(ctx, func, true);

}

static void leave_kernel_launch(CUcontext ctx, CTXstate *ctx_state) {
#ifdef ROUTE_B_NVBIT175_CENSUS
    (void)ctx;
    (void)ctx_state;
    return;
#else
    if (route_b_raw_dir.empty() || !ctx_state->raw_kernel_armed.load(std::memory_order_acquire)) return;
    /* This is the official explicit flush-module path.  No old tracer flag
     * participates: completion is a device-side reported packet count that
     * the receiver must drain before the xz sink is allowed to close. */
    cudaDeviceSynchronize();
    assert(cudaGetLastError() == cudaSuccess);
    ctx_state->device_finished = true;
    fprintf(stdout, "ROUTEB_LIFECYCLE device_kernel_complete kernel=%lu\n",
            ctx_state->active_kernel_id);
    fflush(stdout);
    /* push a flush channel kernel */
    void* args[] = {&ctx_state->channel_dev};
    nvbit_launch_kernel(ctx, ctx_state->flush_channel_func,
                        1, 1, 1, 1, 1, 1, 0, nullptr, args,
                        nullptr);
    /* Make sure GPU is idle */
    cudaDeviceSynchronize();
    assert(cudaGetLastError() == cudaSuccess);
    ctx_state->flush_finished = true;
    fprintf(stdout, "ROUTEB_LIFECYCLE channel_flush_complete kernel=%lu\n",
            ctx_state->active_kernel_id);
    fflush(stdout);
    ctx_state->device_reported = reported_dynamic_instr_counter;
    /* accepted is advanced immediately before written in recv_thread_fun.
     * Waiting on accepted alone leaves a narrow false-reject window where the
     * final fputs succeeded but receiver_written has not yet been published.
     * Both counters are part of the serialized terminal contract. */
    while (ctx_state->receiver_accepted.load(std::memory_order_acquire) <
               ctx_state->device_reported ||
           ctx_state->receiver_written.load(std::memory_order_acquire) <
               ctx_state->device_reported) {
        pthread_yield();
    }
    const uint64_t receiver_accepted =
        ctx_state->receiver_accepted.load(std::memory_order_acquire);
    const uint64_t receiver_written =
        ctx_state->receiver_written.load(std::memory_order_acquire);
    if (receiver_accepted != ctx_state->device_reported ||
        receiver_written != ctx_state->device_reported ||
        ctx_state->drop_count != 0 || ctx_state->overflow_count != 0) {
        fprintf(stderr,
                "ROUTEB_TERMINAL_REJECT device_reported=%lu receiver_accepted=%lu raw_records=%lu drop_count=%lu overflow_count=%lu\n",
                ctx_state->device_reported, receiver_accepted,
                receiver_written, ctx_state->drop_count, ctx_state->overflow_count);
        abort();
    }
    ctx_state->receiver_drained = true;
    fprintf(stdout,
            "ROUTEB_LIFECYCLE receiver_fully_drained kernel=%lu expected=%lu accepted=%lu\n",
            ctx_state->active_kernel_id, ctx_state->device_reported,
            ctx_state->receiver_accepted.load());
    fflush(stdout);
    ctx_state->raw_writer.state = RouteBWriterState::TERMINAL_ACKED;
    if (!close_raw_writer_after_terminal(ctx_state)) abort();
    if (ctx_state->active_selected_function != nullptr) {
        /* The exact target has terminally closed.  Disable its injected calls
         * before the same process continues with unselected Decode32 work. */
        nvbit_enable_instrumented(ctx, ctx_state->active_selected_function, false);
        ctx_state->active_selected_function = nullptr;
    }
    ctx_state->raw_kernel_armed.store(false, std::memory_order_release);
#endif
}

void nvbit_at_cuda_event(CUcontext ctx, int is_exit, nvbit_api_cuda_t cbid,
                         const char* name, void* params, CUresult* pStatus) {
    if (!route_b_census_only &&
        route_b_capture_terminal_complete.load(std::memory_order_acquire)) {
        return;
    }
    pthread_mutex_lock(&cuda_event_mutex);

    /* we prevent re-entry on this callback when issuing CUDA functions inside
     * this function */
    if (skip_callback_flag) {
        pthread_mutex_unlock(&cuda_event_mutex);
        return;
    }
    skip_callback_flag = true;

    CTXstate* ctx_state = ctx_state_map[ctx];

    switch (cbid) {
        // Identify all the possible CUDA launch events without stream
        // parameters, they will not get involved with cuda graph
        case API_CUDA_cuLaunch:
        case API_CUDA_cuLaunchGrid:
            {
                cuLaunch_params *p = (cuLaunch_params *)params;
                CUfunction func = p->f;
                if (!is_exit) {
                    if (!route_b_census_only) ctx_state->need_sync = true;
                    enter_kernel_launch(ctx, func, global_grid_launch_id, cbid,
                                        params);
                } else {
                    leave_kernel_launch(ctx, ctx_state);
                }
            } break;
        // To support kernel launched by cuda graph (in addition to existing kernel
        // launche method), we need to do:
        //
        // 1. instrument kernels at cudaGraphAddKernelNode event. This is for cases
        // that kernels are manually added to a cuda graph.
        // 2. distinguish captured kernels when kernels are recorded to a graph
        // using stream capture. cudaStreamIsCapturing() tells us whether a stream
        // is capturiong.
        // 3. per-kernel instruction counters, since cuda graph can launch multiple
        // kernels at the same time.
        //
        // Three cases:
        //
        // 1. original kernel launch:
        //     1a. for any kernel launch without using a stream, we instrument it
        //     before it is launched, call cudaDeviceSynchronize after it is
        //     launched and read the instruction counter of the kernel.
        //     1b. for any kernel launch using a stream, but the stream is not
        //     capturing, we do the same thing as 1a.
        //
        //  2. cuda graph using stream capturing: if a kernel is launched in a
        //  stream and the stream is capturing. We instrument the kernel before it
        //  is launched and do nothing after it is launched, because the kernel is
        //  not running until cudaGraphLaunch. Instead, we issue a
        //  cudaStreamSynchronize after cudaGraphLaunch is done and reset the
        //  instruction counters, since a cloned graph might be launched afterwards.
        //
        //  3. cuda graph manual: we instrument the kernel added by
        //  cudaGraphAddKernelNode and do the same thing for cudaGraphLaunch as 2.
        //
        // The above method should handle most of cuda graph launch cases.
        // kernel launches with stream parameter, they can be used for cuda graph
        case API_CUDA_cuLaunchKernel_ptsz:
        case API_CUDA_cuLaunchKernel:
        case API_CUDA_cuLaunchCooperativeKernel:
        case API_CUDA_cuLaunchCooperativeKernel_ptsz:
        case API_CUDA_cuLaunchKernelEx:
        case API_CUDA_cuLaunchKernelEx_ptsz:
        case API_CUDA_cuLaunchGridAsync:
            {
                CUfunction func;
                CUstream hStream;

                if (cbid == API_CUDA_cuLaunchKernelEx_ptsz ||
                    cbid == API_CUDA_cuLaunchKernelEx) {
                    cuLaunchKernelEx_params* p =
                        (cuLaunchKernelEx_params*)params;
                    func = p->f;
                    hStream = p->config->hStream;
                } else if (cbid == API_CUDA_cuLaunchKernel_ptsz ||
                           cbid == API_CUDA_cuLaunchKernel ||
                           cbid == API_CUDA_cuLaunchCooperativeKernel_ptsz ||
                           cbid == API_CUDA_cuLaunchCooperativeKernel) {
                    cuLaunchKernel_params* p = (cuLaunchKernel_params*)params;
                    func = p->f;
                    hStream = p->hStream;
                } else {
                    cuLaunchGridAsync_params* p =
                        (cuLaunchGridAsync_params*)params;
                    func = p->f;
                    hStream = p->hStream;
                }

                if (!is_exit) {
                    if (route_b_census_only) {
                        enter_kernel_launch(ctx, func, global_grid_launch_id, cbid,
                                            params, false);
                    } else {
                        cudaStreamCaptureStatus streamStatus;
                        /* check if the stream is capturing, if yes, do not sync */
                        CUDA_SAFECALL(cudaStreamIsCapturing(hStream, &streamStatus));
                        bool stream_capture = (streamStatus == cudaStreamCaptureStatusActive);
                        ctx_state->need_sync = true;
                        enter_kernel_launch(ctx, func, global_grid_launch_id, cbid, params, stream_capture);
                    }
                } else {
                    if (route_b_census_only) {
                        /* no payload/capture lifecycle in census mode */
                    } else {
                        cudaStreamCaptureStatus streamStatus;
                        CUDA_SAFECALL(cudaStreamIsCapturing(hStream, &streamStatus));
                        if (streamStatus != cudaStreamCaptureStatusActive) {
                        if (verbose >= 1) {
                            printf("kernel %s not captured by cuda graph\n", nvbit_get_func_name(ctx, func));
                        }
                        leave_kernel_launch(ctx, ctx_state);
                        } else {
                        if (verbose >= 1) {
                            printf("kernel %s captured by cuda graph\n", nvbit_get_func_name(ctx, func));
                        }
                        }
                    }
                }
            } break;
        case API_CUDA_cuGraphAddKernelNode:
            {
                cuGraphAddKernelNode_params *p = (cuGraphAddKernelNode_params *)params;
                CUfunction func = p->nodeParams->func;

                if (!is_exit) {
                    // cuGraphAddKernelNode_params->nodeParams is the same as
                    // cuLaunchKernel_params up to sharedMemBytes
                    if (!route_b_census_only) ctx_state->need_sync = true;
                    enter_kernel_launch(ctx, func, global_grid_launch_id, cbid, (void*)p->nodeParams, false, true);
                } 
            } break;
        default:
            break;
    };


    skip_callback_flag = false;
    pthread_mutex_unlock(&cuda_event_mutex);
}

void* recv_thread_fun(void* args) {
    CUcontext ctx = (CUcontext)args;
    pthread_mutex_lock(&mutex);
    CTXstate* ctx_state = ctx_state_map.at(ctx);
    ChannelHost* ch_host = &ctx_state->channel_host;
    pthread_mutex_unlock(&mutex);
    char* recv_buffer = (char*)malloc(CHANNEL_SIZE);
    while (ctx_state->recv_thread_done == RecvThreadState::WORKING) {
        uint32_t n = ch_host->recv(recv_buffer, CHANNEL_SIZE);
        for (uint32_t off = 0; off < n; off += sizeof(inst_trace_t)) {
            inst_trace_t* ma = (inst_trace_t*)&recv_buffer[off];
            if (ctx_state->raw_kernel_armed.load(std::memory_order_acquire)) {
                std::optional<std::string> raw =
                    route_b_raw::format(*ma, id_to_opcode_map, lineinfo != 0, true);
                if (!raw.has_value()) {
                    ++ctx_state->drop_count;
                    continue;
                }
                if (fputs(raw->c_str(), ctx_state->raw_writer.handle) < 0) {
                    ++ctx_state->drop_count;
                    continue;
                }
                ctx_state->receiver_accepted.fetch_add(1, std::memory_order_relaxed);
                ctx_state->receiver_written.fetch_add(1, std::memory_order_relaxed);
            } else if (verbose) {
                printf("ACCELSIM_PACKET CTX %p CTA %d,%d,%d WARP %d PC 0x%x OPCODE %d\n",
                       ctx, ma->cta_id_x, ma->cta_id_y, ma->cta_id_z,
                       ma->warpid_tb, ma->vpc, ma->opcode_id);
            }
        }
    }
    free(recv_buffer);
    ctx_state->recv_thread_done = RecvThreadState::FINISHED;
    return NULL;
}

void nvbit_at_ctx_init(CUcontext ctx) {
    pthread_mutex_lock(&mutex);
    if (verbose) {
        printf("MEMTRACE: STARTING CONTEXT %p\n", ctx);
    }
    assert(ctx_state_map.find(ctx) == ctx_state_map.end());
    CTXstate* ctx_state = new CTXstate;
    ctx_state_map[ctx] = ctx_state;

    if (!route_b_census_only) {
#ifndef ROUTE_B_NVBIT175_CENSUS
        nvbit_load_tool_module(ctx, (const void*)flush_channel_bin,
                               &ctx_state->tool_module);
        nvbit_find_function_by_name(ctx, ctx_state->tool_module, "flush_channel",
                                    &ctx_state->flush_channel_func);
#endif
    }

    pthread_mutex_unlock(&mutex);
}

void nvbit_tool_init(CUcontext ctx) {
    pthread_mutex_lock(&mutex);
    assert(ctx_state_map.find(ctx) != ctx_state_map.end());
    /* Launch census has no selected instruction payload.  Avoid allocating a
     * managed data channel solely to observe CUDA launch identities; the full
     * official per-context channel/receiver path remains mandatory whenever a
     * Route-B capture is armed. */
    if (!route_b_census_only) init_context_state(ctx);
    pthread_mutex_unlock(&mutex);
}

void nvbit_at_ctx_term(CUcontext ctx) {
    pthread_mutex_lock(&mutex);
    skip_callback_flag = true;
    if (verbose) {
        printf("MEMTRACE: TERMINATING CONTEXT %p\n", ctx);
    }
    /* get context state from map */
    assert(ctx_state_map.find(ctx) != ctx_state_map.end());
    CTXstate* ctx_state = ctx_state_map[ctx];

    // flush channel if there is a kernel launch before context termination
    // without a device synchronization.
    if (ctx_state->channel_dev != nullptr && ctx_state->need_sync) {
#ifndef ROUTE_B_NVBIT175_CENSUS
        void* args[] = {&ctx_state->channel_dev};
        nvbit_launch_kernel(ctx, ctx_state->flush_channel_func,
                            1, 1, 1, 1, 1, 1, 0, nullptr, args,
                            nullptr);
        cudaDeviceSynchronize();
        assert(cudaGetLastError() == cudaSuccess);
#endif
    }

    /* Notify receiver thread and wait for receiver thread to
     * notify back */
    if (ctx_state->recv_thread_done != RecvThreadState::INIT) {
        ctx_state->recv_thread_done = RecvThreadState::STOP;
        while (ctx_state->recv_thread_done != RecvThreadState::FINISHED)
            ;
    }

    if (ctx_state->channel_dev != nullptr) {
        ctx_state->channel_host.destroy(false);
        cudaFree(ctx_state->channel_dev);
    }
    skip_callback_flag = false;
    delete ctx_state;
    pthread_mutex_unlock(&mutex);
}

void nvbit_at_graph_node_launch(CUcontext ctx, CUfunction func,
                                          CUstream stream,
                                          uint64_t launch_handle) {
    func_config_t config = {0};
    const char* func_name = nvbit_get_func_name(ctx, func);
    uint64_t pc = nvbit_get_func_addr(ctx, func);

    pthread_mutex_lock(&mutex);
    nvbit_set_at_launch(ctx, func, (uint64_t)global_grid_launch_id, stream,
                        launch_handle);
    nvbit_get_func_config(ctx, func, &config);

    printf(
        "MEMTRACE: CTX 0x%016lx - LAUNCH - Kernel pc 0x%016lx - "
        "Kernel name %s - grid launch id %ld - grid size %d,%d,%d "
        "- block size %d,%d,%d - nregs %d - shmem %d - cuda stream "
        "id %ld\n",
        (uint64_t)ctx, pc, func_name, global_grid_launch_id, config.gridDimX,
        config.gridDimY, config.gridDimZ, config.blockDimX, config.blockDimY,
        config.blockDimZ, config.num_registers,
        config.shmem_static_nbytes + config.shmem_dynamic_nbytes,
        (uint64_t)stream);
    // grid id can be changed here, since nvbit_set_at_launch() has copied its
    // value above.
    global_grid_launch_id++;
    pthread_mutex_unlock(&mutex);
}
