# Validator status

- The broad opcode scan was intentionally stopped on explicit review-checkpoint direction before it produced a result. Its status is `STOPPED_PER_REVIEW_DIRECTIVE`; it is not used as evidence.
- The bounded required ULDC occurrence count completed: 7168.
- The current worktree grammar smoke rejected the real Q05 traceg with `missing immediate`.
- The independently built frozen consumer parser at commit `25aa29862239a408099639ae9d5f1a0ea4fee1e1` rejected the same traceg with the same error and return code 2.
- Therefore the current and accepted consumer parser results are consistent. `CURRENT_ULDC_BLOCKER_IS_NOT_ACCEPTED_CONSUMER_PARSER` is false.
