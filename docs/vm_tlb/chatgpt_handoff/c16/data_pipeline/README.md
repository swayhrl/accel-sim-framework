# C16 Data Pipeline — ChatGPT → Codex Handoff

Ownership: ChatGPT.

Read in order:

1. `CURRENT_STATE.md`
2. `DISCUSSION_REFERENCE.md`
3. `CODEX_NEXT_STAGE.md`

This directory is the authoritative coordination state for the post-old174 C16 data plane.
Codex must not modify these files unless explicitly authorized.

Long-term roles:

- node109 / RTX4080: GPU producer and capture execution plane;
- new174 / port 2239: ingest, verification, catalog and CPU analysis plane;
- node164 via `/root/share/mnt164`: long-term data plane;
- GitHub: code, schemas, receipts, manifests, catalogs, review packs and handoffs;
- old174 / port 2233: historical source only after accepted final handover.
