# CPU-only reproduction

Use this independent branch, fresh output directories and one reader/check process at a time. No simulator build, GPU execution, scheduler or registration command belongs to this recipe. Large artifacts remain outside Git.

Set `RAW` to the original member path in DERIVED_INPUT_IDENTITY.json and `OUT` to a fresh directory outside the original trace root. The fixed original SHA is ea268780903d10f61a36634bf90f8b00b7e160c1e0703d345efd4ab3e9c3f1b8. Paths below are placeholders to resolve explicitly, not commands to run with angle brackets.

1. Reconstruct the SASS using [the exact V2 recipe](../DTC_HOTSPOT_FORMAT_CLOSURE_V1/source_profile_v2/RECONSTRUCTION_RECIPE_V2.json). Extract unchanged source SHA 0f679be008be285d26ebd7d71eba47b164914dd52873c26ee63beecda2f68cc0 from historical GPU-app-collection revision 40e0052cebd3f98006190ed09e78f4981ef1a41b or the recorded AccelWattch tar member. Verify official NVIDIA package SHAs using the V2 package receipts; unpack only into a private toolchain prefix. Apply only the recorded GCC macro/header overlay compatibility adjustment. Generate PTX with nvcc9.1.85, assemble with ptxas10.1.243 and dump SASS with cuobjdump11.8. Require the recorded PTX/cubin/SASS hashes, 32 registers and 3072B shared memory. Kernel source is unchanged. This rebuild is a reconstruction, not a recovered capture ELF.
2. Run the profile verifier, then default report-only normalizer:

```bash
python3 util/dtc_l1/hotspot_format_source_profile_v2.py --member "$RAW" --sass "$SASS" --output-dir "$OUT/profile"
python3 util/dtc_l1/hotspot_format_candidate_v2.py --member "$RAW" --profile-validation "$OUT/profile/SOURCE_PROFILE_VALIDATION_V2.json" --report "$OUT/report-only.json"
```

Require the passing 185-PC/full-address receipt and candidate SHA 21cd403581a94451e1f9e7a79950d7effd25319daccc101187233e4a0c985985. Explicit creation adds `--candidate-output "$OUT/derived/kernel-1.traceg"` and uses a different fresh report path. Existing files and original-root destinations are refused. The output is never registered or substituted for an old attempt.

3. Copy the original `kernelslist.g` bytes to the new derived directory, keeping `kernel-1.traceg` as the relative member name. Require list SHA a731bfc2cbb90b51888e92f3fb188ff4fceb123612a7b1ceb1817bc752e89461. This is a **new list path referencing the derived member**. Its identical list bytes do not give it the old ordered-member-set identity. Bind list/member/interpretation identities using the canonical JSON identity contract in DERIVED_INPUT_IDENTITY.json (sorted keys, compact separators, UTF-8; sha256 of identity_contract only).
4. Independently compare the new file and create the exhaustive diagnostic index:

```bash
python3 util/dtc_l1/hotspot_format_qualification_v3.py --original "$RAW" --candidate "$OUT/derived/kernel-1.traceg" --output-dir "$OUT/differential"
python3 util/dtc_l1/test_hotspot_format_candidate_v2.py
```

Require six PCs, 122760 changed records and 2944024 changed active addresses, all other lines byte-identical, and matching compressed/decoded index hashes. The guard test invokes normal and optimized Python; it verifies refusal behavior rather than address semantics. The existing 26-case extracted historical-encoder/frozen-decoder oracle is preserved in the V1 pack; it need not trigger another body scan.

5. The narrow eleven-input screening is independently reproducible without the full629 auditor:

```bash
g++ -O2 -std=c++17 -Wall -Wextra util/dtc_l1/hotspot_format_applicability_v3.cc -o "$OUT/format-reader"
"$OUT/format-reader" docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/r0/PAYLOAD_MEMBERS.tsv "$OUT/format-members.tsv" "$OUT/format-witnesses.tsv"
python3 util/dtc_l1/hotspot_format_mode0_followup_v3.py --format-members "$OUT/format-members.tsv" --report "$OUT/mode0-followup.json"
```

The reader excludes Hotspot, checks inventory sizes and only inspects memory mask/mode/token counts and anchor indicators. It does not rehash each body, validate CTA/warp geometry, recount active instructions, inspect all ISA forms or rerun the old full629 audit. A focused follow-up reads only members already flagged for excess mode0 words. Reuse original inventory/body audit identities as explicitly historical evidence. These commands are for reproduction; this round performed one format screening, not repeated full sweeps.
