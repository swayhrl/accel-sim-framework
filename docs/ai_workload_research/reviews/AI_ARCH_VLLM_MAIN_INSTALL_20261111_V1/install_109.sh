#!/usr/bin/env bash
set -Eeuo pipefail

install_root=/data/c16/aiarch_vllm_main_install_20261111_v1
venv=/data/c16/envs/aiarch-vllm-main-ca3c154d-v1
wheel_url='https://wheels.vllm.ai/ca3c154d26749c2b59d9d99050d2bd631d2c63f7/vllm-0.34.0rc1.dev167%2Bgca3c154d2-cp38-abi3-manylinux_2_28_x86_64.whl'

mkdir -p "$install_root"
printf '%s\n' "$wheel_url" > "$install_root/wheel_url.txt"
if [[ -e "$venv" ]]; then
  echo "Target already exists: $venv" >&2
  exit 2
fi
python3 -m venv "$venv"
"$venv/bin/python" -m pip install --disable-pip-version-check 'uv==0.13.7'
export UV_CACHE_DIR="$install_root/uv_cache"
export UV_NO_PROGRESS=1
"$venv/bin/uv" pip install --python "$venv/bin/python" --torch-backend=auto \
  --extra-index-url https://wheels.vllm.ai/nightly "$wheel_url"
"$venv/bin/uv" pip freeze --python "$venv/bin/python" > "$install_root/freeze.txt"
"$venv/bin/python" -m pip check > "$install_root/pip_check.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$install_root/installed_utc.txt"
