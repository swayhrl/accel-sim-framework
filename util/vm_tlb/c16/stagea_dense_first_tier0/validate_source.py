#!/usr/bin/env python3
"""CPU-only source, observer, and result-schema validation."""

import argparse
import ast
import hashlib
import json
from pathlib import Path


V1_SHA = "1f68c1117623cbc46f98f51f17ba798d8bf5ffb103f427b9d7b916ced0a35020"
V2_SHA = "7f2a76a375eaa4f652553fc523f785a753180ef1402291e54beb2256ed02bb22"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal_columns(tree):
    found = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != "write_tsv":
            continue
        if len(node.args) < 3:
            continue
        path_expr, fields_expr = node.args[0], node.args[2]
        if not isinstance(path_expr, ast.BinOp) or not isinstance(path_expr.op, ast.Div) or not isinstance(path_expr.right, ast.Constant):
            continue
        name = path_expr.right.value
        if not isinstance(fields_expr, (ast.List, ast.Tuple)):
            continue
        found[name] = [item.value for item in fields_expr.elts if isinstance(item, ast.Constant)]
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--result-schema", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    root = repo / "util/vm_tlb/c16/stagea_dense_first_tier0"
    checks = {}
    checks["v1_sha_exact"] = sha(repo / "util/vm_tlb/c16/stagea_runtime_qualification/runner.py") == V1_SHA
    checks["v2_sha_exact"] = sha(root / "observer_v2_authority.py") == V2_SHA
    for name in ("runner.py", "campaign.py", "nsys_extract.py", "postprocess_exact.py", "preflight.py", "contract_poll.py"):
        compile((root / name).read_text(), str(root / name), "exec")
    checks["python_compile"] = True
    schema = json.loads(args.result_schema.read_text())
    source_tree = ast.parse((root / "postprocess_exact.py").read_text())
    columns = literal_columns(source_tree)
    mismatches = {}
    for name, rule in schema["row_rules"].items():
        if not name.endswith(".tsv"):
            continue
        if columns.get(name) != rule["columns"]:
            mismatches[name] = {"expected": rule["columns"], "actual": columns.get(name)}
    checks["result_tsv_schemas_exact"] = not mismatches
    campaign_text = (root / "campaign.py").read_text()
    checks["one_lock_path"] = campaign_text.count('/data/c16/locks/c16_gpu_campaign.lock') == 1
    checks["nsys_domains_exact"] = '"--trace=cuda,nvtx"' in campaign_text
    checks["no_forbidden_gpu_tools_in_executor"] = all(term not in campaign_text for term in ("ncu ", "nvbit", "cuobjdump", "accel-sim"))
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "schema_mismatches": mismatches,
              "source_sha256": {name: sha(root / name) for name in ("runner.py", "campaign.py", "nsys_extract.py", "postprocess_exact.py", "preflight.py", "contract_poll.py", "test_synthetic.py")}}
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
