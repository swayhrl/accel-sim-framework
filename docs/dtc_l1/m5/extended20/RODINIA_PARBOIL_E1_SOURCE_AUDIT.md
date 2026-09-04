# Extended-20 E1 Rodinia/Parboil source audit

Status: **SOURCE/LAUNCHER/OUTPUT-CONTRACT RECOVERED — BUILD/PTX/INPUT/SMOKE PENDING**

This is E1 provenance preparation only.  It neither admits an M5.E2 run nor
converts historical launcher entries into FORMAL performance evidence.  Every
entry remains subject to a post-M5.2 common-anchor recheck.

## Candidate repositories

| suite | clean candidate commit | selected source root |
| --- | --- | --- |
| Rodinia 3.1 | `gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1` | `src/cuda/rodinia/3.1/cuda/` |
| Parboil | `parboil@4e0fc54866546efa44fe93af57c9cef62f6c8eb9` | `benchmarks/` |

The checked candidate worktrees were clean when these identities were read.
Git tree/blob object IDs below identify source content; they are not executable
or PTX hashes.

## Rodinia 3.1 selected entries

| approved workload | source tree | Makefile blob | source/launcher evidence | output-contract state |
| --- | --- | --- | --- | --- |
| `cfd_097k` | `fe8279d4be56b847d9af28cae64221dd55576314` | `76df25d3a8b3bc735578493436c383501ff02de9` | `cfd/euler3d.cu` SHA-256 `b5015e61e413dbf711a1e928505d5591f21639644a156dfe31f2e126ce788079`; launcher preserves `./data/fvcorr.domn.097K` only as a commented lead | no native final checker/reference frozen |
| `btree` | `26cdc6bcb8332767f274a5ed7e0305862d8e1abf` | `e77c6b94f76585bee758fa7c987d85332d6234b2` | `b+tree/main.c` SHA-256 `f461ed1696a757de44b4d3453b5699e5cb8cc0b71ff06be8a650ce44f26ef918`; launcher: `file ./data/mil.txt command ./data/command.txt` | source emits verification-oriented output; reference/checker pending |
| `dwt2d` | `698ebcbedd3b3e8b304847d64784bf5d1afafcbb` | `1ffd3c77588cd08134444c758f3de96b899a5baf` | `dwt2d/main.cu` SHA-256 `7c8278f352ca43f992ca9da380011fe82a831d93a0e6a7e4e2e6ddf4fdf56ed6`; launcher: `./data/192.bmp -d 192x192 -f -5 -l 3` | emitted image contract identified; reference/checker pending |
| `gaussian` | `2838e708e1591ac0bfdd2ff9c5de5917e56abce0` | `87d3b64fb39d76ff915b5cebe1a880edcdd1e66b` | `gaussian/gaussian.cu` accepts `-f` or `-s`; launcher leads `-f ./data/matrix4.txt`, `-s 16`, `-f ./data/matrix208.txt`, `-s 64`, `-s 256` | source comment names `ge_3.dat` for verification; exact reference/checker pending |
| `hotspot1` | `351b090ddbd315e40f1745895c2dffd51a79c98b` | `b45c30a634a62e10abde5d523329f90dc5652fe9` | `hotspot/hotspot.cu` SHA-256 `0f679be008be285d26ebd7d71eba47b164914dd52873c26ee63beecda2f68cc0`; launcher: `512 2 2 ./data/temp_512 ./data/power_512 output.out` | writes named output; reference/checker pending |
| `lud` | `ac7c71d010fa1e51f8bd5a50e192a6d9e114ac15` | `665e44424d65741ddcb908911147d552cefb04de` | `lud/cuda/lud.cu` parses `-s`/`-i` and `-v`; launcher primary: `-s 256 -v` | source built-in verification path identified; exact output smoke pending |

`cfd_097k` is the approved portfolio name.  The only launcher occurrence for
the `097K` domain input is commented, so it is a provenance lead—not an
admitted input identity—until the file is materialized and byte-hashed.

## Parboil selected entries

