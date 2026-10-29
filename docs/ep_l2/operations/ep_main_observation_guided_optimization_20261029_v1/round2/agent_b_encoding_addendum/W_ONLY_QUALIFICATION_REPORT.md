# W-only Qualification and W/V Optimization: Round 2

This readable English addendum replaces only the presentation entry point of the original report. The original frozen directory, report bytes, evidence and manifest remain unchanged. Its manifest SHA256 is fd3837abf742f307719af4bb98511385b3fb0010147317cb6cc5c44b7c2655a8. The old Markdown report was damaged by text encoding in a PowerShell-to-SSH pipe. It contains 1,525 question marks. The original JSON evidence was checked separately: no JSON file in the frozen delivery contains a question mark. This addendum changes no numeric evidence or qualification status.

## Source and execution boundary

Primary source: Core 78f4b59e865b136eede74df74c44c210f5b4ca04; Framework 9dd1ee57a83d83b56b7874bc7c716185ab52c8f7; accepted ELF SHA256 78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a; vendor f90c430c3a1ce8f08c09942a5a1c3a797bb2295b; libgpgpusim.a SHA256 e5a743a2bb796d82f58109251f43d5c1997d5c1f7fdeac61213416da3835b697.

Only matching Source78 production component libraries were linked. No production source or accepted ELF was changed. There were zero full application/model launches, zero Trace/raw-body scans, and zero dispatcher, registry or controller writes. The accepted Core and Framework remained tracked-clean. Source92, host-write V3, MSHR64 and D's preview patch were not integrated.

## Actual CPU component results

CPU_ACTUAL_EXECUTION_FINAL.json records all three controls passing:

1. Real 32-set, 8-way W_ONLY construction: FT2, TVD off, RO runtime off, 1,168 physical slots, line MSHR128, descriptor512, WAD128, bank P1, empty resources and ownership consistency. This control constructs production objects but issues no requests.
2. Existing test_ft_partition.cc: real partition, lower-full pressure, WAD128, distinct staging/set_done lifetimes and complete drain. It uses 142 synthetic requests and a one-set, one-way synthetic cache. It is not a 32x8 application-pressure result.
3. Existing test_ft_a1.cc: 64-set, 16-way cross-cycle fill, identity redirect, version tokens, exact-once replies, lower acceptance, set_done, P1 and complete drain.

CPU_32X8_REQUESTS_EXECUTION_FINAL.json adds a real 32x8/IPOLY production-path control: nine requests, seven pending reads, one dirty replacement/writeback, seven reverse-order returns, P1 and complete drain pass. Same-set addresses are selected with the production config.set_index() function. These checks use symbolic protocol/version data; they do not prove full-program numeric correctness or application performance.

This is PROVEN CPU component behavior. It is not application OFF/ON non-interference, native qualification, a new accepted application, or a self-issued Main formal-mode CPU certificate. One-SM/one-channel, zero-ROP and externally controlled lower-memory conditions are declared CPU-fixture conditions, not the formal application's complete 282-option hardware profile.

## Preserved failures and private test-input corrections

The earlier exact3 resource HOLD remains untouched. This round preserves the following additional failures:

- Attempt 1: a compile on CPU0 exceeded its own 60-second wall limit; stderr was empty and no fixture completed. This is not a protocol failure. The explicit next engineering attempt used a sampled low-load CPU and a 180-second compile limit.
- Attempt 2: compilation passed, but the old never-executed synthetic overlay used unregistered -rop_latency. The option parser rejected it before successful construction. A private CPU overlay uses the registered -gpgpu_l2_rop_latency name.
- Attempt 3: construction passed. The one-channel fixture inherited IPOLY memory-partition indexing, which supports 16/32/64 channels. The private one-channel overlay explicitly selects partition indexing0, matching existing one-channel fixtures.
- The first new 32x8 request fixture incorrectly assumed linear set stride under the real P/IPOLY mapping. The next private fixture selects addresses using production set_index(). Both versions and the original failure remain available.

No correctness assertion was removed and no protocol guard was relaxed. These are fixture/input defects or execution limits, not evidence of a production W_ONLY protocol bug. All final positive controls retain assertions.

## Host component results and limits

The old five-mode Host draft incorrectly accepted only four observer environment keys, while actual accepted S specs also contain EPL2_LIFE_WIRE=SUMMARY_STAGE. It therefore rejected the real accepted S environment. The private candidate allows exactly those five keys, requires SUMMARY_STAGE and keeps all four heavy observers off. Unknown keys, heavy observers on and WIRE drift remain rejected. The original Host draft is unchanged.

HOST_CONTRACT_ACTUAL_CONTROLS.json records 38 passing pure controls: five formal flags/history profiles, background and Source mismatch rejection, geometry/P2/MSHR64/quota/stat/282/trace mismatch rejection, disabled-RO certificate rejection, missing enabled-RO certificate rejection, missing modeCPU/HostQ rejection and rejection of the old CPU HOLD as a qualification.

HOST_NUMERIC_PRESERVATION_ACTUAL.json records successful pure import, package verification and numeric-factory creation. The original numeric body 7cc347a6c62974eedf9e1e39b007c2716fa886d26057f005c938c820b48e1817 and final suffix bf91f534869a1ec59aea92ee2de961d50e16e68a28eed636448ca83122339432 remain identical. No full raw was validated and no native actor or full Host wrapper was executed.

