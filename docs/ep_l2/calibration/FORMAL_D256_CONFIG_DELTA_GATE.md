# Formal D256 runtime-config binding gate

Status: **PASS**

The retained formal C7e 850-MHz campaign manifest records
`runtime_config_composite_sha256` as
`85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d`.
The D256 formal contract binds to that exact digest. Its normalized effective
configuration is the formal semantic base, so its permitted configuration
delta is the empty set (`allowed_config_fields: []`).

This gate is provenance evidence only. It does not authorize a new baseline
decision or any simulator execution.
