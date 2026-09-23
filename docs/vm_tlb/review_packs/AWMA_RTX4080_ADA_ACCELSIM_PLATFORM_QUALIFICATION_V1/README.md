# AWMA RTX4080 Ada Accel-Sim Platform Qualification V1

Start with `QUALIFICATION_DECISION.md`.

Outcome: `RTX4080_ADA_PLATFORM_NOT_QUALIFIED`.

The engineering portion succeeded: public RTX4080 scale, reviewed upstream SM89/Ada support, a cold-built binary, terminal parser execution for generic anchors plus M0/M1/AI T2, and exactly two bounded calibration passes. The frozen candidate has calibration errors below 22% for the three comparable pointer anchors.

The qualification gate failed because only one of three held-out traces preserves Native workload scale, and that point has 43.48% error. The other two traces are useful parser smokes but cannot support runtime error. This pack intentionally does not promote a publication baseline and does not run the post-qualification AWMA VM overlay smoke.

Implementation commit: `aeec5b9a69865012b16ac0a6627143e29f1fee06`. Final config SHA256: `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`. Binary SHA256: `4ca40e642f92121caad40d1b1566b0b6478870101d66592bfc28fb6f7299615f`.
