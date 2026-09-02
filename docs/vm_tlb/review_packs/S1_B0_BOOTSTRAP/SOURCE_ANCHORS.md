# Source anchors

| Item | Recorded value |
| --- | --- |
| Core base SHA | `73774727e25fadf89df6f30ef5cf014091115db7` |
| Core current source SHA | `73774727e25fadf89df6f30ef5cf014091115db7` |
| Core branch | `hrl/vm-core-v0` |
| Core worktree | `/workspace/worktrees/gpgpu-sim-vm-core` |
| Core remote | `origin = https://github.com/accel-sim/gpgpu-sim_distribution.git` |
| Core remote status | `NOT_WRITABLE`; official remote was never pushed to |
| Framework base SHA | `3016c658f810bdae9a14bf4534ee99e9945eedae` |
| Framework source SHA before docs commit | `3016c658f810bdae9a14bf4534ee99e9945eedae` |
| Framework branch | `hrl/vm-core-v0` |
| Framework worktree | `/workspace/worktrees/accel-sim-vm-core` |
| Framework remotes | `origin = git@github.com:swayhrl/accel-sim-framework.git`; `upstream = https://github.com/accel-sim/accel-sim-framework.git` |
| Framework remote status | `WRITABLE` for `origin`, verified by `git push --dry-run` |
| Binary | `gpu-simulator/bin/release/accel-sim.out` |
| Binary SHA-256 | `56ca98159450eb13c9374beaaeb01ab96c60337e674e2138102b1c2ecee25d51` |

The Framework documentation commit is self-referential to this pack, so its final
SHA is supplied by `git rev-parse HEAD` in the final delivery rather than embedded
in a file that it changes.
