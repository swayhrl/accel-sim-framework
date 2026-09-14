# C16 RTX4080 userspace runtime receipts (U1–U3)

## U1 — CPython 3.10.12

`PASS_USERSPACE_CPYTHON310_BUILD`

- Prefix: `/data/c16/env/cpython-3.10.12`
- Dependency prefix: `/data/c16/env/build-deps-cpython310`
- CPython source SHA256: `a43cd383f3999a6f4a7db2062b2fc9594fefa73e175b3aedafa295a51a7bb65c`
- Successful repair receipt: `/data/c16/results/C16_U1_CPYTHON310_RPATH_REPAIR2_20260914T102135Z`
- Successful repair receipt SHA256 manifest: `12f5a5f4714537848bdbbe590d4d0177f64d47e69d38023e7ba373d35bd03f0d`

The initial install exposed a private shared-library RUNPATH error. It was repaired
in userspace; CPython imports `bz2`, `ctypes`, `lzma`, `readline`, `sqlite3`,
`ssl`, and `zlib` with the recorded user environment:

```text
LD_LIBRARY_PATH=/data/c16/env/cpython-3.10.12/lib:/data/c16/env/build-deps-cpython310/lib
```

These are new RTX4080 userspace build commands, not claimed historical commands.

## U2 — exact 66-wheel runtime closure

`PASS_HASH_CLOSED_OFFLINE_RUNTIME`

- Wheelhouse: `/data/c16/wheelhouse/c16-g-cp310-cu124` (66 wheels)
- Manifest SHA256: `ebae0934de68b36e08da5db0e6bfdc47880620205e8bf6d8c8afe8906abc2d2d`
- Requirements SHA256: `8085caecebf1e641cb6ab1f2c0e2d8e8cfd5007fd8236b6c10771b223052fa82`
- Materialization receipt: `/data/c16/results/C16_U2_WHEELHOUSE_MATERIALIZE_20260914T103049Z`
- Offline-install receipt: `/data/c16/results/C16_U2_OFFLINE_INSTALL_20260914T103139Z`
- Offline `pip check`: `No broken requirements found.`

Verified imports: Python 3.10.12; torch `2.5.1+cu124` with CUDA build `12.4`;
transformers `4.46.3`; AutoAWQ `0.2.7.post3`. `libtorch_cuda.so` SHA256 is the
known-good `761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a`.

## U3 — PyTorch CUDA canary

`C16_U3_PYTORCH_CUDA_CANARY_PASS`

- Source: `util/vm_tlb/c16/host_4080/c16_pytorch_cuda_canary.py`
- Source SHA256: `f6fc08146b57c1738e52a0a271c76ddd0c0b278bc86a01c60170c5f7ec6a9dda`
- Successful receipt: `/data/c16/results/C16_U3_PYTORCH_CUDA_CANARY_20260914T103459Z`
- Receipt SHA256 manifest: `4c6546fc71c21bca28f7e8f4e1923ae1651bfea2e430ef70f9b79d8dece01156`

The successful fixture set `CUDA_MODULE_LOADING=EAGER`, bound
`CUDA_VISIBLE_DEVICES=GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`, and used
`CUBLAS_WORKSPACE_CONFIG=:4096:8` for deterministic GEMM. It observed RTX 4080
CC 8.9 as `cuda:0`, kept all tensors CUDA resident, and produced elementwise
checksum `28672.0` and GEMM checksum `17178123264.0`.

The prior U3 directory `C16_U3_PYTORCH_CUDA_CANARY_20260914T103401Z` preserves the
first deterministic-GEMM failure, whose direct cause was the missing user-level
`CUBLAS_WORKSPACE_CONFIG`; no host change was needed.
