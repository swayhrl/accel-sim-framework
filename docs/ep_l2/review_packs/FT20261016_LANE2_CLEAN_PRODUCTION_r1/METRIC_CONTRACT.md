# R1-METRIC correction

`served_sectors` and `served_sector_bytes` count the requested valid sector mask only when an actual TVD response enters L2-to-ICNT. They do not count dirty-line bytes carried by WB, unique misses prevented, or DRAM bytes saved. The old C++ `avoided_lower_sectors/avoided_lower_bytes` are deprecated compatibility aliases to SERVED values, explicitly marked in source, and are not exported as savings. Historical module packs remain immutable and their stronger wording is superseded here.

Actual accepted lower reads are observed in l2_cache::lower_accepted AFTER real memport push, independently of response accounting. Matched OFF/ON fixture pairs use the same source/binary/stimulus and differ only by TVD switch; the raw packet/byte observations are reported separately. Physical DRAM transfer savings require separately matched native DRAM counters; NOT_MEASURED here.
