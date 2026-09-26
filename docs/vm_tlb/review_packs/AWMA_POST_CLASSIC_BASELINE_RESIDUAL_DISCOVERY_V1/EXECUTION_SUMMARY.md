# Execution summary

## Commit history

- parent coordination: `d1b58f8a4a0beac3f9c760f5933faf7e701a1152`;
- L1 0/80 preregistration: `3e6e38811afe2cc0c6c7d336d0b7ef8cd92ad4f9`;
- Level-1 Observatory preregistration:
  `62eb91b45f5a01b934a1e480c77bc4f269c8f474`;
- final evidence/report commit: the commit containing this file.

## Changed-file summary

Only this stage's review pack and four execution/analysis scripts under
`util/vm_tlb/awma/` are added. No simulator/Core/config/trace, Lane B, Lane E
prep, coordination, or frozen PREL1 source is modified.

## Validation summary

- seven accepted Lane-B reference rows and request-set conclusions reused;
- four 0/80 causal diagnostics PASS;
- four exact-neutral Level-1 Observatory replays PASS;
- all coverage, terminal, duplicate-application, and quiescence gates PASS;
- indexed raw hashes and review-pack manifest PASS.

## Open issues and boundaries

- 10-cycle L1 latency is a frozen simulator parameter, not an RTX4080 public
  hardware fact;
- Level 1 does not pair each address-apply event to cache admission;
- repeated MSHR-full retries on SPLITKV/A1/A2 remain observed but are not a
  causal runtime fraction; no capacity intervention was needed after the
  differentiated-candidate gate failed;
- no new problem/candidate survives, so there is no formal-development or
  holdout plan from this stage.
