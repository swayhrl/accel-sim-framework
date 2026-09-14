# Pre-Capture Planning B — Additional Guidance for Unattended Formal Campaign

Ownership: ChatGPT

The existing pre-capture planning goal remains unchanged. This note only sharpens its outputs so a later multi-hour formal campaign can run without operator intervention.

Before STOP, ensure the final capture matrix includes:

1. **Scenario admission intent** per deployment:
   - which historical scenarios actually need formal tracing;
   - which are smoke/control only;
   - which axes are covered by S2/S3/S4;
   - which same-shape content variants can be deduplicated when kernel populations are equivalent.

2. **Ordered representative portfolio** per selected scenario/phase:
   - 4–6 preferred targets total where justified;
   - semantic stratum/role;
   - duration/population evidence;
   - exact function identity;
   - launch selector;
   - static GLOBAL MREF set;
   - NCU evidence;
   - REPRESENTATIVE vs CONTROL classification.

3. **Pre-frozen fallback candidates**:
   - at least one alternate within each important semantic stratum when available;
   - no fallback may be an arbitrary target discovered during formal capture.

4. **Unattended decision fields** in `CAPTURE_CAMPAIGN_V1.tsv`:

```text
model
revision
deployment
scenario
phase
semantic_stratum
target_rank
target_class
exact_function
code_object/static_map_identity
launch_selector
mref_selector
duration_share_or_population_basis
ncu_memory_basis
fallback_group
resource_preflight_required
max_wall_minutes
max_raw_gib
estimated_wall_minutes
estimated_raw_gib
```

5. **Resource preflight command/contract** for every selected scenario:
   exact model + exact frozen input + runtime/dtype/backend, with no retokenization or CPU offload.

6. **Campaign time estimate**:
   best / expected / worst for the entire first wave, not only per target.

7. **Quality warning from RTX3090 history**:
   a target is not acceptable merely because it yields addresses. Representative targets must be justified from the phase population and should not collapse to a tiny address footprint unexpectedly. Historical anchor-local results must not be repeated as phase-wide claims.

Do not start the large formal NVBit campaign in this planning task.
