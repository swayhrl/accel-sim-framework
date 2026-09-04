# Post-capture audit

RF0 independently verified both main-server archives: expected SHA256, zstd/tar
listing, internal `SHA256SUMS`, run root, raw/traceg files, manifests, sidecars,
logs, classifier output, and provenance are present. Therefore
`GPU_HOST_NO_LONGER_REQUIRED`.

RF3: real TP4/NCCL is evidenced by embedded trace headers. The all-COMPUTE
classifier output is a filename-only classification limitation, not proof of no
collectives. RF4: traceg text exposes instruction memory addresses and widths;
`analyze_trace_address_coverage.py` is a read-only streaming analyzer. A full
prefill scan was impractical on current scratch due high decompressed expansion,
so no coverage number is claimed.
