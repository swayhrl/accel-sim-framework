# A10A prior artifact discovery

## Goal

Discover real prior Mascar and MeDiC GPGPU-Sim reproduction artifacts under /workspace/repos.

This phase is read-only with respect to all prior repos.

## Required tracked script

Create:

    scripts/accelsim/a10a_discover_prior_workflows.sh

## Search scope

Default root:

    /workspace/repos

Allow override:

    ACCELSIM_A10_SEARCH_ROOT

Allow explicit prior roots:

    ACCELSIM_A10_PRIOR_ROOTS

If ACCELSIM_A10_PRIOR_ROOTS is set, search those roots first.

## Bounded search rules

Do not perform an unbounded huge recursive grep.

Exclude directories named or matching:

    .git
    build
    cmake-build
    gpu-simulator/build
    hw_run
    traces
    trace
    .local_runs
    .local_traces
    .local_logs
    __pycache__
    node_modules

Only inspect text-like files smaller than 10 MB by default.

File extensions to inspect:

    .md
    .txt
    .sh
    .py
    .csv
    .json
    .yaml
    .yml
    .log
    .out
    .config
    .cfg
    .ini
    .list

Artifact names and terms to search:

    Mascar
    MASCAR
    mascar
    MeDiC
    MEDIC
    medic
    GPGPU-Sim
    gpgpu-sim
    benchmark
    workload
    stats
    review_pack
    rodinia
    parboil
    polybench
    sdk
    cutlass

## Review pack handling

Prior repos may contain review_packs/*.tar.gz.

Do not extract whole large tarballs blindly.

For each candidate tar.gz:

1. Run:
       tar -tf PACK
2. Save the tar listing under:
       .local_reports/A10A_tar_listing_PACKNAME_TIMESTAMP.txt
3. If listing contains small text-like files relevant to Mascar or MeDiC, extract only those files into:
       .local_runs/a10_prior_reviewpacks/PACK_BASENAME/
4. Do not extract traces, binaries, object files, build dirs, or huge files.

## Output CSV

Create:

    .local_reports/A10A_prior_artifact_inventory_TIMESTAMP.csv

Columns:

    artifact_id
    source_root
    source_path
    artifact_type
    paper_hint
    matched_terms
    size_bytes
    mtime
    extracted_path
    notes

artifact_type values can include:

    repo
    doc
    script
    config
    stats_csv
    log
    review_pack
    review_pack_member
    unknown_text

paper_hint values:

    Mascar
    MeDiC
    both
    unknown

## Markdown report

Create:

    .local_reports/A10A_prior_artifact_discovery_TIMESTAMP.md

Include:

- search roots
- excluded dirs
- number of candidate repos
- number of candidate files
- number of review packs
- extraction actions
- top likely Mascar artifacts
- top likely MeDiC artifacts
- blockers

## Status

Use:

    PASS
    PARTIAL_PASS_NO_REVIEW_PACKS
    BLOCKED_NO_PRIOR_ARTIFACTS
    FAILED_SEARCH_ERROR

## A10A pass criteria

- Script exists and is executable.
- Inventory CSV exists.
- Report exists.
- The report clearly distinguishes real artifacts from guesses.
