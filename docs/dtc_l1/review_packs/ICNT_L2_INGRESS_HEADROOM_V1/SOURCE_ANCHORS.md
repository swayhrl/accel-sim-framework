# R5 source anchors

R5.0 is recorded by the committed source receipt:
[`SG3_ICNT_L2_INGRESS_SOURCE_RECEIPT_V1.md`](../../iscas2027/granularity/sg3/SG3_ICNT_L2_INGRESS_SOURCE_RECEIPT_V1.md).

It establishes the four-field order of `gpgpu_dram_partition_queues` as
`ICNT->L2:L2->DRAM:DRAM->L2:L2->ICNT`, the default first-field value of 64,
and the `memory_sub_partition::full(SECTOR_CHUNCK_SIZE)` ingress-admission
condition that is counted by the legacy printed `gpu_stall_dramfull` label.
The source receipt also records why that label must be reported as
`gpu_stall_icnt2mem`, not interpreted as a DRAM-full counter.

The only R5 overlays are source-hashed in the four-row registry:

- G: `256:64:64:64`;
- H: the same first-field-only ingress change plus the accepted E detailed-DRAM
  clock tuple `1410.0:1410.0:1410.0:1700.0`.

No L2 capacity/MSHR/miss-queue, remaining partition-queue field, scheduler,
return-queue, mapping, DTC, Core, runtime, trace, or workload identity is
changed by this stage.
