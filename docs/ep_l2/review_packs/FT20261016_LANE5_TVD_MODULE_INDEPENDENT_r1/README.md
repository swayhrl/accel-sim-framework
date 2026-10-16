# Lane 5 independent Lane 2 module validation r1

Status: **MODULE_ONLY_PASS / PRODUCTION_INTEGRATION_PENDING**.

Frozen producer Core: `56abbacc1192d68995e78561899719649f838079`.
Independent Lane 5 consumer test: `08b8cb72` (full SHA in SOURCE_MANIFEST).
Exact producer Framework publication, consumed receipt and all binary/input/log
hashes are retained in this pack. No live producer working tree was rebuilt.

Executed under a shared one-CPU / 4-GiB build lease, subsequently released:

1. Producer's seven directory/payload-bank scenario groups, normal: PASS.
2. Same producer fixture, ASan+UBSan: PASS.
3. Consumer-owned handle-indexed 32-byte sector/version reference, normal: PASS.
4. Same consumer reference, ASan+UBSan: PASS.

The consumer compares bytes at the handle actually returned by the module
against an independent address/version expectation, including a changed version
after same-handle promotion. It checks lookup delay, partial-sector refusal,
dirty-inflight read forwarding, write/atomic wait classification, true lower
data-handoff gate, exact-once response, stale incarnation and final directory
cleanup. Atomic numeric execution and full cache producer wiring are not tested.

## Execution reproduction

Extract `src/`, `tests/ep_l2/run_tvd_directory.sh` and
`tests/ep_l2/test_tvd_directory.cc` from the frozen Core commit using git archive
into a private snapshot. Set EP_L2_LANE2_BUILD to separate normal/sanitizer output
directories. Run the script with EP_L2_SANITIZE=0 and then =1.

Consumer compile: g++ -std=c++11 -Wall -Wextra -Werror -O1 -g,
include snapshot/src, compile util/ep_l2/ft_lane5/test_tvd_consumer.cc;
sanitizer adds -fsanitize=address,undefined -fno-omit-frame-pointer.
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1;
UBSAN_OPTIONS=halt_on_error=1. Exact compile commands are in RESULTS.json.

Raw source snapshot and outputs remain at
`/workspace/results/ep_l2_ft20261016/lane5_lane2_independent_r1/`.
These are production-linkable directory module checks, not calls through
`l2_cache::access`, real victim generation, WAD preview bypass, or ICNT response
enqueue. No U_WB_TVD16 result, cache-data correctness qualification or performance
speedup is established by this pack. The new formal experiment count remains 0.
