// One fully handshaked C2P candidate-pruning lane.
//
// A miss is queued, sent to the Snapshot Matrix, probed against candidates in
// deterministic nearest-cluster order, and either completes as a peer hit or
// is forwarded unchanged to the normal lower-memory path.  Exact probe
// responses are authoritative; Snapshot false positives only cost probes.
module c2p_query_engine #(
    parameter integer NUM_SMS = 64,
    parameter integer SID_W = 6,
    parameter integer TAG_W = 64,
    parameter integer CLUSTER_SIZE = 8,
    parameter integer REQUEST_FIFO_DEPTH = 8,
    parameter integer PROBE_TIMEOUT = 32
) (
    input  wire                 clk,
    input  wire                 reset,

    input  wire                 miss_valid,
    output wire                 miss_ready,
    input  wire [SID_W-1:0]     miss_sid,
    input  wire [TAG_W-1:0]     miss_tag,

    output wire                 snapshot_req_valid,
    input  wire                 snapshot_req_ready,
    output wire [TAG_W-1:0]     snapshot_req_tag,
    input  wire                 snapshot_rsp_valid,
    output wire                 snapshot_rsp_ready,
    input  wire [NUM_SMS-1:0]   snapshot_rsp_candidates,

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

    localparam integer FIFO_AW = $clog2(REQUEST_FIFO_DEPTH);
    localparam integer COUNT_W = $clog2(REQUEST_FIFO_DEPTH + 1);
    localparam integer NUM_CLUSTERS = NUM_SMS / CLUSTER_SIZE;
    localparam integer CLUSTER_W =
        (NUM_CLUSTERS <= 1) ? 1 : $clog2(NUM_CLUSTERS);
    localparam integer CLUSTER_RANK_W = CLUSTER_W;
    localparam integer CLUSTER_SHIFT = $clog2(CLUSTER_SIZE);
    localparam integer TIMEOUT_W =
        (PROBE_TIMEOUT <= 1) ? 1 : $clog2(PROBE_TIMEOUT + 1);
    localparam [2:0] S_IDLE = 3'd0, S_QUERY = 3'd1,
                     S_WAIT_SNAPSHOT = 3'd2, S_PICK = 3'd3,
                     S_PROBE = 3'd4, S_WAIT_PROBE = 3'd5,
                     S_PEER_HIT = 3'd6, S_LOWER = 3'd7;

    reg [SID_W-1:0] fifo_sid [0:REQUEST_FIFO_DEPTH-1];
    reg [TAG_W-1:0] fifo_tag [0:REQUEST_FIFO_DEPTH-1];
    reg [FIFO_AW-1:0] fifo_head;
    reg [FIFO_AW-1:0] fifo_tail;
    reg [COUNT_W-1:0] fifo_count;
    reg [2:0] state;
    reg [SID_W-1:0] active_sid;
    reg [TAG_W-1:0] active_tag;
    reg [NUM_SMS-1:0] candidate_mask;
    reg [SID_W-1:0] selected_sid;
    reg [CLUSTER_RANK_W-1:0] cluster_rank;
    reg had_candidate;
    reg no_candidate;
    reg [TIMEOUT_W-1:0] probe_age;
    integer cluster_delta;
    integer clusters_seen;
    integer lane_i;
    reg [CLUSTER_W-1:0] active_cluster;
    reg [CLUSTER_W-1:0] scan_cluster;
    reg scan_found;
    reg [SID_W-1:0] scan_sid;

    wire pop_fifo = (state == S_IDLE) && (fifo_count != 0);
    wire push_fifo = miss_valid && miss_ready;
    assign miss_ready = (fifo_count < REQUEST_FIFO_DEPTH) || pop_fifo;

    // Search one cluster per cycle.  The old all-64-SM min-distance cone was
    // functionally correct but put division, distance comparison, and a
    // 64-way priority encoder on the request-to-probe timing path.  This
    // walker preserves C++'s ordering (nearer cluster, then lower SID) while
    // limiting the per-cycle datapath to one CLUSTER_SIZE-wide encoder.
    always @* begin
        active_cluster = active_sid >> CLUSTER_SHIFT;
        scan_cluster = active_cluster;
        clusters_seen = 1;
        for (cluster_delta = 1;
             cluster_delta < NUM_CLUSTERS;
             cluster_delta = cluster_delta + 1) begin
            if (active_cluster >= cluster_delta) begin
                if (cluster_rank == clusters_seen[CLUSTER_RANK_W-1:0])
                    scan_cluster = active_cluster - cluster_delta;
                clusters_seen = clusters_seen + 1;
            end
            if ((active_cluster + cluster_delta) < NUM_CLUSTERS) begin
                if (cluster_rank == clusters_seen[CLUSTER_RANK_W-1:0])
                    scan_cluster = active_cluster + cluster_delta;
                clusters_seen = clusters_seen + 1;
            end
        end

        scan_found = 1'b0;
        scan_sid = {SID_W{1'b0}};
        for (lane_i = 0; lane_i < CLUSTER_SIZE; lane_i = lane_i + 1) begin
            if (!scan_found &&
                candidate_mask[scan_cluster * CLUSTER_SIZE + lane_i]) begin
                scan_found = 1'b1;
                scan_sid = scan_cluster * CLUSTER_SIZE + lane_i;
            end
        end
    end

    assign snapshot_req_valid = (state == S_QUERY);
    assign snapshot_req_tag = active_tag;
    assign snapshot_rsp_ready = (state == S_WAIT_SNAPSHOT);
    assign probe_req_valid = (state == S_PROBE);
    assign probe_req_sid = selected_sid;
    assign probe_req_tag = active_tag;
    assign probe_rsp_ready = (state == S_WAIT_PROBE);
    assign peer_hit_valid = (state == S_PEER_HIT);
    assign peer_hit_sid = selected_sid;
    assign peer_hit_tag = active_tag;
    assign lower_req_valid = (state == S_LOWER);
    assign lower_req_tag = active_tag;
    assign lower_req_no_candidate = no_candidate;

    always @(posedge clk) begin
        if (reset) begin
            fifo_head <= {FIFO_AW{1'b0}};
            fifo_tail <= {FIFO_AW{1'b0}};
            fifo_count <= {COUNT_W{1'b0}};
            state <= S_IDLE;
            active_sid <= {SID_W{1'b0}};
            active_tag <= {TAG_W{1'b0}};
            candidate_mask <= {NUM_SMS{1'b0}};
            selected_sid <= {SID_W{1'b0}};
            cluster_rank <= {CLUSTER_RANK_W{1'b0}};
            had_candidate <= 1'b0;
            no_candidate <= 1'b0;
            probe_age <= {TIMEOUT_W{1'b0}};
        end else begin
            if (push_fifo) begin
                fifo_sid[fifo_tail] <= miss_sid;
                fifo_tag[fifo_tail] <= miss_tag;
                fifo_tail <= fifo_tail + 1'b1;
            end
            if (pop_fifo)
                fifo_head <= fifo_head + 1'b1;
            case ({push_fifo, pop_fifo})
                2'b10: fifo_count <= fifo_count + 1'b1;
                2'b01: fifo_count <= fifo_count - 1'b1;
                default: fifo_count <= fifo_count;
            endcase

            case (state)
                S_IDLE: begin
                    if (pop_fifo) begin
                        active_sid <= fifo_sid[fifo_head];
                        active_tag <= fifo_tag[fifo_head];
                        had_candidate <= 1'b0;
                        no_candidate <= 1'b0;
                        state <= S_QUERY;
                    end
                end
                S_QUERY: begin
                    if (snapshot_req_ready)
                        state <= S_WAIT_SNAPSHOT;
                end
                S_WAIT_SNAPSHOT: begin
                    if (snapshot_rsp_valid) begin
                        candidate_mask <= snapshot_rsp_candidates;
                        candidate_mask[active_sid] <= 1'b0;
                        had_candidate <=
                            |(snapshot_rsp_candidates &
                              ~({{(NUM_SMS-1){1'b0}}, 1'b1} << active_sid));
                        cluster_rank <= {CLUSTER_RANK_W{1'b0}};
                        state <= S_PICK;
                    end
                end
                S_PICK: begin
                    if (scan_found) begin
                        selected_sid <= scan_sid;
                        candidate_mask[scan_sid] <= 1'b0;
                        state <= S_PROBE;
                    end else if (cluster_rank == NUM_CLUSTERS - 1) begin
                        no_candidate <= !had_candidate;
                        state <= S_LOWER;
                    end else begin
                        cluster_rank <= cluster_rank + 1'b1;
                    end
                end
                S_PROBE: begin
                    if (probe_req_ready) begin
                        probe_age <= {TIMEOUT_W{1'b0}};
                        state <= S_WAIT_PROBE;
                    end
                end
                S_WAIT_PROBE: begin
                    if (probe_rsp_valid) begin
                        if (probe_rsp_hit)
                            state <= S_PEER_HIT;
                        else begin
                            cluster_rank <= {CLUSTER_RANK_W{1'b0}};
                            state <= S_PICK;
                        end
                    end else if (probe_age == PROBE_TIMEOUT - 1) begin
                        no_candidate <= 1'b0;
                        state <= S_LOWER;
                    end else begin
                        probe_age <= probe_age + 1'b1;
                    end
                end
                S_PEER_HIT: begin
                    if (peer_hit_ready)
                        state <= S_IDLE;
                end
                S_LOWER: begin
                    if (lower_req_ready)
                        state <= S_IDLE;
                end
                default: state <= S_IDLE;
            endcase
        end
    end

    initial begin
        if (NUM_SMS > (1 << SID_W))
            $error("SID_W cannot encode NUM_SMS C2P requesters");
        if (REQUEST_FIFO_DEPTH < 2 ||
            (REQUEST_FIFO_DEPTH & (REQUEST_FIFO_DEPTH - 1)) != 0)
            $error("C2P request FIFO depth must be a power of two >= 2");
        if (CLUSTER_SIZE == 0 || PROBE_TIMEOUT == 0)
            $error("C2P cluster size and probe timeout must be nonzero");
        if ((NUM_SMS % CLUSTER_SIZE) != 0 ||
            (CLUSTER_SIZE & (CLUSTER_SIZE - 1)) != 0)
            $error("C2P requires a power-of-two cluster size that divides NUM_SMS");
    end
endmodule
