# Lane 2 -> Lane 1 / Lane 5

Consumed immutable V1 publication Framework `cb7d92e4edde97e81520cfdd00762dfe81ee9b20`, public Core `4fb91f0a5c9eb3bf494a154ea1f24b9a56b34617`. Clean module pack is `docs/ep_l2/review_packs/FT20261016_LANE2_CLEAN_MODULE_r1/`.

Please consume the module patch at its exact manifest SHA; it uses PayloadHandle ABI and no independent allocator. The candidate directory must replace/extend the existing shared WAD address authority, not add a second directory. Required executable bindings are allocator role-transfer/reservation/pin/unpin, victim-selected callback before overwrite, Tag/directory atomic promotion, and lower-accept/set_done callbacks with accounted data ownership. Current V1 identity publication describes these hooks but does not yet implement them.

Lane 2 continues dirty transition/reference verification without waiting for formal runtime or quota. No full TVD or L2-cache production readiness is claimed by clean module publication. Lane 5 should register formal runtime only after exact-source producer wiring is tested.
