// Minimal Retry570 NVBit 1.8 exact-function static-map discriminator.
//
// This deliberately omits nvbit_at_ctx_init, nvbit_tool_init, CUDA memory
// allocation, instrumentation, launch filtering, and all target-mapper cache
// machinery.  It is used once on the bounded index_select microreproducer to
// distinguish NVBit's exact-function map path from the richer mapper's
// lifecycle/fast-path implementation.  It is never a C16 capture producer.

#include <atomic>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <unistd.h>
#include <vector>

#include "nvbit.h"
#include "nvbit_tool.h"

static std::string target_function_mangled;
static std::string map_path;
static std::string code_object_sha256;
static std::atomic<bool> map_emitted{false};

static void require_environment() {
    const char* function = getenv("C16_NVBIT_TARGET_FUNCTION_MANGLED");
    const char* path = getenv("C16_NVBIT_STATIC_MAP_PATH");
    const char* code_object = getenv("C16_NVBIT_CODE_OBJECT_SHA256");
    if (function == nullptr || function[0] == '\0' || path == nullptr || path[0] == '\0'
        || code_object == nullptr || strlen(code_object) != 64) {
        fprintf(stderr, "C16_EXACT_MAP_ONLY_CONFIG_ERROR missing exact function, map path, or libtorch SHA256\n");
        abort();
    }
    for (size_t index = 0; index < 64; ++index) {
        if (!(isdigit(static_cast<unsigned char>(code_object[index]))
              || (code_object[index] >= 'a' && code_object[index] <= 'f'))) {
            fprintf(stderr, "C16_EXACT_MAP_ONLY_CONFIG_ERROR malformed libtorch SHA256\n");
            abort();
        }
    }
    target_function_mangled = function;
    map_path = path;
    code_object_sha256 = code_object;
}

static std::string tsv_escape(const char* value) {
    std::string escaped = value == nullptr ? "" : value;
    for (char& character : escaped) {
        if (character == '\t' || character == '\n' || character == '\r') character = ' ';
    }
    return escaped;
}

static bool has_memory_reference_operand(Instr* instruction) {
    for (int index = 0; index < instruction->getNumOperands(); ++index) {
        if (instruction->getOperand(index)->type == InstrType::OperandType::MREF) return true;
    }
    return false;
}

static const char* memory_space_name(InstrType::MemorySpace space) {
    return InstrType::MemorySpaceStr[static_cast<int>(space)];
}

static bool extract_launch_function(nvbit_api_cuda_t callback, void* parameters, CUfunction* function) {
    if (callback == API_CUDA_cuLaunchKernelEx_ptsz || callback == API_CUDA_cuLaunchKernelEx) {
        *function = static_cast<cuLaunchKernelEx_params*>(parameters)->f;
        return true;
    }
    if (callback == API_CUDA_cuLaunch || callback == API_CUDA_cuLaunchKernel_ptsz
        || callback == API_CUDA_cuLaunchGrid || callback == API_CUDA_cuLaunchGridAsync
        || callback == API_CUDA_cuLaunchKernel || callback == API_CUDA_cuLaunchCooperativeKernel
        || callback == API_CUDA_cuLaunchCooperativeKernel_ptsz) {
        // NVBit's own v1.8 tools use the cuLaunchKernel layout for this
        // driver-launch family; retain the same ABI treatment here.
        *function = static_cast<cuLaunchKernel_params*>(parameters)->f;
        return true;
    }
    return false;
}

static void emit_map(CUcontext context, CUfunction function) {
    const std::vector<Instr*>& instructions = nvbit_get_instrs(context, function);
    std::string temporary = map_path + ".tmp." + std::to_string(getpid());
    std::ofstream output(temporary, std::ios::out | std::ios::trunc);
    if (!output.good()) {
        fprintf(stderr, "C16_EXACT_MAP_ONLY_ERROR unable to create map\n");
        return;
    }
    const std::string full_name = tsv_escape(nvbit_get_func_name(context, function));
    const std::string mangled_name = tsv_escape(nvbit_get_func_name(context, function, true));
    std::ostringstream address;
    address << "0x" << std::hex << nvbit_get_func_addr(context, function);
    output << "nvbit_static_index\tvector_ordinal\tinstruction_offset\topcode\tmemory_space\tis_load\tis_store\thas_mref\tsass\tfunction_full_name\tfunction_mangled_name\tfunction_address\tlibtorch_cuda_sha256\n";
    for (size_t ordinal = 0; ordinal < instructions.size(); ++ordinal) {
        Instr* instruction = instructions[ordinal];
        output << instruction->getIdx() << '\t' << ordinal << '\t' << instruction->getOffset() << '\t'
               << tsv_escape(instruction->getOpcode()) << '\t'
               << memory_space_name(instruction->getMemorySpace()) << '\t'
               << (instruction->isLoad() ? 1 : 0) << '\t' << (instruction->isStore() ? 1 : 0) << '\t'
               << (has_memory_reference_operand(instruction) ? 1 : 0) << '\t'
               << tsv_escape(instruction->getSass()) << '\t' << full_name << '\t' << mangled_name << '\t'
               << address.str() << '\t' << code_object_sha256 << '\n';
    }
    output.close();
    if (!output.good() || rename(temporary.c_str(), map_path.c_str()) != 0) {
        fprintf(stderr, "C16_EXACT_MAP_ONLY_ERROR unable to finalize map\n");
        unlink(temporary.c_str());
        return;
    }
    map_emitted.store(true, std::memory_order_release);
    printf("C16_EXACT_MAP_ONLY_COMPLETE function_mangled=%s static_instruction_count=%zu map=%s\n",
           mangled_name.c_str(), instructions.size(), map_path.c_str());
    fflush(stdout);
}

void nvbit_at_init() {
    require_environment();
    printf("C16_EXACT_MAP_ONLY_TOOL_READY no_ctx_init=1 no_tool_init=1 no_cuda_allocation=1 exact_function=%s\n",
           target_function_mangled.c_str());
    fflush(stdout);
}

void nvbit_at_cuda_event(CUcontext context, int is_exit, nvbit_api_cuda_t callback,
                         const char*, void* parameters, CUresult*) {
    if (is_exit || map_emitted.load(std::memory_order_acquire)) return;
    CUfunction function = nullptr;
    if (!extract_launch_function(callback, parameters, &function) || function == nullptr) return;
    if (target_function_mangled != std::string(nvbit_get_func_name(context, function, true))) return;
    emit_map(context, function);
}

void nvbit_at_term() {
    printf("C16_EXACT_MAP_ONLY_TERMINAL map_emitted=%d\n", map_emitted.load(std::memory_order_acquire) ? 1 : 0);
    fflush(stdout);
}
