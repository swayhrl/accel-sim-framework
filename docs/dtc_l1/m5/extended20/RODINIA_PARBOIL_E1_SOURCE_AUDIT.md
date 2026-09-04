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

## Remaining hard E1 work

- materialize each selected canonical input and freeze its byte SHA-256;
- reproduce source-compatible builds and extract executable/PTX hashes;
- capture the complete command/toolchain/launch geometry;
- run each source-defined output smoke against its frozen checker/reference;
- recheck every identity against the M5.2 Core/Framework/config/parser anchor
  before allowing any E2 job into its runtime registry.

No workload was built, executed, reordered, substituted, or performance-ranked
by this audit.
