// Kept in a separate compilation unit so NVBit retains the injected device
// function even though it has no semantic work or trace side effect.
extern "C" __device__ __noinline__ void c16_timing_probe_noop() {
    asm volatile("");
}
