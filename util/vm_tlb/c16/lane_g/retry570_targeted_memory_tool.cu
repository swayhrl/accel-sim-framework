// Diagnostic-only NVBit 1.8 mapper and one-record exact-memory tracer.
//
// This is intentionally not an Accel-Sim trace producer.  It maps a function
// through NVBit's own Instr vector, then (only when an exact getIdx target is
// supplied) instruments one directly evidenced GLOBAL LDG/STG/ATOM Instr*.

#include <assert.h>
#include <atomic>
#include <cctype>
#include <cstring>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

#include "nvbit.h"
#include "nvbit_tool.h"
#include "utils/utils.h"
#include "retry570_targeted_memory_common.h"

extern "C" __device__ void capture_target_memory(
    int predicate, uint64_t address, uint64_t launch_id, uint32_t static_index,
    uint64_t record_address);

struct ContextState {
    TargetRecord* record = nullptr;
    unsigned long long target_launch_count = 0;
    bool target_instrumented = false;
    bool target_instruction_found = false;
    bool map_emitted = false;
};

static pthread_mutex_t mutex;
// ``mutex`` protects the only slow/side-effecting path: target-function map
// construction and instrumentation.  It is deliberately *not* acquired for
// generic CUDA API callbacks or cache-confirmed non-target launches.
static std::atomic<bool> skip_callback{false};
static std::unordered_map<CUcontext, ContextState*> contexts;
enum class FunctionClassification { TARGET, NON_TARGET };
// A separate reader/writer lock protects cache construction.  A CUDA launch
// that is already known not to be the exact function takes only a shared,
// O(1) lookup and returns; non-launch callbacks take no lock at all.
static pthread_rwlock_t classification_lock;
static std::unordered_map<CUfunction, FunctionClassification> function_classification;
static std::string target_function_mangled;
static std::string map_path;
static std::string code_object_sha256;
static bool trace_enabled = false;
static uint32_t target_static_index = 0;

static void require_environment() {
    const char* function = getenv("C16_NVBIT_TARGET_FUNCTION_MANGLED");
    const char* path = getenv("C16_NVBIT_STATIC_MAP_PATH");
    if (function == nullptr || function[0] == '\0' || path == nullptr || path[0] == '\0') {
        fprintf(stderr, "C16_TARGETED_NVBIT_CONFIG_ERROR missing exact function or map path\n");
        abort();
    }
    target_function_mangled = function;
    map_path = path;
    const char* code_object = getenv("C16_NVBIT_CODE_OBJECT_SHA256");
    if (code_object == nullptr || strlen(code_object) != 64) {
        fprintf(stderr, "C16_TARGETED_NVBIT_CONFIG_ERROR missing libtorch_cuda SHA256\n");
        abort();
    }
    for (size_t index = 0; index < 64; ++index) {
        if (!(isdigit(static_cast<unsigned char>(code_object[index])) ||
              (code_object[index] >= 'a' && code_object[index] <= 'f'))) {
            fprintf(stderr, "C16_TARGETED_NVBIT_CONFIG_ERROR malformed libtorch_cuda SHA256\n");
            abort();
        }
    }
    code_object_sha256 = code_object;
    const char* index = getenv("C16_NVBIT_TARGET_INSTR_INDEX");
    if (index != nullptr && index[0] != '\0') {
        char* end = nullptr;
        unsigned long value = strtoul(index, &end, 10);
        if (end == index || *end != '\0' || value > UINT32_MAX) {
            fprintf(stderr, "C16_TARGETED_NVBIT_CONFIG_ERROR malformed target static index\n");
            abort();
        }
        trace_enabled = true;
        target_static_index = static_cast<uint32_t>(value);
    }
}

static std::string tsv_escape(const char* value) {
    std::string escaped = value == nullptr ? "" : value;
    for (char& character : escaped) {
        if (character == '\t' || character == '\n' || character == '\r') character = ' ';
    }
    return escaped;
}

