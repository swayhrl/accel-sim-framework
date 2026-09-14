// Route-B V2 exact-function NVBit static mapper.
//
// This is a map-only, diagnostic producer.  Unlike the historical V1 mapper,
// it does not accept a caller-declared libtorch_cuda SHA as ownership proof.
// It follows CUDA library/module callbacks, resolves the CUfunction's actual
// CUmodule with cuFuncGetModule, and emits a map only if that module has a
// concrete path/SHA entry in the pre-closed code-object manifest.

#include <atomic>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <dlfcn.h>
#include <fstream>
#include <map>
#include <mutex>
#include <sstream>
#include <string>
#include <unistd.h>
#include <vector>

#include "nvbit.h"
#include "nvbit_tool.h"

struct Owner { std::string path; std::string sha256; std::string source; };

static std::string target_mangled;
static std::string output_path;
static std::string fatbin_registry_path;
static std::map<std::string, std::string> manifest_sha;
static std::map<CUlibrary, Owner> library_owners;
static std::map<CUmodule, Owner> module_owners;
static std::map<void*, Owner> pending_loads;
static std::mutex ownership_mutex;
static std::atomic<bool> map_emitted{false};
static std::atomic<bool> owner_unresolved{false};

static bool valid_sha(const std::string& value) {
    if (value.size() != 64) return false;
    for (char c : value) if (!std::isxdigit(static_cast<unsigned char>(c)) || (c >= 'A' && c <= 'F')) return false;
    return true;
}

static std::string escape_tsv(const char* value) {
    std::string out = value == nullptr ? "" : value;
    for (char& c : out) if (c == '\t' || c == '\n' || c == '\r') c = ' ';
    return out;
}

static std::string canonical_or_original(const char* path) {
    if (path == nullptr || path[0] == '\0') return "";
    char* resolved = realpath(path, nullptr);
    if (resolved == nullptr) return std::string(path);
    std::string result(resolved); free(resolved); return result;
}

static Owner owner_from_path(const char* path, const char* source) {
    Owner owner; owner.path = canonical_or_original(path); owner.source = source;
    auto it = manifest_sha.find(owner.path);
    if (it != manifest_sha.end()) owner.sha256 = it->second;
    return owner;
}

static void load_manifest(const char* manifest) {
    std::ifstream input(manifest);
    if (!input.good()) { fprintf(stderr, "C16_ROUTE_B_V2_CONFIG_ERROR unreadable code-object manifest\n"); abort(); }
    std::string line;
    while (std::getline(input, line)) {
        if (line.empty() || line[0] == '#') continue;
        const size_t tab = line.rfind('\t');
        if (tab == std::string::npos) { fprintf(stderr, "C16_ROUTE_B_V2_CONFIG_ERROR malformed code-object manifest\n"); abort(); }
        const std::string path = canonical_or_original(line.substr(0, tab).c_str());
        const std::string sha = line.substr(tab + 1);
        if (path.empty() || !valid_sha(sha) || manifest_sha.count(path) != 0) {
            fprintf(stderr, "C16_ROUTE_B_V2_CONFIG_ERROR invalid/duplicate code-object manifest entry\n"); abort();
        }
        manifest_sha.emplace(path, sha);
    }
    if (manifest_sha.empty()) { fprintf(stderr, "C16_ROUTE_B_V2_CONFIG_ERROR empty code-object manifest\n"); abort(); }
}

static void require_environment() {
    const char* function = getenv("C16_NVBIT_TARGET_FUNCTION_MANGLED");
    const char* path = getenv("C16_NVBIT_STATIC_MAP_PATH");
    const char* manifest = getenv("C16_NVBIT_CODE_OBJECT_MANIFEST");
    const char* registry = getenv("C16_NVBIT_FATBIN_OWNER_REGISTRY_PATH");
    if (function == nullptr || function[0] == '\0' || path == nullptr || path[0] == '\0' || manifest == nullptr || manifest[0] == '\0' || registry == nullptr || registry[0] == '\0') {
        fprintf(stderr, "C16_ROUTE_B_V2_CONFIG_ERROR missing function/map/code-object manifest\n"); abort();
    }
    target_mangled = function; output_path = path; fatbin_registry_path = registry; load_manifest(manifest);
}

static bool owner_from_fatbin_registry(Owner* owner) {
    std::ifstream input(fatbin_registry_path); std::string line;
    while (std::getline(input, line)) {
        const size_t tab = line.find('\t');
        if (tab == std::string::npos || line.substr(0, tab) != target_mangled) continue;
        Owner candidate = owner_from_path(line.substr(tab + 1).c_str(), "cudaRegisterFunction_host_stub");
        if (!candidate.path.empty() && valid_sha(candidate.sha256)) { *owner = candidate; return true; }
    }
    return false;
}

