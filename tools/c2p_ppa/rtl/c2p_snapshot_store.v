// Four-copy C2P Snapshot storage boundary.
//
// The functional branch keeps independent arrays so a query reads its tag-mask
// and three Bloom rows concurrently.  Selecting USE_SRAM_MACRO replaces those
// arrays with four technology-owned 1R1W macro wrappers.  The external macro
// module is deliberately not supplied here: its Liberty/LEF/GDS contract is
// technology-specific and documented in openroad/snapshot_macro_manifest.md.
module c2p_snapshot_store #(
    parameter integer NUM_SMS = 64,
    parameter integer TOTAL_ROWS = 5120,
    parameter integer ROW_W = 13,
    parameter integer USE_SRAM_MACRO = 0
) (
    input  wire                 clk,
    input  wire                 reset,

    input  wire                 clear_valid,
    output wire                 clear_ready,
    input  wire [ROW_W-1:0]     clear_row,

    input  wire                 write_valid,
    output wire                 write_ready,
    input  wire [ROW_W-1:0]     write_row0,
    input  wire [ROW_W-1:0]     write_row1,
    input  wire [ROW_W-1:0]     write_row2,
    input  wire [ROW_W-1:0]     write_row3,
    input  wire [NUM_SMS-1:0]   write_mask,

    input  wire                 query_valid,
    output wire                 query_ready,
    input  wire [ROW_W-1:0]     query_row0,
    input  wire [ROW_W-1:0]     query_row1,
    input  wire [ROW_W-1:0]     query_row2,
    input  wire [ROW_W-1:0]     query_row3,
    output reg                  query_rsp_valid,
    input  wire                 query_rsp_ready,
    output reg [NUM_SMS-1:0]    query_rsp_data0,
    output reg [NUM_SMS-1:0]    query_rsp_data1,
    output reg [NUM_SMS-1:0]    query_rsp_data2,
    output reg [NUM_SMS-1:0]    query_rsp_data3
);

    assign clear_ready = 1'b1;
    // Clear owns the one write port during reset/rebuild.  C2P's update
    // producer must retain valid until this boundary accepts the bit-set.
    assign write_ready = !clear_valid;
    assign query_ready = !query_rsp_valid || query_rsp_ready;

    generate
        if (USE_SRAM_MACRO) begin : g_macro
            wire [NUM_SMS-1:0] macro_read0;
            wire [NUM_SMS-1:0] macro_read1;
            wire [NUM_SMS-1:0] macro_read2;
            wire [NUM_SMS-1:0] macro_read3;
            wire macro_write = clear_valid || write_valid;
            wire [NUM_SMS-1:0] macro_wdata =
                clear_valid ? {NUM_SMS{1'b0}} : write_mask;
            wire [NUM_SMS-1:0] macro_wmask =
                clear_valid ? {NUM_SMS{1'b1}} : write_mask;

            // c2p_snapshot_sram_1r1w is supplied by the selected macro
            // integration.  It has one registered read port and one masked
            // write port; all four instances receive a broadcast update.
            c2p_snapshot_sram_1r1w #(.ADDR_W(ROW_W), .DATA_W(NUM_SMS)) copy0 (
                .clk(clk), .rd_en(query_valid), .rd_addr(query_row0),
                .rd_data(macro_read0), .wr_en(macro_write),
                .wr_addr(clear_valid ? clear_row : write_row0),
                .wr_data(macro_wdata), .wr_mask(macro_wmask));
            c2p_snapshot_sram_1r1w #(.ADDR_W(ROW_W), .DATA_W(NUM_SMS)) copy1 (
                .clk(clk), .rd_en(query_valid), .rd_addr(query_row1),
                .rd_data(macro_read1), .wr_en(macro_write),
                .wr_addr(clear_valid ? clear_row : write_row1),
                .wr_data(macro_wdata), .wr_mask(macro_wmask));
            c2p_snapshot_sram_1r1w #(.ADDR_W(ROW_W), .DATA_W(NUM_SMS)) copy2 (
                .clk(clk), .rd_en(query_valid), .rd_addr(query_row2),
                .rd_data(macro_read2), .wr_en(macro_write),
                .wr_addr(clear_valid ? clear_row : write_row2),
                .wr_data(macro_wdata), .wr_mask(macro_wmask));
            c2p_snapshot_sram_1r1w #(.ADDR_W(ROW_W), .DATA_W(NUM_SMS)) copy3 (
                .clk(clk), .rd_en(query_valid), .rd_addr(query_row3),
                .rd_data(macro_read3), .wr_en(macro_write),
                .wr_addr(clear_valid ? clear_row : write_row3),
                .wr_data(macro_wdata), .wr_mask(macro_wmask));

            // The macro read data is registered by the SRAM on the accepted
            // query edge.  Keep it combinational at this wrapper boundary so
            // query_rsp_valid and the four rows become visible together in
            // the following cycle, preserving the matrix's two-cycle API.
            always @* begin
                query_rsp_data0 = macro_read0;
                query_rsp_data1 = macro_read1;
                query_rsp_data2 = macro_read2;
                query_rsp_data3 = macro_read3;
            end
            always @(posedge clk) begin
                if (reset) begin
                    query_rsp_valid <= 1'b0;
                end else begin
                    if (query_rsp_valid && query_rsp_ready)
                        query_rsp_valid <= 1'b0;
                    if (query_valid && query_ready) begin
                        query_rsp_valid <= 1'b1;
                        query_rsp_data0 <= macro_read0;
                        query_rsp_data1 <= macro_read1;
                        query_rsp_data2 <= macro_read2;
                        query_rsp_data3 <= macro_read3;
                    end
                end
            end
        end else begin : g_reference
            reg [NUM_SMS-1:0] copy0 [0:TOTAL_ROWS-1];
            reg [NUM_SMS-1:0] copy1 [0:TOTAL_ROWS-1];
            reg [NUM_SMS-1:0] copy2 [0:TOTAL_ROWS-1];
            reg [NUM_SMS-1:0] copy3 [0:TOTAL_ROWS-1];

            always @(posedge clk) begin
                if (reset) begin
                    query_rsp_valid <= 1'b0;
                    query_rsp_data0 <= {NUM_SMS{1'b0}};
                    query_rsp_data1 <= {NUM_SMS{1'b0}};
                    query_rsp_data2 <= {NUM_SMS{1'b0}};
                    query_rsp_data3 <= {NUM_SMS{1'b0}};
                end else begin
                    if (clear_valid) begin
                        copy0[clear_row] <= {NUM_SMS{1'b0}};
                        copy1[clear_row] <= {NUM_SMS{1'b0}};
                        copy2[clear_row] <= {NUM_SMS{1'b0}};
                        copy3[clear_row] <= {NUM_SMS{1'b0}};
                    end else if (write_valid && write_ready) begin
                        copy0[write_row0] <= copy0[write_row0] | write_mask;
                        copy1[write_row1] <= copy1[write_row1] | write_mask;
                        copy2[write_row2] <= copy2[write_row2] | write_mask;
                        copy3[write_row3] <= copy3[write_row3] | write_mask;
                    end

                    if (query_rsp_valid && query_rsp_ready)
                        query_rsp_valid <= 1'b0;
                    if (query_valid && query_ready) begin
                        query_rsp_valid <= 1'b1;
                        query_rsp_data0 <= copy0[query_row0];
                        query_rsp_data1 <= copy1[query_row1];
                        query_rsp_data2 <= copy2[query_row2];
                        query_rsp_data3 <= copy3[query_row3];
                    end
                end
            end
        end
    endgenerate
endmodule
