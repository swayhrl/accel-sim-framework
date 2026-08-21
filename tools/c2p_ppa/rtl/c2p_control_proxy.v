// C2P PPA flow fixture, not a complete C2P implementation.
//
// This control slice represents one query-issue lane of the C2P model: remove
// the requester from a 64-SM candidate bitmap, choose the nearest remaining
// candidate in deterministic priority order, and account for the finite issue
// and target-probe resources.  Snapshot rows and FIFO payload storage are
// intentionally outside this module; those are reported separately as SRAM.
module c2p_control_proxy #(
    parameter NUM_SMS = 64,
    parameter SID_W = 6,
    parameter COUNT_W = 9,
    parameter QUERY_DEPTH = 256,
    parameter TARGET_DEPTH = 32
) (
    input  wire                 clk,
    input  wire                 reset,
    input  wire                 query_valid,
    input  wire [SID_W-1:0]     requester_sid,
    input  wire [NUM_SMS-1:0]   candidate_bitmap,
    input  wire                 target_accept,
    input  wire                 query_pop,
    output wire                 query_ready,
    output wire                 probe_valid,
    output wire [SID_W-1:0]     probe_sid,
    output wire                 fallback_no_candidate
);

    reg [NUM_SMS-1:0] candidate_mask;
    reg               candidate_found;
    reg [SID_W-1:0]   candidate_sid;
    integer i;

    always @* begin
        candidate_mask = candidate_bitmap;
        candidate_mask[requester_sid] = 1'b0;
        candidate_found = 1'b0;
        candidate_sid = {SID_W{1'b0}};
        // The complete model orders by physical distance.  This fixed order is
        // deliberately sufficient only for a synthesis control-path fixture.
        for (i = 0; i < NUM_SMS; i = i + 1) begin
            if (candidate_mask[i] && !candidate_found) begin
                candidate_found = 1'b1;
                candidate_sid = i[SID_W-1:0];
            end
        end
    end

    reg [COUNT_W-1:0] query_count;
    reg [COUNT_W-1:0] target_count;
    wire query_push = query_valid && query_ready;
    wire probe_fire = probe_valid && target_accept;

    assign query_ready = (query_count < QUERY_DEPTH);
    assign probe_valid = query_valid && candidate_found &&
                         (target_count < TARGET_DEPTH);
    assign probe_sid = candidate_sid;
    assign fallback_no_candidate = query_valid && !candidate_found;

    always @(posedge clk) begin
        if (reset) begin
            query_count <= {COUNT_W{1'b0}};
            target_count <= {COUNT_W{1'b0}};
        end else begin
            case ({query_push, query_pop})
                2'b10: query_count <= query_count + 1'b1;
                2'b01: query_count <= query_count - 1'b1;
                default: query_count <= query_count;
            endcase
            case ({probe_fire, query_pop})
                2'b10: target_count <= target_count + 1'b1;
                2'b01: target_count <= target_count - 1'b1;
                default: target_count <= target_count;
            endcase
        end
    end
endmodule
