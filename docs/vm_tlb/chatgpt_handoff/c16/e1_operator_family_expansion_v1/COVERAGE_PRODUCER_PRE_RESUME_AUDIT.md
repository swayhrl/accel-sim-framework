# Coverage Producer Preliminary Audit Before 174 Resume

## Producer

`hrl/c16-e1-coverage-scaling-109-v1@18acd7dcc10118c68b450d226a8e7ca80c51ad72`

No producer rerun is requested.

## Preliminary evidence closure

Producer reports and raw spot-checks are internally consistent with:

- 28 layers x gate/up/down all qweight-backed;
- stable opportunity shares:
  - gate ~14.76%
  - up ~16.84%
  - down ~15.78%
  - all FFN projections ~47.39%;
- N28 selected up_proj coverage ~16.63%;
- all 28 selected up_proj layers MATERIAL_LOCAL;
- median N28 local benefit ~25%;
- N28 run-aligned whole-decode benefit ~0.892%;
- N14A/N14B robustness;
- FULLHINT_N28 only ~+0.079 percentage points over FAIR_N28;
- stage label `COVERAGE_SCALING_POSITIVE_BUT_SUBTHRESHOLD`.

## Key interpretation to preserve

The N28 result contains a large accounting residual:

- summed selected up_proj local saving median ~0.5674 ms;
- observed decode saving median ~0.1229 ms;
- realization ratio ~0.216.

Because N28 selects all up_proj, there is no non-selected up_proj bucket.

Therefore approximately 0.44 ms is outside the selected-up_proj accounting.

Do not name this residual "collateral slowdown" without direct evidence.

It may include:
- gate/down or other work becoming slower;
- cache/service tradeoffs;
- overlap/timing-boundary effects;
- another downstream effect.

The next operator-family stage measures all 84 FFN projections under policy conditions to decompose it.

## Real producer packaging

Coverage native raw files contain:
- condition/mode/set_name;
- selected_layers;
- module_census;
- all 28 up_proj occurrences;
- decode_step_ms;
- policy_receipt;
- ordered `policy_transitions`;
- requested/actual set-aside;
- no-reset flags.

N28 has:
- 112 timed up_proj decode occurrences (28 layers x D0-D3);
- 140 policy transitions (28 layers x PREFILL/D0/D1/D2/D3).

The existing 174 pre-data consumer may normalize this split schema deterministically before applying its frozen validators.

Every normalized field must retain raw source SHA provenance.

## NCU multi-pass

Coverage NCU profiles can use multiple application replay passes.

Require:
- every PASS replay receipt has identical semantic/token/policy identity;
- BASE `profiler__replayer_passes` equals PASS receipt count.

## FULLHINT boundary

FULLHINT trigger fired exactly under the frozen rule.

Producer ran:
- CONTROL_FULL_N8
- FULLHINT_N8
- CONTROL_FULL_N28
- FULLHINT_N28.

The additional N28 NCU trigger did not fire because the FAIR-vs-FULLHINT difference is below 0.5 percentage points.

The consumer must not require extra FULLHINT NCU evidence.

## Frozen decision rule

174 must independently apply its pre-data coverage decision rule.

Producer label is cross-check only.

No simulator or trace authorization follows automatically from producer closure.
