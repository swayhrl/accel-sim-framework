# Inventory Method

This CPU-only deterministic inventory reads Git tree `ec620d9a6227acd934656c4d0c86079820d7a339` through Git blobs and walks `/root/share/c16_recovery_v3` without writing to it. SHA256 is recomputed for every regular recovery-endpoint file at or below `536870912` bytes. Larger files are inventoried with exact size and an explicit `SKIPPED_UNREASONABLE...` SHA field rather than a fabricated digest.

Local `AUTHORITATIVE` classification requires an exact path+SHA match from committed recovery/copyback receipts (`62428f2cea9ed4cd2def11339311d4347282d9c7`); filename-only classification is prohibited. The script writes only this output directory and invokes no CUDA/GPU/LLM executable.
