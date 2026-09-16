#!/usr/bin/env bash
set -euo pipefail
log=${1:?lifecycle log required}
need() { grep -q "$1" "$log" || { echo "TERMINAL_RECEIPT_REJECT missing=$1"; exit 1; }; }
need '^ROUTEB_LIFECYCLE device_kernel_complete '
need '^ROUTEB_LIFECYCLE channel_flush_complete '
need '^ROUTEB_LIFECYCLE receiver_fully_drained '
need '^ROUTEB_LIFECYCLE trace_sink_closed '
need '^ROUTEB_TERMINAL_COMPLETE '
need '^ROUTEB_LIFECYCLE postprocessing_started$'
need '^ROUTEB_LIFECYCLE postprocessing_completed$'
line() { grep -n "$1" "$log" | head -n1 | cut -d: -f1; }
a=$(line '^ROUTEB_LIFECYCLE device_kernel_complete ')
b=$(line '^ROUTEB_LIFECYCLE channel_flush_complete ')
c=$(line '^ROUTEB_LIFECYCLE receiver_fully_drained ')
d=$(line '^ROUTEB_LIFECYCLE trace_sink_closed ')
e=$(line '^ROUTEB_TERMINAL_COMPLETE ')
f=$(line '^ROUTEB_LIFECYCLE postprocessing_started$')
g=$(line '^ROUTEB_LIFECYCLE postprocessing_completed$')
if ! { [ "$a" -lt "$b" ] && [ "$b" -lt "$c" ] && [ "$c" -lt "$d" ] && [ "$d" -lt "$e" ] && [ "$e" -lt "$f" ] && [ "$f" -lt "$g" ]; }; then
  echo TERMINAL_RECEIPT_REJECT reason=order
  exit 1
fi
terminal=$(grep '^ROUTEB_TERMINAL_COMPLETE ' "$log")
for required in 'drop_count=0' 'overflow_count=0'; do
  case "$terminal" in *"$required"*) ;; *) echo "TERMINAL_RECEIPT_REJECT missing=$required"; exit 1;; esac
done
echo TERMINAL_RECEIPT_PASS
