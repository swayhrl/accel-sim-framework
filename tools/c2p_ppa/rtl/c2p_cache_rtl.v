// Read-side C2P RTL top: Snapshot metadata plus one handshaked query lane.
// The peer-probe and lower-memory ports intentionally carry tags only; the
// surrounding L1/L2 integration owns the original request payload and data.
module c2p_cache_rtl #(
    parameter integer NUM_SMS = 64,
    parameter integer SID_W = 6,
    parameter integer TAG_W = 64,
    parameter integer NUM_BANKS = 64,
    parameter integer BF_ROWS_PER_BANK = 64,
    parameter integer TAG_MASK_ROWS_PER_BANK = 16,
    parameter integer CLUSTER_SIZE = 8,
    parameter integer QUERY_FIFO_DEPTH = 8,
    parameter integer PROBE_TIMEOUT = 32
) (
    input  wire                 clk,
    input  wire                 reset,
    input  wire                 update_valid,
    output wire                 update_ready,
    input  wire [SID_W-1:0]     update_sid,
    input  wire [TAG_W-1:0]     update_tag,
    input  wire                 miss_valid,
    output wire                 miss_ready,
    input  wire [SID_W-1:0]     miss_sid,
    input  wire [TAG_W-1:0]     miss_tag,
    output wire                 probe_req_valid,
    input  wire                 probe_req_ready,
    output wire [SID_W-1:0]     probe_req_sid,
    output wire [TAG_W-1:0]     probe_req_tag,
    input  wire                 probe_rsp_valid,
    output wire                 probe_rsp_ready,
    input  wire                 probe_rsp_hit,
    output wire                 peer_hit_valid,
    input  wire                 peer_hit_ready,
    output wire [SID_W-1:0]     peer_hit_sid,
    output wire [TAG_W-1:0]     peer_hit_tag,
    output wire                 lower_req_valid,
    input  wire                 lower_req_ready,
    output wire [TAG_W-1:0]     lower_req_tag,
    output wire                 lower_req_no_candidate
);

    wire snapshot_req_valid;
    wire snapshot_req_ready;
    wire [TAG_W-1:0] snapshot_req_tag;
    wire snapshot_rsp_valid;
    wire snapshot_rsp_ready;
    wire [NUM_SMS-1:0] snapshot_rsp_candidates;

    c2p_snapshot_matrix #(
        .NUM_SMS(NUM_SMS), .SID_W(SID_W), .TAG_W(TAG_W),
        .NUM_BANKS(NUM_BANKS), .BF_ROWS_PER_BANK(BF_ROWS_PER_BANK),
        .TAG_MASK_ROWS_PER_BANK(TAG_MASK_ROWS_PER_BANK)
    ) snapshot_matrix (
        .clk(clk), .reset(reset),
        .update_valid(update_valid), .update_ready(update_ready),
        .update_sid(update_sid), .update_tag(update_tag),
        .query_valid(snapshot_req_valid), .query_ready(snapshot_req_ready),
        .query_tag(snapshot_req_tag), .query_rsp_valid(snapshot_rsp_valid),
        .query_rsp_ready(snapshot_rsp_ready),
        .query_rsp_candidates(snapshot_rsp_candidates)
    );

    c2p_query_engine #(
        .NUM_SMS(NUM_SMS), .SID_W(SID_W), .TAG_W(TAG_W),
        .CLUSTER_SIZE(CLUSTER_SIZE), .REQUEST_FIFO_DEPTH(QUERY_FIFO_DEPTH),
        .PROBE_TIMEOUT(PROBE_TIMEOUT)
    ) query_engine (
        .clk(clk), .reset(reset),
        .miss_valid(miss_valid), .miss_ready(miss_ready),
        .miss_sid(miss_sid), .miss_tag(miss_tag),
        .snapshot_req_valid(snapshot_req_valid),
        .snapshot_req_ready(snapshot_req_ready),
        .snapshot_req_tag(snapshot_req_tag),
        .snapshot_rsp_valid(snapshot_rsp_valid),
        .snapshot_rsp_ready(snapshot_rsp_ready),
        .snapshot_rsp_candidates(snapshot_rsp_candidates),
        .probe_req_valid(probe_req_valid), .probe_req_ready(probe_req_ready),
        .probe_req_sid(probe_req_sid), .probe_req_tag(probe_req_tag),
        .probe_rsp_valid(probe_rsp_valid), .probe_rsp_ready(probe_rsp_ready),
        .probe_rsp_hit(probe_rsp_hit),
        .peer_hit_valid(peer_hit_valid), .peer_hit_ready(peer_hit_ready),
        .peer_hit_sid(peer_hit_sid), .peer_hit_tag(peer_hit_tag),
        .lower_req_valid(lower_req_valid), .lower_req_ready(lower_req_ready),
        .lower_req_tag(lower_req_tag),
        .lower_req_no_candidate(lower_req_no_candidate)
    );
endmodule
