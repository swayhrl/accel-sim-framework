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
// macro wrappers without changing the matrix protocol. Query and update
// address generation both pass through an explicit elastic BF engine, so no
// request-side hash cone feeds the SRAM address path.
module c2p_snapshot_matrix #(
    parameter integer NUM_SMS = 64,
    parameter integer SID_W = 6,
    parameter integer TAG_W = 64,
    parameter integer NUM_BANKS = 64,
    parameter integer BF_ROWS_PER_BANK = 64,
    parameter integer TAG_MASK_ROWS_PER_BANK = 16,
    parameter integer BF_HASHES = 3,
    parameter integer READ_LATENCY = 2,
    parameter integer USE_SRAM_MACRO = 0,
    parameter integer USE_ASAP7_SRAM = 0
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

    wire [NUM_SMS-1:0] update_mask = {{(NUM_SMS-1){1'b0}}, 1'b1} << update_sid;
    wire store_clear_valid = clearing;
    wire store_clear_ready;
    wire store_update_ready;
    wire store_query_ready;
    wire update_bf_in_valid = update_valid && update_ready;
    wire update_bf_in_ready;
    wire update_bf_out_valid;
    wire update_bf_out_ready = store_update_ready;
    wire [ROW_W-1:0] update_row0;
    wire [ROW_W-1:0] update_row1;
    wire [ROW_W-1:0] update_row2;
    wire [ROW_W-1:0] update_row3;
    wire [NUM_SMS-1:0] update_bf_mask;
    wire query_bf_in_valid = query_valid && query_ready;
    wire query_bf_in_ready;
    wire query_bf_out_valid;
    wire query_bf_out_ready = store_query_ready;
    wire [ROW_W-1:0] query_row0;
    wire [ROW_W-1:0] query_row1;
    wire [ROW_W-1:0] query_row2;
    wire [ROW_W-1:0] query_row3;
    wire query_bf_aux_unused;
    wire store_query_valid = query_bf_out_valid;
    wire store_query_rsp_valid;
    wire store_query_rsp_ready = query_waiting &&
                                 (!query_rsp_valid || query_rsp_ready);
    wire [NUM_SMS-1:0] store_query_rsp_data0;
    wire [NUM_SMS-1:0] store_query_rsp_data1;
    wire [NUM_SMS-1:0] store_query_rsp_data2;
    wire [NUM_SMS-1:0] store_query_rsp_data3;

    // The two engines are independent because a normal Snapshot store has a
    // read port and a write port.  A 1RW macro implementation may still
    // arbitrate their completed requests at the store boundary.
    c2p_bf_engine #(
        .TAG_W(TAG_W), .ROW_W(ROW_W), .NUM_BANKS(NUM_BANKS),
        .BF_ROWS_PER_BANK(BF_ROWS_PER_BANK),
        .TAG_MASK_ROWS_PER_BANK(TAG_MASK_ROWS_PER_BANK), .AUX_W(NUM_SMS)
    ) update_bf_engine (
        .clk(clk), .reset(reset),
        .in_valid(update_bf_in_valid), .in_ready(update_bf_in_ready),
        .in_tag(update_tag), .in_aux(update_mask),
        .out_valid(update_bf_out_valid), .out_ready(update_bf_out_ready),
        .out_row0(update_row0), .out_row1(update_row1),
        .out_row2(update_row2), .out_row3(update_row3),
        .out_aux(update_bf_mask)
    );

    c2p_bf_engine #(
        .TAG_W(TAG_W), .ROW_W(ROW_W), .NUM_BANKS(NUM_BANKS),
        .BF_ROWS_PER_BANK(BF_ROWS_PER_BANK),
        .TAG_MASK_ROWS_PER_BANK(TAG_MASK_ROWS_PER_BANK), .AUX_W(1)
    ) query_bf_engine (
        .clk(clk), .reset(reset),
        .in_valid(query_bf_in_valid), .in_ready(query_bf_in_ready),
        .in_tag(query_tag), .in_aux(1'b0),
        .out_valid(query_bf_out_valid), .out_ready(query_bf_out_ready),
        .out_row0(query_row0), .out_row1(query_row1),
        .out_row2(query_row2), .out_row3(query_row3),
        .out_aux(query_bf_aux_unused)
    );

    // The store keeps each of the four encoded rows in an independent read
    // replica.  Both branches use the same clear/update/query handshakes.
    generate
        if (USE_ASAP7_SRAM) begin : g_asap7_sram
            c2p_snapshot_store_asap7 #(
                .NUM_SMS(NUM_SMS), .TOTAL_ROWS(TOTAL_ROWS), .ROW_W(ROW_W)
            ) store (
                .clk(clk), .reset(reset),
                .clear_valid(store_clear_valid), .clear_ready(store_clear_ready),
                .clear_row(clear_row),
                .write_valid(update_bf_out_valid),
                .write_ready(store_update_ready),
                .write_row0(update_row0), .write_row1(update_row1),
                .write_row2(update_row2), .write_row3(update_row3),
                .write_mask(update_bf_mask),
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
        end else begin : g_default_store
            c2p_snapshot_store #(
                .NUM_SMS(NUM_SMS), .TOTAL_ROWS(TOTAL_ROWS), .ROW_W(ROW_W),
                .USE_SRAM_MACRO(USE_SRAM_MACRO)
            ) store (
                .clk(clk), .reset(reset),
                .clear_valid(store_clear_valid), .clear_ready(store_clear_ready),
                .clear_row(clear_row),
                .write_valid(update_bf_out_valid),
                .write_ready(store_update_ready),
                .write_row0(update_row0), .write_row1(update_row1),
                .write_row2(update_row2), .write_row3(update_row3),
                .write_mask(update_bf_mask),
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
        end
    endgenerate

    assign update_ready = !clearing && update_bf_in_ready;
    assign query_ready = !clearing && !query_waiting &&
                         (!query_rsp_valid || query_rsp_ready) &&
                         query_bf_in_ready;

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

            if (query_bf_in_valid)
                query_waiting <= 1'b1;

            if (store_query_rsp_valid && store_query_rsp_ready) begin
                // The store response register is the second Snapshot-storage
                // cycle.  The preceding BF-engine latency is explicit and is
                // outside this storage contract.
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
        if (USE_ASAP7_SRAM && USE_SRAM_MACRO)
            $error("select either the generic or ASAP7 Snapshot macro adapter");
    end
endmodule
