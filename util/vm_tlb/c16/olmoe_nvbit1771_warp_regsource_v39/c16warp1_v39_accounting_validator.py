#!/usr/bin/env python3
"""Independent fail-closed accounting check for C16WARP1 Channel receipts."""
import json
import sys

REQUIRED = (
    "producer_logical_records", "producer_overflow", "receiver_packets_accepted",
    "receiver_first_sequence", "receiver_last_sequence", "receiver_sequence_gap_count",
    "receiver_duplicate_sequence_count", "receiver_terminal_seen", "receiver_terminal_count",
    "finalized_c16warp1_records_written",
)

def validate(receipt):
    missing = [key for key in REQUIRED if key not in receipt]
    if missing: raise ValueError("missing " + ",".join(missing))
    if receipt["producer_overflow"] != 0: raise ValueError("producer overflow")
    if receipt["receiver_sequence_gap_count"] != 0: raise ValueError("sequence gap")
    if receipt["receiver_duplicate_sequence_count"] != 0: raise ValueError("duplicate sequence")
    if receipt.get("receiver_malformed_packet", False): raise ValueError("malformed packet")
    if not receipt["receiver_terminal_seen"] or receipt["receiver_terminal_count"] != 1:
        raise ValueError("receiver terminal closure")
    counts = (receipt["producer_logical_records"], receipt["receiver_packets_accepted"],
              receipt["finalized_c16warp1_records_written"])
    if len(set(counts)) != 1: raise ValueError("producer/receiver/finalized count mismatch")
    count = counts[0]
    if count and receipt["receiver_first_sequence"] != 0: raise ValueError("first sequence")
    if count and receipt["receiver_last_sequence"] != count - 1: raise ValueError("last sequence")
    return "NO_UNACCOUNTED_RECORDS_PROVEN"

if __name__ == "__main__":
    try:
        print(validate(json.load(open(sys.argv[1]))))
    except Exception as error:
        print("REJECT", error)
        raise SystemExit(2)
