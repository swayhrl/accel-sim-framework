// Logical Snapshot Matrix used by the C2P read-side query engine.
//
// The default parameters match the simulator contract: 64 banks, each with
// 64 Bloom rows and 16 tag-mask rows, and one candidate bit per SM.  A query
// reads the tag-mask row plus three double-hash Bloom rows and returns their
// bitwise intersection after READ_LATENCY cycles.  Updates only set bits; an
// exact remote L1 probe is therefore still required for correctness.
//
// Storage is delegated to c2p_snapshot_store.  Its default is a functional
// four-copy reference array; USE_SRAM_MACRO selects four explicit masked-write
// macro wrappers without changing the matrix protocol.
module c2p_snapshot_matrix #(
    parameter integer NUM_SMS = 64,
    parameter integer SID_W = 6,
    parameter integer TAG_W = 64,
    parameter integer NUM_BANKS = 64,
    parameter integer BF_ROWS_PER_BANK = 64,
    parameter integer TAG_MASK_ROWS_PER_BANK = 16,
    parameter integer BF_HASHES = 3,
    parameter integer READ_LATENCY = 2,
    parameter integer USE_SRAM_MACRO = 0
) (
    input  wire                 clk,
    input  wire                 reset,

    input  wire                 update_valid,
    output wire                 update_ready,
    input  wire [SID_W-1:0]     update_sid,
    input  wire [TAG_W-1:0]     update_tag,

    input  wire                 query_valid,
    output wire                 query_ready,
    input  wire [TAG_W-1:0]     query_tag,
    output reg                  query_rsp_valid,
    input  wire                 query_rsp_ready,
    output reg  [NUM_SMS-1:0]   query_rsp_candidates
);

    localparam integer TOTAL_BF_ROWS = NUM_BANKS * BF_ROWS_PER_BANK;
    localparam integer TOTAL_ROWS =
        NUM_BANKS * (BF_ROWS_PER_BANK + TAG_MASK_ROWS_PER_BANK);
    localparam integer ROW_W = $clog2(TOTAL_ROWS);
    reg               query_waiting;
    reg               clearing;
    reg [ROW_W-1:0]   clear_row;

    function [31:0] fold_hash;
        input [63:0] value;
        input [31:0] salt;
        reg [63:0] x;
        begin
            x = value ^ ({32'b0, salt} * 64'h9e3779b97f4a7c15);
            x = x ^ (x >> 30);
            x = x * 64'hbf58476d1ce4e5b9;
            x = x ^ (x >> 27);
            x = x * 64'h94d049bb133111eb;
            x = x ^ (x >> 31);
            fold_hash = x[31:0] ^ x[63:32];
        end
    endfunction

    function [9:0] reverse_low10;
        input [TAG_W-1:0] tag;
        integer bit_i;
        begin
            for (bit_i = 0; bit_i < 10; bit_i = bit_i + 1)
                reverse_low10[9-bit_i] = tag[bit_i];
        end
    endfunction

    function [ROW_W-1:0] query_row;
        input [TAG_W-1:0] tag;
        input integer row_sel;
        reg [9:0] reversed;
        reg [31:0] h1;
        reg [31:0] h2;
        integer index;
        integer bank;
        integer offset;
        begin
            reversed = reverse_low10(tag);
            if (row_sel == 0) begin
                bank = (reversed / TAG_MASK_ROWS_PER_BANK) % NUM_BANKS;
                offset = BF_ROWS_PER_BANK +
                         (reversed % TAG_MASK_ROWS_PER_BANK);
            end else begin
                h1 = fold_hash(tag, 32'h243f6a88);
                h2 = fold_hash(tag, 32'h85a308d3);
                index = (row_sel * h1 + h2) & (TOTAL_BF_ROWS - 1);
                bank = index / BF_ROWS_PER_BANK;
                offset = index % BF_ROWS_PER_BANK;
            end
            query_row = bank * (BF_ROWS_PER_BANK + TAG_MASK_ROWS_PER_BANK) +
                        offset;
        end
    endfunction

    wire [ROW_W-1:0] update_row0 = query_row(update_tag, 0);
    wire [ROW_W-1:0] update_row1 = query_row(update_tag, 1);
    wire [ROW_W-1:0] update_row2 = query_row(update_tag, 2);
    wire [ROW_W-1:0] update_row3 = query_row(update_tag, 3);
    wire [ROW_W-1:0] query_row0 = query_row(query_tag, 0);
    wire [ROW_W-1:0] query_row1 = query_row(query_tag, 1);
    wire [ROW_W-1:0] query_row2 = query_row(query_tag, 2);
    wire [ROW_W-1:0] query_row3 = query_row(query_tag, 3);
    wire [NUM_SMS-1:0] update_mask = {{(NUM_SMS-1){1'b0}}, 1'b1} << update_sid;
    wire store_clear_valid = clearing;
    wire store_clear_ready;
    wire store_update_ready;
    wire store_query_ready;
    wire store_query_valid = query_valid && query_ready;
    wire store_query_rsp_valid;
    wire store_query_rsp_ready = query_waiting &&
                                 (!query_rsp_valid || query_rsp_ready);
    wire [NUM_SMS-1:0] store_query_rsp_data0;
    wire [NUM_SMS-1:0] store_query_rsp_data1;
    wire [NUM_SMS-1:0] store_query_rsp_data2;
    wire [NUM_SMS-1:0] store_query_rsp_data3;

    // The store keeps each of the four encoded rows in an independent read
    // replica.  Both branches use the same clear/update/query handshakes.
    c2p_snapshot_store #(
        .NUM_SMS(NUM_SMS), .TOTAL_ROWS(TOTAL_ROWS), .ROW_W(ROW_W),
        .USE_SRAM_MACRO(USE_SRAM_MACRO)
    ) store (
        .clk(clk), .reset(reset),
        .clear_valid(store_clear_valid), .clear_ready(store_clear_ready),
        .clear_row(clear_row),
        .write_valid(update_valid && update_ready),
        .write_ready(store_update_ready),
        .write_row0(update_row0), .write_row1(update_row1),
        .write_row2(update_row2), .write_row3(update_row3),
        .write_mask(update_mask),
        .query_valid(store_query_valid), .query_ready(store_query_ready),
        .query_row0(query_row0), .query_row1(query_row1),
        .query_row2(query_row2), .query_row3(query_row3),
        .query_rsp_valid(store_query_rsp_valid),
        .query_rsp_ready(store_query_rsp_ready),
        .query_rsp_data0(store_query_rsp_data0),
        .query_rsp_data1(store_query_rsp_data1),
        .query_rsp_data2(store_query_rsp_data2),
        .query_rsp_data3(store_query_rsp_data3)
    );

    assign update_ready = !clearing && store_update_ready;
    assign query_ready = !clearing && !query_waiting &&
                         (!query_rsp_valid || query_rsp_ready) &&
                         store_query_ready;

    always @(posedge clk) begin
        if (reset) begin
            query_waiting <= 1'b0;
            query_rsp_valid <= 1'b0;
            query_rsp_candidates <= {NUM_SMS{1'b0}};
            clearing <= 1'b1;
            clear_row <= {ROW_W{1'b0}};
        end else begin
            // A row-at-a-time reset maps to a real masked-write SRAM clear;
            // it avoids inferring thousands of resettable flip-flops for the
            // 40 KiB logical matrix.  Miss/update admission stays blocked
            // until the matrix is known clear.
            if (clearing) begin
                if (clear_row == TOTAL_ROWS - 1 && store_clear_ready)
                    clearing <= 1'b0;
                else if (store_clear_ready)
                    clear_row <= clear_row + 1'b1;
            end
            if (query_rsp_valid && query_rsp_ready)
                query_rsp_valid <= 1'b0;

            if (store_query_valid)
                query_waiting <= 1'b1;

            if (store_query_rsp_valid && store_query_rsp_ready) begin
                // A store read is one cycle and this response register is the
                // second.  This preserves the C2P two-cycle Snapshot contract.
                query_rsp_candidates <= store_query_rsp_data0 &
                                        store_query_rsp_data1 &
                                        store_query_rsp_data2 &
                                        store_query_rsp_data3;
                query_rsp_valid <= 1'b1;
                query_waiting <= 1'b0;
            end
        end
    end

    initial begin
        if (NUM_BANKS * TAG_MASK_ROWS_PER_BANK != 1024)
            $error("C2P tag-mask geometry must cover 1024 reverse-tag rows");
        if ((TOTAL_BF_ROWS & (TOTAL_BF_ROWS - 1)) != 0)
            $error("C2P Bloom row count must be a power of two");
        if (BF_HASHES != 3)
            $error("This RTL matches the C2P default of three Bloom hashes");
        if (READ_LATENCY != 2)
            $error("C2P macro adapter currently implements a two-cycle read");
    end
endmodule
