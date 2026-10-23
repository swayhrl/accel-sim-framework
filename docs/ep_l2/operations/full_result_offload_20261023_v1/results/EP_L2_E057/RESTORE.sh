#!/bin/sh
set -eu
: "${1:?Pass an authorized NEW ABSENT native Target destination}"
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 -B "$HERE/full_result_bundle.py" --restore "$HERE" --destination "$1"
