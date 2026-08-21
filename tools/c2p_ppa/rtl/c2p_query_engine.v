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
    reg had_candidate;
    reg no_candidate;
    reg [TIMEOUT_W-1:0] probe_age;
    integer sid_i;
    integer best_distance;
    integer this_distance;
    reg candidate_found;
    reg [SID_W-1:0] candidate_sid;

    wire pop_fifo = (state == S_IDLE) && (fifo_count != 0);
    wire push_fifo = miss_valid && miss_ready;
    assign miss_ready = (fifo_count < REQUEST_FIFO_DEPTH) || pop_fifo;

    function integer cluster_distance;
        input integer from_sid;
        input integer to_sid;
        integer from_cluster;
        integer to_cluster;
        begin
            from_cluster = from_sid / CLUSTER_SIZE;
            to_cluster = to_sid / CLUSTER_SIZE;
            if (from_cluster == to_cluster)
                cluster_distance = 0;
            else if (from_cluster > to_cluster)
                cluster_distance = 1 + from_cluster - to_cluster;
            else
                cluster_distance = 1 + to_cluster - from_cluster;
        end
    endfunction

    always @* begin
        candidate_found = 1'b0;
        candidate_sid = {SID_W{1'b0}};
        best_distance = NUM_SMS;
        for (sid_i = 0; sid_i < NUM_SMS; sid_i = sid_i + 1) begin
            this_distance = cluster_distance(active_sid, sid_i);
            if (candidate_mask[sid_i] &&
                (!candidate_found || this_distance < best_distance ||
                 (this_distance == best_distance && sid_i < candidate_sid))) begin
                candidate_found = 1'b1;
                candidate_sid = sid_i[SID_W-1:0];
                best_distance = this_distance;
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
                        state <= S_PICK;
                    end
                end
                S_PICK: begin
                    if (candidate_found) begin
                        selected_sid <= candidate_sid;
                        candidate_mask[candidate_sid] <= 1'b0;
                        state <= S_PROBE;
                    end else begin
                        no_candidate <= !had_candidate;
                        state <= S_LOWER;
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
                        else
                            state <= S_PICK;
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
    end
endmodule
