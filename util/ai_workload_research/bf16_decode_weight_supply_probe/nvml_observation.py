"""CPU-testable normalization for the installed NVML Python binding."""
def normalize_used_gpu_memory(value):
    if value is None:
        return None
    value = int(getattr(value, "value", value))
    return None if value < 0 or value == (1 << 64) - 1 else value
