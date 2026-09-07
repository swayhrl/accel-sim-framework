# Known gaps and evidence limits

- `prefill-paper` is nonterminal. Its liveness snapshot is not a result and
  leaves the prefill four-profile comparison incomplete.
- Start time, end time, elapsed runtime, and duplicate telemetry-record
  identity are not represented by the immutable manifest/final scalar format;
  the terminal metrics table records `NOT_AVAILABLE` rather than inferring
  them.
- Disabled and ideal profiles do not emit the VM telemetry scalar family;
  corresponding cells are deliberately `NOT_AVAILABLE`.
- This checkpoint does not run C4, scan traces, add telemetry, or perform
  offline locality analysis.
- The historical host-CUDA attribution is superseded by the existing direct
  Core-local runtime record. `INPUT_PROVENANCE.tsv` binds the frozen binary and
  Core-local runtime SHA-256 without rewriting any formal manifest.
