# A10 Prior Artifact Discovery

`scripts/accelsim/a10a_discover_prior_workflows.sh` performs read-only discovery under `/workspace/repos` or `ACCELSIM_A10_SEARCH_ROOT`.

The search excludes `.git`, build directories, traces, local run directories, downloaded application collections, and other large generated trees. Text-like files are limited to 10 MB by default. Review packs are listed with `tar -tf`; only small relevant text members are extracted under `.local_runs/a10_prior_reviewpacks/`.

Output:

- `.local_reports/A10A_prior_artifact_inventory_TIMESTAMP.csv`
- `.local_reports/A10A_prior_artifact_discovery_TIMESTAMP.md`

The inventory records source path, artifact type, paper hint, matched terms, size, mtime, and any extracted review-pack path. It is an evidence inventory, not a workload mapping.
