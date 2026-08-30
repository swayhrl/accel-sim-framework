# Source anchors

| Item | Immutable SHA |
|---|---|
| Core D512 parent | `878f80869ce212e779df20b6421e4dc7f987825d` |
| Core M0a candidate | `666f0ba2d7b6a027f395346e274a934c19fdd3c1` |
| Framework D512 parent | `aae62b66685f15437cecf0193934f628e6fac6ae` |
| Framework M0a candidate | `2da5dba0d0ca60dfa2ee5c12cb3b315c2c54120d` |
| runtime_config_composite_sha256 | `d3aaf8a1a090c13e52985d60a70e7b3839aa0793d7db56722a7b3e8da3389b10` |

The candidate was clean when frozen. Core is published at writable remote
`fork/hrl/ep-l2-m0a-observability-v0`; Framework is published at
`origin/hrl/ep-l2-m0a-observability-v0`.

The runtime contract is base `8ccad878…`, trace `19dd14b3…`, D512
`49226901…`, M0a-OFF `24faa69d…`, and M0a-ON `8f1e03de…`. The sole active
OFF/ON delta is `-gpgpu_ep_l2_m0a_stats 0 -> 1`.

Trace `kernelslist.g` SHA256 identities:

| workload | SHA256 |
|---|---|
| vectorAdd_4M | `755319919723f68f25aa7c64b9bdcaf5699b9aca38e7b664825e81d49f306e9a` |
| convolutionSeparable | `ab2290810368438cabf35a3c0fcb9686473aaa2235607a6e2bc0347f651ff484` |
| spmv | `da1065944705e52eb270304233f0865cf80f7618b5597f73af7096d20a194394` |
| cfd_097k | `ce71e70525c6299a6be1bae3790b0eeb0417e1f4608cbd10e706c0a14fdd6b46` |
| sad | `36c0931b5a7cd780dc16fd5466cba2ed31d4a2c1dbf062721f55bbcef1d7a2a8` |
| scan (live) | `6e8572dff8fa6ff912fce3f834009d2e62ace23e3671d083bd901d42af6bcee8` |
