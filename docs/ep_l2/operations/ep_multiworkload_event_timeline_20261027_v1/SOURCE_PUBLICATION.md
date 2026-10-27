# Observer source review

Executing Core: [`78f4b59e865b136eede74df74c44c210f5b4ca04`](https://github.com/swayhrl/gpgpu-sim/commit/78f4b59e865b136eede74df74c44c210f5b4ca04), on independent branch `hrl/ep-l2-multiworkload-event-timeline-20261027-v1`. The actual Core commit was pushed without changing its metadata, and independently read back through the GitHub connector. No accepted EP-MAIN branch was merged or changed.

Executing Framework remains `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`. This documentation review branch is a research artifact, not the Framework identity of the executing binary. ELF SHA: `78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a`; static-library SHA: `e5a743a2bb796d82f58109251f43d5c1997d5c1f7fdeac61213416da3835b697`.

The new Core adds bounded passive endpoint notifications and explicit LIFE SUMMARY_STAGE wire output. Event defaults OFF; no new cache probe, queue operation or scheduling decision is introduced. The new producer requires its own application qualification.

Source checkout, CPU protocols, exact per-input compatibility, loader-only identity, application acceptance and storage restoration are separate evidence populations. A seven-character Framework banner is tied to the complete immutable source and binary identities; the initial legacy eight-character guard failure is preserved, and no second help invocation was made.
