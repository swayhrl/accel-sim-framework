# M4A-C0 rented-host pilot review pack

Final status: `PILOT_PASS_READY_FOR_GOAL_CAPTURE`.

The historical Hugging Face credential blocker was superseded by the authorized
checksum-verified local snapshot route. P5 completed with the exact frozen
`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08` snapshot;
P6 completed one real TP=4 `DIAGNOSTIC_PILOT` `decode1` trace; P7 copied the
bundle back and started the frozen SM86 parser on 35 real trace kernels. The
diagnostic bundle is not formal evidence and must not be relabeled as such.

Persistent copy-back root: `/workspace/m4a-rented-host-pilot/` on the main
development server. Its selected source/destination SHA256 comparisons are
recorded in `COPYBACK_AND_PARSER.md`.
