# B — source r3; real functional validation remains incomplete

Original174, authority d9263fa2431592b33e900d9b48c6f20029d8b544, same isolated
B branch. Exact current Core/remote tree/file proof is in RECEIPT.json.
Previous clean89a75b24, r2 b90ed7c1, Framework3174a3287 and review packs r1/r2,
old RO/parameter candidates/raw/ledgers remain preserved. Goal stays active.

This increment fixes a concrete source state gap: if a WB was already accepted,
its payload is roleTVD/TVD_INFLIGHT before a later reader pins it. set_done
while that reader is blocked defers state change. R2 response_commit completed
only roleWB, potentially leaving this roleTVD slot INFLIGHT after last unpin.
R3 finishes exact directory-matched state for BOTH roles, after actual enqueue
and unpin, with stable handle/generation and no extra data/response storage.
This is SOURCE reasoning; old/new native failure/pass has not been observed.

New real-path test SOURCES: genuine63+1 cache responses fill the existing64-entry
ICNT FIFO while a victim bank token/pin is held, real done occurs, then response
retirement must publish TVD_VALID exactly once. A separate CLEAN_ONLY case
reuses the old accepted WB slot through an actual native fill with new generation,
checks immutable packet, same-address wait/no duplicate lower issue and old done
preserving the new owner. Explicit public-arbiter contention is a constructed
case, not an application opportunity. Existing bank-full/partial-dirty native
cases now have a separate finite selector. All21 process inputs are NOT_RUN.

A integration friction reduced: new adapter_A44_r3 is based on exact frozen
A44c940b7 rather than84359d4. Separate-index git apply --cached --check passes;
real index and six actual public B source files are unchanged. A's independent
diagnostic/observer source is preserved; new guard explicitly rejects TVD plus
local diagnostic/observer until that combination is integrated/qualified.
A alone applies public hooks, closes shared metadata ports/cost and builds.
No native equivalence or effective config dump is inferred from this text check.

At this continuation's initial dependency read A still had no qualified binary
and E had no admission/handoff. No repeated disk survey or watcher is used.
Last bounded resource observation13:34UTC was5600256000B workspace<48GiB.
B launched no compiler, native test, simulator, lease or full application.
Actual cache hits, returned-version agreement and native DRAM read change
remain UNKNOWN. Full functional objective is not achieved. Need exact A source/
ABI, E fresh legal admission, actual finite evidence and independent acceptance.
