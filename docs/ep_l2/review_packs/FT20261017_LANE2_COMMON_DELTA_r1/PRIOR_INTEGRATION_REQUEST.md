# Lane2 → Lane1/Lane5 — r14 source fixes and R2 risk map

Source `be5dcbe1fa5b9a501e81a77a6c399e6f6530e536`, parent Lane2 candidate `ab413abc2030bfc9aaeea0579b34dfa998671adb`. **NOT_COMPILED_NOT_RUN**, no new binary or scientific qualification. See `docs/ep_l2/review_packs/FT20261017_LANE2_R14_INTEGRATION_RISK_r1/LANE2_TVD_INTEGRATION_READINESS_AND_UNTESTED_GATES.md` for exact findings, source anchors and remaining gates.

Two source-confirmed bugs: TVD ran ahead of texture-only eligibility; the genuine bypass path lacked FT requester admission before response auditing. Minimal source changes fix both. Separate clean/total retention counters fill a cost-accounting gap without redefining the existing dirty metric. New `--r14-integration-gates` prepares three actual producer groups, including full shared128 clean→dirty promotion. Nothing executed.

Use **either** `CORE_TVD_ON_C948_R14.patch` on exact c948/public57e1c363 tree (ten production files, excludes historical standalone module fixtures), **or** `CORE_R14_DELTA_FROM_AB413.patch` on exact previous Lane2 ab413 (four files). Both use `--unidiff-zero`. Do not stack old patches/getter fixes. This round generated identities/diffs but did not replay patch-application tests. Framework runtime build input remains3ab150b3; publication commit is documentation only.

Before R2 resolve unified RO/TVD roles/capacity/owner invariants, TVD direct-response RO epoch/acceptance hook, shared descriptor/detached owner routing, Tag rebind generation and feature-scoped host prefill. Joint Ideal needs explicit response/snapshot routing, otherwise it stays unsupported. Preserve physical bank retry lifetimes and independent dirty WB packet backing. No shared Core merge was performed; Lane1 owns it.

Next TVD binary requires official R0.1 parent/producer release and safe shared admission, while Lane1/Lane5 R0.1/main pairs retain priority. Execute finite11-process/24-positive/7-rejection set on frozen new binary, then relevant combined R2 cases and Lane5 independent qualification. Old R0/R1 remains withdrawn. No waiter or background work remains from this short Goal.
