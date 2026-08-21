// Logical Snapshot Matrix used by the C2P read-side query engine.
//
// The default parameters match the simulator contract: 64 banks, each with
// 64 Bloom rows and 16 tag-mask rows, and one candidate bit per SM.  A query
// reads the tag-mask row plus three double-hash Bloom rows and returns their
// bitwise intersection after READ_LATENCY cycles.  Updates only set bits; an
// exact remote L1 probe is therefore still required for correctness.
//
// This is the functional/reference storage implementation.  The physical
// macro adapter deliberately has a separate boundary: a real 1R1W SRAM needs
// a technology-specific masked-write implementation and cannot be inferred
// honestly from this behavioral array.
module c2p_snapshot_matrix #(
    parameter integer NUM_SMS = 64,
    parameter integer SID_W = 6,
    parameter integer TAG_W = 64,
    parameter integer NUM_BANKS = 64,
    parameter integer BF_ROWS_PER_BANK = 64,
    parameter integer TAG_MASK_ROWS_PER_BANK = 16,
    parameter integer BF_HASHES = 3,
    parameter integer READ_LATENCY = 2
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
    localparam integer DELAY_W = (READ_LATENCY <= 1) ? 1 : $clog2(READ_LATENCY);

    reg [NUM_SMS-1:0] snapshot [0:TOTAL_ROWS-1];
    reg [NUM_SMS-1:0] row_data0;
    reg [NUM_SMS-1:0] row_data1;
    reg [NUM_SMS-1:0] row_data2;
    reg [NUM_SMS-1:0] row_data3;
    reg               query_pending;
    reg [DELAY_W-1:0] query_delay;
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

    // The reference array can accept one fill/rebuild update every cycle.
    // A physical macro adapter may apply backpressure while it serializes
    // masked writes; its ready signal becomes this port's ready in that flow.
    assign update_ready = !clearing;
    assign query_ready = !clearing && !query_pending &&
                         (!query_rsp_valid || query_rsp_ready);

    always @(posedge clk) begin
        if (reset) begin
            row_data0 <= {NUM_SMS{1'b0}};
            row_data1 <= {NUM_SMS{1'b0}};
            row_data2 <= {NUM_SMS{1'b0}};
            row_data3 <= {NUM_SMS{1'b0}};
            query_pending <= 1'b0;
            query_delay <= {DELAY_W{1'b0}};
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
                snapshot[clear_row] <= {NUM_SMS{1'b0}};
                if (clear_row == TOTAL_ROWS - 1)
                    clearing <= 1'b0;
                else
                    clear_row <= clear_row + 1'b1;
            end
            if (query_rsp_valid && query_rsp_ready)
                query_rsp_valid <= 1'b0;

            if (!clearing && update_valid && update_ready) begin
                snapshot[update_row0] <= snapshot[update_row0] | update_mask;
                snapshot[update_row1] <= snapshot[update_row1] | update_mask;
                snapshot[update_row2] <= snapshot[update_row2] | update_mask;
                snapshot[update_row3] <= snapshot[update_row3] | update_mask;
            end

            if (!clearing && query_valid && query_ready) begin
                // Sample all rows together.  The four-copy physical design
                // supplies these four reads in parallel; this reference keeps
                // the same externally visible latency.
                row_data0 <= snapshot[query_row0];
                row_data1 <= snapshot[query_row1];
                row_data2 <= snapshot[query_row2];
                row_data3 <= snapshot[query_row3];
                query_pending <= 1'b1;
                query_delay <= READ_LATENCY - 1;
            end

            if (query_pending) begin
                if (query_delay == 0) begin
                    query_rsp_candidates <= row_data0 & row_data1 &
                                            row_data2 & row_data3;
                    query_rsp_valid <= 1'b1;
                    query_pending <= 1'b0;
                end else begin
                    query_delay <= query_delay - 1'b1;
                end
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
    end
endmodule
