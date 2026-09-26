# Validation

- Lane B handoff judgement and seven exact request-set overlaps consumed from
  commit `9efe8236e0c6338addfef5480e1da91bffb504eb`.
- Four 0/80 diagnostics: correctness/coverage/quiescence PASS.
- Four Level-1 Observatory replays: exact cycles, instructions, CTAs, and
  L1/L2/MSHR/PTW/PTE service counts versus accepted reference PASS.
- H2 zero-collision result is source-derived from the reference's reverse scan,
  not inferred from missing events.
- All indexed raw hashes, JSON/TSV schemas, pack manifest, diff check, and final
  git closure are validated at closeout.
