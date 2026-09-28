# Open issues

- Split1 is materially beneficial only at the tested `up_proj_M256`; it is not material at `down_proj_M256`.
- Both M1 conditions regress by more than 5%, strongly excluding a universal split1 policy.
- NCU counters are semantic-range kernel totals under application replay/cache-control none and are not tensor-level byte attribution.
- No full-model performance, extra M values, operators, backends, or split factors were tested by contract.
- Registers, static shared memory, and kernel duration were recorded only because the prescribed NCU export exposed them without adding metrics.
- No automatic follow-up experiment is authorized.
