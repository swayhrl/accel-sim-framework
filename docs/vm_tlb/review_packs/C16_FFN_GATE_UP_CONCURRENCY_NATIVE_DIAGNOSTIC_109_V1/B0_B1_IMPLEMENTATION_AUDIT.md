# B0/B1 implementation audit

Status: **CORRECTNESS_MISMATCH_STOP**.

- Authority and contract SHA: exact PASS.
- Accepted producer: `071297ae7f4aa772a27fae0cf31ad47ab7d967be` / tree `1e6a4f5ed19dfc76f91795524a29ac652156c653`.
- Base runner SHA256: `ad922629a9898c01400a165b2f6565659f1c6e422784c10bc1d013265c45b5fb`.
- Diagnostic runner SHA256: `c57ca31cd86cf1575024661164ef2bb14a1656c9cac64a5820862b97b13f0ebb`.
- B0: opt-in is off; no producer stream or dependency-event construction occurs.
- B1: exactly two producer streams and three non-timing dependency events per MLP call.
- DAG: gate projection plus SiLU and up projection branch independently; original stream joins before multiply/down.
- Lifetime: hidden is registered on both producers; activated/up are registered on original consumer.
- No layer/device synchronize, busy-wait, priority change, kernel change, NCU, NVBit, SASS, or Accel-Sim was added.
- Canary B0 passed frozen tokens. B1 produced `[143907, 11, 476, 304]` instead of `[23578, 11, 323, 3950]`.
- Per contract, formal timing was not started. Static lifetime intent is documented but runtime safety is not claimed.
