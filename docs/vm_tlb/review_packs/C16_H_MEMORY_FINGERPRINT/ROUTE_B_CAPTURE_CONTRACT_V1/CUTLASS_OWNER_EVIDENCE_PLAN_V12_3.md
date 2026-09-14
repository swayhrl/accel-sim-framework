# Llama S0 CUTLASS owner-evidence retry plan (V12.3)

This is a CPU-only plan for the two terminally unresolved V2 requests.  It
does not change their status, selection denominators, or final-request IDs.

| request | phase | exact runtime mangle | current status |
| --- | --- | --- | --- |
| `LLAMA_S0_G1_V2_944c439ce7856ba1` | Decode | `_ZN7cutlass7Kernel2I66cutlass_80_wmma_tensorop_f16_s161616gemm_f16_16x16_128x1_tn_align8EEvNT_6ParamsE` | `FAILED_CLOSED / CODE_OBJECT_IDENTITY_UNRESOLVED` |
| `LLAMA_S0_G1_V2_b7ce44b72eb0e85e` | Prefill | `_ZN7cutlass7Kernel2I66cutlass_80_tensorop_f16_s16816gemm_relu_f16_128x128_32x5_tn_align8EEvNT_6ParamsE` | `FAILED_CLOSED / CODE_OBJECT_IDENTITY_UNRESOLVED` |

## Prior evidence, and its limit

The V2 mapper already establishes `CUfunction -> CUmodule` with
`cuFuncGetModule`; records `cuModuleLoad*` and cuLibrary module-handle chains;
and has a hash-closed `__cudaRegisterFunction` exact-device-name to host-DSO
fallback.  Its loader evidence relies on `dladdr(image)`.  The two CUTLASS
modules did not yield an owner accepted by any of those chains.  The Q1 tiny
fixture's exact host-symbol receipt is not evidence for either CUTLASS mangle
and must not be reused.

## Retry A: registered-fatbin content chain

Add a bounded registration observer which records, for every *successful*
`__cudaRegisterFatBinary`/`__cudaRegisterFunction` pair:

```text
fatbin_handle, exact_device_mangle, fatbin_content_sha256,
registration-caller DSO path, registration-caller DSO SHA256
```

The image digest is permitted only after a format-specific, bounds-checked
fatbin parser obtains an exact span; unknown, truncated, or ambiguous headers
are terminal-unresolved.  Before retry, freeze an inventory mapping each
allowed DSO SHA to its embedded fatbin-content SHA(s).  A map may close only
if the target's exact observed mangle has one unique registration row and its
image digest has one unique inventory owner.  The `CUfunction` mangle and its
`CUmodule` from the existing mapper remain mandatory.

**New direct evidence versus the previous attempt:** the previous fatbin
registry held only `device_name -> dladdr(host)`.  This retry adds the opaque
registration handle and a content digest of the actual registered CUDA image,
which is independently joined to a frozen embedded-image inventory.  A caller
return address alone is diagnostic only and never closes ownership.

## Retry B: module-loader image content chain

For `cuModuleLoadData`, `cuModuleLoadDataEx`, `cuModuleLoadFatBinary`, and
`cuLibraryLoadData`, retain the returned module/library handle and attempt a
format-specific, bounds-checked digest of the submitted image.  Freeze a
separate `image_content_sha256 -> {code_object_path, code_object_sha256}`
manifest before the run.  Closure requires this exact chain:

```text
target CUfunction --cuFuncGetModule--> CUmodule
CUmodule <--successful loader return-- submitted image digest
submitted image digest --unique frozen manifest--> code-object path + SHA
```

cuLibrary additionally requires its same-handle `cuLibraryGetModule` edge.
No unbounded memory read, `dladdr(image)`, name-only join, caller-DSO, or
"last loader" state may substitute for this chain.

**New direct evidence versus the previous attempt:** the prior loader path
only asked the process loader to name the address carrying the image.  This
retry retains the actual driver loader handle and cryptographically binds the
loaded image bytes to a pre-frozen content inventory.  It can therefore close
heap/JIT-backed images only when their bytes match a declared code object, and
otherwise remains fail-closed.

## Bounded disposition

Run at most one targeted map attempt per unresolved exact function per retry
mechanism.  A terminal receipt must contain the exact function/mangle,
`CUmodule` handle, applicable handle-chain fields, image digest, matched path
and SHA, and the observer binary SHA.  Failure leaves both original rows
`FAILED_CLOSED`; no coverage denominator may be reduced and no nearby CUTLASS
kernel may replace either row.
