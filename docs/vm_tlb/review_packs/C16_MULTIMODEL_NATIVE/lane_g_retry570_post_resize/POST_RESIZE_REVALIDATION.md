# Retry570 post-resize revalidation

Status: `C16_RETRY570_POST_RESIZE_REVALIDATED`.

The restarted and expanded node was observed as RTX3090 / SM86 with new UUID
`GPU-0c257cc7-45dd-5533-5435-7f42e7008e0e`, driver `570.124.04`, CUDA toolkit
12.4.131, and the unchanged CPython 3.10 Torch `2.5.1+cu124` runtime.  The
fixed NVBit 1.8 archive, official tools, and C16 tracer all match their prior
SHA256 anchors.  The mounted remote data disk has 198,796,951,552 bytes
available, passing the 100 GiB formal-capture gate.

Exactly one non-model PyTorch elementwise C16-tracer sanity ran after the
restart.  It exited normally in two seconds and emitted nonzero trace data;
the raw tree was transferred and hash-closed locally.  The full 1.7.6/1.8
matrix was intentionally not rerun.

This is infrastructure revalidation only.  No model asset or C target was
transferred, read as an outcome, modified, or executed.  The next permitted
stage is the M1 Llama model-level qualification diagnostic.
