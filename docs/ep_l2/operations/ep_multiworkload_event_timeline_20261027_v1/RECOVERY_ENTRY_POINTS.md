# Genuine164 recovery entry points and closed SHA receipts

All payloads are COPY_ONLY/SOURCE_KEEP on genuine164. The index contains complete SHA256 values, exact input/Source/spec/DONE bindings, actual native restore receipts and scope. Archive restoration never grants scientific acceptance.

Genuine164 root: `/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261027_ep_multiworkload_application_v1`. The tested174 mount is the corresponding `/root/share/mnt164/huangrulin/...` namespace; verify the mount source before use.

|Recovery parcel|Archive SHA256|Manifest SHA256|Actual native restore checks|
|---|---|---|---|
|`recovery/frozen_source_runtime_v1`|`d0be1464c2fe20a090e377a6679fbe541d98d60eba6e944c83f5d345f7e63a13`|`4461c903d520c42729e6c919456c1c447ed50ac8b8d4e3444e27c028ac9ff6e3`|two separate native targets; full reopened SHA and native metadata PASS|
|`recovery/final_evidence_v1`|`024b4cdbf2b9b695d0502eb615a5d98e4db876cd2c37dd87a5e4b2bac17da0e7`|`e1640813346f4a67cc9d6a0a9e3fa1768799ce492e60bda459251f80f421b160`|two separate native targets; full reopened SHA and native metadata PASS|

`recovery/publication_closure_v1` is published after the final review commit and contains its Git archive, exact HEAD/parent/tree identity, Source identity, final evidence receipt and recovery index. Its immutable NAS COMMIT/RECEIPT close the publication boundary; the outer SHA is reported separately at delivery, avoiding a self-referential Git commit hash.

For an archived native bundle, use the `RESTORE_MULTI.py` packaged in that exact bundle with `--destination` pointing to a fresh Linux native ext4 directory. The tool verifies its pinned engine/V9/manifest/archive identities. Tests here ran on174 under the existing qualified shared-owner resource guarantees; another restore environment needs its own resource compatibility review. Source/runtime and evidence parcels additionally contain `CONTENTS.json` with each inner member SHA and the named `.tar.gz` payload. Full inner payload readback was checked before publication.

Accepted application payloads are under `accepted/<cohort>/<uuid>`; BICG is an unaccepted forensic payload and remains spent. Exact paths and archive/manifest SHA are indexed, not inferred from filenames. Source/runtime contains the frozen ELF/static library and tracked Core plus available Framework runtime Source; it does not claim a full sparse Framework nonruntime checkout or a complete replacement build-toolchain installation. Third-party/runtime dependencies retain their exact identity references.

DWT is different: `technical_negative/EP_MULTI_DWT_S_ET1_20261027_V1/12d2b7cd-0548-457f-b3b1-56f672c88b7b` stores its engineering parcel. Two native parcel restores and two full original-file-tree native engineering restores were actually verified. The latter use the independently derived103,505,920B bound; original103,452,672B exceeded its frozen scientific96MiB limit and remains NOT_ACCEPTED. The standalone strict recovery helper and its27 synthetic controls are linked in ORIGINAL_FULL_RESTORE_HELPER_MANIFEST.json. No replay/model invocation is part of recovery.

The final evidence payload is a terminal snapshot before its own NAS receipt/final Git publication. The publication-closure parcel supplies those later small records. Original Trace bodies were never copied here: the exact genuine164 inputs and prior attestations remain separate, with fresh small-command/member metadata joins and their stated capture/semantic limits.
