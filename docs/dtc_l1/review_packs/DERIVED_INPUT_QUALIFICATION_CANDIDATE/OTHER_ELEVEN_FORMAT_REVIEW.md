# Limited eleven-input format applicability review

Scope: one CPU-only sequential **memory-format** pass across the other 628 members (11 workloads, Hotspot excluded), reusing existing r0 member identities and the previous full629 body audit. The new pass checks inventory file sizes, header version, printed mask, address mode and payload length, sparse mode1 masks and nonzero-first-lane anchors. It does not repeat body SHA verification, geometry, CTA/warp completeness, terminal/active-instruction totals, ISA support, cache-reference bounds or native validation. FORMAT_MEMBERS.tsv enumerates every inspected member; FORMAT_WORKLOADS.tsv gives all counts. The inventory and former audit remain explicitly historical identity evidence.

The screening covers 35144966 memory records: 3273798 mode0, 31871168 mode1 and no mode2 records. It finds no sparse mode1 mask, short mode0 list, malformed mode1 payload, unknown mode or mode2 issue. **Absence of sparse masks alone was insufficient:** 98476 mode1 records have nonzero first P and nonzero stride. Zero-stride nonzero-first records are separately counted (32352); changing an anchor cannot change their constant active address.

| Workload | Members | New format finding | Supported conclusion |
|---|---:|---|---|
| ATAX | 2 | No screened risk indicator | Historical dual-mask mechanisms examined here produce no active-address difference for these observed formats |
| BICG | 2 | No screened risk indicator | Same bounded conclusion |
| GESUMMV | 1 | No screened risk indicator | Same bounded conclusion |
| GEMM | 1 | No screened risk indicator | Same bounded conclusion |
| MRI-Q | 4 | No screened risk indicator | Same bounded conclusion |
| NN | 1 | No screened risk indicator | Same bounded conclusion |
| Gaussian | 510 | No screened risk indicator | Same bounded conclusion; no repeat full body audit of its 510 members |
| DWT2D | 10 | 18686 excess mode0 lists | Targeted follow-up accounts for all of them: full32 lists with P=0, hence no consumed active memory addresses; unused STG immediate fields may differ under hypothetical normalization. No normalization is performed |
| Btree | 2 | 6000 active excess mode0 lists, all full32; 5792 nonzero-first/zero-stride mode1 records | Under historical E-list lane association, 5792 of the 6000 lists change one consumed LDG address. Do not certify native addresses or propose a new Btree input without review. Constant-stride0 mode1 anchors do not alter addresses |
| LUD | 94 | 57536 nonzero-first/nonzero-stride mode1 records; 26560 nonzero-first/zero-stride | The first class has unresolved historical E-anchor applicability; the second class is address-invariant to anchoring |
| 2DConvolution | 1 | 40940 nonzero-first/nonzero-stride mode1 records, header version3 | Producer binding is not established by version3. Historical version3 already existed before the mask fix; anchors require separate source/producer evidence |

This is a limited proof for the historical mechanisms examined, not comprehensive native-input or producer qualification. Under that producer contract, P is a subset of E. For mode0, an address-list count equal to popcount(P) forces E=P, so ascending-lane association agrees. For mode1, contiguous P starting at lane0 forces first(E)=0 and gives the same addresses; stride0 is address-invariant to the first-E anchor. The old encoder requires contiguous E. Other encoders, compiler behavior, data identities or missing capture receipts are outside this proof.

## Concrete unresolved evidence

**LUD:** member1, original line104, PC0540/LDS.U, P=0000fffe, base0x40, stride64. E=0000ffff and E=0000fffe are both contiguous, have at least two lanes and contain P. They encode the same base/stride/P after predicates are applied, while active lane1 is respectively 0x80 or 0x40. Both raw fixtures can be constructed as base+64*(lane-first(E)). Original compressed bytes alone do not choose. This is an address-information counterexample, not proof that both paths match the entire original executable. Additional producer/binary/source applicability evidence could eliminate one; that separate investigation is outside this limited review.

**2DConvolution:** member1 line58, PC0120/LDG.E.SYS, P=fffffffe, base0x7fdc00000004, stride4. E=ffffffff or E=fffffffe give active lane1 0x7fdc00000008 or 0x7fdc00000004. The header's version3 is not a fix receipt: historical revision475a282dd5baabfc481b3be44963e92fc3df34cc declares TRACER_VERSION3 while printing active_mask&predicate_mask and encoding active_mask. Its SHA is in the source evidence register. The retained launcher names a tracer_tool.so path but has no immutable library/source identity. Fetch/extraction date20260821 and CUDA11.0 do not resolve that binding.

**Btree:** member1 line691, PC1c40/LDG.E.SYS, P=10000000. Original full32 list word0 is 0x7f8eed50bc04, but word28 is 0x7f8ef0d10f88. Frozen consumption gives lane28 the former; historical full32 E-list association gives the latter. MODE0_FOLLOWUP.json records this original-line SHA and all aggregate differences. This is direct raw-vector evidence under the historical list contract, not an adopted input repair.

FORMAT_WITNESSES.tsv retains at most two records per indicator per member; it is a witness selection, not a full affected-record index for the other workloads. FORMAT_MEMBERS.tsv counts every screened record. Only Hotspot has the exhaustive candidate-change index in this round. A focused follow-up read only the 10 members already flagged for excess mode0 words and accounted for every flagged record; no unflagged member or full629 audit was repeated.

## Review boundary

The user was notified of Btree/LUD and subsequently of 2DConvolution, with the concrete alternatives above. No formula, new input definition, result relabeling, HOLD, acceptance or scheduler change is selected for these inputs. The review question is whether to finish the independent Hotspot candidate submission while registering these as separate unresolved risks, or pause submission and define another bounded semantic investigation. An unanswered scope question is not approval.

Until reviewed, this pack must not be cited as "all eleven other inputs are qualified/unaffected," nor as proof of native GM12 fidelity. Existing original-path runs and result identities are preserved; Lane A owns their scientific-admission review. Do not use this finding to silently exclude workloads or rename an incomplete aggregate GM12.
