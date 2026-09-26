# Resource assumptions

The adaptation has no auxiliary unbounded request/result table. Group comparison is over the existing `warp_inst_t::m_accessq`, whose source address generation is bounded by configured warp size and `MAX_ACCESSES_PER_INSN_PER_THREAD=8`; the result is retained in existing `mem_access_t` objects until consumption. The simulator timing contract assumes same-cycle grouping at the frozen resident prelaunch observation point and unchanged one-port V1 translation admission. This is a source-supported simulator proxy, not RTL/PPA/Fmax evidence.

Per-SID/per-real-cycle observer HWMs for compare, leader, registration, READY read, and consume are in `COMPARISON_RESULTS.json`; no sampled maximum is hard-coded as capacity.

One resident LDST instruction is evaluated per SID cycle. Its accessq grouping is a same-cycle combinational adaptation; the frozen physical translation controller still admits through its one L1 port. A ready leader result is delivered to all compatible resident members in that simulator cycle, with no separately modeled delivery port and fanout bounded by the source accessq. This declared timing choice explains why identical suppression sets can produce different interleavings and cycles from PREL1.
