# AWMA native TLB reconnaissance probe

This isolated benchmark measures dependent global-memory pointer-chain timing on
one or more active warp lane-0 chains. It reports cycles/load and a register-only
loop control. Address spacing is an experimental address stride, not an asserted
hardware page size. Results are reconnaissance-only and never rewrite simulator
lookup constants.
