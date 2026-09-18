#include <assert.h>
#include <limits.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <fstream>
#include <string>
#include <unordered_map>
#include <vector>

#include "nvbit.h"
#include "nvbit_tool.h"
#include "utils/channel.hpp"
#include "utils/utils.h"
#include "c16warp1_v39_common.h"

extern "C" __device__ void c16warp1_record_mref(int, uint64_t, uint32_t,
    uint64_t, uint64_t, uint64_t, uint64_t);
extern "C" __device__ void c16warp1_record_reg(int, uint32_t, uint32_t,
    uint32_t, uint64_t, uint64_t, uint64_t, uint64_t);

#define C16_CHANNEL_SIZE (1l << 20)

enum class ReceiverState { INIT, WORKING, STOP, FINISHED };

struct Config {
    std::string function_name;
    std::string output;
    uint32_t static_index;
    uint32_t occurrence;
    uint32_t operand;
    unsigned long long capacity;
    int cta_begin;
    int cta_end;
    int load_addr_lo;
};

struct Accounting {
    uint64_t receiver_records = 0;
    uint64_t first_sequence = 0;
    uint64_t last_sequence = 0;
    uint64_t sequence_gaps = 0;
    uint64_t duplicate_sequences = 0;
    uint64_t expected_sequence = 0;
    bool have_sequence = false;
    bool malformed_packet = false;
    uint64_t terminal_count = 0;
};

struct CtxState {
    ChannelDev* channel_dev = nullptr;
    ChannelHost channel_host;
    CUmodule tool_module = nullptr;
    CUfunction flush_channel_func = nullptr;
    c16warp1_device_counters_t* counters = nullptr;
    // The receiver runs on the pthread created by ChannelHost; preserve the
    // official scaffold's volatile stop/finished handshake.
    volatile ReceiverState receiver_state = ReceiverState::INIT;
    bool need_sync = false;
    bool installed = false;
    bool install_failed = false;
    bool selected_launch_seen = false;
    uint32_t matching_occurrences = 0;
    Accounting accounting;
    std::vector<c16warp1_wrec_t> records;
};

#include "tool_func/flush_channel.c"

static pthread_mutex_t mutex;
static pthread_mutex_t cuda_event_mutex;
static std::unordered_map<CUcontext, CtxState*> contexts;
static bool skip_callback = false;
static Config config;

static unsigned long long parse_u64(const char* key, bool required,
                                    unsigned long long fallback = 0) {
    const char* value = getenv(key);
    if (!value || !*value) {
        if (required) { fprintf(stderr, "C16_WARP_CONFIG_ERROR missing=%s\n", key); abort(); }
        return fallback;
    }
    char* end = nullptr;
    unsigned long long parsed = strtoull(value, &end, 0);
    if (!end || *end) { fprintf(stderr, "C16_WARP_CONFIG_ERROR invalid=%s\n", key); abort(); }
    return parsed;
}

static void parse_config() {
    const char* name = getenv("C16_WARP_FUNCTION");
    const char* output = getenv("C16_WARP_OUTPUT");
    if (!name || !*name || !output || !*output) {
        fprintf(stderr, "C16_WARP_CONFIG_ERROR function/output required\n"); abort();
    }
    config.function_name = name;
    config.output = output;
    config.static_index = (uint32_t)parse_u64("C16_WARP_STATIC", true);
    config.occurrence = (uint32_t)parse_u64("C16_WARP_FUNCTION_OCCURRENCE", true);
    config.operand = (uint32_t)parse_u64("C16_WARP_OPERAND", true);
    config.capacity = parse_u64("C16_WARP_CAPACITY", true);
    config.cta_begin = (int)parse_u64("C16_CTA_BEGIN", false, 0);
    config.cta_end = (int)parse_u64("C16_CTA_END", false, INT_MAX);
    config.load_addr_lo = getenv("C16_WARP_LOAD_ADDR_LO") ?
        (int)parse_u64("C16_WARP_LOAD_ADDR_LO", false) : -1;
    if (!config.capacity || config.cta_begin > config.cta_end) {
        fprintf(stderr, "C16_WARP_CONFIG_ERROR capacity/cta range\n"); abort();
    }
}

