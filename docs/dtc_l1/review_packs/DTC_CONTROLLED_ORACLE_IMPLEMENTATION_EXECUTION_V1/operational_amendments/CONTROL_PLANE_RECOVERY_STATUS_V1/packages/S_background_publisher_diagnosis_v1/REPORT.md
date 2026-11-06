# Background publication stall: diagnosis and recovery

The original watcher was alive and polling. Its Git commit hit the60-second command timeout and left an empty dedicated-index lock at10:14:23UTC. Later cycles continued collecting new results but failed at read-tree. WATCH_STATE stayed old because the exception path updates LAST_WATCH_ERROR instead; do_select was the normal60-second sleep.

Before recovery, no process held the dedicated index/lock and the only live Git process used an unrelated worktree. Local and remote HEAD were both2237e312. Main held the unique publication lock, preserved index/staging evidence and renamed only the verified orphan lock. The watcher was not restarted.

The same PID340280/start1070422329 then published8 closed results as0c73683dd4310705f8d9b0e841efee143581fa3a. Exact remote SHA, original fetch/show receipt and an independent GitHub connector content fetch agree on MANIFEST SHA25644150a9b1380eb639a32350842bae31d8b734ed3d7128fb0bd02197a991fd2a8.

No controller, model, registry or Git history was changed by this diagnostic. Dedicated-index preimage bytes are referenced in Main's recovery receipt and are intentionally excluded from this small review package. The old LAST_WATCH_ERROR is retained historical evidence. Scientific progress must be read from runtime evidence/current matrix, not publication-state timestamps.

Future engineering work may improve heartbeat/error reporting and qualify safer command-specific timeout/reap behavior. No watcher-source change is installed now, and failed-push commits must be preserved without reset or force.
