#!/usr/bin/env python3
"""Reproduce and freeze the authorized FFN timeline patch application method."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


AUTHORIZATION_COMMIT = "08f38d7163da95e895aaba10d72231a6d350dfe2"
BASE_COMMIT = "eae1cc4d831ae8459da558cf1358bb8daf8d76e6"
BASE_PATH = "util/vm_tlb/c16/e1_operator_family_natural.py"
BASE_SHA256 = "902bd8993483290850072afc37245aa7ba80afd821952c7a91fabec0b8e18ea5"
PATCH_PATH = "docs/vm_tlb/review_packs/C16_FFN_TIMELINE_CAPTURE_IDENTITY_RECOVERY_AND_AUTHORIZATION_174NEW_V1/INSTRUMENTATION_DELTA.patch"
PATCH_SHA256 = "06cc0656125e0d5900330f6576b071637de1d09a7e1c9f501929d5577b1361be"
CONTRACT_PATH = "docs/vm_tlb/review_packs/C16_FFN_TIMELINE_CAPTURE_IDENTITY_RECOVERY_AND_AUTHORIZATION_174NEW_V1/AUTHORIZED_FFN_TIMELINE_CAPTURE_CONTRACT_V1.json"
CONTRACT_SHA256 = "cc081ee281b672bd8ff76cb8ae3e226194c0eec44f6f8916ed4fbbfb8facd2f9"
EXPECTED_GNU_SHA256 = "ad922629a9898c01400a165b2f6565659f1c6e422784c10bc1d013265c45b5fb"
EXPECTED_GIT_SHA256 = "4e4a6061ded405b79cd41bafdd2c74ec7ac92e0e54a1ae9c208ee49b335107bf"
PACK = "docs/vm_tlb/review_packs/C16_FFN_TIMELINE_PATCH_APPLICATION_CONTRACT_CORRECTION_174NEW_V1"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_show(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repo)


def check_instrumentation(source: bytes) -> dict:
    text = source.decode("utf-8")
    compile(text, BASE_PATH, "exec")
    required = {
        "timeline_nvtx_argument": 'parser.add_argument("--timeline-nvtx"' in text,
        "semantic_range": "    def semantic_range(label, call):" in text,
        "mlp_wrapper": "    def make_mlp_forward(layer_index, mlp):" in text,
        "decode_wall": 'torch.cuda.nvtx.range_push("C16_FFN_TIMELINE_DECODE_D0_D3")' in text,
        "activation_range": "_ACTIVATION" in text,
        "multiply_range": "_MULTIPLY" in text,
        "result_receipt": 'result["timeline_nvtx"] = args.timeline_nvtx' in text,
    }
    if not all(required.values()):
        raise AssertionError(f"missing expected instrumentation point: {required}")
    positions = {
        "main": text.index("def main():"),
        "argument": text.index('parser.add_argument("--timeline-nvtx"'),
        "semantic_range": text.index("    def semantic_range(label, call):"),
        "mlp_wrapper": text.index("    def make_mlp_forward(layer_index, mlp):"),
        "projection_hook": text.index("    def make_pre(layer_index, role):"),
        "entrypoint": text.index('if __name__ == "__main__":'),
    }
    if not (positions["main"] < positions["argument"] < positions["semantic_range"] < positions["mlp_wrapper"] < positions["projection_hook"] < positions["entrypoint"]):
        raise AssertionError(f"instrumentation placement drift: {positions}")
    if text.rstrip().splitlines()[-1] != "    main()":
        raise AssertionError("instrumentation was appended after the module entry point")
    return {"required_points": required, "positions": positions, "syntax": "PASS", "tail": "PASS_NO_APPENDED_BLOCK"}


def reproduce(repo: Path) -> dict:
    base = git_show(repo, BASE_COMMIT, BASE_PATH)
    patch_at_authorization = git_show(repo, AUTHORIZATION_COMMIT, PATCH_PATH)
    contract_at_authorization = git_show(repo, AUTHORIZATION_COMMIT, CONTRACT_PATH)
    if sha256(base) != BASE_SHA256:
        raise AssertionError("accepted base runner SHA mismatch")
    if sha256(patch_at_authorization) != PATCH_SHA256:
        raise AssertionError("authorized patch SHA mismatch")
    if sha256(contract_at_authorization) != CONTRACT_SHA256:
        raise AssertionError("authorized contract SHA mismatch")
    if (repo / PATCH_PATH).read_bytes() != patch_at_authorization:
        raise AssertionError("working-tree patch bytes differ from authorization commit")
    if (repo / CONTRACT_PATH).read_bytes() != contract_at_authorization:
        raise AssertionError("working-tree scientific contract differs from authorization commit")

    patch_version = subprocess.check_output(["patch", "--version"], text=True).splitlines()[0]
    git_version = subprocess.check_output(["git", "--version"], text=True).strip()
    with tempfile.TemporaryDirectory(prefix="c16_ffn_patch_application_") as temp_name:
        temp = Path(temp_name)
        gnu_target = temp / "gnu" / BASE_PATH
        gnu_target.parent.mkdir(parents=True)
        gnu_target.write_bytes(base)
        gnu_run = subprocess.run(
            ["patch", "-s", str(gnu_target)],
            input=patch_at_authorization,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if gnu_run.returncode != 0:
            raise AssertionError(f"GNU patch failed: {gnu_run.stderr.decode(errors='replace')}")
        gnu_bytes = gnu_target.read_bytes()
        gnu_sha = sha256(gnu_bytes)
        if gnu_sha != EXPECTED_GNU_SHA256:
            raise AssertionError(f"GNU patch result drift: {gnu_sha}")
        instrumentation = check_instrumentation(gnu_bytes)

        git_root = temp / "git"
        git_target = git_root / BASE_PATH
        git_target.parent.mkdir(parents=True)
        git_target.write_bytes(base)
        subprocess.run(["git", "init", "-q"], cwd=git_root, check=True)
        subprocess.run(["git", "add", BASE_PATH], cwd=git_root, check=True)
        subprocess.run(["git", "-c", "user.name=C16", "-c", "user.email=c16@example.invalid", "commit", "-qm", "base"], cwd=git_root, check=True)
        git_run = subprocess.run(
            ["git", "apply", str(repo / PATCH_PATH)],
            cwd=git_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        git_bytes = git_target.read_bytes()
        git_sha = sha256(git_bytes)
        if git_run.returncode != 0 or git_sha != EXPECTED_GIT_SHA256:
            raise AssertionError(f"git apply reproduction drift: rc={git_run.returncode} sha={git_sha}")
        if git_sha == EXPECTED_GNU_SHA256:
            raise AssertionError("git apply result was incorrectly admitted")
        try:
            compile(git_bytes.decode("utf-8"), BASE_PATH, "exec")
        except SyntaxError as exc:
            git_syntax = {"status": "FAIL_AS_EXPECTED", "exception": type(exc).__name__, "line": exc.lineno, "message": exc.msg}
        else:
            raise AssertionError("malformed git apply result unexpectedly compiled")

    return {
        "schema_version": 1,
        "status": "PASS_GNU_PATCH_ONLY",
        "scientific_identity_change": "NONE",
        "instrumentation_change": "NONE",
        "authorization_commit": AUTHORIZATION_COMMIT,
        "base": {"source_commit": BASE_COMMIT, "source_path": BASE_PATH, "base_source_sha256": BASE_SHA256},
        "patch": {"path": PATCH_PATH, "patch_sha256": PATCH_SHA256, "bytes_unchanged_from_authorization": True},
        "authorized_application": {
            "application_tool": "GNU patch",
            "tool_version": patch_version,
            "working_directory": "repository root",
            "exact_command": f"patch -s {BASE_PATH} < {PATCH_PATH}",
            "return_code": gnu_run.returncode,
            "result_sha256": gnu_sha,
            "expected_result_sha256": EXPECTED_GNU_SHA256,
            "status": "PASS_EXACT",
            "instrumentation_validation": instrumentation,
        },
        "prohibited_application": {
            "application_tool": "git apply",
            "tool_version": git_version,
            "working_directory": "repository root",
            "exact_command": f"git apply {PATCH_PATH}",
            "return_code": git_run.returncode,
            "result_sha256": git_sha,
            "expected_malformed_result_sha256": EXPECTED_GIT_SHA256,
            "authorized": False,
            "reason": "The normalized zero-context insertion hunks are application-tool-sensitive. git apply relocates the insertions to the file tail, outside main, producing a syntactically invalid runner.",
            "syntax_validation": git_syntax,
            "status": "REPRODUCED_BUT_REJECTED",
        },
        "contract_invariants": {
            "authorized_contract_path": CONTRACT_PATH,
            "authorized_contract_sha256": CONTRACT_SHA256,
            "model_input_runtime_scenario_unchanged": True,
            "measurement_protocol_unchanged": True,
            "gpu_budget_unchanged": True,
            "canary_and_formal_counts_unchanged": True,
        },
    }


def write_pack(repo: Path, out: Path) -> None:
    receipt = reproduce(repo)
    out.mkdir(parents=True, exist_ok=True)
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    (out / "PATCH_APPLICATION_RECEIPT.json").write_bytes(receipt_bytes)

    correction = f"""# FFN timeline patch application contract correction

