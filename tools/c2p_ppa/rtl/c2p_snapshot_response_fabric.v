// Registered self-routing response fabric for one Snapshot copy.
//
// The fabric is an ENGINE_W-stage network of 2x2 elastic switches. It replaces
// a flat 64-bank-to-128-engine data crossbar with O(ENGINES*log2(ENGINES))
// registered links. Contending packets remain at their upstream switch and are
// retried, so the network never drops an accepted bank response.
module c2p_snapshot_response_switch2x2 #(
    parameter integer OWNER_W = 7,
    parameter integer DATA_W = 64,
    parameter integer ROUTE_BIT = 0
) (
    input wire clk, input wire reset,
    input wire a_valid, output wire a_ready,
    input wire [OWNER_W-1:0] a_owner, input wire [DATA_W-1:0] a_data,
    input wire b_valid, output wire b_ready,
    input wire [OWNER_W-1:0] b_owner, input wire [DATA_W-1:0] b_data,
    output wire lo_valid, input wire lo_ready,
    output wire [OWNER_W-1:0] lo_owner, output wire [DATA_W-1:0] lo_data,
    output wire hi_valid, input wire hi_ready,
    output wire [OWNER_W-1:0] hi_owner, output wire [DATA_W-1:0] hi_data
);
    reg lo_valid_r, hi_valid_r;
    reg [OWNER_W-1:0] lo_owner_r, hi_owner_r;
    reg [DATA_W-1:0] lo_data_r, hi_data_r;
    wire a_hi = a_owner[ROUTE_BIT];
    wire b_hi = b_owner[ROUTE_BIT];
    wire lo_take = !lo_valid_r || lo_ready;
    wire hi_take = !hi_valid_r || hi_ready;
    // Fixed A-before-B priority only applies when both packets target one
    // output. The denied input stays valid until its upstream buffer retries.
    assign a_ready = a_valid && (a_hi ? hi_take : lo_take);
    assign b_ready = b_valid && (b_hi ? hi_take : lo_take) &&
                     !(a_valid && (a_hi == b_hi));
    assign lo_valid = lo_valid_r;
    assign hi_valid = hi_valid_r;
    assign lo_owner = lo_owner_r;
    assign hi_owner = hi_owner_r;
    assign lo_data = lo_data_r;
    assign hi_data = hi_data_r;

    always @(posedge clk) begin
        if (reset) begin
            lo_valid_r <= 1'b0; hi_valid_r <= 1'b0;
            lo_owner_r <= {OWNER_W{1'b0}}; hi_owner_r <= {OWNER_W{1'b0}};
            lo_data_r <= {DATA_W{1'b0}}; hi_data_r <= {DATA_W{1'b0}};
        end else begin
            if (lo_take) begin
                if (a_valid && !a_hi) begin
                    lo_valid_r <= 1'b1; lo_owner_r <= a_owner; lo_data_r <= a_data;
                end else if (b_valid && !b_hi) begin
                    lo_valid_r <= 1'b1; lo_owner_r <= b_owner; lo_data_r <= b_data;
                end else lo_valid_r <= 1'b0;
            end
            if (hi_take) begin
                if (a_valid && a_hi) begin
                    hi_valid_r <= 1'b1; hi_owner_r <= a_owner; hi_data_r <= a_data;
                end else if (b_valid && b_hi) begin
                    hi_valid_r <= 1'b1; hi_owner_r <= b_owner; hi_data_r <= b_data;
                end else hi_valid_r <= 1'b0;
            end
        end
    end
endmodule

