# Current combined host layout; bounded cost disclosure

HOST_LAYOUT_DISCLOSURE.json records a separate sizeof-only CPU executable compiled against each fixed source header with the production gnu++17 dialect. It constructs no model, loads no model library and accepts no trace. The existing actual-LDST CTest independently reports the same combined header dimensions and LDST3392bytes. The initial wrong C++11 probe failed to compile; its stderr is retained, and no Core source was changed.

|C++ object|fixed X2 bytes|combined AG3 bytes|difference bytes|
|---|---:|---:|---:|
|OO physical_line|48|96|48|
|OO PIB entry|56|64|8|
|config|56|60|4|
|service_entry|40|48|8|
|OO frontend object|488|824|336|

At640 physical objects and128 resident PIB entry objects, the selected header object-size difference is `640*48 + 128*8 + 336 = 32080 bytes/SM`. This is a stated full-occupancy object-size calculation, not measured RSS, a claim that every dynamic entry is permanently allocated, or the complete process overhead. The frontend's embedded config is already included; adding its4bytes again would double count it. The service-entry difference, LDST difference, allocator/node storage, vector/list backing allocations and temporary assertion maps are outside this subtotal. Service-object sizes are reported separately because their actual population must be joined to their owning structures before deriving a total.

Do not copy the standalone AD producer's33112bytes/SM estimate into this combined ABI. AE changes config/frontend layout, and a full aggregate would require the current owning-population and LDST accounting. The exact subtotal and its exclusions above are the supported disclosure. Default-OFF software still contains the new C++ metadata; this does not create a free modeled payload bank or extra queue/port capacity.

The measured object dimensions are host implementation facts. A hardware implementation might pack flags, generations, cursors and timestamps differently; diagnostic counters are not automatically required hardware state. RTL area, timing, power, same-frequency operation and equal-area comparisons remain UNAVAILABLE. AE additionally assumes that its frozen XOR row selection costs no extra simulated Tag cycle; no timing or area proof is supplied. None of these CPU measurements is an application speedup result.
