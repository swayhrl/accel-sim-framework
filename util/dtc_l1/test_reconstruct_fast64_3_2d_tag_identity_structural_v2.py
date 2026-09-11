#!/usr/bin/env python3
"""Static regression for the isolated 2D structural-provenance recovery."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
reconstruct = ROOT / "util/dtc_l1/reconstruct_fast64_3_2d_tag_identity_structural_v2.py"
continuation = ROOT / "util/dtc_l1/auto_recover_fast64_2d_tag_identity_v3.sh"
source = reconstruct.read_text(encoding="utf-8")
control = continuation.read_text(encoding="utf-8")
assert "V1 and publishes a distinct" in source
assert "source_summary_sha256" in source
assert "os.link(temporary, V2)" in source
assert "FAST64_3_2D_STRUCTURAL_V2_ALREADY_EXISTS" in source
assert "old_controller_live" in control
assert "auto_continue_fast64_2d_tag_identity_v2.sh" in control
assert "dispatch_fast64_4_2d_tag_identity_v2.sh" in control
assert "PARTIAL_NAMESPACE_REFUSE" in control
print("FAST64_3_2D_TAG_IDENTITY_STRUCTURAL_V2_STATIC_REGRESSION_PASS")
