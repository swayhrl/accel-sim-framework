// Scalable C2P Snapshot address front end.
//
// This composes the paper-shaped BF-engine pool with a 64-bank/four-copy
// arbiter. Its bank request outputs are the direct contract for a physical
// Snapshot macro array: one row command per copy/bank in each cycle. Each
// engine tracks which of its four rows have issued, so copy-bank conflicts do
// not require a global all-or-nothing matching network. Each copy returns
// owner-tagged data through a registered self-routing packet fabric; the
// response joiner releases an engine only after its completed Snapshot result
// has been consumed.
//
// It is intentionally separate from the functional single-lane cache top
// until the target-L1 request queues and macro-array response router use this
// interface.
module c2p_snapshot_banked_frontend #(
    parameter integer ENGINES = 128,
    parameter integer TAG_W = 64,
    parameter integer ROW_W = 13,
    parameter integer AUX_W = 1,
    parameter integer NUM_BANKS = 64,
    parameter integer ENGINE_W = (ENGINES <= 1) ? 1 : $clog2(ENGINES)
) (
    input  wire                         clk,
    input  wire                         reset,
    input  wire [ENGINES-1:0]           in_valid,
    output wire [ENGINES-1:0]           in_ready,
    input  wire [ENGINES*TAG_W-1:0]     in_tag,
    input  wire [ENGINES*AUX_W-1:0]     in_aux,

    output wire [4*NUM_BANKS-1:0]       bank_req_valid,
    input  wire [4*NUM_BANKS-1:0]       bank_req_ready,
    output wire [4*NUM_BANKS*ENGINE_W-1:0] bank_req_owner,
    output wire [4*NUM_BANKS*ROW_W-1:0] bank_req_row,
    input  wire [4*NUM_BANKS-1:0]       bank_rsp_valid,
    output wire [4*NUM_BANKS-1:0]       bank_rsp_ready,
    input  wire [4*NUM_BANKS*ENGINE_W-1:0] bank_rsp_owner,
    input  wire [4*NUM_BANKS*64-1:0]    bank_rsp_data,

    output wire [ENGINES-1:0]           out_valid,
    input  wire [ENGINES-1:0]           out_ready,
    output wire [ENGINES*64-1:0]        out_data0,
    output wire [ENGINES*64-1:0]        out_data1,
    output wire [ENGINES*64-1:0]        out_data2,
    output wire [ENGINES*64-1:0]        out_data3,
    output wire [ENGINES*AUX_W-1:0]     out_aux
);

    wire [ENGINES-1:0] engine_valid;
    wire [ENGINES-1:0] engine_ready;
    wire [ENGINES*ROW_W-1:0] engine_row0;
    wire [ENGINES*ROW_W-1:0] engine_row1;
    wire [ENGINES*ROW_W-1:0] engine_row2;
    wire [ENGINES*ROW_W-1:0] engine_row3;
    wire [ENGINES*6-1:0] engine_bank0;
    wire [ENGINES*6-1:0] engine_bank1;
    wire [ENGINES*6-1:0] engine_bank2;
    wire [ENGINES*6-1:0] engine_bank3;
    wire [ENGINES-1:0] engine_grant0;
    wire [ENGINES-1:0] engine_grant1;
    wire [ENGINES-1:0] engine_grant2;
    wire [ENGINES-1:0] engine_grant3;
    wire [ENGINES-1:0] copy0_valid;
    wire [ENGINES-1:0] copy1_valid;
    wire [ENGINES-1:0] copy2_valid;
    wire [ENGINES-1:0] copy3_valid;
    wire [ENGINES-1:0] copy0_ready;
    wire [ENGINES-1:0] copy1_ready;
    wire [ENGINES-1:0] copy2_ready;
    wire [ENGINES-1:0] copy3_ready;
    wire [ENGINES*64-1:0] copy0_data;
    wire [ENGINES*64-1:0] copy1_data;
    wire [ENGINES*64-1:0] copy2_data;
    wire [ENGINES*64-1:0] copy3_data;
    reg [3:0] engine_sent [0:ENGINES-1];
    wire [ENGINES-1:0] engine_need0;
    wire [ENGINES-1:0] engine_need1;
    wire [ENGINES-1:0] engine_need2;
    wire [ENGINES-1:0] engine_need3;
    integer engine_i;

    generate
        genvar sent_g;
        for (sent_g = 0; sent_g < ENGINES; sent_g = sent_g + 1) begin : g_sent
            assign engine_need0[sent_g] = engine_valid[sent_g] && !engine_sent[sent_g][0];
            assign engine_need1[sent_g] = engine_valid[sent_g] && !engine_sent[sent_g][1];
            assign engine_need2[sent_g] = engine_valid[sent_g] && !engine_sent[sent_g][2];
            assign engine_need3[sent_g] = engine_valid[sent_g] && !engine_sent[sent_g][3];
            assign engine_ready[sent_g] = out_valid[sent_g] && out_ready[sent_g];
        end
    endgenerate

    c2p_bf_engine_array #(
        .ENGINES(ENGINES), .TAG_W(TAG_W), .ROW_W(ROW_W), .AUX_W(AUX_W)
    ) engines (
        .clk(clk), .reset(reset), .in_valid(in_valid), .in_ready(in_ready),
        .in_tag(in_tag), .in_aux(in_aux), .out_valid(engine_valid),
        .out_ready(engine_ready), .out_row0(engine_row0),
        .out_row1(engine_row1), .out_row2(engine_row2),
        .out_row3(engine_row3), .out_bank0(engine_bank0),
        .out_bank1(engine_bank1), .out_bank2(engine_bank2),
        .out_bank3(engine_bank3), .out_aux(out_aux)
    );

    c2p_snapshot_bank_arbiter #(
        .ENGINES(ENGINES), .NUM_BANKS(NUM_BANKS), .ROW_W(ROW_W),
        .ENGINE_W(ENGINE_W)
    ) banks (
        .lane_valid(engine_valid),
        .lane_need0(engine_need0), .lane_need1(engine_need1),
        .lane_need2(engine_need2), .lane_need3(engine_need3),
        .lane_row0(engine_row0), .lane_row1(engine_row1),
        .lane_row2(engine_row2), .lane_row3(engine_row3),
        .lane_bank0(engine_bank0), .lane_bank1(engine_bank1),
        .lane_bank2(engine_bank2), .lane_bank3(engine_bank3),
        .bank_ready(bank_req_ready),
        .bank_req_valid(bank_req_valid), .bank_req_owner(bank_req_owner),
        .bank_req_row(bank_req_row),
        .lane_grant0(engine_grant0), .lane_grant1(engine_grant1),
        .lane_grant2(engine_grant2), .lane_grant3(engine_grant3)
    );

    c2p_snapshot_response_fabric #(.ENGINES(ENGINES), .NUM_BANKS(NUM_BANKS)) copy0_rsp (
        .clk(clk), .reset(reset),
        .bank_rsp_valid(bank_rsp_valid[0*NUM_BANKS +: NUM_BANKS]),
        .bank_rsp_ready(bank_rsp_ready[0*NUM_BANKS +: NUM_BANKS]),
        .bank_rsp_owner(bank_rsp_owner[0*NUM_BANKS*ENGINE_W +: NUM_BANKS*ENGINE_W]),
        .bank_rsp_data(bank_rsp_data[0*NUM_BANKS*64 +: NUM_BANKS*64]),
        .out_valid(copy0_valid), .out_ready(copy0_ready), .out_data(copy0_data)
    );
    c2p_snapshot_response_fabric #(.ENGINES(ENGINES), .NUM_BANKS(NUM_BANKS)) copy1_rsp (
        .clk(clk), .reset(reset),
        .bank_rsp_valid(bank_rsp_valid[1*NUM_BANKS +: NUM_BANKS]),
        .bank_rsp_ready(bank_rsp_ready[1*NUM_BANKS +: NUM_BANKS]),
        .bank_rsp_owner(bank_rsp_owner[1*NUM_BANKS*ENGINE_W +: NUM_BANKS*ENGINE_W]),
        .bank_rsp_data(bank_rsp_data[1*NUM_BANKS*64 +: NUM_BANKS*64]),
        .out_valid(copy1_valid), .out_ready(copy1_ready), .out_data(copy1_data)
    );
    c2p_snapshot_response_fabric #(.ENGINES(ENGINES), .NUM_BANKS(NUM_BANKS)) copy2_rsp (
        .clk(clk), .reset(reset),
        .bank_rsp_valid(bank_rsp_valid[2*NUM_BANKS +: NUM_BANKS]),
        .bank_rsp_ready(bank_rsp_ready[2*NUM_BANKS +: NUM_BANKS]),
        .bank_rsp_owner(bank_rsp_owner[2*NUM_BANKS*ENGINE_W +: NUM_BANKS*ENGINE_W]),
        .bank_rsp_data(bank_rsp_data[2*NUM_BANKS*64 +: NUM_BANKS*64]),
        .out_valid(copy2_valid), .out_ready(copy2_ready), .out_data(copy2_data)
    );
    c2p_snapshot_response_fabric #(.ENGINES(ENGINES), .NUM_BANKS(NUM_BANKS)) copy3_rsp (
        .clk(clk), .reset(reset),
        .bank_rsp_valid(bank_rsp_valid[3*NUM_BANKS +: NUM_BANKS]),
        .bank_rsp_ready(bank_rsp_ready[3*NUM_BANKS +: NUM_BANKS]),
        .bank_rsp_owner(bank_rsp_owner[3*NUM_BANKS*ENGINE_W +: NUM_BANKS*ENGINE_W]),
        .bank_rsp_data(bank_rsp_data[3*NUM_BANKS*64 +: NUM_BANKS*64]),
        .out_valid(copy3_valid), .out_ready(copy3_ready), .out_data(copy3_data)
    );

    c2p_snapshot_response_joiner #(.ENGINES(ENGINES), .DATA_W(64)) responses (
        .copy0_valid(copy0_valid), .copy0_ready(copy0_ready), .copy0_data(copy0_data),
        .copy1_valid(copy1_valid), .copy1_ready(copy1_ready), .copy1_data(copy1_data),
        .copy2_valid(copy2_valid), .copy2_ready(copy2_ready), .copy2_data(copy2_data),
        .copy3_valid(copy3_valid), .copy3_ready(copy3_ready), .copy3_data(copy3_data),
        .clk(clk), .reset(reset), .out_valid(out_valid), .out_ready(out_ready),
        .out_data0(out_data0), .out_data1(out_data1),
        .out_data2(out_data2), .out_data3(out_data3)
    );

    always @(posedge clk) begin
        if (reset) begin
            for (engine_i = 0; engine_i < ENGINES; engine_i = engine_i + 1)
                engine_sent[engine_i] <= 4'b0;
        end else begin
            for (engine_i = 0; engine_i < ENGINES; engine_i = engine_i + 1) begin
                if (!engine_valid[engine_i] || engine_ready[engine_i])
                    engine_sent[engine_i] <= 4'b0;
                else
                    engine_sent[engine_i] <= engine_sent[engine_i] |
                                             {engine_grant3[engine_i], engine_grant2[engine_i],
                                              engine_grant1[engine_i], engine_grant0[engine_i]};
            end
        end
    end
endmodule
