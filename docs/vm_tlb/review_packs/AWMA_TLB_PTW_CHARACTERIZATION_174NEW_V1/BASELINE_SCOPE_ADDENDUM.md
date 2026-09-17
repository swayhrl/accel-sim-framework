# Baseline scope addendum

H0 is archived and read-only: SIM_INPUT, SIM_BASELINE, SIM_RUN and SIM_EVIDENCE are not modified or reissued. New characterization profiles consume the same frozen Q05 Prefill SIM_INPUT and are scoped only as `FIXED_WINDOW_PROGRESS_SENSITIVITY`.

The historical whole-VA KV object map is not used for R0. Core source `vm_translation.cc:132-201` makes an empty object-map path a disabled map returning `OBJECT_UNKNOWN`; guarded attribution paths record telemetry only. Segment mapping is separately disabled for R0; ordinary paging mapping remains the intended data SimVA→SimPA path.