| approved workload | source tree | CUDA Makefile blob | checker SHA-256 | launcher input/output lead |
| --- | --- | --- | --- | --- |
| `bfs` | `afa0831398a8f9a9404b3af84f0215d5a539e28c` | `f1d6fb48bc148ff15fd2657657a2cec08c3ebb19` | `9b9909c5b200fdfcca1cc9a90057a3b9e7f279199c20e03d0eab6a6dd9e36d25` | `-i ./data/NY/input/graph_input.dat -o bfs-NY.out` |
| `cutcp` | `4d6a48cc1c39dc956d4373fc85b4b62d4e128aa8` | `45337449f62169675e568d90ed0b0dd929252d8a` | `105bafc261f911bd61066eb5f9131079426d69e1d120e88a1a2da4d76fb772a1` | `-i ./data/small/input/watbox.sl40.pqr -o lattice.dat` |
| `histo` | `962e5f02f939890572b6fdd183db0fa3e0c888c3` | `9e337126a5c80877d1f0d911f8bf34245c415950` | `f6ab91aaec126207b7c774e49f3d15bc8fc5ca4243b083d5cabcce31de9b420e` | `-i ./data/default/input/img.bin -o ref.bmp -- 20 4` |
| `mri-q` | `d95ee2cd5aaa26c402af3830ce8bd7e7796ac405` | `edd50283a8d9d54ffefff9119a694a3aee33eb0c` | `a2c8ee8ae69ae8b97d55945b14ab5936c789aa09fb43d3d236d0e134d8e0d4ce` | `-i ./data/small/input/32_32_32_dataset.bin -o 32_32_32_dataset.out` |
| `sad` | `1ee2d108295f7cc5229821df6efe4aba12a5f68c` | `230deb28ec7dd70f98c2f4b41e2b53f832c2544d` | `f54e330eb7d86342cfce7e1b7ee6657c1455afc87ccf404abebeb6cf86f8f6d1` | `-i ./data/default/input/reference.bin,./data/default/input/frame.bin -o out.bin` |
| `stencil` | `f8b919918aa3b866cb6081526f69dab57359d3fc` | `eeff9081c71a7e6259250ffaa80f22a9d1486c55` | `857d606af1e5a614c38378f2ae4f8f1836f2b063376ab2faa30a1fcb0272f1ad` | `-i ./data/small/input/128x128x32.bin -o 128x128x32.out -- 128 128 32 100` |

All Parboil `tools/compare-output` files are source candidates only.  Their
interpreter/dependency identity, reference-input/output byte hashes and an
actual source-defined PASS remain E1 requirements.

## Parboil selected input identities

The six launcher-selected input sets below are materialized in the clean
`parboil@4e0fc54866546efa44fe93af57c9cef62f6c8eb9` candidate checkout.  These
are deterministic input identities for future E1 smoke work; they do not by
themselves prove that the CUDA build or output checker is compatible with the
M5 simulator runtime.

| workload | repository-relative input | Git blob | SHA-256 |
| --- | --- | --- | --- |
| `bfs` | `datasets/bfs/NY/input/graph_input.dat` | `0157cfbe12b2677b3669bf2cdfae3f549abb22f7` | `6de0d396b9675326bec4764ff1d9ae6b788b36281c5d0fcafad386fa9e7f14bd` |
| `cutcp` | `datasets/cutcp/small/input/watbox.sl40.pqr` | `917c3faa3a75ed47e8eb3d0d158690358f17793d` | `7b2059d475ecebc5007570617959ebea62cfc94668f38dc8f7e8690379490f84` |
| `histo` | `datasets/histo/default/input/img.bin` | `f42bc53c648e1da7213ecabd8a0ec0ea5b5598ae` | `4b1783ec5606cae0791cdc369732397e8f082736d4cbeb010008553ddec1307a` |
| `mri-q` | `datasets/mri-q/small/input/32_32_32_dataset.bin` | `db8385bb0ea6916e969fdba41a0355ab2a1ca471` | `c3d4e1a79b1c51570d36d44c366b36b67500008dbe78aa01578383f2eb26d961` |
| `sad` | `datasets/sad/default/input/reference.bin` | `94fb04f5014bcdfc10c383c6fddc6e29daa3ef30` | `7962566f7ae96f234f39dcfc916c5fd847eef25dc1112ef790e1b7d814de968c` |
| `sad` | `datasets/sad/default/input/frame.bin` | `f8142c46a0cf2ce6695a639d213ad50cefd8c605` | `5b0375c637c7f6fdfc936c9a5f1623891c4c7fa72dcdcf4ed62bf5ce89497251` |
| `stencil` | `datasets/stencil/small/input/128x128x32.bin` | `aea526505970f6ce114de1ac73db6c9764146536` | `f58af01bb8300328ac35a72d4ad267b3fc7685d5146a7108eb987441ea844ebf` |

