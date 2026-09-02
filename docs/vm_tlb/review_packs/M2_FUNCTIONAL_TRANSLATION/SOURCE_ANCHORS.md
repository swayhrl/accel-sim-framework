# M2 source anchors

- Core baseline: `73774727e25fadf89df6f30ef5cf014091115db7`.
- Repaired M2 head: `3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`.
- Preserved provisional G3-1 parent: `8c613a356e6a146951cd59c9929046c6c4cfd856`.
- Framework handoff and validation source head before this documentation update:
  `e6b8d6b6034acd34f5f5176c3b0f4c3a865c09dc`.

The Core repair changes only `vm_translation` retry accounting/resource
behavior and its directed tests.  The Framework contains no M2-RF simulator
source change; its prior `4012be3606c300d11e7b34826ee1cb22b0852b93`
dependency-generation repair remains part of the cold-build provenance.

Status labels: source claims are `VERIFIED_CODE`; commands and logs cited by
the validation documents are `VERIFIED_RUN`.
