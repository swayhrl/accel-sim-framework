# M5.E2 payload-identity supersession

`M5_E2_JOB_MANIFEST_TEMPLATE.tsv` is an E1-era PTX-shaped template and remains
historical planning evidence. Before E2 activation after M5.2, its effective
row identity is extended with `execution_payload_kind`, `payload_identity`,
`trace_bundle_id`, `capture_result_manifest_sha256`, `kernelslist_g_sha256`,
`traceg_set_sha256`, and `capture_app_correctness`. A TRACE row cannot use the
PTX-only field as its formal payload identity; a PTX exception explicitly does.
