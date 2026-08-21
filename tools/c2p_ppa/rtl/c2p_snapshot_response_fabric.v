// Two-cycle self-routing response fabric for one Snapshot copy.
//
// Per copy, an engine cannot reissue until its joined response retires. Thus
// duplicate owners are illegal and route layers only arbitrate temporary link
// conflicts. Two elastic cuts retain the two-cycle response boundary without
// storing a 71-bit packet at every one of the seven route hops.
module c2p_snapshot_response_route2x2 #(
    parameter integer OWNER_W = 7, parameter integer DATA_W = 64,
    parameter integer ROUTE_BIT = 0
) (
    input wire a_valid, output wire a_ready,
    input wire [OWNER_W-1:0] a_owner, input wire [DATA_W-1:0] a_data,
    input wire b_valid, output wire b_ready,
    input wire [OWNER_W-1:0] b_owner, input wire [DATA_W-1:0] b_data,
    output wire lo_valid, input wire lo_ready,
    output wire [OWNER_W-1:0] lo_owner, output wire [DATA_W-1:0] lo_data,
    output wire hi_valid, input wire hi_ready,
    output wire [OWNER_W-1:0] hi_owner, output wire [DATA_W-1:0] hi_data
);
    wire a_hi = a_owner[ROUTE_BIT];
    wire b_hi = b_owner[ROUTE_BIT];
    wire same_link = a_valid && b_valid && (a_hi == b_hi);
    wire a_lo = a_valid && !a_hi;
    wire a_hi_valid = a_valid && a_hi;
    wire b_lo = b_valid && !b_hi;
    wire b_hi_valid = b_valid && b_hi;
    assign lo_valid = a_lo || b_lo;
    assign hi_valid = a_hi_valid || b_hi_valid;
    assign lo_owner = a_lo ? a_owner : b_owner;
    assign lo_data = a_lo ? a_data : b_data;
    assign hi_owner = a_hi_valid ? a_owner : b_owner;
    assign hi_data = a_hi_valid ? a_data : b_data;
    assign a_ready = a_hi ? hi_ready : lo_ready;
    assign b_ready = (b_hi ? hi_ready : lo_ready) && !same_link;
endmodule

