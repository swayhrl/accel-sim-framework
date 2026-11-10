#!/usr/bin/env bash
set -euo pipefail

root=/data/c16/aiarch_hybrid_asset_qualification_20261110_v1/models/qwen3_5_4b
base=https://hf-mirror.com/Qwen/Qwen3.5-4B/resolve/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a
for name in LICENSE README.md chat_template.jinja config.json merges.txt model.safetensors.index.json preprocessor_config.json tokenizer.json tokenizer_config.json video_preprocessor_config.json vocab.json; do
  curl -fL -sS --connect-timeout 10 --retry 2 --retry-delay 3 --max-time 180 -o "$root/$name.part" "$base/$name"
  mv "$root/$name.part" "$root/$name"
  chmod 600 "$root/$name"
  sha256sum "$root/$name"
done
