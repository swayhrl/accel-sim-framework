# ROUTE_B_Q1_INTEGRATION_READY

This is a CPU-built, GPU-unexecuted Route-B Q1 handoff.  It is independent of
the blocked representative-selection disposition.  Lane A alone may execute
the commands below on the RTX3090.

## Frozen source authority

| item | path | SHA-256 |
| --- | --- | --- |
| Q1 fixture source | `util/vm_tlb/c16/lane_g/fixtures/route_b_q1_tiny.cu` | `5bd873b3fc5e339fba8a594a635ab4237a0eb5540c7d753a2ebfece32875d40d` |
| Route-B host tool | `util/vm_tlb/c16/lane_g/route_b_memory_event_tool.cu` | `f3802a418c739060b2e0116a5ad91e3b2df3d7132d5bb9f884c377b8ce289b4e` |
| Route-B device callback | `util/vm_tlb/c16/lane_g/route_b_memory_event_inject.cu` | `b2c5f174a728bd0fb57ae57d6cd3ddaf37b5594cae0fda054493b194ea863876` |
| Q1 static-whitelist freezer | `util/vm_tlb/c16/lane_g/route_b_q1_fixture.py` | `1ad9162d4346cc0d144d4342afedcd4e73d9b546fdf37d3b9b6d6185dbb5f716` |

Exact runtime function: `c16_route_b_q1_global_ldst_predicate`.

The fixture does two launches of that exact function.  It contains direct
`uint32_t` GLOBAL source/destination accesses, so its frozen source defines a
four-byte access width; the whitelist freezer refuses to infer width from
opcode text.  Its predicate is `threadIdx.x % 3 != 1`.  The expected checksum
is `044a6de6746b6ab2`.

## CPU validation already completed

```text
python3 -m unittest tests/vm_tlb/c16/lane_g/test_route_b_memory_event_contract.py \
  tests/vm_tlb/c16/lane_g/test_route_b_memory_event_host.py \
  tests/vm_tlb/c16/lane_g/test_route_b_producer_q0.py \
  tests/vm_tlb/c16/lane_g/test_route_b_q1_fixture.py
# 18 tests: OK

make -C util/vm_tlb/c16/lane_g/fixtures -f Makefile.route_b_q1_tiny \
  NVCC=/usr/local/cuda-11.8/bin/nvcc OUT=/tmp/c16_route_b_q1_tiny_cpu_build
# PASS; CPU-build artifact SHA-256:
# 0fac79b2cb17d2c16aabdcf8430231560b8498c4f152857387dc2f464a03c919
```

The local CPU worktree has CUDA 11.8 but not an NVBit 1.7.5 installation, so
the NVBit shared object was not locally linked.  Lane A must build it against
its hash-closed NVBit 1.7.5 root, then bind the resulting fixture executable
SHA (not the CPU-build artifact SHA above) in its producer manifest.

## Lane-A Q1 execution sequence

Use a fresh, empty Q1 run directory and retain all files named below.  The
numbers are deliberately bounded: event capacity `512`, actual raw JSONL cap
`1048576` bytes.

```bash
Q1_ROOT=/root/autodl-tmp/c16_retry570/route_b_q1
mkdir -p "$Q1_ROOT"

make -C util/vm_tlb/c16/lane_g/fixtures -f Makefile.route_b_q1_tiny \
  NVCC=nvcc ARCH=sm_86 OUT="$Q1_ROOT/route_b_q1_tiny"
sha256sum "$Q1_ROOT/route_b_q1_tiny" | tee "$Q1_ROOT/fixture.sha256"

# The V2 map tool must observe the actual owner, never receive a guessed one.
printf '%s\t%s\n' "$Q1_ROOT/route_b_q1_tiny" "$(sha256sum "$Q1_ROOT/route_b_q1_tiny" | awk '{print $1}')" > "$Q1_ROOT/code_objects.tsv"
printf '%s\t%s\n' c16_route_b_q1_global_ldst_predicate "$Q1_ROOT/route_b_q1_tiny" > "$Q1_ROOT/fatbin_owners.tsv"
make -C util/vm_tlb/c16/lane_g -f Makefile.retry570_route_b_v2_static_map_tool \
  NVBIT_HOME="$NVBIT_HOME" ARCH=sm_86 OUT="$Q1_ROOT/static_map.so"
C16_NVBIT_TARGET_FUNCTION_MANGLED=c16_route_b_q1_global_ldst_predicate \
C16_NVBIT_STATIC_MAP_PATH="$Q1_ROOT/EXACT_FUNCTION_STATIC_MAP.tsv" \
C16_NVBIT_CODE_OBJECT_MANIFEST="$Q1_ROOT/code_objects.tsv" \
C16_NVBIT_FATBIN_OWNER_REGISTRY_PATH="$Q1_ROOT/fatbin_owners.tsv" \
LD_PRELOAD="$Q1_ROOT/static_map.so" "$Q1_ROOT/route_b_q1_tiny"

python3 util/vm_tlb/c16/lane_g/route_b_q1_fixture.py \
  --static-map "$Q1_ROOT/EXACT_FUNCTION_STATIC_MAP.tsv" \
  --code-object "$Q1_ROOT/route_b_q1_tiny" \
  --whitelist-json "$Q1_ROOT/whitelist.json" \
  --whitelist-tsv "$Q1_ROOT/whitelist.tsv" | tee "$Q1_ROOT/whitelist_receipt.json"

make -C util/vm_tlb/c16/lane_g -f Makefile.route_b_memory_event_tool \
  NVBIT_HOME="$NVBIT_HOME" ARCH=sm_86 OUT="$Q1_ROOT/route_b_memory_event_tool.so"
```

Before the capture run, call `write_verified_producer_manifest` with the
fixture executable SHA, exact static-map SHA, Q1 whitelist SHA, and cap
`1048576`.  Then run the same fixture once under the Route-B tool with:

```text
C16_ROUTE_B_EXACT_FUNCTION_MANGLED=c16_route_b_q1_global_ldst_predicate
C16_ROUTE_B_EVENT_CAPACITY=512
C16_ROUTE_B_HOST_OUTPUT_CAP_BYTES=1048576
C16_ROUTE_B_WHITELIST_TSV=$Q1_ROOT/whitelist.tsv
C16_ROUTE_B_RAW_JSONL=$Q1_ROOT/raw.jsonl
```

Also supply the verified-manifest, run/deployment/scenario/phase/decode-step
environment variables required by `route_b_memory_event_tool.cu`.  Parse only
with `write_parse_manifest`; acceptance requires exactly one `COMPLETE`
terminal, `overflow_count=0`, `drop_count=0`, terminal `event_count` equal to
the decoded LANE_EVENT count, and `stat(raw.jsonl).st_size <= 1048576`.

The tool serializes `events_already_serialized + launch_local_sequence` and
the parser groups dynamic warp instances by
`(kernel_launch_id, warp_instruction_instance_id)`.  Thus the two fixture
launches intentionally exercise both buffer-reset hazards without claiming
hardware-global ordering.
