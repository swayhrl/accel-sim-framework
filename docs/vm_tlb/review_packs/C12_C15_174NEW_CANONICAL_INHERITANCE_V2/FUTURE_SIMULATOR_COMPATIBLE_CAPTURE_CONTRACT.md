# Future simulator-compatible capture contract

Future capture intended for Accel-Sim replay must emit, per kernel and in deterministic global order:

- kernel launch sequence, phase, grid/block and context/stream identity;
- static instruction identity and opcode/access kind;
- warp/CTA ID, active mask and per-lane virtual address;
- byte width and read/write/atomic semantics;
- synchronization/control markers and instruction ordering across all shards;
- trace schema/version and producer commit;
- a simulator-ready `kernelslist.g` and `.traceg.xz` payload (or a formally specified lossless converter output);
- object-map labels, ASID/epoch, VA width and page-size policy as sidecars;
- SHA256 for every payload, list, sidecar and converter binary/config.

Capture acceptance requires decoder record-count/address checks, deterministic re-read hashes, and a bounded parser smoke before any performance replay. Missing fields remain `UNKNOWN`; do not synthesize them from neighboring records.
