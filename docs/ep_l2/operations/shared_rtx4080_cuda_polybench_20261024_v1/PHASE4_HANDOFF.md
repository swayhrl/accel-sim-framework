# Phase 4: real Vulkan/NvSci routes and full-image native reference

This increment follows source commit 05deed354421978d2592308d8c296f9a6a194e78. All native probes pending at the phase 3 checkpoint have now completed under the existing cooperative GPU lock after the bulk stencil job released it. This lane still has produced no production trace or simulator result.

## Complete fixed v11.8 scope update

`phase4_evidence/manifests/CUDA_V118_FULL205_ACTUAL_BUILD_ROUTES_V2.json` updates the frozen 205-program scope from 186 to 187 program names with actual ELF build routes. Eighteen names retain their explicit Windows D3D, QNX Screen, DLA, NvMedia or Tegra-only EGLSync prerequisites. The earlier NvSci dependency gap is resolved with an actual official x86 package and unchanged-source native execution. Build, actual native numerical quality, exact input identity and producer/consumer semantics remain independent qualifications.

NVIDIA's official [Jetson r38.4 host package documentation](https://docs.nvidia.com/jetson/archives/r38.4/DeveloperGuide/SD/SoftwarePackagesAndTheUpdateMechanism.html#updating-a-host) lists NvSci for x86 Ubuntu hosts. The public repository actually supplies `nvsci_7.0.4.0_amd64.deb`, 2,295,100 bytes, SHA256 `a4131d6efa8ed1424e7e72f78e75ba436cde9f625655ec362f2eb35419ce2b2c`. Its SHA matches the official HTTPS Packages index. The package contains actual x86 NvSciBuf/NvSciSync and dependency libraries plus headers. Private `dpkg-deb -x` extraction executed no package scripts and changed no system libraries, services, kernel modules or devices. The direct109 acquisition timeout and successful local-network/SSH fallback are preserved as separate receipts.

The original fixed v11.8 cudaNvSci source builds without source changes into an sm89 ELF. Its original default teapot input is 1024x1024. Actual native execution created the NvSci buffer, image and synchronization objects on the RTX4080, rotated the image, converted it to grayscale through two host-thread streams, and wrote the final PPM with exit zero. This is actual interoperability capability evidence; API symbol presence was only an earlier preflight.

## Numerical validation

`phase4_evidence/nvsci_full_image_cpu_reference_v1/PROOF.json` independently checks all 1,048,576 output pixels and all 3,145,728 RGB channels against a scalar mathematical reference for theta0.5 rotation, normalized wrap texture coordinates, half-texel bilinear filtering, byte conversion and grayscale. Epsilon4 was fixed before observing the output, with no fraction of mismatches allowed. Actual maximum error is 1: 3,123,684 channels are equal and 22,044 differ by 1. Every pixel has equal R/G/B.

The reference tolerance accounts for the texture interpolator's documented [8 fractional bits](https://docs.nvidia.com/cuda/archive/12.9.1/cuda-c-programming-guide/index.html#linear-filtering) and integer conversion. It is bounded full-image numerical agreement, not bit-exact texture implementation or a trace semantic qualification. The original GPU/native output remains unchanged. The reusable CPU CLI verifies source and runtime input hashes, shape, full output and its own identity; deliberate input-byte and output-pixel corruptions both return rejection exit2. Frozen CLI and proofs are included in this increment.

The official4.2.9 histogram now also has a separate successful native variant enabling the source's own `USE_SMEM_ATOMICS` branch. Its original canonical warp-tag algorithm failure remains retained. Full default 67,108,864-byte input and 16 benchmark runs are preserved, and every 64-bin and 256-bin CPU reference count matches. This variant changes GPU source and requires a shared-atomic semantic profile.

## Actual Vulkan route

The private owned Xvfb display successfully presented Vulkan output rendered by the NVIDIA RTX4080, with actual device UUID `ce6cba36-415b-4e27-40e2-bded6bc1ee59` checked in vulkaninfo and actual NVIDIA vkcube rendering. Xvfb is only a display transport; software GPU rendering is not accepted. Original canonical interactive programs remain preserved.

Three separate host variants now execute exactly four displayed-frame draw calls with original computation/window/image dimensions and checked final CUDA completion:

- simpleVulkan: original 256x256 wave mesh.
- simpleVulkanMMAP: original 50,000 Monte Carlo points per call, four calls totaling 200,000 reported points.
- vulkanImageCUDA: original 1024x1024 teapot input and 800x600 window.

The wave/MonteCarlo host simulation time is explicitly fixed to frame_index/60, so these are new input/time variants. Source patches modify only host loop/time/completion code; the extracted 1, 1 and 4 device function bodies respectively remain byte-identical to the original source. The wrapper, actual application ELF, shader inputs, source and private runtime dependencies all have distinct fixed hashes. The Python wrapper identity cannot substitute for loaded CUDA module identity. Four-frame completion and API success do not prove full pixel or mathematical correctness for these three graphics variants.

The original simpleGLES_EGLOutput finite file-QA branch also exits zero and reports its original prefix comparison OK. It executes no interactive DRM/display path. The source's limited output/reference extent remains explicit; no full mesh comparison is claimed.

All Vulkan, EGL and NvSci external graphics/buffer/image/semaphore initialization remains outside the c8 HtoD-only input profile. Ordinary producer admission does not silently expand to these special resource lifetimes.

## Incremental import, archive and integrity

`STAGE3_INCREMENTAL_NATIVE_CANDIDATES_V3.json` preserves all 186 previous content IDs and adds 6 completed contents: EGLOutput file-QA, unchanged-source NvSci, the official histogram shared-atomic variant and the three finite Vulkan variants. There are now 192 contents from 222 audited attempts in this incremental family, separate from the original baseline. The Vulkan display capability canary is a qualification task and is not counted as a workload. The NvSci later numerical proof is an overlay on the same content identity; no native receipt or earlier status record was rewritten.

`COLD_ARCHIVE_PHASE4_INCREMENTAL_MEMBER_MANIFEST_V1.json` lists 2,497 unique regular-file contents totaling 3,043,470,182 bytes, with SHA256, sizes, frozen mtimes and aliases, plus 784 previous/source input references. Original source archives are stored once, installed dependency prefixes are not duplicated when their original debs are retained, and closed source variants/ELFs/native outputs/oracle evidence remain SourceKEEP. The bulk coordinator owns the sole NAS sender. This manifest is an inventory and no deletion authorization receipt.

`PHASE4_REVIEW_EXPORT_RECEIPT_V1.json` maps every Git evidence member back to its source path/SHA and references byte-identical earlier evidence. Production traces, full dependency packages and source archives are not embedded in Git. A fresh isolated no-alternates reachable strict fsck is required before bundle delivery; original source/log whitespace remains byte-identical rather than reformatted.
