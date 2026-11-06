# scan/OFF read-only progress audit

The `completed` value is cumulative retired active-thread instructions, not GPU cycles. At snapshot seq 3010, it reached 1,954,886,116 of the frozen 1,963,460,720 declared instructions. The latest ~600 seconds of existing progress records show 26,095,872 additional retired instructions; this is verified useful progress, without a completion-time prediction.

The flushed raw log contains exact completed statistics for kernels 1–32: 1,929,362,032 cumulative instructions, 159,952 CTAs, and 6,415,828 cumulative cycles. The frozen final kernel33 is `uniformUpdate`, with 34,098,688 instructions and 6,656 CTAs. The 33rd SIMULATE phase and retirement beyond kernel32 identify work on this final declared kernel. Phase epoch133 is a transition counter, not a kernel ID or cycle count.

The current Oracle terminal cycles are L1=2,075,101, M=2,090,347 and L2=2,164,410; all preserve the same declared 33-kernel instruction/CTA totals. These are cycles and must not be compared directly with the ~1.9B progress instructions. Current OFF is not yet an accepted full-input result. Historical same-input DH-P0=6,648,993 cycles is context from another Core/binary, not a replacement.

Input scope remains the full declared trace, not newly certified native application capture or numerical correctness. Open gzip streams, terminal strict status and final OFF counters remain incomplete. No ETA, model start, process/debugger action, registry mutation or manuscript change was made. See JSON files for SHA-bound evidence and exact source lines.
