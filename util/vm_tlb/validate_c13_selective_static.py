#!/usr/bin/env python3
"""Fail fast if C13's exclusion overlay can alter common PPN registration."""
from pathlib import Path

CORE = Path('/workspace/worktrees/gpgpu-sim-vm-m4b-c13-diagnostics')
src = (CORE / 'src/gpgpu-sim/vm_translation.cc').read_text()
hdr = (CORE / 'src/gpgpu-sim/vm_translation.h').read_text()
gpu = (CORE / 'src/gpgpu-sim/gpu-sim.cc').read_text()

assert 'class weight_segment_exclusion_map' in hdr
assert 'std::string exclusion_map_path' in hdr
assert 'C13_WEIGHT_SEGMENT_EXCLUSION_V1' in src
assert 'm_weight_segment_exclusions.excludes(lookup.key)' in src
assert 'm_weight_segment_exclusions(config.segment.exclusion_map_path)' in src
assert 'bool weight_segment_map::registered_ppn' in src
# The overlay must be consulted only at the optional Segment resolution site;
# registered_ppn must remain free of it so conventional PTW retains C12 PPNs.
registered = src[src.index('bool weight_segment_map::registered_ppn'):src.index('weight_segment_exclusion_map::weight_segment_exclusion_map')]
assert 'exclusion' not in registered
assert '-gpgpu_vm_weight_segment_exclude_map' in gpu
print('C13_SELECTIVE_STATIC_PASS')
