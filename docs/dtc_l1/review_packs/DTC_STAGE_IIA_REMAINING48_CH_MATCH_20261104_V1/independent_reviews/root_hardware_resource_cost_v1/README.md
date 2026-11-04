# Fixed downstream resource cost

The fixed Core and accepted effective options establish20 DRAM controllers,2 L2 subpartitions per controller and40 identical256KiB L2 banks:10MiB data. L2 MSHR192, merge4 and miss queue32 per bank remain unchanged.

| Profile | FR entries/controller | FR entries total | Extra vsP0 | Shared credits/partition | Extra shared allowance total |
| --- | ---: | ---: | ---: | ---: | ---: |
| P0 | 64 | 1280 | 0 | 255 | 0 |
| F128 | 128 | 2560 | 1280 | 319 | 1280 |
| F256 | 256 | 5120 | 3840 | 447 | 3840 |

The source computes shared limit as `FR + return_queue192 - (subpartitions2 - 1)` with separate write queues disabled. Each subpartition retains its one private credit. Credits are arbitration accounting, not an independent added SRAM queue: the two extra columns must not be summed as separate buffer storage.

These are logical capacity counts. Physical entry encoding, payload/metadata storage, ports, arbitration, delay, area and energy are not modeled by multiplying simulator C++ objects or host RSS. CH conventional96KiB and DH80KiB physical pool plus its compatibility cache/Tag/PIB/completion structures remain unequal. Matching F settings does not imply equal area or free hardware. No performance optimum is claimed and no new run is authorized.
