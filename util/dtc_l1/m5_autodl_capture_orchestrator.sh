#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
pin=0db04452ec1c47630e4b08002067d82c6811e243
control_ref=hrl/decoupled-l1-exp-m5-v0
control_repo=git@github.com:swayhrl/accel-sim-framework.git
host=; port=; user=; identity=; data_root=; local_store=; polybench_src=; nvbit_archive=; capture_command=; remote_archive=; dry=0
while (($#)); do
  case $1 in
    --host) host=$2; shift 2 ;;
    --port) port=$2; shift 2 ;;
    --user) user=$2; shift 2 ;;
    --identity-file) identity=$2; shift 2 ;;
    --remote-data-root) data_root=$2; shift 2 ;;
    --local-trace-store) local_store=$2; shift 2 ;;
    --polybench-src) polybench_src=$2; shift 2 ;;
    --nvbit-archive) nvbit_archive=$2; shift 2 ;;
    --control-repo) control_repo=$2; shift 2 ;;
    --capture-command) capture_command=$2; shift 2 ;;
    --remote-archive) remote_archive=$2; shift 2 ;;
    --dry-run) dry=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[[ -n $host && -n $user && -n $data_root && -n $local_store ]] || { echo "usage: $0 --host H --user U --remote-data-root ROOT --local-trace-store DIR [--port P] [--identity-file FILE] [--polybench-src DIR --nvbit-archive FILE] [--control-repo URL] [--capture-command CMD --remote-archive PATH] [--dry-run]" >&2; exit 2; }
mkdir -p "$local_store"; state=$local_store/M5_0BT_AUTODL_ORCHESTRATOR.state
printf 'SIM_HOST_START\n' >"$state"
if ((dry)); then
  printf '%s\n' SSH_CONNECTIVITY_PASS REMOTE_PREFLIGHT_PASS M5_CONTROL_CHECKOUT_PREPARED TRACER_PIN_CHECKOUT_PREPARED SOURCES_AND_INPUTS_STAGED BICG_CAPTURE_PENDING ARCHIVE_COPYBACK_PENDING >>"$state"
  exit 0
fi
ssh_opts=(-o BatchMode=yes)
[[ -n $port ]] && ssh_opts+=(-p "$port")
[[ -n $identity ]] && ssh_opts+=(-i "$identity")
remote="$user@$host"
ssh "${ssh_opts[@]}" "$remote" "test -d '$data_root' && df -Pk '$data_root' && command -v rsync tar zstd git make g++ /usr/local/cuda-11.8/bin/nvcc"
printf '%s\n' SSH_CONNECTIVITY_PASS REMOTE_PREFLIGHT_PASS >>"$state"
# Current control checkout holds the controller; pinned checkout is tracer-only.
ssh "${ssh_opts[@]}" "$remote" "set -e; mkdir -p '$data_root'; test -d '$data_root/m5-control/.git' || git clone --branch '$control_ref' '$control_repo' '$data_root/m5-control'; git -C '$data_root/m5-control' fetch origin '$control_ref'; git -C '$data_root/m5-control' checkout -B '$control_ref' 'origin/$control_ref'; test -d '$data_root/tracer-pin/.git' || git clone '$control_repo' '$data_root/tracer-pin'; git -C '$data_root/tracer-pin' fetch origin '$pin'; git -C '$data_root/tracer-pin' checkout --detach '$pin'"
printf '%s\n' M5_CONTROL_CHECKOUT_PREPARED TRACER_PIN_CHECKOUT_PREPARED >>"$state"
[[ -n $polybench_src && -n $nvbit_archive ]] || { printf '%s\n' SOURCES_AND_INPUTS_STAGING_REQUIRED BICG_CAPTURE_PENDING >>"$state"; exit 0; }
[[ -d $polybench_src && -f $nvbit_archive ]] || { echo "local PolyBench/NVBit staging inputs missing" >&2; exit 2; }
ssh "${ssh_opts[@]}" "$remote" "mkdir -p '$data_root/sources/polybench' '$data_root/inputs'"
rsync -a -e "ssh ${ssh_opts[*]}" "$polybench_src/" "$remote:$data_root/sources/polybench/"
rsync -a --partial --append-verify -e "ssh ${ssh_opts[*]}" "$nvbit_archive" "$remote:$data_root/inputs/nvbit-1.8.tar.bz2"
printf '%s\n' SOURCES_AND_INPUTS_STAGED BICG_CAPTURE_PENDING >>"$state"
if [[ -z $capture_command ]]; then
  capture_command="CUDA_VISIBLE_DEVICES=0 NVCC=/usr/local/cuda-11.8/bin/nvcc util/dtc_l1/capture_m5_paper10_traces.sh --polybench-src '$data_root/sources/polybench' --tracer-framework-src '$data_root/tracer-pin' --nvbit-archive '$data_root/inputs/nvbit-1.8.tar.bz2' --out '$data_root/m5-paper10-traces' --workloads bicg --pilot-only"
  remote_archive="$data_root/m5-paper10-traces/archives/bicg.tar.zst"
fi
[[ -n $remote_archive ]] || { echo "--remote-archive required with a custom capture command" >&2; exit 2; }
case $capture_command in
  *"--workloads bicg"*"--pilot-only"*"--tracer-framework-src"*) ;;
  *) echo "capture command must be the BICG pilot with tracer-framework-src" >&2; exit 2 ;;
esac
# A blocking SSH owns natural completion; it does not poll or kill the worker.
printf '%s\n' BICG_CAPTURE_RUNNING >>"$state"
ssh "${ssh_opts[@]}" "$remote" "cd '$data_root/m5-control' && $capture_command"
printf '%s\n' BICG_CAPTURE_ARCHIVE_PASS >>"$state"
local_archive=$local_store/archives/bicg.tar.zst
mkdir -p "$(dirname "$local_archive")"
rsync -a --partial --append-verify -e "ssh ${ssh_opts[*]}" "$remote:$remote_archive" "$local_archive"
remote_sha=$(ssh "${ssh_opts[@]}" "$remote" "sha256sum '$remote_archive' | awk '{print \$1}'")
local_sha=$(sha256sum "$local_archive" | awk '{print $1}')
[[ $remote_sha == "$local_sha" ]] || { echo "archive copyback SHA mismatch" >&2; exit 1; }
printf '%s\n' ARCHIVE_COPYBACK_SHA_PASS >>"$state"
tar --zstd -xf "$local_archive" -C "$local_store"
python3 - "$script_dir/m5_trace_capture_controller.py" "$local_store/bicg" <<'PY'
import importlib.util,sys
p=sys.argv[1]
s=importlib.util.spec_from_file_location("m5c",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
if not m.valid_bundle(__import__("pathlib").Path(sys.argv[2])): raise SystemExit("internal bundle SHA revalidation failed")
PY
printf '%s\n' INTERNAL_BUNDLE_REVALIDATION_PASS TRANSFER_RECEIPT_PENDING >>"$state"
printf '{"archive_sha256":"%s","status":"TRANSFER_PASS"}\n' "$local_sha" >"$local_store/bicg.transfer.json"
printf '%s\n' TRANSFER_PASS RETURN_TO_PERSISTENT_GOAL >>"$state"
