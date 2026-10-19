"""PREPARED_NOT_TESTED. Pure output-protocol classifier; no CLI or process API.

This module does NOT establish launch authority, ELF provenance, resource
admission or loaded-library identity by itself. The parent must join its own
authenticated direct-Popen/admission/cleanup and static ABI receipts first.
No import-time execution, reference-memory lookup or value injection exists.
"""
import re

ORDER = ("shared", "masked", "with-e", "ae", "ad", "no-e",
         "wrong-byte", "missing-sector", "wrong-generation", "early-release")
VALUE_MODES = frozenset(("shared", "masked", "with-e", "ae", "ad"))
MAX_LOG_BYTES = 1024 * 1024
_BYTES = re.compile(r"^SEM1_BYTE uid=(\d+) byte=(\d+) got=(\d+) expected=(\d+)$")

def reject(reason):
    return {"status": "REJECT_OUTPUT_PROTOCOL", "reason": reason,
            "authority_or_native_PASS": False}

def classify(mode, returncode, stdout, stderr, *, expected_library_path,
             execution_failure_reason=None):
    """Classify one completed, authenticated case; stdout/stderr must be bytes.

    A normal result is CONDITIONAL_SECTOR_VALUES, CONDITIONAL_COUNTERMODEL or
    EXPECTED_TARGETED_REJECTION, never full correctness or authorization PASS.
    The caller must stop the cohort on REJECT, timeout/resource/cleanup failure.
    """
    if mode not in ORDER:
        return reject("unregistered mode")
    if execution_failure_reason is not None:
        return reject("execution/resource/ownership failure overrides expected exit")
    if not isinstance(stdout, bytes) or not isinstance(stderr, bytes):
        return reject("raw byte logs required")
    if max(len(stdout), len(stderr)) > MAX_LOG_BYTES // 2:
        return reject("512 KiB per-stream log bound")
    if len(stdout) + len(stderr) > MAX_LOG_BYTES:
        return reject("one MiB combined log bound")
    try:
        out, err = stdout.decode("utf-8"), stderr.decode("utf-8")
    except UnicodeDecodeError:
        return reject("invalid UTF8 protocol")
    if not expected_library_path or not expected_library_path.startswith("/"):
        return reject("post-build exact library path required")
    lines = out.splitlines()
    libraries = [x[len("SEM1_LIBRARY "):] for x in lines if x.startswith("SEM1_LIBRARY ")]
    if any(x != expected_library_path for x in libraries) or len(libraries) > 1:
        return reject("wrong or duplicate reported library path")
    results = [x for x in lines if x.startswith("SEM1_RESULT ")]
    byte_lines = [x for x in lines if x.startswith("SEM1_BYTE ")]
    markers = [x for x in lines if x.startswith("SEM1_REJECT ")]
    counter = [x for x in lines if x.startswith("SEM1_CONDITIONAL_COUNTERMODEL ")]
    known = ("SEM1_LIBRARY ", "SEM1_RESULT ", "SEM1_BYTE ", "SEM1_REJECT ",
             "SEM1_CONDITIONAL_COUNTERMODEL ")
    if any(x.startswith("SEM1_") and not x.startswith(known) for x in lines):
        return reject("unknown SEM1 protocol record")
    if mode in ("wrong-generation", "early-release"):
        # Core gpu-sim.cc crash_handler handles SIGABRT then _exit(1).
        # Buffered C++ stdout need not flush, so library line can be absent.
        if returncode != 1 or results or byte_lines or markers or counter:
            return reject("target assertion did not terminate at its expected boundary")
        normalized = " ".join(err.split())
        if "SIGABRT" not in err or "SIGSEGV" in err or "Assertion" not in err:
            return reject("not the source-bound assertion/abort")
        if mode == "wrong-generation":
            required = ("sem1_accept_sector", "fill_identity_matches(identity) && sector < 4")
        else:
            required = ("oo_frontend::release", "physical.allocated",
                        "physical.generation == identity.generation",
                        "!physical.tag_valid", "!physical.ref_count")
        if not all(x in normalized for x in required):
            return reject("wrong assertion site or expression")
        return {"status": "EXPECTED_TARGETED_REJECTION", "case": mode,
                "scope": "actual diagnostic generation guard" if mode == "wrong-generation"
                         else "combined actual Tag/allocation/generation/Ref release guard",
                "loaded_library_stdout": "PRESENT" if libraries else
                    "UNAVAILABLE_ABORT_USES__exit_BEFORE_STDOUT_FLUSH",
                "native_or_architectural_values": "UNPROVEN"}
    if len(libraries) != 1:
        return reject("normally returning case missing actual dladdr path")
    if re.search(r"assertion|CRASH:|SIGSEGV|SIGABRT|segmentation fault", err, re.I):
        return reject("unexpected crash/assertion")
    if mode == "missing-sector":
        if (returncode != 2 or results or byte_lines or counter or
                markers != ["SEM1_REJECT incomplete_return_no_consumer_result"]):
            return reject("incomplete-return rejection protocol mismatch")
        return {"status": "EXPECTED_TARGETED_REJECTION", "case": mode,
                "scope": "source asserts live Ref; withheld return and no final output protocol",
                "not_claimed": "independent inspection of every internal collected vector"}
    if markers:
        return reject("unexpected rejection marker")
    groups = {}
    for line in byte_lines:
        match = _BYTES.fullmatch(line)
        if not match:
            return reject("malformed byte observation")
        uid, byte, got, want = map(int, match.groups())
        if byte in groups.setdefault(uid, {}):
            return reject("duplicate consumer/byte")
        groups[uid][byte] = (got, want)
    consumers = 10 if mode == "ad" else 4 if mode in ("with-e", "no-e") else 3
    requested = {31, 32} if mode == "masked" else {0, 1, 2, 3}
    if len(groups) != consumers or any(set(v) != requested for v in groups.values()):
        return reject("incomplete actual byte population")
    mismatches = []
    for uid, data in groups.items():
        for byte, (got, want) in data.items():
            expected = 153 if mode in ("no-e", "with-e") and uid == max(groups) and byte == 0 else byte
            if want != expected or not (0 <= got <= 255):
                return reject("reference contract or byte range changed")
            if got != want:
                mismatches.append((uid, byte, got, want))
    if mode == "wrong-byte":
        if returncode != 1 or results or counter or len(mismatches) != 3:
            return reject("wrong-byte negative did not fail specifically")
        if not all(byte == 0 and got == 1 and want == 0 for _,byte,got,want in mismatches):
            return reject("wrong mismatch set")
        return {"status": "EXPECTED_TARGETED_REJECTION", "case": mode,
                "scope": "three real collected consumers detect corrupted packet byte"}
    if returncode != 0 or len(results) != 1:
        return reject("normal value/countermodel case did not complete")
    fields = results[0].split()[1:]
    if any("=" not in item for item in fields):
        return reject("malformed result")
    pairs = [item.split("=", 1) for item in fields]
    result = dict(pairs)
    expected = {"mode": mode, "actual_ldst": "1", "conditional_sector_values": "1",
                "kernels": "0", "GPU_cycle_calls": "0",
                "accepted_packets": "8" if mode == "with-e" else "4",
                "consumers": str(consumers), "architectural_values": "UNPROVEN",
                "native": "UNPROVEN"}
    if len(result) != len(pairs) or result != expected:
        return reject("result population or semantic boundary changed")
    if mode == "no-e":
        required = "SEM1_CONDITIONAL_COUNTERMODEL external_publish_without_E cached_old_byte; store_execution=0"
        if counter != [required] or mismatches != [(max(groups), 0, 0, 153)]:
            return reject("no-E must retain exactly the fixed external-publication countermodel")
        return {"status": "CONDITIONAL_COUNTERMODEL", "case": mode,
                "scope": "external fixture publication without modeled store/E",
                "native_or_architectural_values": "UNPROVEN"}
    if mode not in VALUE_MODES or mismatches or counter:
        return reject("unexpected value mismatch or countermodel")
    return {"status": "CONDITIONAL_SECTOR_VALUES", "case": mode,
            "consumers": consumers, "scope": "explicit fixture bytes through real routing",
            "native_or_architectural_values": "UNPROVEN"}
