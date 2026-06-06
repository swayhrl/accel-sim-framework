#!/usr/bin/env bash

# Sourceable Accel-Sim environment wrapper.

_accelsim_env_sourced=0
if [ "${BASH_SOURCE[0]}" != "$0" ]; then
  _accelsim_env_sourced=1
fi

_accelsim_env_finish() {
  local code="$1"
  if [ "$_accelsim_env_sourced" -eq 1 ]; then
    return "$code"
  fi
  exit "$code"
}

_accelsim_env_prepend_path() {
  local var_name="$1"
  local entry="$2"
  [ -d "$entry" ] || return 0
  eval "local current=\"\${$var_name:-}\""
  case ":$current:" in
    *":$entry:"*) ;;
    *)
      if [ -n "$current" ]; then
        eval "export $var_name=\"$entry:\$current\""
      else
        eval "export $var_name=\"$entry\""
      fi
      ;;
  esac
}

_accelsim_script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ACCELSIM_REPO="$(cd "$_accelsim_script_dir/../.." && pwd)"
export ACCELSIM_ROOT="$ACCELSIM_REPO/gpu-simulator"
export GPGPUSIM_ROOT="$ACCELSIM_ROOT/gpgpu-sim"
export GPUWATTCH_ROOT="$GPGPUSIM_ROOT"

_accelsim_cuda_default="/usr/local/cuda-11.8"
if [ -d "$_accelsim_cuda_default" ]; then
  export CUDA_INSTALL_PATH="$_accelsim_cuda_default"
elif [ -n "${CUDA_INSTALL_PATH:-}" ] && [ -d "$CUDA_INSTALL_PATH" ]; then
  export CUDA_INSTALL_PATH
elif [ -d "/usr/local/cuda" ]; then
  export CUDA_INSTALL_PATH="/usr/local/cuda"
else
  echo "ERROR: no CUDA installation found at $_accelsim_cuda_default or /usr/local/cuda" >&2
  _accelsim_env_finish 1
fi

export CUDA_HOME="$CUDA_INSTALL_PATH"
export CUDA_PATH="$CUDA_INSTALL_PATH"
_accelsim_env_prepend_path PATH "$CUDA_INSTALL_PATH/bin"
_accelsim_env_prepend_path LD_LIBRARY_PATH "$CUDA_INSTALL_PATH/lib64"
_accelsim_env_prepend_path LD_LIBRARY_PATH "$CUDA_INSTALL_PATH/lib"

for _accelsim_required in "$ACCELSIM_REPO" "$ACCELSIM_ROOT" "$GPGPUSIM_ROOT"; do
  if [ ! -d "$_accelsim_required" ]; then
    echo "ERROR: required path does not exist: $_accelsim_required" >&2
    _accelsim_env_finish 1
  fi
done

if [ -f "$ACCELSIM_ROOT/setup_environment.sh" ]; then
  _accelsim_env_nounset_was_on=0
  case "$-" in
    *u*)
      _accelsim_env_nounset_was_on=1
      set +u
      ;;
  esac
  if [ "${ACCELSIM_ENV_VERBOSE:-0}" = "1" ]; then
    # shellcheck source=/dev/null
    source "$ACCELSIM_ROOT/setup_environment.sh" "${ACCELSIM_CONFIG:-release}"
    _accelsim_env_source_rc=$?
  else
    # shellcheck source=/dev/null
    source "$ACCELSIM_ROOT/setup_environment.sh" "${ACCELSIM_CONFIG:-release}" >/dev/null
    _accelsim_env_source_rc=$?
  fi
  if [ "$_accelsim_env_nounset_was_on" -eq 1 ]; then
    set -u
  fi
  if [ "$_accelsim_env_source_rc" -ne 0 ]; then
    _accelsim_env_finish "$_accelsim_env_source_rc"
  fi
fi

export ACCELSIM_REPO
export ACCELSIM_ROOT
export GPGPUSIM_ROOT
export GPUWATTCH_ROOT="$GPGPUSIM_ROOT"
export CUDA_INSTALL_PATH
export CUDA_HOME="$CUDA_INSTALL_PATH"
export CUDA_PATH="$CUDA_INSTALL_PATH"

if [ "${ACCELSIM_ENV_VERBOSE:-0}" = "1" ]; then
  echo "ACCELSIM_REPO=$ACCELSIM_REPO"
  echo "ACCELSIM_ROOT=$ACCELSIM_ROOT"
  echo "GPGPUSIM_ROOT=$GPGPUSIM_ROOT"
  echo "CUDA_INSTALL_PATH=$CUDA_INSTALL_PATH"
fi

unset _accelsim_cuda_default _accelsim_required _accelsim_script_dir
unset _accelsim_env_nounset_was_on _accelsim_env_source_rc
_accelsim_env_finish 0
