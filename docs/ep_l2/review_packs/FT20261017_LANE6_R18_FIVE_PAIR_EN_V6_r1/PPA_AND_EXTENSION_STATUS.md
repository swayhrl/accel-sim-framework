# Cost and qualification boundaries at EN-v6

This revision receives WB-only applications produced by Core
`7b8e6ac70b8fe0f1bd37efca11acb5284938825d`, Framework
`9bd17f9db3e8cbbc3fdad7283d1e292918546fd5`, binary
`23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee`.
New numerical evidence is simulator timing/counters and symbolic lifecycle
qualification; it is not RTL, place-and-route, silicon area, STA or power.

| Account | Supported representation / status | Does not establish |
|---|---|---|
| Primary payload | Both modes1168×128B =149504B =146KiB/slice;64 slices9.125MiB | Same macro organization, ports, energy or hit latency |
| Copy latch | Common128B/slice =8KiB/chip outside primary pool | Incremental U area advantage; latch remains common |
| Bank service |4×292 slots; at most1 modeled line operation/bank/physical GPU cycle | Equal clock frequency, layout wire length or pipeline latency |
| Tag handle |11-bit slot index; gross1024(11+G) bits/slice if explicit generation widthG | Measured incremental bits; baseline may share fields; G mapping unchosen |
| WB handles/control | Up to128(11+G) bits plus owner/state/transaction representation | Actual packed RTL area, proof that all fields are incremental |
| Other metadata |512 descriptors,128 Line-MSHRs,128 WAD; same primary limits | Free owner/generation comparators, bank-compatible allocator, retry/rollback logic |
| Verification versions |Symbolic32B-sector/request identity proof state | Payload numerical RAM storage or a measured hardware ECC/version array |
| New proposed queue headroom |+128 entries/slice,8192 chip entries, unapproved | Equal resource/PPA competitor or a free DRAM speedup |

The earlier source field ledger is preserved as historical. It is not silently
promoted from an old source revision to a repaired-release incremental netlist.
C++ object sizes include compiler/container/runtime effects and are not used
as silicon area. No performance counter is converted to watts or energy.

Before an efficiency claim, choose SRAM macros/ports, widths and bounded pin/
generation representations; account for baseline common fields and lower data
carriers, arbiters, comparators, routing and added stages. Synthesize both
matched designs with a declared technology/constraints and perform STA/power
under a trace/activity model. None of that work was performed this round.

Current extension status was read directly from exact GitHub heads, retained in
`validation/EXTENSION_STATUS_BINDINGS.json` and the three status snapshots:

- TVD/Lane2: R2 rebase and its three new directed groups NOT_COMPILED_NOT_RUN;
  common B1/C1/C2 work does not qualify the TVD mechanism. No official integrated
  TVD production binary or accepted application evidence is used here.
- RO/Lane3: isolated A2/A3 source-bound C++ old-red/new-green evidence exists,
  including18 small process invocations; complete19 production obligations,
  final integration and independent scientific qualification remain pending.
  No accepted RO application performance is used.
- Ideal/Lane4: R1.1 integration handoff exists; new C++ cases uncompiled and
  original18 application cells NOT_RUN. No official same-binary R1.1 production
  matrix is available. Old ideal/withdrawn performance is not rehabilitated.

These historical Lane status snapshots cannot override current Lane5 V2
scientific acceptance. TVD, RO and all Ideal flags are OFF in every main result.
