#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -lt 3 ]; then echo 'three run paths required' >&2; exit 2; fi
terminal=/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2/util/tracer_nvbit/route_b_1771/route_b_terminal_receipt_verify.sh
first=''
mkdir -p /data/c16/awma/simcompat-v2/route_b/b2_verification
out=/data/c16/awma/simcompat-v2/route_b/b2_verification/live_consistency.tsv
printf 'run\tdevice_reported\treceiver_accepted\traw_records\tgrammar_instructions\tcta_count\twarp_keys\tstructure_sha\topcode_receipt_sha\n' > "$out"
for run in "$@"; do
  "$terminal" "$run/lifecycle.log" >/dev/null
  trace=$(find "$run/raw" -maxdepth 1 -type f -name 'kernel-*.trace.xz' | sort | head -n1)
  traceg=$(find "$run/raw" -maxdepth 1 -type f -name 'kernel-*.traceg.xz' | sort | head -n1)
  [ -n "$trace" ] && [ -n "$traceg" ]
  xz -t "$trace" "$traceg"
  term=$(grep '^ROUTEB_TERMINAL_COMPLETE ' "$run/lifecycle.log")
  device=$(printf '%s\n' "$term" | sed -n 's/.*device_reported=\([0-9][0-9]*\).*/\1/p')
  recv=$(printf '%s\n' "$term" | sed -n 's/.*receiver_accepted=\([0-9][0-9]*\).*/\1/p')
  written=$(printf '%s\n' "$term" | sed -n 's/.*raw_records=\([0-9][0-9]*\).*/\1/p')
  raw=$(xz -dc "$trace" | awk 'BEGIN{s=0;n=0} /^#traces format/{s=1;next} s && NF{n++} END{print n}')
  grammar=$(sed -n 's/.*"instructions":\([0-9][0-9]*\).*/\1/p' "$traceg.grammar.json")
  ctas=$(xz -dc "$trace" | awk 'BEGIN{s=0} /^#traces format/{s=1;next} s&&NF{print $1,$2,$3}' | sort -u | wc -l)
  warps=$(xz -dc "$trace" | awk 'BEGIN{s=0} /^#traces format/{s=1;next} s&&NF{print $1,$2,$3,$4}' | sort -u | wc -l)
  struct=$(xz -dc "$traceg" | awk '/^thread block = /||/^warp = /||/^insts = /' | sha256sum | awk '{print $1}')
  opcode=$(sha256sum "$traceg.grammar.json" | awk '{print $1}')
  if [ "$device" != "$recv" ] || [ "$recv" != "$written" ] || [ "$written" != "$raw" ] || [ "$raw" != "$grammar" ]; then
    echo "B2_LIVE_REJECT count_mismatch run=$run device=$device recv=$recv written=$written raw=$raw grammar=$grammar" >&2
    exit 1
  fi
  if [ "$ctas" -ne 98 ] || [ "$warps" -ne 3136 ]; then
    echo "B2_LIVE_REJECT real_packet_metadata run=$run ctas=$ctas warps=$warps" >&2
    exit 1
  fi
  if ! xz -dc "$trace" | grep -F -e 'LDG.E.64' -e 'STG.E.64' >/dev/null; then
    echo "B2_LIVE_REJECT no_memory_packet run=$run" >&2
    exit 1
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$run" "$device" "$recv" "$raw" "$grammar" "$ctas" "$warps" "$struct" "$opcode" >> "$out"
  if [ -z "$first" ]; then first="$struct,$opcode"; elif [ "$first" != "$struct,$opcode" ]; then
    echo "B2_LIVE_REJECT fresh_process_structure_or_opcode_mismatch run=$run" >&2
    exit 1
  fi
done
echo B2_LIVE_CONSISTENCY_PASS
