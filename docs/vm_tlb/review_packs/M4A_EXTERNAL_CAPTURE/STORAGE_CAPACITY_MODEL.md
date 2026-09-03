# Storage capacity model

Observed retained inputs: model snapshot 2.48 GB, CUDA 12.6 7.46 GB, venv 5.31
GB, NVBit tracer tree 10.6 MB. Formal prefill: 724 raw (3.365 GB), 724 traceg
(161 MB), 3.527 GB archive. Formal decode1: 772 raw (738 MB), 772 traceg (37
MB), 774 MB archive. Disk free was 978 GiB before prefill, 970 GiB before
decode1, and 968 GiB after decode1; peak free was not sampled, so is UNKNOWN.

For future Llama-3.2-1B Route-E work, use 100 GiB practical minimum, 250 GiB
recommended, and 500 GiB conservative capacity. Streaming offline analysis may
need far more scratch than compressed archives because traceg expansion is high;
its peak was not measured. After archive integrity and
main-server SHA256 equality, regenerable remote run directories and duplicate
remote archives may be deleted; keep the verified main-server archives, source
manifests, sidecars, and checksum records.
