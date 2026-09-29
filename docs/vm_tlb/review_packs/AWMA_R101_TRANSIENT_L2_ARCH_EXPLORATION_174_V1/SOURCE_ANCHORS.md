# Source anchors

Evidence labels follow the project `AGENTS.md` contract.

- coordination (`VERIFIED_CODE`):
  `6533872601bb81dae1475b35d365f9dbe418cb23`
- accepted simulator baseline (`VERIFIED_RUN`):
  `AWMA_RTX4080_SIM_BASELINE_V1 @ 8d1f14a32f5538660d74da86ccb03a2c504c5735`
- accepted baseline binary SHA-256:
  `a866c219b7d71a3075e032c9179bcd679074d6f2e9f1750b435170aabb413b24`
- platform config SHA-256:
  `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`
- trace config SHA-256:
  `a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b`
- baseline Core source file SHA-256:
  - `gpu-cache.cc`: `8b8fcc3f9356da6005d0898c50298553270484ba58bcab1765ef5615e75d7cbb`
  - `gpu-cache.h`: `5ef6f6d26ffa4b162a41b6f6d55d5a4506075875fde31597710055f66a0a5bcf`
  - `gpu-sim.cc`: `61509c07c4cb416c52f7bd83ed9bcca5da0fbba6baef37fd6157677915c8e9c2`
- frozen formal candidate binary SHA-256 (`VERIFIED_RUN`):
  `32b38a66ba6b9eee5a9047873992fec42fcc4dbbff6adf247d425aec2b650c5d`
- dynamically loaded frozen Core library SHA-256:
  `f18cd8d4c2dd8927d6ad454295e434b902032042e83bbab03afcbd02b23921bf`
- implementation patch SHA-256:
  `aa2637f3379f1c0b6184db98a41f276dcdd6bcef86cb72331b18c52cf6232676`
- framework full-drain source SHA-256:
  `c6a8e6315226c6d45ae93f2280999d5975328d306cb09f161f1d4d73f3ef4323`
- frozen candidate Core source SHA-256:
  - `gpu-cache.cc`: `1374b2a8f6ff7d459e8a2504d8f65bd419a691f0a19fce7e5d8bc5c30c8cc9d8`
  - `gpu-cache.h`: `b1d69c31f13f3c282656fbbcb7288322317bb98a77481a8ca1aeb35bf317b944`
  - `gpu-sim.cc`: `4ad64ded553e864add32fafd74a1723dd9f75298911b68288793de358d0b0a12`
  - `gpu-sim.h`: `821d2c4a9f32bcdfe91e377c3aaef4796d015c85c2ee073c36a067bbc2c7f891`
  - `shader.cc`: `bedf095f1073170ea59ebac6c037a6055428615e72915103766683035f88eec6`
  - `l2cache.cc`: `cd181a81f81cd0c715e62c09941cf56c55a49d1ba6cdccc744c2f6b1bfad886b`
  - `l2cache.h`: `80d1c2e23e0cacdbc84067cdc21a4992bfb0f2ad38cdef0309539c043f340fc8`
  - `awma_transient_l2_policy.h`: `5215910e621a791b0efbf6d159349fedd0081d81edfc8beea2bb811a159bedbf`
- accepted simulator-input producer:
  `bb902283b7ce9e1902b460383fbd3e0bedbd884d`
- accepted payload/output SHA-256:
  `1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234` /
  `36aaed3f8360aa099301ae1d705bc2e6ab5ba61586adaf7ead93ecab808dc1b0`
- R101 Native authority: `cfbe6503585fa1b10d979db5d26fb9be3a80e563`
- R101R1 Native authority: `422faf4d8fcdb5ac49068dcf19a6e783954a29a8`
- Round13 literature authority:
  `a63574628b2daf20dd3c9256f53d5cd3ff7df26f`

The platform remains a model-relative RTX4080/Ada configuration. Nothing here
upgrades simulator resource/timing parameters into hardware facts.

## Formal result receipts

- B0 command / summary / log:
  `52015f7d50858a634d127d10fbb98c12db31aca52d9345a0aa9ec8627b6e0aae` /
  `d34d9cf0fda696e414d947830c81c1c7450954be3ef1615694d04bb803482373` /
  `d1926bc687d9c7187ef577a5143b848b9ad98a15b79330971cac8f9a7e0aea8a`;
- O1 command / summary / log:
  `719f287a3e64dd6eecfbc304df3f11d134ecf0209abcdce9c9255cda07b38adc` /
  `59e0ef3d53043d255595a1e8184b627b26b9025f32f4fd113be1dab418738eaf` /
  `fa89bdbd6877ba8be88486b9d9f25f8a6c3dd93f31da3a696c7d1e1f384ed9b5`;
- M1 command / summary / log:
  `8db391922b1c4d0c1c0ca5c97c6129b3c47b5a22cb82e3309f8530e7f3b75a9f` /
  `d5ce6e84a68a9fb98744513b93f04ea0f81ac58374b6fc6c46f449e29024fc98` /
  `cf396fe75d6db09a554db0810e69ecd5c9441078ca0b047bcf7c1e33b9c5f9fd`.

Formal tools:

- matrix runner:
  `973f351f052fb61340138560dd5f5decbcb6ce4c7a0c94b15e1338e87b552aeb`;
- summarizer:
  `05eda1f021336bba4ebed018ba8657492a0df0b1318c00eecd2c1378b161a1d4`;
- fail-closed finalizer:
  `0f358e1abf83411b277f4d3e43c1bc190986a341e74a13bcd99e14fd134c88ce`;
- per-kernel extractor:
  `accb16a3aefb8d5c0e59bc084500e2fb33b00c41d14d884eac0ead7bc45b8d35`;
- generated per-kernel M1 telemetry:
  `b9cbd1d284ae741c225a1cf1b8bde7ed7a296b3e99ec5bbdb67640d117d883f1`.


Raw closure:

- raw-index builder:
  `0d3cec2f6dfe7e9b3fe966e59375c88e02bd09d18dcc14e468b511ea1b1ec895`;
- `RAW_DATA_INDEX.tsv`:
  `dce8e811d657f25560e991a8516f24df919ba385428e880d8ef2f98bc40f8393`;
- node164 `NODE164_EVIDENCE_SHA256SUMS` (94 entries):
  `7679686e76e7a1f110a9da6735e43f0d963b7b49d4dfb59865b584f06c3f3b3a`.
