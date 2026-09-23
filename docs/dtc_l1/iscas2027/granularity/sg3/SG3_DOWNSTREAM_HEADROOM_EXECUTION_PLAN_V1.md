# SG3 downstream-headroom execution plan V1

This is the Phase-B execution receipt produced after the committed Phase-A
queue trigger (`SG3_BICG_DOWNSTREAM_HEADROOM_INTERPRETATION_V1.md`).  It
predeclares exactly four queue-headroom rows in the companion TSV:
BICG/GESUMMV × IO/OO, with the default GPU-wide DTC cap=8192.

The source-defined `cache_miss_queue` is per L2 bank.  Its configuration field
is the first value in the final `queue:result_fifo:data_port` tuple; the
overlay changes only `32:0,32` to `128:0,32`.  It holds capacity, MSHR entries,
merge limit, sector atom, and data/fill port width fixed.  No port row is
authorized because the independent port trigger was not met.

Each launch uses a fresh UUID, immutable runner copy, fresh run directory, and
the existing strict observer-ON validator.  GESUMMV rows remain limited to two
concurrent heavy processes.  No cell outside the TSV may be launched.
