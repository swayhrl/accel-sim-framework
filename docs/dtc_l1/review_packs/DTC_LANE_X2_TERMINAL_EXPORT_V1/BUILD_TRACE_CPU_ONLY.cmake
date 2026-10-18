# Copy to an isolated recipe directory as CMakeLists.txt; use -S there.
# Builds the unchanged Framework trace executable against the independently
# built Core shared library, as the Framework Makefile does. No workload runs.
# Avoids fetching the optional Python binding dependency required by the
# Framework top-level CMake. No Core/Framework source file is generated/edited.
cmake_minimum_required(VERSION 3.17)
project(DTC_LANE_X_TRACE_BUILD LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_BUILD_TYPE Release)
string(REPLACE "-DNDEBUG" "" CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")
foreach(required CORE_ROOT FRAMEWORK_ROOT CORE_BUILD CORE_SHA FRAMEWORK_SHA)
  if(NOT DEFINED ${required})
    message(FATAL_ERROR "Missing ${required}")
  endif()
endforeach()
file(WRITE "${CMAKE_BINARY_DIR}/accelsim_version.h"
     "const char *g_accelsim_version=\"accelsim-lane-x-framework-${FRAMEWORK_SHA}-core-${CORE_SHA}\";\n")
set(trace_root "${FRAMEWORK_ROOT}/gpu-simulator")
include_directories("${CORE_ROOT}/src" "${CORE_ROOT}/libcuda"
                    "/usr/local/cuda-11.8/include" "${CMAKE_BINARY_DIR}"
                    "${trace_root}/ISA_Def" "${trace_root}/trace-driven"
                    "${trace_root}/trace-parser"
                    "${FRAMEWORK_ROOT}/util/tracer_nvbit/tracer_tool")
file(GLOB driven_sources "${trace_root}/trace-driven/*.cc")
file(GLOB parser_sources "${trace_root}/trace-parser/*.cc")
add_executable(accel-sim.out "${trace_root}/accel-sim.cc"
               "${trace_root}/main.cc" ${driven_sources} ${parser_sources})
target_compile_definitions(accel-sim.out PRIVATE DEBUG=0)
target_link_libraries(accel-sim.out PRIVATE "${CORE_BUILD}/libcudart.so"
                       m z GL zstd pthread)
set_target_properties(accel-sim.out PROPERTIES BUILD_RPATH "${CORE_BUILD}")
