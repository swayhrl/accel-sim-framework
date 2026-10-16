# R0.1 real admission hold — no repaired runtime release

The one official build driver was actually invoked once on Framework34b32a01 / Core62dc1d17. It refused before CMake/compiler due to the unchanged workspace48GiB floor plus2GiB measured build headroom. This is workspace disk, not memory. See FINAL_RESOURCE_CHECK.json for current exact bytes and deficit.

Lane1 recovered1,091,817,472 actual free bytes by only deleting its inactive, source/hash/inode-indexed .o/.a caches. That recovery was insufficient as shared usage changed. No original raw, trace, CSV, config, unique binary or other-project file was removed; R0/R1 binary content/mtime checks pass. No own process/lease remains, no repeated admission loop or background job runs.

R0.1 source and real producer tests are delivered but uncompiled. No runtime-ready, data correctness, application or independent PASS is asserted. Lane5 owns safe workspace recovery and independent acceptance; the exact resume command is only executable after actual admission. Do not lower the floor or label the old six application rows accepted.
