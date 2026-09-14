// Route-B V1 host-side NVBit producer.  Raw output is C16_ROUTE_B_LANE_EVENT_V1:
// one executing lane per record with an explicit warp_instruction_instance_id.
// It never reconstructs a dynamic warp instruction from adjacent atomic slots.

#include <atomic>
#include <cctype>
#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <map>
#include <pthread.h>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

#include "nvbit.h"
#include "nvbit_tool.h"
#include "utils/utils.h"
#include "route_b_memory_event_common.h"

extern "C" __device__ void route_b_append_memory_event(
    int predicate, uint64_t address, uint64_t launch_id, uint32_t static_index,
    uint32_t mref_ordinal, uint32_t instruction_offset, uint32_t width_bytes,
    uint32_t access_kind, uint64_t buffer_address);

namespace {
constexpr uint32_t kRead = 1, kWrite = 2, kAtomic = 3;
struct WhitelistEntry {
    uint32_t static_index, mref_ordinal, instruction_offset, width_bytes, access_kind;
    std::string opcode;
};
struct ContextState {
    RouteBBuffer* device_buffer = nullptr;
    RouteBBuffer* host_buffer = nullptr;
    size_t buffer_bytes = 0;
    uint64_t launch_id = 0;
    uint64_t total_events = 0, total_overflow = 0, total_drop = 0, total_raw_bytes = 0;
    bool instrumented = false;
    bool terminal_written = false;
    std::string function_mangled;
};

static pthread_mutex_t mutex;
static std::unordered_map<CUcontext, ContextState*> contexts;
static std::map<std::pair<uint32_t, uint32_t>, WhitelistEntry> whitelist;
static std::string exact_function, output_jsonl, run_id, deployment_id, scenario_id, phase_id, decode_step;
static uint32_t capacity = 0;
static uint64_t host_output_cap_bytes = 0;
static std::atomic<bool> suppress_callbacks{false};

static std::string env_required(const char* key) {
    const char* value = getenv(key);
    if (value == nullptr || value[0] == '\0') {
        fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_CONFIG_ERROR missing %s\n", key);
        abort();
    }
    return value;
}
static uint32_t parse_u32(const std::string& value, const char* label) {
    char* end = nullptr; unsigned long parsed = strtoul(value.c_str(), &end, 10);
    if (end == value.c_str() || *end != '\0' || parsed > UINT32_MAX) {
        fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_CONFIG_ERROR malformed %s\n", label); abort();
    }
    return static_cast<uint32_t>(parsed);
}
static uint64_t parse_u64(const std::string& value, const char* label) {
    char* end = nullptr; unsigned long long parsed = strtoull(value.c_str(), &end, 10);
    if (end == value.c_str() || *end != '\0') {
        fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_CONFIG_ERROR malformed %s\n", label); abort();
    }
    return static_cast<uint64_t>(parsed);
}
static uint32_t access_code(const std::string& access) {
    if (access == "READ") return kRead;
    if (access == "WRITE") return kWrite;
    if (access == "ATOMIC") return kAtomic;
    fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_CONFIG_ERROR bad access kind\n"); abort();
}
static std::vector<std::string> split_tab(const std::string& line) {
    std::vector<std::string> result; std::stringstream input(line); std::string field;
    while (std::getline(input, field, '\t')) result.push_back(field);
    return result;
}
static void load_whitelist() {
    // TSV columns: static_index,mref_ordinal,instruction_offset,width_bytes,
    // access_kind,opcode,memory_space,has_mref.  The Python preflight manifest
    // has already verified file SHA identities and canonical whitelist SHA.
    std::ifstream input(env_required("C16_ROUTE_B_WHITELIST_TSV"));
    if (!input.good()) { fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_CONFIG_ERROR unreadable whitelist\n"); abort(); }
    std::string line; bool header = true;
    while (std::getline(input, line)) {
        if (header) { header = false; continue; }
        if (line.empty()) continue;
        auto field = split_tab(line);
        if (field.size() != 8 || field[6] != "GLOBAL" || field[7] != "1") {
            fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_CONFIG_ERROR non-GLOBAL/non-MREF whitelist row\n"); abort();
        }
        WhitelistEntry entry{parse_u32(field[0], "static_index"), parse_u32(field[1], "mref_ordinal"),
                              parse_u32(field[2], "instruction_offset"), parse_u32(field[3], "width_bytes"),
                              access_code(field[4]), field[5]};
        if (entry.width_bytes == 0 || !whitelist.emplace(std::make_pair(entry.static_index, entry.mref_ordinal), entry).second) {
            fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_CONFIG_ERROR duplicate/invalid whitelist row\n"); abort();
        }
    }
    if (whitelist.empty()) { fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_CONFIG_ERROR empty whitelist\n"); abort(); }
}
static bool extract_launch_function(nvbit_api_cuda_t callback, void* parameters, CUfunction* function) {
    switch (callback) {
        case API_CUDA_cuLaunch: case API_CUDA_cuLaunchGrid: case API_CUDA_cuLaunchGridAsync:
            *function = static_cast<cuLaunch_params*>(parameters)->f; return true;
        case API_CUDA_cuLaunchKernel: case API_CUDA_cuLaunchKernel_ptsz:
        case API_CUDA_cuLaunchCooperativeKernel: case API_CUDA_cuLaunchCooperativeKernel_ptsz:
            *function = static_cast<cuLaunchKernel_params*>(parameters)->f; return true;
        case API_CUDA_cuLaunchKernelEx: case API_CUDA_cuLaunchKernelEx_ptsz:
            *function = static_cast<cuLaunchKernelEx_params*>(parameters)->f; return true;
        default: return false;
    }
}
static bool matches_exact_function(CUcontext context, CUfunction function) {
    return nvbit_get_func_name(context, function, true) == ::exact_function;
}
static int mref_count(Instr* instruction) {
    int count = 0;
    for (int index = 0; index < instruction->getNumOperands(); ++index)
        if (instruction->getOperand(index)->type == InstrType::OperandType::MREF) ++count;
    return count;
}
static void instrument_whitelisted_mrefs(CUcontext context, CUfunction function, ContextState* state) {
    if (state->instrumented) return;
    const std::vector<Instr*>& instructions = nvbit_get_instrs(context, function);
    for (Instr* instruction : instructions) {
        const uint32_t index = instruction->getIdx();
        const int available_mrefs = mref_count(instruction);
        for (int ordinal = 0; ordinal < available_mrefs; ++ordinal) {
            auto found = whitelist.find(std::make_pair(index, static_cast<uint32_t>(ordinal)));
            if (found == whitelist.end()) continue;
            const WhitelistEntry& entry = found->second;
            if (instruction->getMemorySpace() != InstrType::MemorySpace::GLOBAL ||
                instruction->getOffset() != entry.instruction_offset) {
                fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_CONFIG_ERROR map/instruction mismatch\n"); abort();
            }
            nvbit_insert_call(instruction, "route_b_append_memory_event", IPOINT_BEFORE);
            nvbit_add_call_arg_guard_pred_val(instruction);
            nvbit_add_call_arg_mref_addr64(instruction, ordinal);
            nvbit_add_call_arg_launch_val64(instruction, 0);
            nvbit_add_call_arg_const_val32(instruction, index);
            nvbit_add_call_arg_const_val32(instruction, ordinal);
            nvbit_add_call_arg_const_val32(instruction, entry.instruction_offset);
            nvbit_add_call_arg_const_val32(instruction, entry.width_bytes);
            nvbit_add_call_arg_const_val32(instruction, entry.access_kind);
            nvbit_add_call_arg_const_val64(instruction, reinterpret_cast<uint64_t>(state->device_buffer));
        }
    }
    state->instrumented = true;
}
static std::string json_escape(const std::string& value) {
    std::string out; for (char c : value) { if (c == '"' || c == '\\') out += '\\'; out += c; } return out;
}
static const char* access_name(uint32_t code) { return code == kRead ? "READ" : code == kWrite ? "WRITE" : code == kAtomic ? "ATOMIC" : "INVALID"; }
static void append_readback(ContextState* state) {
    if (state->host_buffer == nullptr) return;
    suppress_callbacks.store(true, std::memory_order_relaxed);
    CUDA_SAFECALL(cudaDeviceSynchronize());
    CUDA_SAFECALL(cudaMemcpy(state->host_buffer, state->device_buffer, state->buffer_bytes, cudaMemcpyDeviceToHost));
    suppress_callbacks.store(false, std::memory_order_relaxed);
    std::ofstream out(output_jsonl, std::ios::out | std::ios::app);
    if (!out.good()) { fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_RUNTIME_ERROR output open\n"); abort(); }
    const uint64_t count = state->host_buffer->next_sequence > capacity ? capacity : state->host_buffer->next_sequence;
    const uint64_t prospective_bytes = count * sizeof(RouteBLaneEvent);
    if (state->total_raw_bytes + prospective_bytes > host_output_cap_bytes) {
        // Do not write a partial stream whose terminal would look successful.
        state->total_overflow += count;
        state->total_drop += state->host_buffer->drop_count;
        state->total_overflow += state->host_buffer->overflow_count;
        out.close();
        return;
    }
    for (uint64_t slot = 0; slot < count; ++slot) {
        const RouteBLaneEvent& e = state->host_buffer->records[slot];
        auto found = whitelist.find(std::make_pair(e.static_index, e.mref_ordinal));
        if (e.record_kind != ROUTE_B_LANE_EVENT || found == whitelist.end()) { ++state->total_drop; continue; }
        out << "{\"record_kind\":\"LANE_EVENT\",\"raw_schema\":\"C16_ROUTE_B_LANE_EVENT_V1\","
            << "\"sequence_label\":\"OBSERVED_CALLBACK_ORDER\",\"observed_event_sequence\":" << e.observed_callback_sequence
            << ",\"warp_instruction_instance_id\":" << e.warp_instruction_instance_id << ",\"kernel_launch_id\":" << e.launch_id
            << ",\"function_mangled_name\":\"" << json_escape(state->function_mangled) << "\",\"deployment_id\":\"" << json_escape(deployment_id)
            << "\",\"run_id\":\"" << json_escape(run_id) << "\",\"scenario_id\":\"" << json_escape(scenario_id)
            << "\",\"phase\":\"" << json_escape(phase_id) << "\",\"decode_step\":\"" << json_escape(decode_step)
            << "\",\"cta\":[" << e.cta_x << ',' << e.cta_y << ',' << e.cta_z << "],\"warp_id\":" << e.warp_id
            << ",\"static_index\":" << e.static_index << ",\"instruction_offset\":" << e.instruction_offset
            << ",\"opcode\":\"" << json_escape(found->second.opcode) << "\",\"mref_ordinal\":" << e.mref_ordinal
            << ",\"access_kind\":\"" << access_name(e.access_kind) << "\",\"width_bytes\":" << e.width_bytes
            << ",\"memory_space\":\"GLOBAL\",\"active_mask\":" << e.active_mask << ",\"predicate_mask\":" << e.predicate_mask
            << ",\"predicate_semantics\":\"GUARD_PREDICATE_MASK\",\"executing_mask\":" << e.executing_mask << ",\"lane_id\":" << e.lane_id
            << ",\"gpu_va\":" << e.gpu_va << "}\n";
    }
    state->total_events += count;
    state->total_raw_bytes += prospective_bytes;
    state->total_overflow += state->host_buffer->overflow_count;
    state->total_drop += state->host_buffer->drop_count;
    out.close();
}
static void emit_terminal(ContextState* state) {
    if (state->terminal_written || !state->instrumented) return;
    std::ofstream out(output_jsonl, std::ios::out | std::ios::app);
    if (!out.good()) { fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_RUNTIME_ERROR terminal output open\n"); abort(); }
    const bool complete = state->total_overflow == 0 && state->total_drop == 0;
    out << "{\"record_kind\":\"TERMINAL\",\"terminal_status\":\"" << (complete ? "COMPLETE" : "FAILED_CLOSED")
        << "\",\"overflow_count\":" << state->total_overflow << ",\"drop_count\":" << state->total_drop
        << ",\"event_count\":" << state->total_events << "}\n";
    out.close(); state->terminal_written = true;
}
}  // namespace

void nvbit_at_init() {
    // Python write_verified_producer_manifest must complete before launch.
    (void)env_required("C16_ROUTE_B_VERIFIED_MANIFEST");
    exact_function = env_required("C16_ROUTE_B_EXACT_FUNCTION_MANGLED");
    output_jsonl = env_required("C16_ROUTE_B_RAW_JSONL"); run_id = env_required("C16_ROUTE_B_RUN_ID");
    deployment_id = env_required("C16_ROUTE_B_DEPLOYMENT_ID"); scenario_id = env_required("C16_ROUTE_B_SCENARIO_ID");
    phase_id = env_required("C16_ROUTE_B_PHASE"); decode_step = env_required("C16_ROUTE_B_DECODE_STEP");
    capacity = parse_u32(env_required("C16_ROUTE_B_EVENT_CAPACITY"), "event capacity");
    if (capacity == 0) { fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_CONFIG_ERROR zero capacity\n"); abort(); }
    host_output_cap_bytes = parse_u64(env_required("C16_ROUTE_B_HOST_OUTPUT_CAP_BYTES"), "host output cap");
    if (host_output_cap_bytes < sizeof(RouteBLaneEvent) || static_cast<uint64_t>(capacity) * sizeof(RouteBLaneEvent) > host_output_cap_bytes) {
        fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_CONFIG_ERROR event capacity exceeds host output cap\n"); abort();
    }
    load_whitelist(); pthread_mutex_init(&mutex, nullptr);
    printf("C16_ROUTE_B_LANE_EVENT_TOOL_READY whitelist_rows=%zu capacity=%u\n", whitelist.size(), capacity); fflush(stdout);
}
void nvbit_at_ctx_init(CUcontext context) { pthread_mutex_lock(&mutex); contexts[context] = new ContextState(); pthread_mutex_unlock(&mutex); }
void nvbit_tool_init(CUcontext context) {
    pthread_mutex_lock(&mutex); auto it = contexts.find(context); if (it == contexts.end() || it->second->device_buffer) { pthread_mutex_unlock(&mutex); return; }
    ContextState* state = it->second; state->buffer_bytes = sizeof(RouteBBuffer) + (static_cast<size_t>(capacity) - 1) * sizeof(RouteBLaneEvent);
    CUDA_SAFECALL(cudaMalloc(&state->device_buffer, state->buffer_bytes)); CUDA_SAFECALL(cudaMallocHost(&state->host_buffer, state->buffer_bytes));
    pthread_mutex_unlock(&mutex);
}
void nvbit_at_cuda_event(CUcontext context, int is_exit, nvbit_api_cuda_t callback, const char*, void* parameters, CUresult*) {
    if (suppress_callbacks.load(std::memory_order_relaxed)) return; CUfunction function = nullptr;
    if (!extract_launch_function(callback, parameters, &function) || function == nullptr || !matches_exact_function(context, function)) return;
    pthread_mutex_lock(&mutex); auto it = contexts.find(context); if (it == contexts.end()) { pthread_mutex_unlock(&mutex); return; }
    ContextState* state = it->second;
    if (!is_exit) {
        if (!state->device_buffer) { fprintf(stderr, "C16_ROUTE_B_LANE_EVENT_RUNTIME_ERROR missing buffer\n"); abort(); }
        instrument_whitelisted_mrefs(context, function, state); CUDA_SAFECALL(cudaMemset(state->device_buffer, 0, state->buffer_bytes));
        RouteBBuffer header{}; header.capacity = capacity;
        CUDA_SAFECALL(cudaMemcpy(state->device_buffer, &header, offsetof(RouteBBuffer, records), cudaMemcpyHostToDevice));
        state->function_mangled = nvbit_get_func_name(context, function, true);
        nvbit_set_at_launch(context, function, state->launch_id++); nvbit_enable_instrumented(context, function, true);
    } else { append_readback(state); }
    pthread_mutex_unlock(&mutex);
}
void nvbit_at_ctx_term(CUcontext context) {
    pthread_mutex_lock(&mutex); auto it = contexts.find(context); if (it == contexts.end()) { pthread_mutex_unlock(&mutex); return; }
    ContextState* state = it->second; emit_terminal(state); if (state->device_buffer) CUDA_SAFECALL(cudaFree(state->device_buffer));
    if (state->host_buffer) CUDA_SAFECALL(cudaFreeHost(state->host_buffer)); delete state; contexts.erase(it); pthread_mutex_unlock(&mutex);
}
