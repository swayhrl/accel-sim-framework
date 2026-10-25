# User-authorized active-science I/O admission change

User instruction on 2026-10-25 (Asia/Shanghai):

> 没关系，你可以传输，解除这个门禁，继续

This supersedes the earlier requirement to stop this archive queue solely because verified active science coincides with `some.avg10 > 5` or `full.avg10 > 1`. Those measurements and actual science identities remain recorded; this particular check becomes monitor-only.

The unchanged sustained severe host-I/O check (`some.avg60 < 25`, `full.avg60 < 20`), SSD and RAM reservations, true164 route/capacity checks, active selected-file writer/reader exclusion, single sender/receiver locks, <=128 MiB raw blocks, <=256 MiB staging, 15 MiB/s Source and 30 MiB/s aggregate limits, immutable transaction identities, range/full-SHA/COMMIT verification, and all retirement restrictions remain in force.

The exact machine-readable authorization is `ACTIVE_SCIENCE_IO_GATE_USER_AUTHORIZATION.json`. Its SHA256 is pinned in the task's resource checker. An absent authorization retains the old check; changed or unknown authorization fails closed.

The old Supervisor caches the old resource module in memory. At a verified common-resource boundary with no running driver, a single controlled replacement loads this authorization. It retains the existing global supervisor lock file, frozen115 queue, driver transaction, original deadline and cumulative check/restart counters. The previous supervisor must exit before its replacement starts. The five-minute Publisher is not restarted. This is a continuation of the existing execution chain, not a new queue, fresh 24-hour budget or parallel migration.
