# Trace-pilot status

No Llama workload trace was run. P6 is prohibited until P5 can load the exact
gated revision with valid credentials; this preserves the model/revision and
prevents an unauthorized substitute.

The only real-host tracing evidence is the P3 generic CUDA/NVBit smoke:

- raw trace retained: `generic-nvbit-smoke/traces/*.trace.xz`;
- postprocessed trace retained: `*.traceg.xz` and `kernelslist.g`;
- archive: `generic-nvbit-smoke.tar.gz`;
- archive SHA256: `0b369d661b5b106d40c29a623365794d2dadb36bdb8666e5c46b447f2a0522eb`.

It establishes the NVBit production chain but is explicitly not Llama evidence,
not `DIAGNOSTIC_PILOT`, and not formal C2 evidence. No formal prefill trace was
attempted. No synthetic KV data or Segmentation work was performed.
