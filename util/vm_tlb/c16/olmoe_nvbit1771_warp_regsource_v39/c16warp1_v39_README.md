# NVBit 1.7.7.1 C16WARP1 producer/receiver

This source is the V39 implementation of the historical C16WARP1 scientific
record contract on top of the official NVBit 1.7.7.1 `mem_trace` Channel
lifecycle.  The on-disk record is not a Channel packet: the internal packet is
`{ uint64_t sequence; WRec record; }`, while the final file remains exactly
`<8sIIQQQ` followed by `<6I32Q` records.

The device producer derives lane addresses from the V20-authoritative source:
loads use `C16_WARP_LOAD_ADDR_LO` and its adjacent high register; non-load MREF
paths use NVBit's MREF address API.  A producer ticket is assigned once per
active warp after the CTA filter.  `producer_next_to_push` serializes Channel
admission by ticket, so receiver order is sequence order rather than an
unverifiable concurrent-warp arrival order.

The host receiver checks static identity and every sequence before accepting a
record.  The official flush/receiver-stop/join lifecycle completes before it
serializes the unchanged C16WARP1 bytes, sidecar accounting, and the one exact
`C16_WARP_TERMINAL` line.

Build on node109:

```sh
make ARCH=sm_89 BIN2C=/usr/local/cuda-12.8/bin/bin2c \
  NVCC='/usr/local/cuda-12.8/bin/nvcc -ccbin=/usr/bin/g++ -D_FORCE_INLINES'
```

`c16warp1_v39_accounting_validator.py` is intentionally independent of the
serializer.  It accepts only producer=receiver=serialized, no overflow, exact
sequence closure, and one terminal closure.