static FunctionClassification classify_function(CUcontext context, CUfunction function) {
    // Cache hits do not do a mangled-name lookup and do not touch the target
    // instrumentation mutex.  The rwlock is needed because NVBit may dispatch
    // callbacks concurrently while an unseen CUfunction is being classified.
    pthread_rwlock_rdlock(&classification_lock);
    auto cached = function_classification.find(function);
    if (cached != function_classification.end()) {
        FunctionClassification result = cached->second;
        pthread_rwlock_unlock(&classification_lock);
        return result;
    }
    pthread_rwlock_unlock(&classification_lock);

    // One new CUfunction performs at most one direct, full-mangled lookup.
    const std::string observed = nvbit_get_func_name(context, function, true);
    const FunctionClassification computed = observed == target_function_mangled
        ? FunctionClassification::TARGET : FunctionClassification::NON_TARGET;
    pthread_rwlock_wrlock(&classification_lock);
    auto inserted = function_classification.emplace(function, computed);
    FunctionClassification result = inserted.first->second;
    pthread_rwlock_unlock(&classification_lock);
    return result;
}

static const char* memory_space_name(InstrType::MemorySpace space) {
    return InstrType::MemorySpaceStr[static_cast<int>(space)];
}

static bool has_memory_reference_operand(Instr* instruction) {
    for (int index = 0; index < instruction->getNumOperands(); ++index) {
        if (instruction->getOperand(index)->type == InstrType::OperandType::MREF) return true;
    }
    return false;
}

static bool direct_global_memory_instruction(Instr* instruction) {
    std::string opcode(instruction->getOpcode());
    bool recognised = opcode.rfind("LDG", 0) == 0 || opcode.rfind("STG", 0) == 0 || opcode.rfind("ATOM", 0) == 0;
    if (!recognised || instruction->getMemorySpace() != InstrType::MemorySpace::GLOBAL) return false;
    return has_memory_reference_operand(instruction);
}

static void emit_native_map(CUcontext context, CUfunction function, ContextState* state) {
    if (state->map_emitted) return;
    const std::vector<Instr*>& instructions = nvbit_get_instrs(context, function);
    std::string temporary = map_path + ".tmp." + std::to_string(getpid());
    std::ofstream output(temporary, std::ios::out | std::ios::trunc);
    if (!output.good()) {
        fprintf(stderr, "C16_NVBIT_STATIC_MAP_ERROR unable to create map\n");
        return;
    }
    output << "nvbit_static_index\tvector_ordinal\tinstruction_offset\topcode\tmemory_space\tis_load\tis_store\thas_mref\tsass\tfunction_full_name\tfunction_mangled_name\tfunction_address\tlibtorch_cuda_sha256\n";
    const std::string full_name = tsv_escape(nvbit_get_func_name(context, function));
    const std::string mangled_name = tsv_escape(nvbit_get_func_name(context, function, true));
    std::ostringstream address;
    address << "0x" << std::hex << nvbit_get_func_addr(context, function);
    for (size_t vector_ordinal = 0; vector_ordinal < instructions.size(); ++vector_ordinal) {
        Instr* instruction = instructions[vector_ordinal];
        output << instruction->getIdx() << '\t' << vector_ordinal << '\t' << instruction->getOffset() << '\t'
               << tsv_escape(instruction->getOpcode()) << '\t'
               << memory_space_name(instruction->getMemorySpace()) << '\t'
               << (instruction->isLoad() ? 1 : 0) << '\t' << (instruction->isStore() ? 1 : 0) << '\t'
               << (has_memory_reference_operand(instruction) ? 1 : 0) << '\t'
               << tsv_escape(instruction->getSass()) << '\t' << full_name << '\t' << mangled_name << '\t'
               << address.str() << '\t' << code_object_sha256 << '\n';
    }
    output.close();
    if (!output.good() || rename(temporary.c_str(), map_path.c_str()) != 0) {
        fprintf(stderr, "C16_NVBIT_STATIC_MAP_ERROR unable to finalize map\n");
        unlink(temporary.c_str());
        return;
    }
    state->map_emitted = true;
    printf("C16_NVBIT_STATIC_MAP_COMPLETE function_mangled=%s function_address=%s static_instruction_count=%zu map=%s\n",
           mangled_name.c_str(), address.str().c_str(), instructions.size(), map_path.c_str());
    fflush(stdout);
}

