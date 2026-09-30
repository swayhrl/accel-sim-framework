import hashlib

from audit_authority import canonical_json, sha_i64


def test_canonical_json_is_stable():
    assert canonical_json([1, 2, 3]) == b"[1,2,3]"


def test_shifted_contract_preserves_natural_order():
    tokens = [11, 22, 33, 44]
    assert tokens[:-1] == [11, 22, 33]
    assert tokens[1:] == [22, 33, 44]


def test_i64_hash_is_storage_exact():
    values = [0, 1, -1, 2**31]
    raw = b"".join(value.to_bytes(8, "little", signed=True) for value in values)
    assert sha_i64(values) == hashlib.sha256(raw).hexdigest()
