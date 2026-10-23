# Source this file in174-new; no model is launched and no global file is changed.
if [ "$(hostname)" != huangrulin-sshfs-174 ]; then
  echo 'HOLD: activate only in verified174-new, never old174' >&2
  return 2 2>/dev/null || exit 2
fi
export EP_L2_DTC_L1_NATIVE_ROOT=/root/data/ep_l2_dtc_l1_native_v2
export PATH="$EP_L2_DTC_L1_NATIVE_ROOT/bin:$PATH"
