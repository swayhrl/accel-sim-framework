# Translation timeline source audit

`translation_key` in frozen `vm_translation.h:18` contains `asid`, `vpn`, and `page_size`; telemetry must retain all three.

`translation_controller::translate` (`vm_translation.cc:2160+`) is the request entry and uses `find_lookup(sid, waiter_uid, key)`. L2-hit fill is at `:2007`; page-walk resolution fills waiters at `:2321` followed by `note_requester_completion`. Walk starts occur at `:2366`/`:2398`. `note_requester_completion` is the completion accounting point.

Diagnostic events may append immutable text only after these existing decisions. No branch result, queue, latency, allocation, fill, replacement, mapping, or scheduling state may be modified.