module c2p_snapshot_response_fabric #(
    parameter integer ENGINES = 128,
    parameter integer NUM_BANKS = 64,
    parameter integer DATA_W = 64,
    parameter integer ENGINE_W = (ENGINES <= 1) ? 1 : $clog2(ENGINES),
    parameter integer STAGES = ENGINE_W
) (
    input wire clk, input wire reset,
    input wire [NUM_BANKS-1:0] bank_rsp_valid,
    output wire [NUM_BANKS-1:0] bank_rsp_ready,
    input wire [NUM_BANKS*ENGINE_W-1:0] bank_rsp_owner,
    input wire [NUM_BANKS*DATA_W-1:0] bank_rsp_data,
    output wire [ENGINES-1:0] out_valid,
    input wire [ENGINES-1:0] out_ready,
    output wire [ENGINES*DATA_W-1:0] out_data
);
    wire [ENGINES-1:0] stage_valid [0:STAGES];
    wire [ENGINES*ENGINE_W-1:0] stage_owner [0:STAGES];
    wire [ENGINES*DATA_W-1:0] stage_data [0:STAGES];
    wire [ENGINES-1:0] stage_ready [0:STAGES-1];

    generate
        genvar in_g;
        for (in_g = 0; in_g < ENGINES; in_g = in_g + 1) begin : g_input
            if (in_g < NUM_BANKS) begin : g_bank_input
                assign stage_valid[0][in_g] = bank_rsp_valid[in_g];
                assign stage_owner[0][in_g*ENGINE_W +: ENGINE_W] =
                    bank_rsp_owner[in_g*ENGINE_W +: ENGINE_W];
                assign stage_data[0][in_g*DATA_W +: DATA_W] =
                    bank_rsp_data[in_g*DATA_W +: DATA_W];
                assign bank_rsp_ready[in_g] = stage_ready[0][in_g];
            end else begin : g_empty_input
                assign stage_valid[0][in_g] = 1'b0;
                assign stage_owner[0][in_g*ENGINE_W +: ENGINE_W] = {ENGINE_W{1'b0}};
                assign stage_data[0][in_g*DATA_W +: DATA_W] = {DATA_W{1'b0}};
            end
        end
        genvar stage_g;
        genvar lane_g;
        for (stage_g = 0; stage_g < STAGES; stage_g = stage_g + 1) begin : g_stage
            for (lane_g = 0; lane_g < ENGINES; lane_g = lane_g + 1) begin : g_lane
                if ((lane_g & (1 << stage_g)) == 0) begin : g_switch
                    localparam integer MATE = lane_g | (1 << stage_g);
                    if (stage_g == STAGES-1) begin : g_last
                    c2p_snapshot_response_switch2x2 #(
                        .OWNER_W(ENGINE_W), .DATA_W(DATA_W), .ROUTE_BIT(stage_g)
                    ) sw (
                        .clk(clk), .reset(reset),
                        .a_valid(stage_valid[stage_g][lane_g]),
                        .a_ready(stage_ready[stage_g][lane_g]),
                        .a_owner(stage_owner[stage_g][lane_g*ENGINE_W +: ENGINE_W]),
                        .a_data(stage_data[stage_g][lane_g*DATA_W +: DATA_W]),
                        .b_valid(stage_valid[stage_g][MATE]),
                        .b_ready(stage_ready[stage_g][MATE]),
                        .b_owner(stage_owner[stage_g][MATE*ENGINE_W +: ENGINE_W]),
                        .b_data(stage_data[stage_g][MATE*DATA_W +: DATA_W]),
                        .lo_valid(stage_valid[stage_g+1][lane_g]), .lo_ready(out_ready[lane_g]),
                        .lo_owner(stage_owner[stage_g+1][lane_g*ENGINE_W +: ENGINE_W]),
                        .lo_data(stage_data[stage_g+1][lane_g*DATA_W +: DATA_W]),
                        .hi_valid(stage_valid[stage_g+1][MATE]), .hi_ready(out_ready[MATE]),
                        .hi_owner(stage_owner[stage_g+1][MATE*ENGINE_W +: ENGINE_W]),
                        .hi_data(stage_data[stage_g+1][MATE*DATA_W +: DATA_W])
                    );
                    end else begin : g_middle
                    c2p_snapshot_response_switch2x2 #(
                        .OWNER_W(ENGINE_W), .DATA_W(DATA_W), .ROUTE_BIT(stage_g)
                    ) sw (
                        .clk(clk), .reset(reset),
                        .a_valid(stage_valid[stage_g][lane_g]),
                        .a_ready(stage_ready[stage_g][lane_g]),
                        .a_owner(stage_owner[stage_g][lane_g*ENGINE_W +: ENGINE_W]),
                        .a_data(stage_data[stage_g][lane_g*DATA_W +: DATA_W]),
                        .b_valid(stage_valid[stage_g][MATE]),
                        .b_ready(stage_ready[stage_g][MATE]),
                        .b_owner(stage_owner[stage_g][MATE*ENGINE_W +: ENGINE_W]),
                        .b_data(stage_data[stage_g][MATE*DATA_W +: DATA_W]),
                        .lo_valid(stage_valid[stage_g+1][lane_g]),
                        .lo_ready(stage_ready[stage_g+1][lane_g]),
                        .lo_owner(stage_owner[stage_g+1][lane_g*ENGINE_W +: ENGINE_W]),
                        .lo_data(stage_data[stage_g+1][lane_g*DATA_W +: DATA_W]),
                        .hi_valid(stage_valid[stage_g+1][MATE]),
                        .hi_ready(stage_ready[stage_g+1][MATE]),
                        .hi_owner(stage_owner[stage_g+1][MATE*ENGINE_W +: ENGINE_W]),
                        .hi_data(stage_data[stage_g+1][MATE*DATA_W +: DATA_W])
                    );
                    end
                end
            end
        end
    endgenerate
    assign out_valid = stage_valid[STAGES];
    assign out_data = stage_data[STAGES];

    initial begin
        if (ENGINES != (1 << ENGINE_W) || NUM_BANKS > ENGINES)
            $error("C2P response fabric requires power-of-two engine lanes");
    end
endmodule
