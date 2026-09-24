# Source anchors

- Accepted S2 representative suite: ba1b4bdbca47e24a56909eec2764e738c509d2f1.
- Accepted cross-context census:
  0a01aa5de4ab7132ab52d18d689e61b635061ae8.
- S2 structural catalog authority:
  2e8680dc4cc25e2409c2ef37a15ae8c2fc29ae9f.
- S2 catalog SHA-256:
  8af6142299a8699db56f69d3d15966ab6f7ad8de31070e4949abef7ee5235139.
- S2 V3 CLUSTER_CATALOG SHA-256:
  a59857d187c649352f9b3852ad9661234f87189679084f808849fb14706c5c79.
- S2 V3 SUITE_TARGETS SHA-256:
  afdecac9f5bfcaa581c15186217d349c47d354d4f68bfa2b3a2eb1ca79055ab6.

The cross-context eight accepted compact strata/recurrence SHA values are
frozen in the selector source and repeated in RUN_RECEIPT.json. The accepted
cross-context RUN_RECEIPT SHA-256 is
e40e8a6d38b865fa4b1fc786abc9735ed9dcdb278de9f9df78a74435408201d6.

Scenario identifiers:

- S2: B1 / T2048 / D32, accepted S2 TEXT.
- T256: B1 / T256 / D32, derived first-256-token control.
- T8192: B1 / T8192 / D32, accepted S3 TEXT.
- B4: B4 / T2048 / D32, replicated S2 input.
- D128: B1 / T2048 / D128, accepted S2 TEXT prefill and deterministic
  Decode continuation.