This is an engineering-only correction to authorization `{AUTHORIZATION_COMMIT}`. The authorized scientific contract, model/input/runtime/scenario identity, instrumentation patch bytes, measurement protocol, GPU budget, and OFF/ON plus formal-run counts are unchanged.

CPU reproduction starts from `{BASE_COMMIT}:{BASE_PATH}` (SHA256 `{BASE_SHA256}`) and the authorized patch (SHA256 `{PATCH_SHA256}`). From the repository root, GNU `{receipt['authorized_application']['tool_version']}` with the exact command below reconstructs the authorized runner SHA256 `{EXPECTED_GNU_SHA256}`:

```sh
{receipt['authorized_application']['exact_command']}
```

Plain `git apply` returns success but yields SHA256 `{EXPECTED_GIT_SHA256}`. Its zero-context insertion hunks are relocated to the file tail; the instrumentation is outside `main` and the result fails Python syntax validation. Therefore `git apply` is explicitly prohibited and cannot satisfy authorization.

Lane7 must discard any previously patched working copy, restore the accepted base bytes, use the exact GNU patch command, hash immediately, and continue only on exact `{EXPECTED_GNU_SHA256}`. Any other result is an immediate STOP.
"""
    (out / "PATCH_APPLICATION_CORRECTION.md").write_text(correction, encoding="utf-8")

    continuation = f"""# Lane7 FFN timeline capture continuation V2

