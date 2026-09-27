# Future runner policy

For B8/B24/BFULL and later runs, keep the existing binary/config semantics. Assign concurrent single-thread simulators to distinct physical cores and avoid SMT siblings for isolation; record the chosen CPU/core/socket/node. This is a variance-control policy, not a measured speedup claim.

Retain progress and terminal receipts plus final cycles/instructions/CTA/kernel statistics. Do not pre-stage the full trace, do not use tmpfs for this workload, and do not predecompress: both compressed tmpfs and predecompressed screens were immaterial. Do not apply the rejected PTX guard patch or set either statistics switch to zero on the authority configuration.
