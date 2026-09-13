#!/usr/bin/env python3
"""Materialize the no-GPU C16 recovery-v2 ledger-scope receipt."""
from __future__ import annotations

import argparse
from pathlib import Path

from c16_native_common import ContractError, atomic_json, sha256_file
from retry570_recovery_budget import CAMPAIGN_ID, MAX_WINDOWS_PER_DEPLOYMENT, initialize


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recovery-ledger", type=Path, required=True); parser.add_argument("--historical-ledger", type=Path, required=True)
    parser.add_argument("--historical-sha256", required=True); parser.add_argument("--deployment-id", required=True); parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.receipt.exists(): raise ContractError("recovery scope receipt already exists")
    before = sha256_file(args.historical_ledger)
    if before != args.historical_sha256: raise ContractError("historical ledger differs before scope initialization")
    ledger = initialize(recovery_ledger=args.recovery_ledger, historical_ledger=args.historical_ledger, expected_historical_sha256=before, deployment_id=args.deployment_id)
    after = sha256_file(args.historical_ledger)
    if after != before: raise ContractError("historical ledger mutated by recovery scope initialization")
    atomic_json(args.receipt, {"schema_version": "C16_G_NVBIT175_RECOVERY_SCOPE_V2", "status": "RECOVERY_BUDGET_NAMESPACE_READY", "scientific_eligible": False,
        "campaign_id": CAMPAIGN_ID, "new_deployment_id": args.deployment_id, "max_nvbit_capture_windows": MAX_WINDOWS_PER_DEPLOYMENT,
        "historical_ledger": {"path": str(args.historical_ledger), "sha256_before": before, "sha256_after": after, "rows_preserved": True},
        "recovery_ledger": {"path": str(args.recovery_ledger), "sha256": sha256_file(args.recovery_ledger), "entry_count": len(ledger["entries"])}})
    print(f"PASS recovery namespace: {args.receipt}")


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL recovery namespace: {exc}")
