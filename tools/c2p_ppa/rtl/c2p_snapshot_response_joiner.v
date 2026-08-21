// Four-copy Snapshot response joiner after per-copy packet routing.
//
// Each copy fabric presents at most one reply for an engine in a cycle. This
// leaves one small data register and valid bit per copy/engine; the expensive
// 64-bank-to-128-engine routing lives in registered self-routing fabrics.
module c2p_snapshot_response_joiner #(
    parameter integer ENGINES = 128,
    parameter integer DATA_W = 64
) (
    input  wire [ENGINES-1:0]              copy0_valid,
    output wire [ENGINES-1:0]              copy0_ready,
    input  wire [ENGINES*DATA_W-1:0]       copy0_data,
    input  wire [ENGINES-1:0]              copy1_valid,
    output wire [ENGINES-1:0]              copy1_ready,
    input  wire [ENGINES*DATA_W-1:0]       copy1_data,
    input  wire [ENGINES-1:0]              copy2_valid,
    output wire [ENGINES-1:0]              copy2_ready,
    input  wire [ENGINES*DATA_W-1:0]       copy2_data,
    input  wire [ENGINES-1:0]              copy3_valid,
    output wire [ENGINES-1:0]              copy3_ready,
    input  wire [ENGINES*DATA_W-1:0]       copy3_data,

    input  wire                            clk,
    input  wire                            reset,
    output reg  [ENGINES-1:0]              out_valid,
    input  wire [ENGINES-1:0]              out_ready,
    output wire [ENGINES*DATA_W-1:0]       out_data0,
    output wire [ENGINES*DATA_W-1:0]       out_data1,
    output wire [ENGINES*DATA_W-1:0]       out_data2,
    output wire [ENGINES*DATA_W-1:0]       out_data3
);

    reg [ENGINES-1:0] got0;
    reg [ENGINES-1:0] got1;
    reg [ENGINES-1:0] got2;
    reg [ENGINES-1:0] got3;
    reg [DATA_W-1:0] data0_r [0:ENGINES-1];
    reg [DATA_W-1:0] data1_r [0:ENGINES-1];
    reg [DATA_W-1:0] data2_r [0:ENGINES-1];
    reg [DATA_W-1:0] data3_r [0:ENGINES-1];
    integer engine_i;

    generate
        genvar engine_g;
        for (engine_g = 0; engine_g < ENGINES; engine_g = engine_g + 1) begin : g_out
            assign copy0_ready[engine_g] = !got0[engine_g] && !out_valid[engine_g];
            assign copy1_ready[engine_g] = !got1[engine_g] && !out_valid[engine_g];
            assign copy2_ready[engine_g] = !got2[engine_g] && !out_valid[engine_g];
            assign copy3_ready[engine_g] = !got3[engine_g] && !out_valid[engine_g];
            assign out_data0[engine_g*DATA_W +: DATA_W] = data0_r[engine_g];
            assign out_data1[engine_g*DATA_W +: DATA_W] = data1_r[engine_g];
            assign out_data2[engine_g*DATA_W +: DATA_W] = data2_r[engine_g];
            assign out_data3[engine_g*DATA_W +: DATA_W] = data3_r[engine_g];
        end
    endgenerate

    always @(posedge clk) begin
        if (reset) begin
            out_valid <= {ENGINES{1'b0}};
            got0 <= {ENGINES{1'b0}};
            got1 <= {ENGINES{1'b0}};
            got2 <= {ENGINES{1'b0}};
            got3 <= {ENGINES{1'b0}};
            for (engine_i = 0; engine_i < ENGINES; engine_i = engine_i + 1) begin
                data0_r[engine_i] <= {DATA_W{1'b0}};
                data1_r[engine_i] <= {DATA_W{1'b0}};
                data2_r[engine_i] <= {DATA_W{1'b0}};
                data3_r[engine_i] <= {DATA_W{1'b0}};
            end
        end else begin
            for (engine_i = 0; engine_i < ENGINES; engine_i = engine_i + 1) begin
                if (out_valid[engine_i] && out_ready[engine_i]) begin
                    out_valid[engine_i] <= 1'b0;
                    got0[engine_i] <= 1'b0;
                    got1[engine_i] <= 1'b0;
                    got2[engine_i] <= 1'b0;
                    got3[engine_i] <= 1'b0;
                end else if (got0[engine_i] && got1[engine_i] &&
                             got2[engine_i] && got3[engine_i]) begin
                    out_valid[engine_i] <= 1'b1;
                end
                if (copy0_valid[engine_i] && copy0_ready[engine_i]) begin
                    got0[engine_i] <= 1'b1;
                    data0_r[engine_i] <= copy0_data[engine_i*DATA_W +: DATA_W];
                end
                if (copy1_valid[engine_i] && copy1_ready[engine_i]) begin
                    got1[engine_i] <= 1'b1;
                    data1_r[engine_i] <= copy1_data[engine_i*DATA_W +: DATA_W];
                end
                if (copy2_valid[engine_i] && copy2_ready[engine_i]) begin
                    got2[engine_i] <= 1'b1;
                    data2_r[engine_i] <= copy2_data[engine_i*DATA_W +: DATA_W];
                end
                if (copy3_valid[engine_i] && copy3_ready[engine_i]) begin
                    got3[engine_i] <= 1'b1;
                    data3_r[engine_i] <= copy3_data[engine_i*DATA_W +: DATA_W];
                end
            end
        end
    end
endmodule
