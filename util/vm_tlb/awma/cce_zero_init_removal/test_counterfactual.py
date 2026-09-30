from pathlib import Path

from common import fixed_meta, init_state_accounting


def test_real_init_state_accounting():
    value = init_state_accounting(151936, 896)
    assert value == {
        "lock_rows": 1187,
        "lock_cols": 14,
        "elements": 16618,
        "bytes": 66472,
        "additional_bytes_vs_c0": 0,
        "full_dc_fp32_bytes": 544538624,
    }


def test_fixed_meta_is_frozen():
    value = fixed_meta()
    assert value["BLOCK_B"] == 128
    assert value["BLOCK_V"] == 128
    assert value["BLOCK_D"] == 32
    assert value["MM_BACK_BLOCK_D"] == 64
    assert value["num_warps"] == 4
    assert value["num_stages"] == 4
    assert value["CCE_AUTOTUNE"] == 0


def test_patch_has_no_full_shadow():
    patch = Path("util/vm_tlb/awma/cce_zero_init_removal/cce_zero_init_removal.patch").read_text()
    assert "tl_lock_first_store_or_add" in patch
    assert "torch.empty_like(c" in patch
    assert "DC_FIRST_STORE=dc_first_store" in patch
    assert "shadow" not in patch.lower()
