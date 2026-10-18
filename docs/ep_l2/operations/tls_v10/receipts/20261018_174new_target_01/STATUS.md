# TLS-V10 target: started, protocol preparation ready; source resource HOLD

New independent target branch: `hrl/tls-v10-174new-target-exec-v1`. Initial remote-readback commit is `0ed56e745dfe44ff4c3547d3b560c1e1eb988008`. Closed V9 remains at `c870ca77456d4d4d70a110411fa5c60934976666`; no C2P/M2D rearchive.

Real164 identity and byte-pinned V9 tooling passed. A new target-only native tmpfs verification environment (24 GiB ceiling, no scientific contents) passed a 33-byte reopen SHA, UID/GID/mode/mtime and directory metadata probe. It does not allocate 24 GiB upfront, consume Share staging, or certify source resource admission. It is volatile proof storage; genuine164 remains the durable archive.

The 128 MiB raw-chunk / 256 MiB allocated bridge proposal is published at `85fe04e41b339d1584084194080fc12109a7dbb0`. Each chunk has an explicitly scoped proof and SOURCE_KEEP ACK; full group acceptance is followed by independent native restoration of **all original files and directories**. Source agreement is required before any COPY_READY is consumed. No new transfer system or second stream.

Source commit `8501782a7f7f23224bd825835f66923757d1ac2c`, checked after the cutoff, reports two live Lane5 sims and failed-closed source freeze with no manifest, hash or bridge payload. Target acknowledges this HOLD and will not bypass it. The cutoff alone is not admission. Source must publish fresh independent Lane/resource PASS and exact frozen selector/COPY_READY.

Current scientific archived/restored bytes: **0**. Target source deletions: **0**. Source recovered bytes: **0**. No Lane PID, registry, lease, quota, budget or scientific result changes. No TLS real164 data root has been created before selector binding.