module c2p_snapshot_response_pipe #(
    parameter integer OWNER_W = 7, parameter integer DATA_W = 64
) (
    input wire clk, input wire reset,
    input wire in_valid, output wire in_ready,
    input wire [OWNER_W-1:0] in_owner, input wire [DATA_W-1:0] in_data,
    output wire out_valid, input wire out_ready,
    output wire [OWNER_W-1:0] out_owner, output wire [DATA_W-1:0] out_data
);
    reg valid_r;
    reg [OWNER_W-1:0] owner_r;
    reg [DATA_W-1:0] data_r;
    assign in_ready = !valid_r || out_ready;
    assign out_valid = valid_r;
    assign out_owner = owner_r;
    assign out_data = data_r;
    always @(posedge clk) begin
        if (reset) begin
            valid_r <= 1'b0;
            owner_r <= {OWNER_W{1'b0}};
            data_r <= {DATA_W{1'b0}};
        end else if (in_ready) begin
            valid_r <= in_valid;
            if (in_valid) begin
                owner_r <= in_owner;
                data_r <= in_data;
            end
        end
    end
endmodule

module c2p_snapshot_response_fabric #(
    parameter integer ENGINES = 128, parameter integer NUM_BANKS = 64,
    parameter integer DATA_W = 64,
    parameter integer ENGINE_W = (ENGINES <= 1) ? 1 : $clog2(ENGINES),
    parameter integer STAGES = ENGINE_W,
    parameter integer MID_STAGES = (STAGES + 1) / 2
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
    wire [ENGINES-1:0] pre_valid [0:MID_STAGES];
    wire [ENGINES*ENGINE_W-1:0] pre_owner [0:MID_STAGES];
    wire [ENGINES*DATA_W-1:0] pre_data [0:MID_STAGES];
    wire [ENGINES-1:0] pre_ready [0:MID_STAGES];
    wire [ENGINES-1:0] mid_valid, mid_ready;
    wire [ENGINES*ENGINE_W-1:0] mid_owner;
    wire [ENGINES*DATA_W-1:0] mid_data;
    wire [ENGINES-1:0] post_valid [0:STAGES-MID_STAGES];
    wire [ENGINES*ENGINE_W-1:0] post_owner [0:STAGES-MID_STAGES];
    wire [ENGINES*DATA_W-1:0] post_data [0:STAGES-MID_STAGES];
    wire [ENGINES-1:0] post_ready [0:STAGES-MID_STAGES];
    wire [ENGINES*ENGINE_W-1:0] out_owner_unused;

    generate
        genvar i, s, l;
        for (i=0; i<ENGINES; i=i+1) begin : g_input
            if (i < NUM_BANKS) begin : g_bank
                assign pre_valid[0][i] = bank_rsp_valid[i];
                assign pre_owner[0][i*ENGINE_W +: ENGINE_W] = bank_rsp_owner[i*ENGINE_W +: ENGINE_W];
                assign pre_data[0][i*DATA_W +: DATA_W] = bank_rsp_data[i*DATA_W +: DATA_W];
                assign bank_rsp_ready[i] = pre_ready[0][i];
            end else begin : g_empty
                assign pre_valid[0][i] = 1'b0;
                assign pre_owner[0][i*ENGINE_W +: ENGINE_W] = {ENGINE_W{1'b0}};
                assign pre_data[0][i*DATA_W +: DATA_W] = {DATA_W{1'b0}};
            end
        end
        for (s=0; s<MID_STAGES; s=s+1) begin : g_pre
            for (l=0; l<ENGINES; l=l+1) if ((l & (1 << s)) == 0) begin : g_switch
                localparam integer M = l | (1 << s);
                c2p_snapshot_response_route2x2 #(.OWNER_W(ENGINE_W),.DATA_W(DATA_W),.ROUTE_BIT(s)) sw (
                    .a_valid(pre_valid[s][l]),.a_ready(pre_ready[s][l]),.a_owner(pre_owner[s][l*ENGINE_W +: ENGINE_W]),.a_data(pre_data[s][l*DATA_W +: DATA_W]),
                    .b_valid(pre_valid[s][M]),.b_ready(pre_ready[s][M]),.b_owner(pre_owner[s][M*ENGINE_W +: ENGINE_W]),.b_data(pre_data[s][M*DATA_W +: DATA_W]),
                    .lo_valid(pre_valid[s+1][l]),.lo_ready((s == MID_STAGES-1) ? mid_ready[l] : pre_ready[s+1][l]),.lo_owner(pre_owner[s+1][l*ENGINE_W +: ENGINE_W]),.lo_data(pre_data[s+1][l*DATA_W +: DATA_W]),
                    .hi_valid(pre_valid[s+1][M]),.hi_ready((s == MID_STAGES-1) ? mid_ready[M] : pre_ready[s+1][M]),.hi_owner(pre_owner[s+1][M*ENGINE_W +: ENGINE_W]),.hi_data(pre_data[s+1][M*DATA_W +: DATA_W]));
            end
        end
        for (l=0; l<ENGINES; l=l+1) begin : g_mid
            c2p_snapshot_response_pipe #(.OWNER_W(ENGINE_W),.DATA_W(DATA_W)) pipe (
                .clk(clk),.reset(reset),.in_valid(pre_valid[MID_STAGES][l]),.in_ready(mid_ready[l]),.in_owner(pre_owner[MID_STAGES][l*ENGINE_W +: ENGINE_W]),.in_data(pre_data[MID_STAGES][l*DATA_W +: DATA_W]),
                .out_valid(mid_valid[l]),.out_ready(post_ready[0][l]),.out_owner(mid_owner[l*ENGINE_W +: ENGINE_W]),.out_data(mid_data[l*DATA_W +: DATA_W]));
            assign post_valid[0][l] = mid_valid[l];
            assign post_owner[0][l*ENGINE_W +: ENGINE_W] = mid_owner[l*ENGINE_W +: ENGINE_W];
            assign post_data[0][l*DATA_W +: DATA_W] = mid_data[l*DATA_W +: DATA_W];
        end
        for (s=0; s<STAGES-MID_STAGES; s=s+1) begin : g_post
            for (l=0; l<ENGINES; l=l+1) if ((l & (1 << (MID_STAGES+s))) == 0) begin : g_switch
                localparam integer M = l | (1 << (MID_STAGES+s));
                c2p_snapshot_response_route2x2 #(.OWNER_W(ENGINE_W),.DATA_W(DATA_W),.ROUTE_BIT(MID_STAGES+s)) sw (
                    .a_valid(post_valid[s][l]),.a_ready(post_ready[s][l]),.a_owner(post_owner[s][l*ENGINE_W +: ENGINE_W]),.a_data(post_data[s][l*DATA_W +: DATA_W]),
                    .b_valid(post_valid[s][M]),.b_ready(post_ready[s][M]),.b_owner(post_owner[s][M*ENGINE_W +: ENGINE_W]),.b_data(post_data[s][M*DATA_W +: DATA_W]),
                    .lo_valid(post_valid[s+1][l]),.lo_ready((s == STAGES-MID_STAGES-1) ? out_ready[l] : post_ready[s+1][l]),.lo_owner(post_owner[s+1][l*ENGINE_W +: ENGINE_W]),.lo_data(post_data[s+1][l*DATA_W +: DATA_W]),
                    .hi_valid(post_valid[s+1][M]),.hi_ready((s == STAGES-MID_STAGES-1) ? out_ready[M] : post_ready[s+1][M]),.hi_owner(post_owner[s+1][M*ENGINE_W +: ENGINE_W]),.hi_data(post_data[s+1][M*DATA_W +: DATA_W]));
            end
        end
        for (l=0; l<ENGINES; l=l+1) begin : g_out
            c2p_snapshot_response_pipe #(.OWNER_W(ENGINE_W),.DATA_W(DATA_W)) pipe (
                .clk(clk),.reset(reset),.in_valid(post_valid[STAGES-MID_STAGES][l]),.in_ready(post_ready[STAGES-MID_STAGES][l]),.in_owner(post_owner[STAGES-MID_STAGES][l*ENGINE_W +: ENGINE_W]),.in_data(post_data[STAGES-MID_STAGES][l*DATA_W +: DATA_W]),
                .out_valid(out_valid[l]),.out_ready(out_ready[l]),.out_owner(out_owner_unused[l*ENGINE_W +: ENGINE_W]),.out_data(out_data[l*DATA_W +: DATA_W]));
        end
    endgenerate
    initial if (ENGINES != (1 << ENGINE_W) || NUM_BANKS > ENGINES || MID_STAGES < 1 || MID_STAGES >= STAGES)
        $error("C2P response fabric requires power-of-two lanes and two route halves");
endmodule
