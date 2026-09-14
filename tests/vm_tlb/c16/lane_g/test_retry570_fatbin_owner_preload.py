from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
SOURCE = (ROOT / "util/vm_tlb/c16/lane_g/retry570_fatbin_owner_preload.cpp").read_text()
MAPPER = (ROOT / "util/vm_tlb/c16/lane_g/retry570_route_b_v2_static_map_tool.cu").read_text()
PARENT = (ROOT / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_nvbit_qualification.py").read_text()

class FatbinOwnerPreloadTest(unittest.TestCase):
    def test_records_runtime_registration_and_mapper_requires_it(self):
        for token in ("__cudaRegisterFatBinary", "__cudaRegisterFunction", "dladdr(host", "C16_NVBIT_FATBIN_OWNER_REGISTRY_PATH"):
            self.assertIn(token, SOURCE)
        for token in ("owner_from_fatbin_registry", "cudaRegisterFunction_host_stub", "fatbin_registry_path"):
            self.assertIn(token, MAPPER)
        self.assertIn("hash-closed fatbin owner preload", PARENT)

if __name__ == "__main__": unittest.main()