This addendum supersedes only the patch-application instruction in the original continuation. It does not alter the authorized scientific contract or capture counts.

1. Read `{CONTRACT_PATH}` and require SHA256 `{CONTRACT_SHA256}`.
2. Discard the prior patched runner and check out `{BASE_PATH}` exactly from `{BASE_COMMIT}`. Require SHA256 `{BASE_SHA256}` before applying anything.
3. Materialize patch `{PATCH_PATH}` from authorization commit `{AUTHORIZATION_COMMIT}` and require SHA256 `{PATCH_SHA256}`. Do not modify its bytes.
4. **Do not use `git apply`.** From the repository root, apply only with GNU patch using:

   ```sh
   patch -s {BASE_PATH} < {PATCH_PATH}
   ```

5. Immediately compute the runner SHA256. Continue only if it is exactly `{EXPECTED_GNU_SHA256}`; every other SHA is an immediate STOP.
6. Then follow the unchanged authorization: one OFF/ON neutrality pair and, only after it passes, one lightweight NSYS `cuda,nvtx` formal capture under the same GPU lock/budget/publication rules.

The known rejected `git apply` result is `{EXPECTED_GIT_SHA256}`. It is malformed and must never be repaired in place; restart from the accepted base instead.
"""
    (out / "LANE7_FFN_TIMELINE_CAPTURE_CONTINUATION_V2.md").write_text(continuation, encoding="utf-8")

    names = ["LANE7_FFN_TIMELINE_CAPTURE_CONTINUATION_V2.md", "PATCH_APPLICATION_CORRECTION.md", "PATCH_APPLICATION_RECEIPT.json"]
    sums = "".join(f"{sha256((out / name).read_bytes())}  {name}\n" for name in sorted(names))
    (out / "SHA256SUMS").write_text(sums, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    if args.check:
        reproduce(repo)
        return
    write_pack(repo, args.output_dir or repo / PACK)


if __name__ == "__main__":
    main()
