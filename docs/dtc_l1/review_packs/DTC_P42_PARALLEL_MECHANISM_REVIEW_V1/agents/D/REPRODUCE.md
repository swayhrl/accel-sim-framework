# Reproduction and evidence boundary

Run `build_report.py` in the original shared agent directory layout. It consumes the sibling A/B/C/E frozen reports, the single shared address index and the existing paper42 counter extract; it does not read trace bodies, active logs or simulator processes.

The six closed original raw-counter extracts are delivered compressed as `CLOSED_RAW_EVIDENCE.json.gz`; decompress to `CLOSED_RAW_EVIDENCE.json` before rebuilding. `extract_closed_remote.py` and `append_source_remote.py` document how the closed original source evidence was acquired; rerunning acquisition is unnecessary. The source commands use `git show` at exact old Core commit, never a checkout or build.

`SOURCE_SEMANTICS.json` records exact full-file source SHA plus line ranges. `DOWNSTREAM_SOURCE_FILES.json` holds the downstream source text; the sibling Agent C original-source bundle provides the remaining source text. All conclusions and provenance are in the report JSON, including actual launch/config/accepted-result identities from Agent A.

This packet authorizes no new scientific execution. Proposed diagnostic experiments are `NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED`.
