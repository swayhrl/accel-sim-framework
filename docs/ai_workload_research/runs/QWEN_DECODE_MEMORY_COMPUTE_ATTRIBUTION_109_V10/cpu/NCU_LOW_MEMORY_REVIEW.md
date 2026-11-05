# NCU low-memory CPU review

The installed NCU2025.1.1 guide explicitly says kernel replay skips memory save/restore when only one replay pass is necessary. CPU-only review cannot establish actual pass count.

Use `--metrics dram__bytes_read.sum,gpu__time_duration.sum --disable-extra-suffixes --graph-profiling node --replay-mode kernel`, with no set/section, one narrowly identified kernel, `--launch-count 1 --kill no --clock-control none --cache-control none`. Explicit metrics suppress the implicit basic set. Duration is a documented metric, but no static evidence proves it necessarily adds a pass.

Accept each real B1/B2 result only with completed numerical output, actual one-pass log, raw `profiler__replayer_passes=1` and `profiler__replayer_bytes_mem_backed_up.sum=0`. Missing statistics are not zero. Proxy success does not prove the real kernel. The V9 broader profile automatically exported these statistics: 7 passes and 103001157154 backed-up bytes total.

No general kernel-replay disable-backup/force-one-pass option was found. Sampling max-passes options do not cap normal DRAM counters. If required, application fallback is `--replay-mode application --app-replay-buffer file --app-replay-match grid --app-replay-mode strict --check-exit-code yes`; this repeats the complete application. File buffering stores result data. Keep graph node mode and validate CUDA13 runtime compatibility separately.

Known asset directory contains only Qwen2.5-3B-Instruct BF16 revision aa8e72537993ba99e69dfaafa59ed015b17504d1 and the same Qwen AWQ variant revision 3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd. An independent qualified dense model, accepted independent identity and qualified independent natural input are NOT_AVAILABLE. No wider search was performed.

JSON records exact source paths, source line anchors, SHA256, reused help evidence, argv options and audit limits. V9 stayed read-only. No GPU/CUDA/NVML, profiler, metric query, model import, installation or download was executed.
