# R5.0 source receipt (pack-local provenance)

Canonical committed receipt:
[`SG3_ICNT_L2_INGRESS_SOURCE_RECEIPT_V1.md`](../../iscas2027/granularity/sg3/SG3_ICNT_L2_INGRESS_SOURCE_RECEIPT_V1.md).

Source confirmation used by R5:

1. `gpgpu_dram_partition_queues` is ordered
   `ICNT->L2:L2->DRAM:DRAM->L2:L2->ICNT`; default is `64:64:64:64`.
2. `memory_sub_partition::full(SECTOR_CHUNCK_SIZE)` performs the finite
   ICNT->L2 admission check for worst-case sector expansion.
3. `gpu_stall_icnt2mem` increments only when that condition and an ICNT
   packet-waiting condition are both true.  Its terminal printed label is the
   legacy `gpu_stall_dramfull`, which is not a DRAM-full counter.
4. R5 changes only the first field to 256; H additionally reuses the accepted
   E DRAM2x clock tuple.  No L2 capacity/MSHR/miss queue, remaining partition
   queue, scheduler, return queue, channel/mapping, DTC, Core, runtime, or
   trace identity changes.
