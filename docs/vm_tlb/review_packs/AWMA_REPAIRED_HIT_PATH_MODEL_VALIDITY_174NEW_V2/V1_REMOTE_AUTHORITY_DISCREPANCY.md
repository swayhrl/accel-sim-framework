# V1 remote authority discrepancy

- User-reported local authority: `b9bb4c6c356f2d98b9213d1d2ac3efdade057901`.
- Local Git object exists and was inspected read-only.
- `git fetch origin` did not establish the expected V1 remote ref.
- GitHub REST ref query for `hrl/awma-repaired-hitpath-validity-174new-v1` returned HTTP 404.
- Coordination V2 ref is present and equals `c13b1dba1e45f97191668ddae21b3e569e53d257`.

Under V2 section 9, a V1 authority mismatch is a whole-goal scientific STOP. No rebuilt-runtime qualification or lookup matrix run is authorized from unverified local-only V1 content.