static bool is_kernel_launch(nvbit_api_cuda_t cbid, void* params, CUfunction* out) {
    if (cbid == API_CUDA_cuLaunchKernel || cbid == API_CUDA_cuLaunchKernel_ptsz) {
        *out = ((cuLaunchKernel_params*)params)->f;
        return true;
    }
    return false;
}

static bool is_mref(Instr* instr) {
    for (int i = 0; i < instr->getNumOperands(); ++i)
        if (instr->getOperand(i)->type == InstrType::OperandType::MREF) return true;
    return false;
}

static void install_selected_instruction(CUcontext ctx, CUfunction function,
                                         CtxState* state) {
    if (state->installed || state->install_failed) return;
    const std::vector<Instr*>& instructions = nvbit_get_instrs(ctx, function);
    for (auto* instr : instructions) {
        const auto space = instr->getMemorySpace();
        if (instr->getIdx() != config.static_index ||
            (space != InstrType::MemorySpace::GLOBAL &&
             space != InstrType::MemorySpace::GLOBAL_TO_SHARED) || !is_mref(instr)) continue;
        unsigned mref_number = 0;
        unsigned total_mrefs = 0;
        for (int operand_index = 0; operand_index < instr->getNumOperands(); ++operand_index) {
            if (instr->getOperand(operand_index)->type != InstrType::OperandType::MREF) continue;
            if (mref_number++ != config.operand) { ++total_mrefs; continue; }
            if (instr->isLoad()) {
                if (config.load_addr_lo < 0) {
                    fprintf(stderr, "C16_WARP_CONFIG_ERROR static=%u load source register required\n",
                            config.static_index);
                    state->install_failed = true;
                    return;
                }
                nvbit_insert_call(instr, "c16warp1_record_reg", IPOINT_BEFORE);
                nvbit_add_call_arg_guard_pred_val(instr);
                nvbit_add_call_arg_reg_val(instr, config.load_addr_lo);
                nvbit_add_call_arg_reg_val(instr, config.load_addr_lo + 1);
            } else {
                nvbit_insert_call(instr, "c16warp1_record_mref", IPOINT_BEFORE);
                nvbit_add_call_arg_guard_pred_val(instr);
                // V20's audited semantic authority uses the source operand index.
                nvbit_add_call_arg_mref_addr64(instr, operand_index);
            }
            nvbit_add_call_arg_const_val32(instr, config.static_index);
            nvbit_add_call_arg_const_val64(instr, (uint64_t)state->counters);
            nvbit_add_call_arg_const_val64(instr, config.capacity);
            const uint64_t packed_cta_range = ((uint64_t)(uint32_t)config.cta_begin << 32) |
                                              (uint32_t)config.cta_end;
            nvbit_add_call_arg_const_val64(instr, packed_cta_range);
            nvbit_add_call_arg_const_val64(instr, (uint64_t)state->channel_dev);
            ++total_mrefs;
            state->installed = true;
            printf("C16_WARP_INSTRUMENTED static=%u mref=%u mode=%s\n",
                   config.static_index, config.operand,
                   instr->isLoad() ? "REGISTER_PAIR" : "MREF");
            fflush(stdout);
            return;
        }
    }
    fprintf(stderr, "C16_WARP_CONFIG_ERROR static=%u matching GLOBAL MREF not found\n",
            config.static_index);
    state->install_failed = true;
}

static void consume_packets(CtxState* state, const char* buffer, uint32_t bytes) {
    if (bytes % sizeof(c16warp1_packet_t) != 0) {
        state->accounting.malformed_packet = true;
        return;
    }
    for (uint32_t offset = 0; offset < bytes; offset += sizeof(c16warp1_packet_t)) {
        const auto* packet = (const c16warp1_packet_t*)(buffer + offset);
        if (packet->record.static_index != config.static_index) {
            state->accounting.malformed_packet = true;
            continue;
        }
        if (!state->accounting.have_sequence) {
            state->accounting.have_sequence = true;
            state->accounting.first_sequence = packet->sequence;
        }
        if (packet->sequence != state->accounting.expected_sequence) {
            if (packet->sequence < state->accounting.expected_sequence)
                ++state->accounting.duplicate_sequences;
            else state->accounting.sequence_gaps += packet->sequence - state->accounting.expected_sequence;
            state->accounting.expected_sequence = packet->sequence + 1;
            continue;
        }
        state->accounting.last_sequence = packet->sequence;
        ++state->accounting.expected_sequence;
        ++state->accounting.receiver_records;
        state->records.push_back(packet->record);
    }
}

