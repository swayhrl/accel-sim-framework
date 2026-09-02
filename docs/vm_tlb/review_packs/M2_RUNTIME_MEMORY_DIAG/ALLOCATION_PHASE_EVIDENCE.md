# D4 allocation-phase evidence

Two bounded measurements were used: `/usr/bin/time -v` and `strace` with
`brk,mmap,mremap,munmap`; a lightweight temporary `operator new[]` probe gave
the requested element count.  All diagnostic instrumentation was removed.

At the failure, `strace` recorded
`mmap(NULL, 34359742464, ...) = -1 ENOMEM`; the probe recorded
`new[] bytes=34359738360`, i.e. 4,294,967,295 pointer-sized slots.  Stack
evidence placed it at `trace_gpgpu_sim::createSIMTCluster()` before trace
replay.  Mode 0/1/2 failed alike, while the standalone VM controller was small.

The old `trace-driven.Makefile.makedepend` did not list Core headers.  Its
object therefore used stale C++ member offsets after Core extended
`shader_core_config`.  A cold rebuild corrected the value to 46 clusters and
completed at about 188 MiB.  The dependency fix makes Core headers explicit in
the three Framework dependency generators.
