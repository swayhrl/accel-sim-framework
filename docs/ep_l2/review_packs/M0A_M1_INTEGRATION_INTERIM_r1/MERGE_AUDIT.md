# Immutable merge audit

| Item | SHA / result |
| --- | --- |
| M1 Core input | `955a50cbb5e8d928b6c7b0c78e1af062b835df44` |
| M1 Framework input/runtime base | `aae62b66685f15437cecf0193934f628e6fac6ae` |
| M0a Core input | `666f0ba2d7b6a027f395346e274a934c19fdd3c1` |
| M0a Framework input | `2da5dba0d0ca60dfa2ee5c12cb3b315c2c54120d` |
| Integrated Core | `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e` |
| Runtime Framework/runner at compact execution | `d61ffd23c926a25fa463a3e6e955c885b45f0f8a` |
| Final framework analysis/pack source | `3d39fd5ad882bc7fd72f5b70bc6342f15519889c` |

Core starts at exact M1 then cherry-picks exact M0a commit. Framework starts at exact M1 Framework, cherry-picks immutable M0a tooling/config commits, then adds only integrated mode/provenance and analyzer semantics. No moving branch tip was merged.
