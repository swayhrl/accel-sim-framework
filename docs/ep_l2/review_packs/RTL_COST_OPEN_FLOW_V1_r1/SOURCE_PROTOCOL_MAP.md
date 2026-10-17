# Finite source protocol to changed-path RTL boundary

Source Core9bd30ed913c5058b5d952fbeb2e67cb5e4644b3f, not Ideal.
Frozen corrected RTL25097f4b6; file hashes are in SOURCE_IDENTITY_START.

| Finite source location | Actual RTL behavior / scope |
|---|---|
| ep-l2-ft-cache.inc:175 ft_access prechecks and physical-cycle service | req_ready checks WAD/full physical pool/victim pins/pending state before capture; no symbolic byte data |
| ep-l2-ft-cache.inc:251 captured victim/index/landing | p_tag/p_old/p_landing/p_staging and native_tag held until commit/abort; no victim re-probe |
| gpu-cache.h:2354 preview_free;2370 reserve;2383 release | full-capacity mapped combinational encoder, mode constants, role/generation FFs, real bank-compatible allocation |
| ep-l2-ft-cache.inc:283 static source read/copy/staging | COPY_READ/RETURN/WRITE, real1024-bit common latch and bank grant; source timing differs as documented |
| ep-l2-ft-cache.inc:315 Unified in-place transfer | victim keeps bytes and becomesWB while new same-bank landing is installed; no static copy grants |
| ep-l2-ft-cache.inc:390 lower_ready;407 lower_accepted | WB bank read, held1024-bit output and128-bit byte mask; valid&&ready frees physical payload, WAD remains |
| gpu-cache.cc:2623 ep_l2_wad_complete; l2cache.cc:2619 actual done hook | done_ticket+generation clears only sent/live WAD; old-address hazard persists until valid completion |
| gpu-cache.h:2710 fill request handle | fill handle/owner/pending-sector qualification and byte-protect merge; stale fill dropped |

Native full-address Tag/LRU/dirty-byte state and Line-MSHR are boundary inputs,
not zero-cost blocks. An actual integrated top instantiates four292x1024
SRAM boundaries; macro technology area and delay are unknown. Native approval
is required before destructive byte writes and differs from symbolic sidecar
rollback. Round-robin/serialized frontend/synchronous-return/extra WB stage
differences are in SIM_RTL_TIMING_GAP. No current SIM throughput or accepted
performance is assigned to this RTL, and no SIM timing patch was made.
