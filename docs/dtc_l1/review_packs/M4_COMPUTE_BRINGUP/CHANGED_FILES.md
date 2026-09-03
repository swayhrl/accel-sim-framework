# M4 changed-file audit

Core M4 implementation range `bfb3b633..cdeec769`:

- `CMakeLists.txt`
- `src/gpgpu-sim/dtc-l1-common.h`
- `src/gpgpu-sim/shader.cc`
- `src/gpgpu-sim/shader.h`
- `tests/dtc_l1_completion_accounting_test.cc`

The range changes no PTX lexer/parser/decode or `abstract_hardware_model.h` file. It adds no fence frontend, membar substitution, forced proxy bit, or regular-fence semantic bypass.

Framework closeout adds the workload manifest, M4 review pack, strict-summary M4 counter keys, and final handoff state.
