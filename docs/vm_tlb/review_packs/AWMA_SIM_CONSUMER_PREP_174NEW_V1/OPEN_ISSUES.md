# Open issues

The current-model simulator-native producer bundle does not yet exist in this
consumer checkpoint. Consequently the exact producer/tracer hashes, trace/list
hashes, terminal receipt, address context, launch dimensions, and formal
`SIM_INPUT_ID` remain pending.

This is the explicit next-stage dependency
`NODE109_SIM_COMPAT_PRODUCER_BUNDLE`, not a blocker to
`174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1`. No node109 access or wait is needed in
this stage.
