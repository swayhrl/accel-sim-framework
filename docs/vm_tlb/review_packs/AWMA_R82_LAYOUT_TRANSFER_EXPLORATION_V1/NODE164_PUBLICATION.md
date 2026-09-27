# node164 publication

Transport: node109 tar stream -> configured hrl174new -> node164 SSHFS mount. Node174 was used only as the existing storage transport; no analysis or simulation ran there and no raw was retained on its local filesystem.

Canonical path: `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/round08_20260927/R82/`.

Pre-close payload manifest SHA256: `f227c54285ab0faae6c9076e6436c2d9f6c10f290f5b4e24dcdd11532d395090`.

Remote pre-close `sha256sum -c SHA256SUMS`: PASS, 86 files. The initial tar returned ownership-restoration warnings on SSHFS; content hashes all passed, and final synchronization uses `--no-same-owner`.

Final remote verification after atomic rename:

- manifest SHA256: `022eeffbc52743a949e7e9375e399ceef52dc8ae41334012814af7909808d130`
- file count: `88`
- content tree hash: `fc54303d94f3af0ae346bfc3f84d35b159f4fc03dbb2e641a0b0aa16945f516e`
- final `sha256sum -c SHA256SUMS`: PASS