static void* receiver_thread(void* argument) {
    CtxState* state = (CtxState*)argument;
    std::vector<char> buffer(C16_CHANNEL_SIZE);
    while (state->receiver_state == ReceiverState::WORKING) {
        const uint32_t received = state->channel_host.recv(buffer.data(), C16_CHANNEL_SIZE);
        if (received) consume_packets(state, buffer.data(), received);
    }
    state->receiver_state = ReceiverState::FINISHED;
    return nullptr;
}

static void init_channel(CtxState* state) {
    state->receiver_state = ReceiverState::WORKING;
    CUDA_SAFECALL(cudaMallocManaged(&state->channel_dev, sizeof(ChannelDev)));
    // Unlike the ChannelDev allocation (owned by the official lifecycle), the
    // producer counter is device-only.  This avoids host-managed page migration
    // from inside an injected warp and is copied back only after the official
    // flush/synchronization boundary.
    CUDA_SAFECALL(cudaMalloc(&state->counters, sizeof(c16warp1_device_counters_t)));
    CUDA_SAFECALL(cudaMemset(state->counters, 0, sizeof(c16warp1_device_counters_t)));
    state->channel_host.init((int)contexts.size(), C16_CHANNEL_SIZE, state->channel_dev,
                             receiver_thread, state);
    nvbit_set_tool_pthread(state->channel_host.get_thread());
}

static void write_accounting(const CtxState* state, uint64_t producer,
                             uint64_t overflow, bool terminal_seen) {
    std::ofstream out(config.output + ".accounting.json");
    out << "{\n"
        << "  \"producer_logical_records\": " << producer << ",\n"
        << "  \"producer_overflow\": " << overflow << ",\n"
        << "  \"receiver_packets_accepted\": " << state->accounting.receiver_records << ",\n"
        << "  \"receiver_first_sequence\": " << state->accounting.first_sequence << ",\n"
        << "  \"receiver_last_sequence\": " << state->accounting.last_sequence << ",\n"
        << "  \"receiver_sequence_gap_count\": " << state->accounting.sequence_gaps << ",\n"
        << "  \"receiver_duplicate_sequence_count\": " << state->accounting.duplicate_sequences << ",\n"
        << "  \"receiver_malformed_packet\": " << (state->accounting.malformed_packet ? "true" : "false") << ",\n"
        << "  \"receiver_terminal_seen\": " << (terminal_seen ? "true" : "false") << ",\n"
        << "  \"receiver_terminal_count\": " << state->accounting.terminal_count << ",\n"
        << "  \"finalized_c16warp1_records_written\": " << state->records.size() << "\n}\n";
}

static void finalize_selected(CtxState* state) {
    if (!state->selected_launch_seen) return;
    c16warp1_device_counters_t host_counters{};
    CUDA_SAFECALL(cudaMemcpy(&host_counters, state->counters, sizeof(host_counters),
                             cudaMemcpyDeviceToHost));
    const uint64_t producer = host_counters.producer_records;
    const uint64_t overflow = host_counters.producer_overflow;
    ++state->accounting.terminal_count;
    std::ofstream trace(config.output, std::ios::binary);
    trace.write("C16WARP1", 8);
    trace.write((const char*)&config.static_index, sizeof(config.static_index));
    trace.write((const char*)&config.occurrence, sizeof(config.occurrence));
    trace.write((const char*)&producer, sizeof(producer));
    trace.write((const char*)&overflow, sizeof(overflow));
    const uint64_t written = state->records.size();
    trace.write((const char*)&written, sizeof(written));
    if (written) trace.write((const char*)state->records.data(), written * sizeof(c16warp1_wrec_t));
    trace.close();
    write_accounting(state, producer, overflow, true);
    printf("C16_WARP_TERMINAL static=%u occurrence=%u records=%llu overflow=%llu\n",
           config.static_index, config.occurrence,
           (unsigned long long)written, (unsigned long long)overflow);
    fflush(stdout);
}

