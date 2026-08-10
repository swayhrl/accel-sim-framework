#!/usr/bin/env bash
# Source this file to bind Accel-Sim to one explicit GPGPU-Sim worktree.
# Usage:
#   export DECOUPLED_L2_GPGPUSIM_ROOT=/absolute/path/to/gpgpu-sim_distribution
#   source scripts/setup_decoupled_l2_env.sh [release|debug]

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "error: source scripts/setup_decoupled_l2_env.sh; do not execute it" >&2
  exit 2
fi

if [[ -z "${DECOUPLED_L2_GPGPUSIM_ROOT:-}" ]]; then
  echo "error: set DECOUPLED_L2_GPGPUSIM_ROOT to the selected GPGPU-Sim worktree" >&2
  return 2
fi

_decoupled_l2_root="$(cd "${DECOUPLED_L2_GPGPUSIM_ROOT}" && pwd)" || return 2
_decoupled_l2_accelsim_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || return 2
_decoupled_l2_config="${1:-release}"

if [[ -n "${GPGPUSIM_ROOT:-}" && "${GPGPUSIM_ROOT}" != "${_decoupled_l2_root}" ]]; then
  echo "error: GPGPUSIM_ROOT (${GPGPUSIM_ROOT}) conflicts with DECOUPLED_L2_GPGPUSIM_ROOT (${_decoupled_l2_root})" >&2
  return 2
fi
if [[ ! -f "${_decoupled_l2_root}/setup_environment" ]]; then
  echo "error: ${_decoupled_l2_root} is not a GPGPU-Sim checkout" >&2
  return 2
fi

export GPGPUSIM_ROOT="${_decoupled_l2_root}"
source "${GPGPUSIM_ROOT}/setup_environment" "${_decoupled_l2_config}" || return $?
if [[ "${GPGPUSIM_ROOT}" != "${_decoupled_l2_root}" ]]; then
  echo "error: GPGPU-Sim setup selected an unexpected root: ${GPGPUSIM_ROOT}" >&2
  return 2
fi
source "${_decoupled_l2_accelsim_root}/gpu-simulator/setup_environment.sh" "${_decoupled_l2_config}" || return $?
if [[ "${GPGPUSIM_ROOT}" != "${_decoupled_l2_root}" ]]; then
  echo "error: Accel-Sim setup changed GPGPUSIM_ROOT to ${GPGPUSIM_ROOT}" >&2
  return 2
fi

echo "Decoupled-L2 environment: ACCELSIM_ROOT=${ACCELSIM_ROOT} GPGPUSIM_ROOT=${GPGPUSIM_ROOT}"
unset _decoupled_l2_root _decoupled_l2_accelsim_root _decoupled_l2_config
