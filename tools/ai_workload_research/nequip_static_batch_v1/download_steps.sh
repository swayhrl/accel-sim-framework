#!/bin/bash
set -euo pipefail
export MAX_JOBS=8 OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 TMPDIR="$TASK_DATA/cache/tmp"
"$TASK_DATA/venv/bin/python" -m pip download --only-binary=:all: --require-hashes --cache-dir "$TASK_DATA/cache/pip" --extra-index-url https://download.pytorch.org/whl/cu126 -r "$TASK_DATA/requirements.lock" -d "$TASK_DATA/wheels" > "$TASK_DATA/raw/wheel_download.log" 2>&1
"$TASK_DATA/venv/bin/python" -m pip install --no-index --find-links "$TASK_DATA/wheels" --require-hashes --only-binary=:all: -r "$TASK_DATA/requirements.lock" --report "$TASK_DATA/raw/install_report.json" > "$TASK_DATA/raw/wheel_install.log" 2>&1
