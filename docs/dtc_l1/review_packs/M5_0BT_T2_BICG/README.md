# M5.0BT T2 — BICG trace replay qualification

Status: **PASS**. This pack qualifies one immutable BICG NVBit-v1.8 payload
for the frozen 80-SM / cap-10240 / ratio-zero formal platform. It is a
qualification result, not a Paper performance registry row.

The same immutable trace bundle was consumed under Base, IO and OO. Each mode
naturally terminated, strict-parsed, and showed no fatal, assertion, deadlock,
trace-corruption, missing-address/opcode or output-mismatch signature.

The two legacy IO/OO summary JSON files retain an earlier one-character
Framework-SHA transcription error. They are preserved; corrected strict
summaries were regenerated from the unchanged simulator stdout with the
runtime Framework SHA below. No executable, configuration, trace, counter or
simulator output was changed.

See [VALIDATION_SUMMARY.md](VALIDATION_SUMMARY.md) and
[MANIFEST.json](MANIFEST.json).
