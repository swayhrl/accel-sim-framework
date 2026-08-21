// Replicated C2P BF-engine front end.
//
// Each engine is independently elastic and produces the tag-mask plus three
// Bloom bank/row addresses for one Snapshot transaction. The flattened ports
// keep this Verilog-2005 compatible while allowing the paper's 128 engines to
// be instantiated by setting ENGINES=128.
module c2p_bf_engine_array #(
    parameter integer ENGINES = 128,
    parameter integer TAG_W = 64,
    parameter integer ROW_W = 13,
    parameter integer AUX_W = 1
) (
    input  wire                         clk,
    input  wire                         reset,
    input  wire [ENGINES-1:0]           in_valid,
    output wire [ENGINES-1:0]           in_ready,
    input  wire [ENGINES*TAG_W-1:0]     in_tag,
    input  wire [ENGINES*AUX_W-1:0]     in_aux,
    output wire [ENGINES-1:0]           out_valid,
    input  wire [ENGINES-1:0]           out_ready,
    output wire [ENGINES*ROW_W-1:0]     out_row0,
    output wire [ENGINES*ROW_W-1:0]     out_row1,
    output wire [ENGINES*ROW_W-1:0]     out_row2,
    output wire [ENGINES*ROW_W-1:0]     out_row3,
    output wire [ENGINES*6-1:0]         out_bank0,
    output wire [ENGINES*6-1:0]         out_bank1,
    output wire [ENGINES*6-1:0]         out_bank2,
    output wire [ENGINES*6-1:0]         out_bank3,
    output wire [ENGINES*AUX_W-1:0]     out_aux
);

    genvar engine_i;
    generate
        for (engine_i = 0; engine_i < ENGINES; engine_i = engine_i + 1) begin : g_engine
            c2p_bf_engine #(
                .TAG_W(TAG_W), .ROW_W(ROW_W), .AUX_W(AUX_W)
            ) engine (
                .clk(clk), .reset(reset),
                .in_valid(in_valid[engine_i]),
                .in_ready(in_ready[engine_i]),
                .in_tag(in_tag[engine_i*TAG_W +: TAG_W]),
                .in_aux(in_aux[engine_i*AUX_W +: AUX_W]),
                .out_valid(out_valid[engine_i]),
                .out_ready(out_ready[engine_i]),
                .out_row0(out_row0[engine_i*ROW_W +: ROW_W]),
                .out_row1(out_row1[engine_i*ROW_W +: ROW_W]),
                .out_row2(out_row2[engine_i*ROW_W +: ROW_W]),
                .out_row3(out_row3[engine_i*ROW_W +: ROW_W]),
                .out_bank0(out_bank0[engine_i*6 +: 6]),
                .out_bank1(out_bank1[engine_i*6 +: 6]),
                .out_bank2(out_bank2[engine_i*6 +: 6]),
                .out_bank3(out_bank3[engine_i*6 +: 6]),
                .out_aux(out_aux[engine_i*AUX_W +: AUX_W])
            );
        end
    endgenerate
endmodule
