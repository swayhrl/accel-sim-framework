# Physical clock correction — supersedes R0/R1 application qualification

This report withdraws primary application/ideal qualification of the frozen
R0 and R1 binaries for the memcpy-warmed production path. Earlier fixture PASS
and exact input/terminal observations remain preserved within their tested scope.
All prior review packs and six completed application logs/CSV are unchanged.
Do not use their observed ratios as accepted EP-L2 primary results. No mean.

Actual Tag access uses physical GPU time + m_memcpy_cycle_offset for native
replacement ordering; FT used that offset time for bank arbitration and WB/WAD
birth. Lower-ready/accepted and response/fill bank calls use physical time.
The same arbiter therefore sees different times within one physical cycle,
resetting service grants, and clipped lifetime accounting may produce zero.

The production partition test invokes real force_l2_tag_update 4096 times,
then naturally replaces an unrelated warmed line. It observes grant deltas per
physical cycle through an observation-only getter. Retained R0 archives: zero
violations at offset0, 124 B16 / 15 U_WB16 at offset4096, max2 grants per bank.
Both runs still drain and satisfy original lifecycle assertions. This proves
that terminal closure alone did not qualify the physical port service budget.
Initial direct warm-hit diagnostics are retained; no assertion was removed.

Minimal repair keeps native Tag timestamps while using physical GPU time for
all FT bank calls and WB/WAD births. A monotonic FT clock assertion detects
future mixing. No capacity, bank/port, trace, oracle or scientific input changes.
The corrected gpu-cache object is linked against exact retained R0 archives;
all archive hashes are recorded and unchanged. Four mode/offset probes pass
(max1 grant), the original directed suite passes, and all four C8/C16 partition
cases pass. Staging lifetime becomes nonzero. This is a validated repair delta,
not a newly frozen official application binary. Runtime patch applies cleanly
to exact R0 and integrated R1; Lane1 is the final public integrator.

Next: Lane1 freezes repaired R0.1 and R1.1 as new identities without replacing
old binaries. Lane5 then incrementally qualifies those identities (mandatory
physical_bank_clock gate), reuses unaffected old OFF evidence and runs new-key
B16/U_WB16 pairs; only then run representative static/copy controls. Existing
terminal-valid rows stay immutable and have superseding acceptance in
APPLICATION_ACCEPTANCE.csv. Four unstarted cells remain NOT_RUN, never zero.
