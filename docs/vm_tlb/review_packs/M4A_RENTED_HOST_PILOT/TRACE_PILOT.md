# Trace-pilot status

The historical credential-only route was not used. P5 instead used the
authorized checksum-verified local snapshot of the exact frozen revision, and
P6 ran one real `DIAGNOSTIC_PILOT` `decode1` trace. It remains diagnostic,
not formal C2 evidence.

The only real-host tracing evidence is the P3 generic CUDA/NVBit smoke:

- raw trace retained: `generic-nvbit-smoke/traces/*.trace.xz`;
- postprocessed trace retained: `*.traceg.xz` and `kernelslist.g`;
- archive: `generic-nvbit-smoke.tar.gz`;
- archive SHA256: `0b369d661b5b106d40c29a623365794d2dadb36bdb8666e5c46b447f2a0522eb`.

It establishes the NVBit production chain but is explicitly not Llama evidence,
not `DIAGNOSTIC_PILOT`, and not formal C2 evidence. No formal prefill trace was
attempted. No synthetic KV data or Segmentation work was performed.

The diagnostic Llama evidence is retained separately in
`/workspace/m4a-rented-host-pilot/r4-diagnostic-decode1/` and in the remote
archive `/root/autodl-tmp/m4a-llama/archives/m4a-llama-decode1-20260902T171148Z.tar.zst`.
It contains 772 raw `*.trace.xz`, 772 derived `*.traceg.xz`, the preserved raw
`kernelslist.g`, a reproducible classification manifest, and a sidecar with a
real Weight allocation and 128 real KV events. No formal prefill trace has yet
been attempted at the point of this pilot closeout.