Rodinia inputs remain `PENDING_FREEZE`: its candidate source checkout contains
the selected programs but not the six launcher data files required to byte-hash
their final input identities.

### Rodinia data-source recovery status

The official Rodinia site identifies 3.1 as the current released suite. The
archived `yuhc/gpu-rodinia` 3.1 source README directs data recovery to the
original package and records this 3.1 data mirror:

```text
https://www.dropbox.com/s/cc6cozpboht3mtu/rodinia-3.1-data.tar.gz?dl=1
```

On 2026-09-04, the original UVA package URL redirected to HTTPS but returned
HTTP 403. The source-recorded mirror resolved to an attachment of 395,919,830
bytes. It has **not** been downloaded or extracted: the active M5.0B
ratio-zero Base wave still has seven long-running workers, and the M5 parallel
batch policy forbids forcing a large source/data materialization while that
resource envelope is active. The exact archive SHA-256 and the selected
Rodinia input-file SHA-256 values therefore remain `PENDING_FREEZE`.

When a measured resource window opens, materialize the archive in a new
isolated directory, first hash the full archive, then identify and hash only
the approved `cfd_097k`, `btree`, `dwt2d`, `gaussian`, `hotspot1`, and `lud`
inputs before any build or simulator smoke. Do not use an unrelated fork's
near-match data as a shortcut.

## Parboil checker runtime contract

The selected checker files are part of the E1 output identity.  `histo` uses
the host `cmp` utility.  The other five declare `#!/usr/bin/env python` but
use Python-2 `file(...)` and/or `print` syntax; the observed host exposes
Python 3.11 and no `python2` executable.  This is a reproducible E1
compatibility task, not permission to omit the source-defined checker or to
substitute a weaker output predicate.

| workload | checker contract | required support modules |
| --- | --- | --- |
| `bfs` | Python-2 `filecompare` + `textfilecompare` float comparison | `filecompare.py`, `textfilecompare.py` |
| `cutcp` | Python-2 `filecompare` + `binaryfilecompare` tolerance comparison | `filecompare.py`, `binaryfilecompare.py` |
| `histo` | `cmp $1 $2`, exact byte comparison | none |
| `mri-q` | Python-2 `filecompare` + `binaryfilecompare` relative/absolute tolerance | `filecompare.py`, `binaryfilecompare.py` |
| `sad` | Python-2 `filecompare` + `binaryfilecompare` exact structured comparison | `filecompare.py`, `binaryfilecompare.py` |
| `stencil` | Python-2 inline binary float tolerance comparison | none |

Support-module identities in the same clean Parboil commit:

| path | Git blob | SHA-256 |
| --- | --- | --- |
| `common/python/filecompare.py` | `eb80e44c90fc634d8ddf74be3dc89dd7c860b8a9` | `8544527c556d11396b5c449700f2d5cc3123024905335521e8e6efcccf23d465` |
| `common/python/binaryfilecompare.py` | `e93b39382a6028b4d52809a2035273505aac7f84` | `921d1b5b65f3789747eecab54a08c94782a5c46f397c15531018fb41251f95e3` |
| `common/python/textfilecompare.py` | `f7cd7abc5d16677f8a7aa8d730625aa24c713cd2` | `50f340e3093bec07fc1ad71933fcdc6c2de85d2193352ef02ccb6df799084c45` |

The checked-in Python-3 compatibility adapter is
`util/dtc_l1/verify_m5_extended_parboil_output.py` (SHA-256
`f656c3bd78c9ae937e94351dd44dec4602b172d2245022ebeb5eb977d3df7431`).
It directly implements the selected native
predicates rather than relying on a generic conversion: BFS text floats,
CUTCP's two source tolerances, exact histo bytes, MRI-Q's source tolerance,
SAD's structured uint16 payload, and stencil's original loop bounds. Its
companion pass/mismatch fixture suite is required to pass before E1 use.

## Remaining hard E1 work

- materialize each selected canonical input and freeze its byte SHA-256;
- reproduce source-compatible builds and extract executable/PTX hashes;
- capture the complete command/toolchain/launch geometry;
- run each source-defined output smoke against its frozen checker/reference;
- recheck every identity against the M5.2 Core/Framework/config/parser anchor
  before allowing any E2 job into its runtime registry.

No workload was built, executed, reordered, substituted, or performance-ranked
by this audit.