static void instrument_exact_instruction(CUcontext context, CUfunction function, ContextState* state) {
    if (!trace_enabled || state->target_instrumented) return;
    const std::vector<Instr*>& instructions = nvbit_get_instrs(context, function);
    for (auto instruction : instructions) {
        if (instruction->getIdx() != target_static_index) continue;
        if (!direct_global_memory_instruction(instruction)) {
            fprintf(stderr, "C16_TARGETED_NVBIT_CONFIG_ERROR target getIdx is not direct GLOBAL LDG/STG/ATOM with MREF\n");
            return;
        }
        nvbit_insert_call(instruction, "capture_target_memory", IPOINT_BEFORE);
        nvbit_add_call_arg_guard_pred_val(instruction);
        nvbit_add_call_arg_mref_addr64(instruction, 0);
        nvbit_add_call_arg_launch_val64(instruction, 0);
        nvbit_add_call_arg_const_val32(instruction, instruction->getIdx());
        nvbit_add_call_arg_const_val64(instruction, reinterpret_cast<uint64_t>(state->record));
        state->target_instrumented = true;
        state->target_instruction_found = true;
        printf("C16_TARGETED_NVBIT_INSTRUMENTED function_mangled=%s nvbit_static_index=%u offset=%u opcode=%s sass=%s\n",
               nvbit_get_func_name(context, function, true), instruction->getIdx(), instruction->getOffset(),
               instruction->getOpcode(), instruction->getSass());
        fflush(stdout);
        return;
    }
    fprintf(stderr, "C16_TARGETED_NVBIT_CONFIG_ERROR target getIdx is absent from NVBit function vector\n");
}

static bool extract_launch_function(nvbit_api_cuda_t callback, void* parameters, CUfunction* function) {
    switch (callback) {
        case API_CUDA_cuLaunch:
        case API_CUDA_cuLaunchGrid:
            *function = static_cast<cuLaunch_params*>(parameters)->f;
            return true;
        case API_CUDA_cuLaunchKernel_ptsz:
        case API_CUDA_cuLaunchKernel:
        case API_CUDA_cuLaunchCooperativeKernel:
        case API_CUDA_cuLaunchCooperativeKernel_ptsz:
            *function = static_cast<cuLaunchKernel_params*>(parameters)->f;
            return true;
        case API_CUDA_cuLaunchKernelEx:
        case API_CUDA_cuLaunchKernelEx_ptsz:
            *function = static_cast<cuLaunchKernelEx_params*>(parameters)->f;
            return true;
        default:
            return false;
    }
}

void nvbit_at_init() {
    require_environment();
    pthread_mutexattr_t attributes;
    pthread_mutexattr_init(&attributes);
    pthread_mutexattr_settype(&attributes, PTHREAD_MUTEX_RECURSIVE);
    pthread_mutex_init(&mutex, &attributes);
    pthread_rwlock_init(&classification_lock, nullptr);
    printf("C16_NVBIT_TARGETED_TOOL_READY trace_enabled=%d exact_function=%s\n", trace_enabled ? 1 : 0, target_function_mangled.c_str());
    fflush(stdout);
}

void nvbit_at_ctx_init(CUcontext context) {
    pthread_mutex_lock(&mutex);
    ContextState* state = new ContextState();
    contexts[context] = state;
    pthread_mutex_unlock(&mutex);
}

