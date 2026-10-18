# AC2 compact collection research

**SCIENTIFIC_STOP_RAW_RETENTION_CAPACITY. Compact is not implemented.**
The proposed2x4KiB banks cannot supply a finite-progress retain-all-raw serial
fallback over the accepted source domain. Production remains AC's160KiB reference;
only CPU capacity evidence and test wiring were added. No simulator campaign.

Core835417b37627e46eaaf215f3ff697263c94a18cc is a test-only STOP artifact, not a
compact performance candidate. Start with [LATEST_REPORT](LATEST_REPORT.md),
[resource contract](COMPACT_RESOURCE_CONTRACT.md) and
[fallback proof](OVERFLOW_FALLBACK_STATE_MACHINE.md). Then read
[CPU matrix](CPU_TEST_MATRIX.md), [equivalence](K0_AND_AC_EQUIVALENCE.md),
[normal export status](NORMAL_EXPORT_DIAGNOSTIC.md),
[cost limits](AREA_TIMING_LIMITATIONS.md), [source delta](SOURCE_DELTA.md),
[SHA binding](SHA_BINDING.json) and [independent handoff](AG_INDEPENDENT_HANDOFF.md).
CPU9/9 is parent regression/resource evidence, never compact integration PASS.
PUBLICATION_RECEIPT and SHA256SUMS bind the release; final receipt commit is
bound externally to avoid a self-referential SHA. No AG campaign is revived.
