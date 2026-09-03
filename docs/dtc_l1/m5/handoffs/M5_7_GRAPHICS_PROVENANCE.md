# M5.7 Graphics Provenance

Status: `CLOSED_WITH_SOURCE_EQUIVALENCE_AND_ONE_UNRESOLVED_SCENE`
Scope: provenance only; this document makes **no simulator-execution or FPS claim**.

## Evidence boundary

The only locally available thesis evidence is the five-row Table-4.1 transcription in
`docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`; it does not contain reference [78], an
archive URL, command line, release tag, or trace.  A repository-wide source/artifact
search found no original thesis project, glmark2 run script, shader/request trace, or
copy of the missing 128x128 2D asset.  The closest reproducible source is the official
[`glmark2`](https://github.com/glmark2/glmark2) history:

- historical anchor `c59072fc810a15bf2e9ae338e9300c6961fc04c5`
  (2014-01-31, after all five relevant scenes already existed), not asserted to be the
  thesis revision;
- release anchor `2023.01` = `42e3d8fe3aa88743ef90348138f643f7b04a9237`.

The seven model/texture Git blobs below are identical at both anchors (and at the
2020.04--2023.01 releases).  Thus their SHA-256 values identify a stable,
source-equivalent asset lineage.  The scene source changed only in small later cleanup
work; its 2014 SHA-256 values are recorded in the manifest.  This establishes neither
the original paper's command line nor its window-system/driver state.

## Required per-workload closure

| Paper name | glmark2 scene/test | source version | shader source | model/texture asset hashes | resolution | vertices | exact/reconstructed options | mapping class | unresolved gaps |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| jellyfish | `jellyfish`; source-equivalent candidate `glmark2 --size 800x600 --benchmark jellyfish` | 2014 anchor above; thesis revision unknown | `jellyfish.vert` `2c0fa04c...`; `jellyfish.frag` `0ad768ff...`; also gradient pass | `jellyfish.jobj` `5004c52d...`; `jellyfish256.png` `f22ee4c...` (256x256) | 800x600 from thesis table; reconstructed invocation | 13,200 from thesis table | Source loads the 256 texture **plus 32 caustic textures**.  The thesis says two 256x256 textures; that difference is retained. | `SOURCE_EQUIVALENT_SCENE_ONLY` | exact version, second texture identity, caustic choice/count, draw count, duration, window options |
| cat-tex | `texture:model=cat:texture=crate-base`; candidate `--size 800x600 --benchmark 'texture:model=cat:texture=crate-base'` | same | `light-basic.vert` `45b986a3...`; `light-basic-tex.frag` `0ec582ee...` | `cat.3ds` `9e535473...`; `crate-base.png` `bf76ecdb...` (512x512) | 800x600 from thesis table; reconstructed invocation | 43,044 from thesis table | Source defaults are model `cube`, texture `crate-base`, filter `nearest`, texgen `false`; selecting `cat` is source-backed but the full paper option string is not. | `SOURCE_EQUIVALENT_SCENE_ONLY` | thesis revision, filter/VBO/validation/duration, original command |
| cube-tex | `texture:model=cube:texture=crate-base`; candidate `--size 800x600 --benchmark 'texture:model=cube:texture=crate-base'` | same | `light-basic.vert` `45b986a3...`; `light-basic-tex.frag` `0ec582ee...` | `cube.3ds` `8d8b716d...`; `crate-base.png` `bf76ecdb...` (512x512) | 800x600 from thesis table; reconstructed invocation | 36 from thesis table | The model/texture are the scene defaults; resolution and other benchmark options remain reconstructed. | `SOURCE_EQUIVALENT_SCENE_ONLY` | thesis revision, duration/window/profile and exact options |
| 2D-tex | no exact mapping recovered; `effect2d` is an explicitly rejected near-match | same, only as negative evidence | `effect-2d.vert` `ecd75aef...`; generated convolution fragment source seeded by `effect-2d-convolution.frag` `cec0cebb...` | `effect-2d.png` `d4c20048...` is **800x600**, not the thesis 128x128 asset | thesis is 256x256; no source-equivalent invocation | 4 from thesis table; `make_grid(1,1,...)` supplies the same four-vertex topology | `effect2d` uses a 4-vertex grid but its asset/resolution do not match.  It is not substituted. | `UNRESOLVED_NO_SUBSTITUTE` | exact scene, 128x128 asset/hash, source revision, kernel/options, command |
| horse | `build:model=horse`; candidate `--size 800x600 --benchmark 'build:model=horse'` | same | `light-basic.vert` `45b986a3...`; `light-basic.frag` `49942f9e...` | `horse.3ds` `1c241dbf...`; no scene texture selected | 800x600 from thesis table; reconstructed invocation | 21,516 from thesis table | Source default is `horse`, VBO `true`, interleave `false`; no texture is selected. | `SOURCE_EQUIVALENT_SCENE_ONLY` | thesis revision, duration/window/profile and exact options |

Abbreviated SHA-256 values expand unambiguously in
[`M5_7_GLMARK2_SOURCE_MANIFEST.tsv`](../graphics/M5_7_GLMARK2_SOURCE_MANIFEST.tsv).
The cat/horse count-and-scene relationship is independently consistent with the
published glmark2 characterization at the [University of Stuttgart repository](https://elib.uni-stuttgart.de/server/api/core/bitstreams/283e15d5-4a68-41e9-bb47-be78ac186c47/content); that is corroboration, not a replacement for the missing thesis reference.

## Explicit non-substitution rule

`2D-tex` remains unresolved.  The superficially similar `effect2d` implementation is
kept only as negative evidence and is excluded from any formal graphics workload list.
Likewise, no source-equivalent row can be called `EXACT` until the original [78]
reference, release/commit, full command, and any divergent asset are recovered.