void nvbit_tool_init(CUcontext context) {
    pthread_mutex_lock(&mutex);
    auto found = contexts.find(context);
    if (found == contexts.end() || found->second->record != nullptr) {
        pthread_mutex_unlock(&mutex);
        return;
    }
    // NVBit 1.8 explicitly forbids CUDA allocation from nvbit_at_ctx_init.
    CUDA_SAFECALL(cudaMallocManaged(&found->second->record, sizeof(TargetRecord)));
    CUDA_SAFECALL(cudaMemset(found->second->record, 0, sizeof(TargetRecord)));
    pthread_mutex_unlock(&mutex);
}

void nvbit_at_cuda_event(CUcontext context, int is_exit, nvbit_api_cuda_t callback,
                         const char*, void* parameters, CUresult*) {
    if (skip_callback.load(std::memory_order_relaxed)) return;
    CUfunction function = nullptr;
    // Non-launch callbacks never acquire the target mutex or ask NVBit for a
    // function name.  This is the fast-path boundary for full-model runs.
    if (!extract_launch_function(callback, parameters, &function) || function == nullptr) return;
    if (classify_function(context, function) != FunctionClassification::TARGET) return;

    // Only the one exact, full-mangled target reaches instrumentation state.
    pthread_mutex_lock(&mutex);
    auto found = contexts.find(context);
    if (found == contexts.end()) {
        pthread_mutex_unlock(&mutex);
        return;
    }
    ContextState* state = found->second;
    if (!is_exit) {
        emit_native_map(context, function, state);
        instrument_exact_instruction(context, function, state);
        if (trace_enabled && state->target_instrumented) {
            if (state->record == nullptr) {
                fprintf(stderr, "C16_TARGETED_NVBIT_RUNTIME_ERROR missing tool-init record allocation\n");
                pthread_mutex_unlock(&mutex);
                return;
            }
            CUDA_SAFECALL(cudaMemset(state->record, 0, sizeof(TargetRecord)));
            nvbit_set_at_launch(context, function, state->target_launch_count);
            nvbit_enable_instrumented(context, function, true);
            printf("C16_TARGETED_NVBIT_FUNCTION_LAUNCH function_mangled=%s launch_id=%llu nvbit_static_index=%u\n",
                   nvbit_get_func_name(context, function, true), state->target_launch_count, target_static_index);
            state->target_launch_count++;
            fflush(stdout);
        }
    } else if (trace_enabled && state->target_instrumented) {
        skip_callback.store(true, std::memory_order_relaxed);
        CUDA_SAFECALL(cudaDeviceSynchronize());
        skip_callback.store(false, std::memory_order_relaxed);
        printf("C16_TARGETED_NVBIT_MEMORY_RECORD function_mangled=%s present=%u address=0x%llx launch_id=%llu nvbit_static_index=%u\n",
               nvbit_get_func_name(context, function, true), state->record->present,
               state->record->address, state->record->launch_id, state->record->static_index);
        fflush(stdout);
    }
    pthread_mutex_unlock(&mutex);
}

void nvbit_at_ctx_term(CUcontext context) {
    pthread_mutex_lock(&mutex);
    auto found = contexts.find(context);
    if (found == contexts.end()) {
        pthread_mutex_unlock(&mutex);
        return;
    }
    ContextState* state = found->second;
    printf("C16_TARGETED_NVBIT_TERMINAL map_emitted=%d target_instrumented=%d target_instruction_found=%d target_launch_count=%llu\n",
           state->map_emitted ? 1 : 0, state->target_instrumented ? 1 : 0,
           state->target_instruction_found ? 1 : 0, state->target_launch_count);
    fflush(stdout);
    if (state->record != nullptr) CUDA_SAFECALL(cudaFree(state->record));
    delete state;
    contexts.erase(found);
    pthread_mutex_unlock(&mutex);
}
