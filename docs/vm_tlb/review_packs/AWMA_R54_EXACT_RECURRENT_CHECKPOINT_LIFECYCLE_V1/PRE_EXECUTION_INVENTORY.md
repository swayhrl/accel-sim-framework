# Pre-execution inventory

Node109 RTX4080/SM89, driver 580.178.04, and adequate disk/memory were confirmed. A dedicated R54 env was created; C16/R53 environments, system CUDA and driver were untouched. The exact Qwen3.5 snapshot was fetched through the revision-preserving mirror transport after direct Hub access stalled. The initial NSYS invocation before script upload is retained as an empty engineering failure; `fastpath_r1` is the only actual model canary.
