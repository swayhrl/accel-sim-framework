# V26 interpretation

DeepSeek MLA persistence is multi-object: key and value `DynamicCache` tensors persist logically across decode while append updates replace storage with enlarged tensors. QK directly reads the cache-after key object, but its operand has a 2048-position persistent prefix plus one just-appended current position. The admitted QK anchor therefore remains `MIXED_PERSISTENT_CACHE_CONSUMER`, never clean single-object direct-read evidence.

V26 formal QK: 20 direct-GLOBAL static MREFs; 16 executed/4 zero; 7116816 active-lane events; overflow zero; ACK PASS. No cross-replay VA comparison, chronology, reuse distance, or cache/TLB causality claim is made.