static bool extract_launch_function(nvbit_api_cuda_t callback, void* parameters, CUfunction* function) {
    switch (callback) {
        case API_CUDA_cuLaunch: case API_CUDA_cuLaunchGrid: case API_CUDA_cuLaunchGridAsync:
            *function = static_cast<cuLaunch_params*>(parameters)->f; return true;
        case API_CUDA_cuLaunchKernel_ptsz: case API_CUDA_cuLaunchKernel:
        case API_CUDA_cuLaunchCooperativeKernel: case API_CUDA_cuLaunchCooperativeKernel_ptsz:
            *function = static_cast<cuLaunchKernel_params*>(parameters)->f; return true;
        case API_CUDA_cuLaunchKernelEx: case API_CUDA_cuLaunchKernelEx_ptsz:
            *function = static_cast<cuLaunchKernelEx_params*>(parameters)->f; return true;
        default: return false;
    }
}

static int mref_count(Instr* instruction) {
    int count = 0;
    for (int i = 0; i < instruction->getNumOperands(); ++i)
        if (instruction->getOperand(i)->type == InstrType::OperandType::MREF) ++count;
    return count;
}

static bool global_mref(Instr* instruction) {
    return instruction->getMemorySpace() == InstrType::MemorySpace::GLOBAL && mref_count(instruction) > 0;
}

static void terminal_unresolved(CUmodule module, const char* reason, const Owner* observed = nullptr) {
    if (owner_unresolved.exchange(true)) return;
    fprintf(stderr, "C16_ROUTE_B_V2_CODE_OBJECT_IDENTITY_UNRESOLVED function_mangled=%s module=%p reason=%s owner_path=%s owner_source=%s\n",
            target_mangled.c_str(), reinterpret_cast<void*>(module), reason,
            observed == nullptr ? "UNOBSERVED" : observed->path.c_str(),
            observed == nullptr ? "UNOBSERVED" : observed->source.c_str());
    fflush(stderr);
}

static bool owner_for_function(CUfunction function, Owner* owner) {
    CUmodule module = nullptr;
    const CUresult result = cuFuncGetModule(&module, function);
    if (result != CUDA_SUCCESS || module == nullptr) { terminal_unresolved(module, "cuFuncGetModule_failed"); return false; }
    std::lock_guard<std::mutex> guard(ownership_mutex);
    auto found = module_owners.find(module);
    if (found == module_owners.end()) {
        if (owner_from_fatbin_registry(owner)) return true;
        terminal_unresolved(module, "module_owner_not_observed"); return false;
    }
    if (found->second.path.empty() || !valid_sha(found->second.sha256)) {
        if (owner_from_fatbin_registry(owner)) return true;
        terminal_unresolved(module, "owner_path_or_manifest_sha_missing", &found->second); return false;
    }
    *owner = found->second; return true;
}

static void emit_map(CUcontext context, CUfunction function, const Owner& owner) {
    const std::vector<Instr*>& instructions = nvbit_get_instrs(context, function);
    const std::string full = escape_tsv(nvbit_get_func_name(context, function));
    const std::string mangled = escape_tsv(nvbit_get_func_name(context, function, true));
    if (mangled != target_mangled) return;
    std::ostringstream addr; addr << "0x" << std::hex << nvbit_get_func_addr(context, function);
    const std::string temporary = output_path + ".tmp." + std::to_string(getpid());
    std::ofstream out(temporary, std::ios::out | std::ios::trunc);
    if (!out.good()) { fprintf(stderr, "C16_ROUTE_B_V2_MAP_ERROR open\n"); return; }
    out << "nvbit_static_index\tvector_ordinal\tinstruction_offset\topcode\tmemory_space\tis_load\tis_store\thas_mref\tmref_count\tsass\tfunction_full_name\tfunction_mangled_name\tfunction_address\tcode_object_path\tcode_object_sha256\n";
    for (size_t ordinal = 0; ordinal < instructions.size(); ++ordinal) {
        Instr* instruction = instructions[ordinal]; const int mrefs = mref_count(instruction);
        out << instruction->getIdx() << '\t' << ordinal << '\t' << instruction->getOffset() << '\t'
            << escape_tsv(instruction->getOpcode()) << '\t'
            << InstrType::MemorySpaceStr[static_cast<int>(instruction->getMemorySpace())] << '\t'
            << (instruction->isLoad() ? 1 : 0) << '\t' << (instruction->isStore() ? 1 : 0) << '\t'
            << (mrefs > 0 ? 1 : 0) << '\t' << mrefs << '\t' << escape_tsv(instruction->getSass()) << '\t'
            << full << '\t' << mangled << '\t' << addr.str() << '\t' << owner.path << '\t' << owner.sha256 << '\n';
    }
    out.close();
    if (!out.good() || rename(temporary.c_str(), output_path.c_str()) != 0) { unlink(temporary.c_str()); fprintf(stderr, "C16_ROUTE_B_V2_MAP_ERROR finalize\n"); return; }
    map_emitted.store(true);
    printf("C16_ROUTE_B_V2_MAP_COMPLETE function_mangled=%s static_instruction_count=%zu owner_path=%s owner_sha256=%s map=%s\n",
           mangled.c_str(), instructions.size(), owner.path.c_str(), owner.sha256.c_str(), output_path.c_str()); fflush(stdout);
}

