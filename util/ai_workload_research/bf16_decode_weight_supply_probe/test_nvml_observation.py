"""Pure CPU regression: never initialize NVML or CUDA."""
import ctypes
import unittest
from nvml_observation import normalize_used_gpu_memory as normalize

class MemoryNormalization(unittest.TestCase):
    def test_unavailable_and_valid_values(self):
        for value in [None, (1 << 64) - 1, ctypes.c_ulonglong(-1), -1]:
            with self.subTest(value=value):
                self.assertIsNone(normalize(value))
        for value in [0, 123456]:
            with self.subTest(value=value):
                self.assertEqual(normalize(value), value)

    def test_installed_binding_sentinel(self):
        import pynvml
        self.assertTrue(hasattr(pynvml, "NVML_VALUE_NOT_AVAILABLE_ulonglong"))
        self.assertIsNone(normalize(pynvml.NVML_VALUE_NOT_AVAILABLE_ulonglong))

if __name__ == "__main__":
    unittest.main()
