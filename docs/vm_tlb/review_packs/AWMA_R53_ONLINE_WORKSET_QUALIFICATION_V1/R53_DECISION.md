# R53 decision

`R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`

A0 instrumentation exactly reproduces official Fast-dLLM v2 outputs. Packed A1 omits passive reuse rows and lowers token-row execution, but changes forced-commit position/token decisions and final output trajectories in both GSM8K and HumanEval. The only permitted correctness repair keeps the physical safe bucket/cohort shape; it restores exact trajectories and outputs but provides zero forward/token-row reduction. Therefore no semantically legal work reduction survives, and formal timing, diagnostic D and holdout are prohibited.
