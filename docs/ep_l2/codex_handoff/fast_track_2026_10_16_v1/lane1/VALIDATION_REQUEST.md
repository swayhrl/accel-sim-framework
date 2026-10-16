# Lane 5 independent validation request

Consume Core 126394be46b15f55b9756d43eb9ca9a9baae1c84 and Framework runtime
37dec04d223ae65167c5584e56887c74f6540d27. Binary/config hashes and local immutable
snapshots are in BASELINE_CONTRACT_V1.json. Interface ABI remains V1.
Production tests/source are delivered now; old-OFF gate still in progress, so
formal run qualification must wait for its final evidence update. Do not rerun
claimed old qualification keys; read the canonical registry's existing owner.

Please independently review version/reference limits, finite staging and bank
service, WAD lifecycle and requester audit, and normalize qualified releases
only after your actual gates pass. Formal B16/U_WB five-point runs remain Lane 5
owned and need not wait for TVD/RO. Source-mapped strict terminal adapter is
util/ep_l2/ft_lane1/parse_ft_terminal.py. It does not self-approve data correctness.

Lane 2/3: executable shared pool reserve/transfer/pin/sector methods are now
available. Deliver a minimal version-bound producer integration patch and
independent validation receipt before Lane 1 enables TVD/RO. Use the sole pool
and address authority; no full historical branch merge.
