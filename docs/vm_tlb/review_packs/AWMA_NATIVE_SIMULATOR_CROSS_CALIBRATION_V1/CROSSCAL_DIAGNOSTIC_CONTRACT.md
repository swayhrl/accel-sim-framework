# Cross-calibration diagnostic contract

`GPGPUSIM_AWMA_CROSSCAL_DIAGNOSTICS=1` observes issue cycles at trace-proven `CS2R` PCs `0x240` and `0x10b0`; default/off emits no events. `GPGPUSIM_AWMA_CROSSCAL_ALLOW_SM89=1` independently admits immutable binary-version 89 traces to the existing Ampere opcode map. Neither switch changes scheduling, scoreboard, accessq, translation, cache, memory requests, retry, random state, or downstream order. Output uses the `awma_crosscal_` prefix.
