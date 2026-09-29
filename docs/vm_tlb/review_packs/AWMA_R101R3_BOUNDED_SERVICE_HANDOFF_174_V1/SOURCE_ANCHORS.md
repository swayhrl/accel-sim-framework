# Source and evidence anchors

## Git authority

- coordination handoff:
  `hrl/awma-r101r3-bounded-service-handoff-v1 @ c811f42d980606ab3da597920984a309121d2ff5`;
- scientific/execution parent:
  `hrl/awma-r101r2-context2-memory-service-174-v1 @ 97d5be184b7f7f35c06d3ee111a8c5ba6efad896`;
- accepted RTX4080/V1 baseline:
  `AWMA_RTX4080_SIM_BASELINE_V1 @ 8d1f14a32f5538660d74da86ccb03a2c504c5735`;
- execution branch:
  `hrl/awma-r101r3-bounded-service-handoff-174-v1`.

The execution branch starts exactly from the scientific parent; the
coordination commit is read as instruction authority and is not merged.

## Accepted input and comparator

- input: `R101_L512_NS_CONTEXT2_EXECORG_V1`;
- ordered trace aggregate:
  `4fee01b73c9076378aeb583ea65254c5d3882c71ab2d0f2aeac857bc25edf2ce`;
- runtime sidecar:
  `67adc56216f25bfc88c98d86aabdf1eeaae87e9f2f8e102f675d5be8ec11e7b5`;
- kernels table:
  `a9cf4bdbc3d551e9e7fc0d41b84a65e89d148085ea92940f04366c2e71704a65`;
- B0 summary:
  `2c7e2cac39d0cbc1d0b1a1bf6eb4a0ec43c571b4595b4c282e93e9d4e966f24b`;
- O2 summary:
  `d8aba6635e29b920266964fc6e8b2c5cda70cc5ccc1b80985de32420cdc8857f`;
- accepted B0 measured ROI: 2,985,319 cycles;
- accepted O2 measured ROI: 1,130,670 cycles.

## Stage A

- analyzer:
  `de7e7841464e3e4d69fa7e97a8fc0f0444d4b4eec8bb71caf9dddc029c1905b3`;
- receipt:
  `f0ba439ae293de7ecb0cdbbe37a663229e59ca13c4dca638da62b13e5187c7be`;
- detailed ledger:
  `3e3097e716b7997550d3766cf75b2fbf52f745c4b43340aaed3ef5673488fd17`;
- existing-evidence table:
  `d2cb519c3668c33f75abea8173e5a008fce3841ef70e628bc5ae928f84b7e97c`;
- composition table:
  `a39c244b9d271e1d193335e75b93b9eccda77e1261609e7d485803af682cf008`;
- availability table:
  `60401088fd68b7a55f8b50041602f52ebbedaebe17825a6149697f1834ea61b6`.

## Frozen S1

- binary:
  `ae3a71d8b75bb6e4b019b0f355801d5e529a3178085d9e8c9671dffee4f1cdfc`;
- Core library:
  `2abc6cdc694a245edf0a61606bad7a9ef487e16da07802cbc32f74e29ebc68fd`;
- exact patch:
  `768804050c22cb85168b2e73daa6414fcd6c519b429dd000ceaec84bfdf037a4`;
- framework entrypoint:
  `c6a8e6315226c6d45ae93f2280999d5975328d306cb09f161f1d4d73f3ef4323`;
- simulator config:
  `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`;
- trace config:
  `a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b`;
- runtime archive manifest:
  `5ead09bbe99c0591a03293a52687806ce8a2ff95979e2c45d2206bbe6b1e0645`;
- formal argv:
  `8062c4e7e56ccde05fd44576a22c67cc0acb4d587eea41e3c32d372356d02a12`;
- formal runner:
  `52b4d37534257421eef37ec1e2138ff5a158731e441ec2eff3356870b55a21e6`;
- formal-at-run summarizer:
  `af69ab68e08a8f8ae871c162b4088ac332372ff6dbb6932c7a7cc7735d6427c3`;
- postprocess-recovery summarizer:
  `47d5a62639706c213ddc7d7fb1a20d6e27bbd9aa3dff0fa9bb82363b51b6351d`;
- recovered PASS summary:
  `586440d438a26a193a664e7fd355be09f18cd81abdafe568db41dd67f9205674`;
- recovery receipt:
  `09366400625b238ee2bdd773f4a25587d4574e527a428b594d0ab9fc61d0c0ab`;
- S1 result table:
  `b15a5264737503bdc42047dccf207102df70d8c3f96673f87bcc9094f304ca5b`;
- run receipts:
  `a8b4d195513eeb35b0cbbd599d445da54e91fb46ceebb1e0cbe9a0fab6d77320`.

The S1 runtime archive is:

`/root/share/mnt164/huangrulin/awma_r101r3_bounded_service_handoff_174_v1/runtime/S1_frozen/`.