static void observe_library_callback(int is_exit, nvbit_api_cuda_t callback, void* parameters) {
    if (callback == API_CUDA_cuLibraryLoadData) {
        auto* p = static_cast<cuLibraryLoadData_params*>(parameters);
        std::lock_guard<std::mutex> guard(ownership_mutex);
        if (!is_exit) { Dl_info info{}; if (p->code != nullptr && dladdr(p->code, &info) != 0) pending_loads[parameters] = owner_from_path(info.dli_fname, "cuLibraryLoadData_dladdr"); }
        else if (p->library != nullptr) { auto it = pending_loads.find(parameters); if (it != pending_loads.end()) { library_owners[*p->library] = it->second; pending_loads.erase(it); } }
    } else if (callback == API_CUDA_cuLibraryLoadFromFile) {
        auto* p = static_cast<cuLibraryLoadFromFile_params*>(parameters);
        std::lock_guard<std::mutex> guard(ownership_mutex);
        if (!is_exit) pending_loads[parameters] = owner_from_path(p->fileName, "cuLibraryLoadFromFile");
        else if (p->library != nullptr) { auto it = pending_loads.find(parameters); if (it != pending_loads.end()) { library_owners[*p->library] = it->second; pending_loads.erase(it); } }
    } else if (callback == API_CUDA_cuLibraryGetModule && is_exit) {
        auto* p = static_cast<cuLibraryGetModule_params*>(parameters);
        if (p->pMod == nullptr) return;
        std::lock_guard<std::mutex> guard(ownership_mutex);
        auto it = library_owners.find(p->library);
        if (it != library_owners.end()) module_owners[*p->pMod] = it->second;
    }
}

// PyTorch extension and ATen kernels commonly arrive through cuModuleLoadData
// rather than the CUDA 12 cuLibrary API.  Treat both loader families as
// ownership evidence; neither path is inferred from a caller-provided DSO.
static void observe_module_load_callback(int is_exit, nvbit_api_cuda_t callback, void* parameters) {
    std::lock_guard<std::mutex> guard(ownership_mutex);
    if (callback == API_CUDA_cuModuleLoadData || callback == API_CUDA_cuModuleLoadDataEx || callback == API_CUDA_cuModuleLoadFatBinary) {
        CUmodule* module = nullptr; const void* image = nullptr;
        if (callback == API_CUDA_cuModuleLoadData) { auto* p = static_cast<cuModuleLoadData_params*>(parameters); module = p->module; image = p->image; }
        else if (callback == API_CUDA_cuModuleLoadDataEx) { auto* p = static_cast<cuModuleLoadDataEx_params*>(parameters); module = p->module; image = p->image; }
        else { auto* p = static_cast<cuModuleLoadFatBinary_params*>(parameters); module = p->module; image = p->fatCubin; }
        if (!is_exit) { Dl_info info{}; if (image != nullptr && dladdr(image, &info) != 0) pending_loads[parameters] = owner_from_path(info.dli_fname, "cuModuleLoadData_dladdr"); }
        else if (module != nullptr) { auto it = pending_loads.find(parameters); if (it != pending_loads.end()) { module_owners[*module] = it->second; pending_loads.erase(it); } }
    } else if (callback == API_CUDA_cuModuleLoad) {
        auto* p = static_cast<cuModuleLoad_params*>(parameters);
        if (!is_exit) pending_loads[parameters] = owner_from_path(p->fname, "cuModuleLoad_file");
        else if (p->module != nullptr) { auto it = pending_loads.find(parameters); if (it != pending_loads.end()) { module_owners[*p->module] = it->second; pending_loads.erase(it); } }
    }
}

void nvbit_at_init() { require_environment(); printf("C16_ROUTE_B_V2_MAP_TOOL_READY manifest_entries=%zu\n", manifest_sha.size()); fflush(stdout); }

void nvbit_at_cuda_event(CUcontext context, int is_exit, nvbit_api_cuda_t callback, const char*, void* parameters, CUresult*) {
    if (callback == API_CUDA_cuLibraryLoadData || callback == API_CUDA_cuLibraryLoadFromFile || callback == API_CUDA_cuLibraryGetModule) { observe_library_callback(is_exit, callback, parameters); return; }
    if (callback == API_CUDA_cuModuleLoad || callback == API_CUDA_cuModuleLoadData || callback == API_CUDA_cuModuleLoadDataEx || callback == API_CUDA_cuModuleLoadFatBinary) { observe_module_load_callback(is_exit, callback, parameters); return; }
    if (is_exit || map_emitted.load() || owner_unresolved.load()) return;
    CUfunction function = nullptr;
    if (!extract_launch_function(callback, parameters, &function) || function == nullptr) return;
    const std::string mangled = nvbit_get_func_name(context, function, true);
    if (mangled != target_mangled) return;
    Owner owner; if (!owner_for_function(function, &owner)) return;
    emit_map(context, function, owner);
}

void nvbit_at_term() { printf("C16_ROUTE_B_V2_MAP_TERMINAL emitted=%d owner_unresolved=%d\n", map_emitted.load() ? 1 : 0, owner_unresolved.load() ? 1 : 0); fflush(stdout); }
