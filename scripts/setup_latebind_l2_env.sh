#!/usr/bin/env bash
# Source this file to bind the LateBind-L2 experiment harness to one explicit
# GPGPU-Sim worktree.  It intentionally does not select a cache backend.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "error: source scripts/setup_latebind_l2_env.sh; do not execute it" >&2
  exit 2
fi

if [[ -z "${LATEBIND_L2_GPGPUSIM_ROOT:-}" ]]; then
  echo "error: set LATEBIND_L2_GPGPUSIM_ROOT to the selected GPGPU-Sim worktree" >&2
  return 2
fi

latebind_root="$(cd "${LATEBIND_L2_GPGPUSIM_ROOT}" && pwd)" || return 2
accelsim_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || return 2
if [[ ! -f "${latebind_root}/setup_environment" ]]; then
  echo "error: ${latebind_root} is not a GPGPU-Sim checkout" >&2
  return 2
fi
if [[ -n "${GPGPUSIM_ROOT:-}" && "${GPGPUSIM_ROOT}" != "${latebind_root}" ]]; then
  echo "error: GPGPUSIM_ROOT conflicts with LATEBIND_L2_GPGPUSIM_ROOT" >&2
  return 2
fi

export GPGPUSIM_ROOT="${latebind_root}"
source "${GPGPUSIM_ROOT}/setup_environment" "${1:-release}" || return $?
source "${accelsim_root}/gpu-simulator/setup_environment.sh" "${1:-release}" || return $?
if [[ "${GPGPUSIM_ROOT}" != "${latebind_root}" ]]; then
  echo "error: setup selected unexpected GPGPU-Sim root ${GPGPUSIM_ROOT}" >&2
  return 2
fi
echo "LateBind-L2 environment: ACCELSIM_ROOT=${ACCELSIM_ROOT} GPGPUSIM_ROOT=${GPGPUSIM_ROOT}"
unset latebind_root accelsim_root
