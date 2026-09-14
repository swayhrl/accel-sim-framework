# C16 RTX4080 host acceptance checklist

This checklist accepts only a new, separately recorded RTX4080 environment. It never treats the RTX3090 hashes as proof that a different GPU, driver, code object, or target map is equivalent.

## Host and Docker

- [ ] Record host OS, kernel, CPU/RAM, disk free space, GPU UUID, GPU model, compute capability, driver, and `nvidia-smi` output in a new receipt.
- [ ] Bind exactly one selected RTX4080 UUID to logical `cuda:0`; record the `CUDA_VISIBLE_DEVICES` value and UUID-to-logical mapping. Do not rely on PCI order.
- [ ] Verify driver compatibility with CUDA 12.4; record `nvcc --version` and `nvdisasm --version`.
- [ ] Record immutable image digest, Docker runtime, mounted model/wheel/raw roots, and container command. Do not use an image tag alone.
- [ ] Ensure at least 100 GiB free in both the capture and copyback locations before a formal multi-window campaign. A smaller disk permits only a separately bounded canary.
- [ ] Prove no stale compute process and no stale `MEASUREMENT_ACTIVE` before every window.

## Runtime and wheelhouse

- [ ] Install only with the 66-wheel manifest SHA `ebae0934de68b36e08da5db0e6bfdc47880620205e8bf6d8c8afe8906abc2d2d` and requirements SHA `8085caecebf1e641cb6ab1f2c0e2d8e8cfd5007fd8236b6c10771b223052fa82`, or explicitly record a new, non-equivalent closure.
- [ ] Verify CPython 3.10.12, torch `2.5.1+cu124`, transformers `4.46.3`, AutoAWQ `0.2.7.post3`, and `torch.version.cuda == 12.4`.
- [ ] Hash `libtorch_cuda.so`; acceptance value is `761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a` only for the known-good package closure.
- [ ] Set `CUDA_MODULE_LOADING=EAGER` before Python starts; record PATH and LD_LIBRARY_PATH rather than inheriting an unrecorded shell.
- [ ] Verify CUDA availability and that every model parameter is CUDA-resident; reject CPU offload and backend/dtype substitution.

## NCU

- [ ] Record `ncu --version` and a bounded baseline CUDA fixture result.
- [ ] Run one bounded tiny metric canary only after permission confirmation. The historical RTX3090 result was `ERR_NVGPUCTRPERM` under NCU `2024.1.1.0`; it is a capability limitation, not a performance result.
- [ ] If the 4080 returns a permission error, record it and stop NCU retries; do not vary root, metrics, targets, or privileges opportunistically.
- [ ] If permitted, freeze the exact metric/command/report SHA before any model NCU work.

## NVBit

- [ ] Verify NVBit 1.7.5 archive SHA `e2290da5e35a43fc4c74917dd08e1d41ece3e21bfca6fd7c6dc590c9c8385328` and `core/libnvbit.a` SHA `562348c32b88bf3e5b32d1895202893adb79f32b896e3cac56b29a306de40a12`.
- [ ] Verify tracer source/binary tuple `ac4f678a815954e4ddb22c15d9a8d3841fca86a3` / `414bdeebebf807a1134a53079ed0b7eee47e7fb3eda72250da25b445f5876ab4` / `9e059b6a5b17a74e597169e365ad05d1e82517decad9974868b2b8a195132ae5`, or produce a new qualified tool closure.
- [ ] Run official `instr_count_bb` and a no-match tracer smoke as diagnostic gates; do not equate either with model capture.
- [ ] Use EAGER; reject LAZY as a known-good model setting. Treat NVBit 1.7.6 and 1.8 only as diagnostic comparisons.
- [ ] Run a bounded zero-trace/no-match prewarm outside measurement. Require normal exit, zero trace files, zero surviving child/GPU process, and `READY` before arming capture.

## PyTorch model canary and raw handoff

- [ ] Verify exact model revision, frozen input/token receipt, dtype, attention backend, no-offload policy, and output checksum before NVBit is armed.
- [ ] Re-map the exact live 4080 function/static instruction from the locally hashed `libtorch_cuda.so`; never reuse the RTX3090 kernel ID, static range, or `DYNAMIC_KERNEL_RANGE` as a guess.
- [ ] Parent creates `MEASUREMENT_ACTIVE` only after READY and a no-pre-arm-trace check; child capture must be bounded and process-group cleaned up on failure.
- [ ] Require at least one exact target trace with complete schema, final newline, address-bearing rows, expected function/static binding, and checksum-stable output.
- [ ] For each raw item: remote SHA/size → copyback → local SHA/size → equality receipt → manifest validation. Keep raw out of Git; retain remote data until the local closure is complete.
- [ ] A successful 4080 canary is a new evidence record, not a retroactive change to any Recovery-V3 scientific asset.
