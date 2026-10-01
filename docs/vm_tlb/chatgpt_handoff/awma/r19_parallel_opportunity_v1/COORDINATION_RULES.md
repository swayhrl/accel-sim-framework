# R19 coordination rules

1. Lane F and G CPU preparation may run concurrently.
2. Lane F/G CUDA is strictly serialized by the existing 109 GPU lock.
3. Lane E is CPU/source-only and never blocks on the GPU.
4. No lane may restart R53.
5. No lane starts node174 simulation.
6. No lane silently substitutes synthetic/random inputs for real AI evidence.
7. Third-party model artifacts must be labeled as such and never upgraded to official authority.
8. A lane may stop early; idle time does not authorize scope expansion.
9. No automatic architecture mechanism follows a positive residual.
