# Network audit

Potential online operations in upstream tooling include `git clone`, `wget`, `curl`, package-manager commands and `pip install`. The V1 offline entrypoints never invoke them. `offline/env.sh` sets `PIP_NO_INDEX=1`; cached sources, wheels and assets must be supplied before transfer. Network use during V1 preparation is restricted to HTTPS cache acquisition and recorded in `offline/manifest.lock` / handoff.
