# Final decision

`MODEL_DERIVED_UVM_NO_DISTINCT_PROBLEM`

Evidence:

- All 10 preregistered cold/repeat points completed under the GPU lock and 20 GiB cap.
- D1 shows the expected cold placement cost and fast resident repeat for a 16.381 GB exact-metadata tensor stream.
- D2 has a sharp, reproducible migration-volume transition at 18.790 GB (1.094x physical VRAM): M0 moves 195.007 GB and M1 moves 270.169 GB. Current-step prefetch worsens both migration volume and time at this point. This is a useful platform boundary, but it is an instance of known UVM oversubscription/prefetch behavior and known KV placement pressure, not a distinct research problem.
- D3 actual routing has high dispersion (64/64 experts observed; normalized entropy 0.9851). The complete OLMoE footprint is only 13.838 GB and remains resident on this 16 GB device, so it provides no natural expert-oversubscription problem. No artificial scaling was introduced.
- The one bounded managed-PyTorch bridge attempt is `NOT_READY`, so end-to-end framework behavior is not established.
- Fault counters are unavailable; no fault/TLB/PPN/page-size mechanism is inferred.

No problem card is emitted and no UVM mechanism development is authorized by this result.
