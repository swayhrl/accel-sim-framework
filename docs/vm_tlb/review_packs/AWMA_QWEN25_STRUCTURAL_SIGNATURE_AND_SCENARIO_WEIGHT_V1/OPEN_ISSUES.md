# Open issues / limits

- S2 has one Prefill pass; it cannot establish Prefill recurrence across inputs.
- S2 stability across 32 decode steps does not imply stability across context,
  batch, content, or longer decode horizons.
- The Lane C exact-safe join intentionally leaves many material V2 strata as
  `MISSING_SIM_TRACE`; this is not a request to capture them in this stage.
- Generic Native-only records cannot be joined to an exact structural stratum
  because their function/shape is UNKNOWN.
