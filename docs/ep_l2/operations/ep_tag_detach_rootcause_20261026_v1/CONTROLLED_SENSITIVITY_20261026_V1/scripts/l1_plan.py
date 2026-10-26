"""Bounded E2 preparation only: never registers, launches, or retries science."""
from pathlib import Path
import hashlib
import json
import math

SOURCE_ENV = Path("/root/data/ep_l2_main_vector_r5_20261023_v1/env")
EXPECTED_SHA256 = {
    "config-0.config": "8ccad878b6abfec8254ecd6c7e0efee2714908dc3a04f611ff8787000e277bd3",
    "config-1.config": "19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e",
    "config-2.config": "492269014ee869f9023cc7ec4fb3ac8dd7da04bf96d34e2e55ffb74d040007b3",
    "config-3.config": "b5ca00bb33a0e75c71b9661789d6480d97be8bede4dec4edf5172637216351f0",
}
BASELINE_DL1 = "S:4:128:128,L:T:m:L:L,A:512:8,16:0,32"
E2_DL1 = "S:4:128:128,L:T:m:L:L,A:512:8,32:0,32"
EXTRA_CONFIG_BYTES = ("-gpgpu_cache:dl1 " + E2_DL1 + "\n").encode("ascii")
BASELINE_CLOCK = "1132.0:1132.0:1132.0:850.0"
BASELINE_ACCESSES = 1500000
BASELINE_MISS_QUEUE_FULL = 1240787
RESIDUAL_FRACTION_THRESHOLD = 0.25


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _effective(blobs):
    result = {}
    for blob in blobs:
        for line in blob.decode("utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            fields = line.split(None, 1)
            if fields[0].startswith("-") and len(fields) == 2:
                result[fields[0]] = fields[1].strip()
    return result


def _dl1_fields(value):
    # Core1093 gpu-cache.h:627-630: final groups are missq:resultfifo,datawidth.
    groups = value.split(",")
    if len(groups) != 5:
        raise ValueError("Unexpected DL1 syntax")
    missq, result_fifo = map(int, groups[3].split(":"))
    return dict(miss_queue=missq, result_fifo=result_fifo,
                data_port_width=int(groups[4]), prefix=groups[:3])


def inspect_sources():
    blobs = []
    for name, expected in EXPECTED_SHA256.items():
        blob = (SOURCE_ENV / name).read_bytes()
        if _sha(blob) != expected:
            raise ValueError("Frozen source config SHA mismatch: " + name)
        blobs.append(blob)
    before = _effective(blobs)
    after = _effective(blobs + [EXTRA_CONFIG_BYTES])
    if before.get("-gpgpu_cache:dl1") != BASELINE_DL1:
        raise ValueError("Baseline DL1 precedence mismatch")
    if before.get("-gpgpu_clock_domains") != BASELINE_CLOCK:
        raise ValueError("Baseline must use 850 MHz DRAM")
    changed = {key: [before.get(key), after.get(key)]
               for key in before.keys() | after.keys()
               if before.get(key) != after.get(key)}
    if changed != {"-gpgpu_cache:dl1": [BASELINE_DL1, E2_DL1]}:
        raise ValueError("E2 must change only the DL1 option")
    a, b = _dl1_fields(BASELINE_DL1), _dl1_fields(E2_DL1)
    if not (a["miss_queue"] == 16 and b["miss_queue"] == 32
            and {k: v for k, v in a.items() if k != "miss_queue"}
            == {k: v for k, v in b.items() if k != "miss_queue"}):
        raise ValueError("E2 must change only miss_queue 16 to 32")
    return blobs, {"source_env": str(SOURCE_ENV),
                   "source_config_sha256": EXPECTED_SHA256,
                   "extra_config_sha256": _sha(EXTRA_CONFIG_BYTES),
                   "extra_config_bytes": len(EXTRA_CONFIG_BYTES),
                   "effective_option_delta": changed,
                   "effective_clock": after["-gpgpu_clock_domains"],
                   "parsed_before": a, "parsed_after": b,
                   "scientific_launches": 0, "registrations": 0}


def build_config(destination):
    """Copy four frozen config byte streams and append exactly config-4.config.

    The destination must be absent or empty; never overwrite an existing member.
    This function does not create a run spec, register E2, or invoke a simulator.
    """
    blobs, report = inspect_sources()
    dest = Path(destination)
    if dest.exists() and (not dest.is_dir() or any(dest.iterdir())):
        raise FileExistsError("Destination must be absent or empty: " + str(dest))
    dest.mkdir(parents=True, exist_ok=True)
    names = list(EXPECTED_SHA256) + ["config-4.config"]
    hashes = {}
    for name, blob in zip(names, blobs + [EXTRA_CONFIG_BYTES]):
        with (dest / name).open("xb") as stream:
            stream.write(blob)
        if (dest / name).read_bytes() != blob:
            raise IOError("Config readback mismatch: " + name)
        hashes[name] = _sha(blob)
    return dict(report, destination=str(dest.resolve()), config_sha256=hashes,
                config_order=names)


def recommend_e2(e1_science_valid, accesses=None, miss_queue_full=None):
    """Information-value recommendation only; native admission remains separate.

    E2 is at 850 MHz and compares to the old accepted 850 MHz baseline, not E1.
    Positive E1 speedup and nonzero detach are deliberately not inputs.
    """
    if e1_science_valid is not True:
        return {"recommendation": "DO_NOT_START_E2", "reason": "E1_NOT_ACCEPTED_VALID",
                "automatic_retry": False}
    if (type(accesses) is not int or accesses != BASELINE_ACCESSES
            or type(miss_queue_full) is not int or miss_queue_full < 0):
        return {"recommendation": "HOLD_NO_START", "reason": "E1_METRICS_MISSING_OR_WRONG_SCOPE",
                "automatic_retry": False}
    residual_fraction = miss_queue_full / BASELINE_MISS_QUEUE_FULL
    worthwhile = residual_fraction >= RESIDUAL_FRACTION_THRESHOLD
    return {"recommendation": "E2_INFORMATION_WORTHWHILE_PENDING_NATIVE_ADMISSION"
            if worthwhile else "SKIP_E2_LOW_RESIDUAL_L1_QUEUE_PRESSURE",
            "e1_retries_per_accepted_access": miss_queue_full / accesses,
            "baseline_retries_per_accepted_access": BASELINE_MISS_QUEUE_FULL / BASELINE_ACCESSES,
            "residual_fraction_of_baseline": residual_fraction,
            "threshold_fraction": RESIDUAL_FRACTION_THRESHOLD,
            "minimum_integer_miss_queue_full": math.ceil(
                BASELINE_MISS_QUEUE_FULL * RESIDUAL_FRACTION_THRESHOLD),
            "reference": "OLD_ACCEPTED_R5_850MHZ_MISSQ16",
            "e2_dram_mhz": 850, "registrations": 0, "scientific_launches": 0,
            "automatic_retry": False}


if __name__ == "__main__":
    # CLI is intentionally read-only. Main owner may explicitly call build_config.
    _, report = inspect_sources()
    print(json.dumps(report, sort_keys=True, indent=2))
