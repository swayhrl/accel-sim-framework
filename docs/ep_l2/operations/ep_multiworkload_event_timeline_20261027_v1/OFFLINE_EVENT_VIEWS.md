# Offline event waveform and UID views

The real new-Core Vector ON accepted raw was decoded and rendered without a model rerun. The pipeline produced 8 files, 11,333,469 bytes in total, in about0.52 host seconds. Raw, catalogue, exact80-byte contract, Core header and implementation hashes are in ACTUAL_VECTOR_OFFLINE_VIEWS_RECEIPT.json.

Portable source: `util/ep_l2/event_timeline_v1/epet_views.py`. Run `python3 -I epet_views.py render --raw RAW --kernel-catalog expected.json --out-root FRESH`. The independently checked catalogue is a JSON list of actual ordered `{"uid":1,"name":"SYMBOL"}` objects. The fixed package is for Core78f4, geometry64 slices/32sets/8ways, contracte5b/header43ab.

Outputs include VERIFIED_EPET_COMPONENT.json, EVENTS.csv, UID_TIMELINES.json, UID_TIMELINE.html and SYNTHETIC_ORDINAL.vcd. The HTML filters exact decimal UID/parent and retains integers as strings. GTKWave may open the VCD directly. VCD display coordinate is notification ordinal with a synthetic format unit; CORE/L2/DRAM counters are actual signals, not invented nanoseconds. Within-tick changes remain distinct.

Actual Vector ON: 36,695,416 notifications, three ordinary high-pressure snapshots, 6,144 unique captured ordinals, 101,908 compressed event bytes and 152,981 wire bytes. The fixed observer object plus declared auxiliary allowance is3,868,584 bytes, below8MiB; broader ELF/static-storage and resident-memory limits are documented in OBSERVER_STATE_AND_OVERHEAD_SCOPE.md. FullNEW and production TagFAIL counters are zero. A critical fourth slot was reserved and unused. Capacity-missed/repeated high-head triggers are declared; a small selected window is not complete application coverage or a latency sample for all requests.

All views are display/component artifacts and confer no source/input/scientific qualification. Missing packet ancestry, incomplete spans and different generation namespaces remain UNKNOWN. CPU synthetic-cpu is an explicitly separate engineering mode. The original package manifest was frozen after CPU checks; the separate actual-app receipt records Main's later real positive offline closure.

The Conv S critical fourth snapshot and its exact source catalogue are documented in `conv_event_timeline_examples/CONV_S_CRITICAL_CAPTURE_TIMELINE.md`:206 retained checks of one UID show R8/Frontend refusal, with the eventual result right-censored. Its offline views occupy16,046,734 bytes; that display-file total is distinct from compressed application event bytes.