The private candidate's engine/parser pins were updated consistently with its new mode-contract hash. This remains an unapproved private candidate. Its scope is Source78, 64 slices, 32x8, L100, P1, 1,168 slots, descriptor512, WAD128, lineMSHR128, MS/B0/M0a111, four heavy observers off and WIRE SUMMARY_STAGE. It rejects 16-set geometry and does not qualify Conv16x8 F-minus-T.

## Mode semantics and resource fairness

| Mode | FT | V clean/dirty | T | M | Actual meaning |
| --- | ---: | --- | ---: | ---: | --- |
| S | 1 | 0/0 | 0 | 0 | Static resident organization and finite WB16; no TVD or RO runtime |
| W_ONLY | 2 | 0/0 | 0 | 0 | Unified physical-pool organization and in-place WB; no TVD or RO runtime |
| WV_ZERO_RO | 2 | 1/1 | 0 | 0 | W plus the complete V package, including paid query, dirty-forward and retention |
| F_MINUS_T | 2 | 1/1 | 0 | 1 | M/RO retained; exact RO certificate required; not WV |
| F | 2 | 1/1 | 1 | 1 | Full mechanism; exact RO certificate required |

The formal capacity overlay states that at 32x8 S's regular resident landing IDs are only 0..255, with WB16 and a source-reachable resident-plus-WB upper bound of272 per slice. Static bypass has no production allocation call. FT2 W/F can borrow physical IDs across the 1,168-slot pool under finite bank, owner, pin and role guards. Equal physical capacity is not equal usable role capacity;272 is not a measured jointly achievable occupancy. Nominal Tag-covered data capacity2MiB and physical payload9.125MiB are distinct.

S-to-W includes pool organization and copy elimination, not a copy-only change. W-to-WV includes paid query, dirty-forward, retention and service costs, not only Victim hits. Real WB readout, WAD until actual completion and bank service remain necessary costs.

## Exact drafts, proposed budget and cost

scientific_drafts/ and EXACT_SPEC_AND_BUDGET_MANIFEST.json contain six independent complete282-option candidates. Each uses the immutable accepted S ordered-config references plus a private mode-only overlay. Input, Source5, geometry, clocks, DRAM latency100, queues and background remain unchanged. Their schema explicitly marks them as drafts, not frozen actor specs. No budget or launch authority is present.

- Low-cost option: FWT W_ONLY and GEMM W_ONLY, two new starts if separately approved. Existing exact S/WV anchors may be reused only after Main review. FWT remains RO-disabled and must not be replaced with RO-F.
- Positive/negative option: Stencil and Scan, each W_ONLY and WV, four new starts if separately approved.
- If Main separately approves all six, the total need is six new starts. This round authorizes and consumes zero. The packages do not accumulate automatically and do not reuse the old227 budget. Additional NI or new-Source application references are outside this six-point proposal.

Historical same-input wall-time anchors are approximately14-15minutes for FWT,1.2-1.4hours for GEMM,4.8-8hours for Stencil and8.1-8.9hours for Scan. New-mode runtime is UNKNOWN. Planning RSS values are about0.74,4.15,0.58 and0.85GiB respectively, using historical maximum times1.1 plus16MiB; these are forecasts, not admission guarantees. Large Trace inputs remain on genuine164. Private fixture binaries total163,322,688bytes and are listed for Main's genuine164 archive and independent SHA restore; they do not belong in Git.

## Remaining qualifications

Main must review the CPU receipts and issue any exact formal modeCPU qualification. Complete Host positive/negative wrapper controls and new HostQ, parser/mode binding, native sole-entry approval, current accepted S-anchor reuse, input eligibility for W_ONLY, a real W terminal/parser/drain acceptance, and a fresh exact user-authorized budget remain open. Existing NI does not automatically cover a new W/F/WV collector or mode path. No new collector was integrated.

D independently confirmed a P1: with m_ro and T1, ordinary non-RO TagFAIL can be denied by the native preview before reaching otherwise legal backend RO relief. This does not apply to these RO-disabled W/WV controls. Application incidence and performance impact in historical F are UNKNOWN. Main should review this before expanding F science. B did not integrate D's patch.

## Structural candidate

C1 service-aware reclaim remains HYPOTHESIS and design-only. Among legally reclaimable optional rows, prefer never-successfully-served rows with an age fallback. Directory-full and bank-compatible selectors require explicit separate definitions: current dirty install prefers CLEAN, current clean install selects oldest across reclaimable kinds, and current bank reclaim selects CLEAN before WB_COMPLETE. Do not flatten these semantics.

Set service_seen only after successful response_commit with real bank service and accepted response enqueue. Reset it at every incarnation/rebind, including dirty promotion. Preserve mandatory state, readers/pins, generation, owner, bank color, revision and preview purity. Logical unpadded state is1,024bytes; extra ports, comparator latency, timing, PPA and application benefit remain UNKNOWN. A future implementation requires an independent Source/ELF and same-binary unchanged-policy S/WV references. Do not splice Source78 performance. Optional retention-cap64/128 scanning remains deferred because saturation and value are not established.

## Evidence identities

The adjacent EVIDENCE_REFS.json lists exact SHA256 references for all original CPU, Host, specification, status, build-capsule and candidate artifacts. Those original bytes remain authoritative. This addendum performs no tests and changes no frozen evidence.
