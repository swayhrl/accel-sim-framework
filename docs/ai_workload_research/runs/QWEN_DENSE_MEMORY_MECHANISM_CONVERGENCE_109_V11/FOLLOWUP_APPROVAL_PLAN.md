# Deferred native resource-response experiment; NOT executed
This is an approval plan, not a promoted hardware mechanism or next Goal.

A true native memory-versus-SM supply axis would require resource-owner and administrator approval for global GPU state changes. Current V11 authorization does not include clocks, power or permissions. No setter was called.

Before approval, identify exact driver/device capabilities with read-only supported-clock/control queries. RTX4080 support and privilege must not be assumed. Save initial clock policy, application/locked limits, power policy, active throttling reasons and device identity. If the original state cannot be queried and restored exactly, do not execute. Reset-to-default is not an adequate substitute for restoring an existing policy.

The owner-approved maintenance window must cover all GPU users, including gated Image-Lab and desktop impact. A bounded controller would vary one supported memory supply level while keeping measured SM supply fixed, then independently vary SM supply while memory is fixed. Balanced order and native fixed-input timing must be separate from profiling. Unsupported clock controls must not be replaced silently by coupled power changes.

Use a separately owned watchdog and exact saved-state restore on normal/error/timeout, followed by read-back; uncertain restoration ends the campaign and requires the resource owner. No privilege escalation, persistence change or permanent setting is authorized here. Concrete setter values/commands remain deferred until supported ranges and restoration can be proven.

This axis could test H_MEM/H_SM response, not prove an innovative mechanism or PPA improvement. Given the present negative hardware-candidate decision and unavailable independent workload, archive Qwen as a baseline rather than automatically scheduling this experiment.
