# Retry570 NVBit callback-bookkeeping root cause

Status: `NVBIT_CORE_MODULE_BOOKKEEPING_PATHOLOGY_CONFIRMED`.

This publication ran only the exact diagnostic `torch.index_select` reproducer. No model/Llama/Qwen, trace, C target, scientific capture, timing result, 300-second watch, or historical 6+6 window ran.

The decisive table is `old census = HANG`, `TRUE RAW = HANG`, and `EMPTY = HANG`. TRUE RAW records only preallocated POD events: 196 entries, zero drops, maximum callback depth 1, zero reentrancy, and final retained event `cuLibraryGetModule` entry. Callback names were decoded after process exit.

EMPTY contains only `nvbit_at_cuda_event(...) { return; }`. Its 5-second GDB snapshot is `std::_Hash_bytes -> elfModuleHashMap::operator[] -> Nvbit::module_loaded -> nvbitToolsCallbackFunc` in injected NVBit 1.8 core. The hot path is neither the RAW recorder nor Lane G's targeted memory tool.

Vendor provenance: `core/libnvbit.a` SHA256 `db221829106673bcd69d1e05766136f80e2df4497fb8415d8c2f298b96c302f7`; `Nvbit::module_loaded` is `nvbit_imp.o`, and `elfModuleHashMap` is `tools_shared_readelf_caches.o`. The vendor archive exposes only embedded name `nvbit.cpp`, not DWARF source lines; this report makes no FILE:LINE or private-STL-layout claim.

TRUE RAW wall accounting: target 25.302602s; remote transaction 25.416366s; local SSH 27.138402s. EMPTY: target 25.317044s; remote transaction 25.423447s; local SSH 25.933204s. Each child process group received TERM at 25s and exited during 2s grace; no KILL was needed.

One-time versus repeated is not determined within this 25-second authorization: the exact first use never returned, while historical EAGER callback-only shifted work before exact marker and also did not complete under short cap. EAGER/prewarm is therefore not ready before `MEASUREMENT_ACTIVE`; a separately authorized bounded finite-completion characterization is required.
