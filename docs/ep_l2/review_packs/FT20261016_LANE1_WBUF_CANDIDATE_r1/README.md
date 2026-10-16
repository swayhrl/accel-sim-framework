# Lane 1 WBUF candidate r1

Status: FUNCTIONAL_CANDIDATE_UNDER_REGRESSION — not a qualified release.
Production implements static WBUF8/16 and U_WB8/16 using the existing pool and
bank arbiter. The initial production fixture passed four capacity/version/drain
modes plus WAD128 and sector/response reference pin groups. U_WB carried 32/40
WB staging objects at C8/C16; static stopped at 8/16. This is boundary evidence,
not benchmark performance. Expanded pool-full/reference qualification follows.
See the public source map and explicit storage/port ledger for the equal common
copy latch, lower packet data backing, role lifetime and generation assumptions.