void nvbit_at_init() {
    // This is part of the official mem_trace 1.7.7.1 initialization contract:
    // ChannelDev and our device-visible accounting allocation must be placed on
    // the device rather than faulting from host-managed backing during a warp.
    setenv("CUDA_MANAGED_FORCE_DEVICE_ALLOC", "1", 1);
    parse_config();
    pthread_mutexattr_t attributes;
    pthread_mutexattr_init(&attributes);
    pthread_mutexattr_settype(&attributes, PTHREAD_MUTEX_RECURSIVE);
    pthread_mutex_init(&mutex, &attributes);
    pthread_mutex_init(&cuda_event_mutex, &attributes);
}

void nvbit_at_ctx_init(CUcontext ctx) {
    pthread_mutex_lock(&mutex);
    CtxState* state = new CtxState;
    contexts[ctx] = state;
    nvbit_load_tool_module(ctx, (const void*)flush_channel_bin, &state->tool_module);
    nvbit_find_function_by_name(ctx, state->tool_module, "flush_channel", &state->flush_channel_func);
    pthread_mutex_unlock(&mutex);
}

void nvbit_tool_init(CUcontext ctx) {
    pthread_mutex_lock(&mutex);
    init_channel(contexts.at(ctx));
    pthread_mutex_unlock(&mutex);
}

void nvbit_at_cuda_event(CUcontext ctx, int is_exit, nvbit_api_cuda_t cbid,
                         const char*, void* params, CUresult*) {
    pthread_mutex_lock(&cuda_event_mutex);
    if (skip_callback) { pthread_mutex_unlock(&cuda_event_mutex); return; }
    // Follow the official scaffold's re-entry guard around all NVBit launch
    // control calls made from this callback.
    skip_callback = true;
    CUfunction function = nullptr;
    if (!is_kernel_launch(cbid, params, &function)) {
        skip_callback = false; pthread_mutex_unlock(&cuda_event_mutex); return;
    }
    CtxState* state = contexts.at(ctx);
    if (config.function_name != std::string(nvbit_get_func_name(ctx, function, true))) {
        skip_callback = false; pthread_mutex_unlock(&cuda_event_mutex); return;
    }
    if (!is_exit) {
        const bool selected = state->matching_occurrences == config.occurrence;
        if (selected) {
            install_selected_instruction(ctx, function, state);
            state->selected_launch_seen = state->installed && !state->install_failed;
            state->need_sync = state->selected_launch_seen;
        }
        // Preserve the official Channel launch setup even though this callback
        // has no dynamic launch arguments.  NVBit uses this boundary to select
        // the instrumented launch image before it may execute.
        nvbit_set_at_launch(ctx, function, (uint64_t)state->matching_occurrences);
        nvbit_enable_instrumented(ctx, function, selected && state->installed && !state->install_failed);
        ++state->matching_occurrences;
    }
    skip_callback = false;
    pthread_mutex_unlock(&cuda_event_mutex);
}

void nvbit_at_ctx_term(CUcontext ctx) {
    pthread_mutex_lock(&mutex);
    CtxState* state = contexts.at(ctx);
    skip_callback = true;
    if (state->need_sync) {
        void* args[] = {&state->channel_dev};
        nvbit_launch_kernel(ctx, state->flush_channel_func, 1, 1, 1, 1, 1, 1, 0, nullptr, args, nullptr);
        CUDA_SAFECALL(cudaDeviceSynchronize());
    }
    if (state->receiver_state != ReceiverState::INIT) {
        state->receiver_state = ReceiverState::STOP;
        while (state->receiver_state != ReceiverState::FINISHED) {}
    }
    finalize_selected(state);
    state->channel_host.destroy(false);
    if (state->counters) cudaFree(state->counters);
    if (state->channel_dev) cudaFree(state->channel_dev);
    contexts.erase(ctx);
    delete state;
    skip_callback = false;
    pthread_mutex_unlock(&mutex);
}
