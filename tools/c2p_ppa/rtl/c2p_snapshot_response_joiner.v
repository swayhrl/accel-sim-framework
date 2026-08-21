// Owner-tagged four-copy Snapshot response joiner.
//
// Each physical copy may return an engine's row in a different cycle. This
// module retains the four independently timed responses and exposes exactly
// one completed Snapshot result per engine. The frontend keeps the BF-engine
// slot occupied until that result is consumed, so an ENGINE_W owner is never
// reused while a prior transaction can still return.
module c2p_snapshot_response_joiner #(
    parameter integer ENGINES = 128,
    parameter integer NUM_BANKS = 64,
    parameter integer DATA_W = 64,
    parameter integer ENGINE_W = (ENGINES <= 1) ? 1 : $clog2(ENGINES)
) (
    input  wire                                  clk,
    input  wire                                  reset,
    input  wire [4*NUM_BANKS-1:0]                bank_rsp_valid,
    input  wire [4*NUM_BANKS*ENGINE_W-1:0]       bank_rsp_owner,
    input  wire [4*NUM_BANKS*DATA_W-1:0]         bank_rsp_data,

    output reg  [ENGINES-1:0]                    out_valid,
    input  wire [ENGINES-1:0]                    out_ready,
    output wire [ENGINES*DATA_W-1:0]             out_data0,
    output wire [ENGINES*DATA_W-1:0]             out_data1,
    output wire [ENGINES*DATA_W-1:0]             out_data2,
    output wire [ENGINES*DATA_W-1:0]             out_data3
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
    integer bank_i;

    generate
        genvar engine_g;
        for (engine_g = 0; engine_g < ENGINES; engine_g = engine_g + 1) begin : g_out
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
            end

            for (bank_i = 0; bank_i < NUM_BANKS; bank_i = bank_i + 1) begin
                if (bank_rsp_valid[bank_i]) begin
                    got0[bank_rsp_owner[bank_i*ENGINE_W +: ENGINE_W]] <= 1'b1;
                    data0_r[bank_rsp_owner[bank_i*ENGINE_W +: ENGINE_W]] <=
                        bank_rsp_data[bank_i*DATA_W +: DATA_W];
                end
                if (bank_rsp_valid[NUM_BANKS + bank_i]) begin
                    got1[bank_rsp_owner[(NUM_BANKS + bank_i)*ENGINE_W +: ENGINE_W]] <= 1'b1;
                    data1_r[bank_rsp_owner[(NUM_BANKS + bank_i)*ENGINE_W +: ENGINE_W]] <=
                        bank_rsp_data[(NUM_BANKS + bank_i)*DATA_W +: DATA_W];
                end
                if (bank_rsp_valid[2*NUM_BANKS + bank_i]) begin
                    got2[bank_rsp_owner[(2*NUM_BANKS + bank_i)*ENGINE_W +: ENGINE_W]] <= 1'b1;
                    data2_r[bank_rsp_owner[(2*NUM_BANKS + bank_i)*ENGINE_W +: ENGINE_W]] <=
                        bank_rsp_data[(2*NUM_BANKS + bank_i)*DATA_W +: DATA_W];
                end
                if (bank_rsp_valid[3*NUM_BANKS + bank_i]) begin
                    got3[bank_rsp_owner[(3*NUM_BANKS + bank_i)*ENGINE_W +: ENGINE_W]] <= 1'b1;
                    data3_r[bank_rsp_owner[(3*NUM_BANKS + bank_i)*ENGINE_W +: ENGINE_W]] <=
                        bank_rsp_data[(3*NUM_BANKS + bank_i)*DATA_W +: DATA_W];
                end
            end
        end
    end
endmodule
