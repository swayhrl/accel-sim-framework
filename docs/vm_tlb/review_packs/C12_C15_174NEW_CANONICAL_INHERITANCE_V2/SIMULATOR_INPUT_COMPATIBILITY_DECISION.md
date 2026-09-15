# Simulator input compatibility decision

Decision: `NOT_PROVEN_LOSSLESS`; boundary is frozen fail-closed.

Current C16 formal artifacts preserve scoped active-lane addresses, phase/kernel identity, object maps, fingerprints and receipts. The observed modern stores are JSONL and MREF-sharded binary data. They do not prove whole-kernel temporal order across shards, static instruction identity/opcode, byte width/access kind for every record, active mask/warp/CTA identity in the simulator grammar, or synchronization/control events needed for faithful coalescing and timing.

The historical simulator requires `kernelslist.g` plus `.traceg.xz` records. No existing repository path was proven to convert current C16 MREF shards into that grammar. Fabricating ordering, widths, opcodes, or coalescing would be a new model, not a lossless conversion; no converter was created.

Modern C16 offline page/cache-line/object metrics remain valid within their accepted scope and are not invalidated by this decision.
