# R17 unattended coordination rules

1. Lane F owns all R17 CUDA work on node109.
2. Lane G is CPU/source-only; it never waits for or polls Lane F.
3. Lane E remains STOP.
4. Both lanes solve ordinary engineering problems autonomously.
5. No automatic hardware or simulator promotion.
6. A negative/closed Lane F result does not cause Lane G to launch a backup experiment.
7. A Lane G novelty concern does not retroactively invalidate already-running Lane F measurements; it is recorded for review.
8. Durable datasets/index/raw live on node164; active environments/caches may live on node109.
9. Git transport failures use bounded fallback and are not scientific rerun reasons.
10. Finish with exact receipts and STOP even if unattended time remains.
