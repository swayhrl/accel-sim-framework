# Qualified normal export protocol

Actual qualification completed and was independently published/fetched at `5c3a40ff81b366bc6fe362518ae4adc23f0597cc`. `NORMAL_TERMINAL_EXPORT_GATE.json` and immutable `normal_export_gate_receipts/independent_v1/` are the result, not the former unpublished draft. Earlier draft/STOP files are retained only in raw `pre_X2_unpublished_draft/`.

The same fixture calls actual production gpu_print_stat→shader_print_dtc_l1_stats on64 real SMs, binds LDST and GPU-print symbols by dladdr to the exact X2 library, captures all103 public counters before/after every print, and observes public cycles0/40/40/43. K1 gives exactly64 unique SMs at every snapshot. Initial no-event UINT64_MAX timestamps, independent changed/retained/reclaimed versus source requests versus ordinary commits, same-boundary last snapshot selection and all negative cases are checked. No direct private observer print is used.

Final synthetic CPU fixture totals are259 requests,258 ordinary commits,2 changed,1 retained and1 reclaimed; they do not forecast or measure Gaussian events. Summing repeated cumulative snapshots produces wrong393 requests and3 reclaims and is rejected. K0 omission and explicitOFF give no event summary and are UNAVAILABLE.

Actual-output mutation tests reject missing/duplicate SMs, missing fields, inconsistent cycles/sentinel, missing/altered frames, unframed private rows and truncated last snapshots. Separate synthetic tests and oldc0 public-output comparisons supplement these checks. Eight old/new corresponding public normal-output boundaries match after removing only X2 export/fixture identity and explicitly host-time-dependent fields. CPU reference oldc0 is never an experimental secondCore.

This PASS proves bounded production normal-export reachability and print nonmutation. It does not prove Gaussian counts, full input correctness, numerical load values, coherence or hardware cost. Full Gaussian terminal export remains NOT_RUN because current I/O resource admission failed.
