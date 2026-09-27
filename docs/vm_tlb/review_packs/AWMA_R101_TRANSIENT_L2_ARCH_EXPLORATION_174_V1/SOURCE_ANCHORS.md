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
- candidate binary SHA-256 (`VERIFIED_RUN`):
  `45dc613501f1eeb4f7199c9952b32c0bd9fd4a0b659e37071dbf0d57ccec9f93`
- implementation patch SHA-256:
  `df34d5b3dba671a7e8987a6b2d336338b31971e812edcb4160099b59cab08da7`
- R101 Native authority: `cfbe6503585fa1b10d979db5d26fb9be3a80e563`
- R101R1 Native authority: `422faf4d8fcdb5ac49068dcf19a6e783954a29a8`
- Round13 literature authority:
  `a63574628b2daf20dd3c9256f53d5cd3ff7df26f`

The platform remains a model-relative RTX4080/Ada configuration. Nothing here
upgrades simulator resource/timing parameters into hardware facts.
