#!/usr/bin/env bash
# Fetch the exact open ASAP7 SRAM view set used by the C2P macro proxy.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
dest=${1:-"$script_dir/third_party/asap7_sram_0p0"}
repo=https://github.com/The-OpenROAD-Project/asap7_sram_0p0.git
revision=9f5af0939e8dd3cc1a9693a50b23441691dd7d25

if [[ ! -d "$dest/.git" ]]; then
    mkdir -p "$(dirname "$dest")"
    git clone "$repo" "$dest"
fi
git -C "$dest" fetch --tags origin
git -C "$dest" checkout --detach "$revision"
for path in \
    generated/verilog/srambank_256x4x64_6t122.v \
    generated/LEF/srambank_256x4x64_6t122.lef \
    generated/LIB/srambank_256x4x64_6t122.lib \
    gds/srambank_64b.gds; do
    [[ -f "$dest/$path" ]] || { echo "missing ASAP7 SRAM view: $path" >&2; exit 2; }
done
printf 'ASAP7 SRAM views ready: %s (%s)\n' "$dest" "$revision"
