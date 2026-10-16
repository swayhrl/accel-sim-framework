# R1 independent incremental qualification

Independent replay of 10 immutable production test executions, six actual CLI
rejections and five full-output R0/R1 ideal-OFF fixture equalities: PASS.
Runtime source diff and primary unchanged-file hashes independently checked.
No frozen R0 binary/result was rebuilt, overwritten or re-run. No application
performance equality across binaries is assumed. R1 application baselines are
new tasks; they await R0 slots and normal runtime hardware closure. R1 vectors
and four diagnostic mode gates bind the exact source/binary in the manifest.

I_WB retains copy/banks, WAD128 and lower queues; I_META retains lower sectors
and requester retirement; I_READ_HIT retains latency, RAW/WAR, banks and actual
response FIFO. I_WB_META has simultaneous WB/metadata pressure coverage. See
INDEPENDENT_CHECKS for tested scope. SASS numerical output remains unavailable;
known-byte fixtures and symbolic sector versions are distinguished. This pack
does not qualify TVD/RO or imply ideal diagnostic performance.
