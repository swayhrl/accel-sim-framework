# PREPARED_NOT_TESTED. Included after project(GPGPU-Sim), fixture target only.
# Core production source and its cudart dependency closure remain exactly b107.
add_executable(dtc_l1_rob1_collector_ldst
  /workspace/worktrees/gpgpu-sim-iscas2027-dtc-rob1-core-174-v1/tests/dtc_l1_rob1_collector_ldst_test.cc)
set_target_properties(dtc_l1_rob1_collector_ldst PROPERTIES
  CXX_STANDARD 17 CXX_STANDARD_REQUIRED ON POSITION_INDEPENDENT_CODE ON)
target_include_directories(dtc_l1_rob1_collector_ldst PRIVATE
  /workspace/worktrees/gpgpu-sim-iscas2027-dtc-rob1-core-174-v1/src
  /workspace/worktrees/gpgpu-sim-iscas2027-dtc-rob1-core-174-v1/libcuda
  /usr/local/cuda-11.8/targets/x86_64-linux/include)
target_compile_options(dtc_l1_rob1_collector_ldst PRIVATE
  -fno-access-control -UNDEBUG)
target_link_libraries(dtc_l1_rob1_collector_ldst PRIVATE cudart)
