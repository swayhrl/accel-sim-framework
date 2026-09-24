# V3 mapping-digest source audit

V3 adds a behavior-neutral observer inside `translation_controller::translate`.
At each existing legal V1 controller call it records the canonical tuple:

`ASID, VPN, page_size, translation_generation, resolved_PPN`.

The observer only calls the existing functional page-table resolver, stores a
canonical map keyed by `translation_key`, asserts repeat consistency, and emits a
sorted-map FNV64 digest from `print_stats`. It does not add a controller call,
alter `consume_ready`, modify an access, fill a TLB, enqueue a request, or alter
downstream arbitration. The V3 source was rebuilt and the digest was checked in
the A1 T2 OFF/ideal pair and in all final ideal points.
