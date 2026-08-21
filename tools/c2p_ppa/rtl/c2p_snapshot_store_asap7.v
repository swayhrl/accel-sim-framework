// C2P Snapshot storage adapter for the open ASAP7 SRAM macro set.
//
// Each srambank_256x4x64_6t122 instance is 1024x64, synchronous, single
// port, and has no bit write-enable.  Five instances make one 5120x64 C2P
// replica; four replicas provide the tag-mask plus three Bloom rows needed by
// one query.  A bit-set update is therefore a two-cycle read-modify-write,
// while a query reads all four replicas in parallel.  The adapter deliberately
// backpressures update/query admission during that RMW transaction rather than
// pretending this 1RW macro is a masked 1R1W memory.
module c2p_snapshot_store_asap7 #(
    parameter integer NUM_SMS = 64,
    parameter integer TOTAL_ROWS = 5120,
    parameter integer ROW_W = 13
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

    localparam integer BANK_ROWS = 1024;
    localparam integer BANKS_PER_COPY = TOTAL_ROWS / BANK_ROWS;
    localparam integer BANK_W = $clog2(BANKS_PER_COPY);
    localparam integer S_IDLE = 0;
    localparam integer S_UPDATE_WRITE = 1;
    localparam integer S_QUERY_WAIT = 2;
    localparam integer S_QUERY_HOLD = 3;

    reg [1:0] state;
    reg [ROW_W-1:0] update_row0_r;
    reg [ROW_W-1:0] update_row1_r;
    reg [ROW_W-1:0] update_row2_r;
    reg [ROW_W-1:0] update_row3_r;
    reg [NUM_SMS-1:0] update_mask_r;
    reg [BANK_W-1:0] query_bank0_r;
    reg [BANK_W-1:0] query_bank1_r;
    reg [BANK_W-1:0] query_bank2_r;
    reg [BANK_W-1:0] query_bank3_r;

    wire idle = state == S_IDLE;
    // Clear is only used while the matrix blocks normal traffic.  Query wins
    // over a simultaneous normal update, which prevents query starvation.
    assign clear_ready = idle;
    assign query_ready = idle && !clear_valid;
    assign write_ready = idle && !clear_valid && !query_valid;
    wire clear_fire = clear_valid && clear_ready;
    wire query_fire = query_valid && query_ready;
    wire write_fire = write_valid && write_ready;

    wire [BANK_W-1:0] clear_bank = clear_row[ROW_W-1 -: BANK_W];
    wire [BANK_W-1:0] query_bank0 = query_row0[ROW_W-1 -: BANK_W];
    wire [BANK_W-1:0] query_bank1 = query_row1[ROW_W-1 -: BANK_W];
    wire [BANK_W-1:0] query_bank2 = query_row2[ROW_W-1 -: BANK_W];
    wire [BANK_W-1:0] query_bank3 = query_row3[ROW_W-1 -: BANK_W];
    wire [BANK_W-1:0] update_bank0 = update_row0_r[ROW_W-1 -: BANK_W];
    wire [BANK_W-1:0] update_bank1 = update_row1_r[ROW_W-1 -: BANK_W];
    wire [BANK_W-1:0] update_bank2 = update_row2_r[ROW_W-1 -: BANK_W];
    wire [BANK_W-1:0] update_bank3 = update_row3_r[ROW_W-1 -: BANK_W];

    wire [BANKS_PER_COPY*NUM_SMS-1:0] copy0_data;
    wire [BANKS_PER_COPY*NUM_SMS-1:0] copy1_data;
    wire [BANKS_PER_COPY*NUM_SMS-1:0] copy2_data;
    wire [BANKS_PER_COPY*NUM_SMS-1:0] copy3_data;
    wire [NUM_SMS-1:0] update_old0 =
        copy0_data[update_bank0*NUM_SMS +: NUM_SMS];
    wire [NUM_SMS-1:0] update_old1 =
        copy1_data[update_bank1*NUM_SMS +: NUM_SMS];
    wire [NUM_SMS-1:0] update_old2 =
        copy2_data[update_bank2*NUM_SMS +: NUM_SMS];
    wire [NUM_SMS-1:0] update_old3 =
        copy3_data[update_bank3*NUM_SMS +: NUM_SMS];
    wire [NUM_SMS-1:0] query_data0 =
        copy0_data[query_bank0_r*NUM_SMS +: NUM_SMS];
    wire [NUM_SMS-1:0] query_data1 =
        copy1_data[query_bank1_r*NUM_SMS +: NUM_SMS];
    wire [NUM_SMS-1:0] query_data2 =
        copy2_data[query_bank2_r*NUM_SMS +: NUM_SMS];
    wire [NUM_SMS-1:0] query_data3 =
        copy3_data[query_bank3_r*NUM_SMS +: NUM_SMS];

    genvar bank;
    generate
        for (bank = 0; bank < BANKS_PER_COPY; bank = bank + 1) begin : g_bank
            wire clear_sel = clear_fire && (clear_bank == bank);
            wire query_sel0 = query_fire && (query_bank0 == bank);
            wire query_sel1 = query_fire && (query_bank1 == bank);
            wire query_sel2 = query_fire && (query_bank2 == bank);
            wire query_sel3 = query_fire && (query_bank3 == bank);
            wire update_read0 = write_fire && (write_row0[ROW_W-1 -: BANK_W] == bank);
            wire update_read1 = write_fire && (write_row1[ROW_W-1 -: BANK_W] == bank);
            wire update_read2 = write_fire && (write_row2[ROW_W-1 -: BANK_W] == bank);
            wire update_read3 = write_fire && (write_row3[ROW_W-1 -: BANK_W] == bank);
            wire update_write0 = (state == S_UPDATE_WRITE) && (update_bank0 == bank);
            wire update_write1 = (state == S_UPDATE_WRITE) && (update_bank1 == bank);
            wire update_write2 = (state == S_UPDATE_WRITE) && (update_bank2 == bank);
            wire update_write3 = (state == S_UPDATE_WRITE) && (update_bank3 == bank);

            srambank_256x4x64_6t122 copy0 (
                .clk(clk), .ADDRESS(clear_sel ? clear_row[9:0] :
                                    update_write0 ? update_row0_r[9:0] :
                                    write_fire ? write_row0[9:0] : query_row0[9:0]),
                .wd(clear_sel ? {NUM_SMS{1'b0}} : update_old0 | update_mask_r),
                .banksel(clear_sel | query_sel0 | update_read0 | update_write0),
                .read(query_sel0 | update_read0), .write(clear_sel | update_write0),
                .dataout(copy0_data[bank*NUM_SMS +: NUM_SMS]));
            srambank_256x4x64_6t122 copy1 (
                .clk(clk), .ADDRESS(clear_sel ? clear_row[9:0] :
                                    update_write1 ? update_row1_r[9:0] :
                                    write_fire ? write_row1[9:0] : query_row1[9:0]),
                .wd(clear_sel ? {NUM_SMS{1'b0}} : update_old1 | update_mask_r),
                .banksel(clear_sel | query_sel1 | update_read1 | update_write1),
                .read(query_sel1 | update_read1), .write(clear_sel | update_write1),
                .dataout(copy1_data[bank*NUM_SMS +: NUM_SMS]));
            srambank_256x4x64_6t122 copy2 (
                .clk(clk), .ADDRESS(clear_sel ? clear_row[9:0] :
                                    update_write2 ? update_row2_r[9:0] :
                                    write_fire ? write_row2[9:0] : query_row2[9:0]),
                .wd(clear_sel ? {NUM_SMS{1'b0}} : update_old2 | update_mask_r),
                .banksel(clear_sel | query_sel2 | update_read2 | update_write2),
                .read(query_sel2 | update_read2), .write(clear_sel | update_write2),
                .dataout(copy2_data[bank*NUM_SMS +: NUM_SMS]));
            srambank_256x4x64_6t122 copy3 (
                .clk(clk), .ADDRESS(clear_sel ? clear_row[9:0] :
                                    update_write3 ? update_row3_r[9:0] :
                                    write_fire ? write_row3[9:0] : query_row3[9:0]),
                .wd(clear_sel ? {NUM_SMS{1'b0}} : update_old3 | update_mask_r),
                .banksel(clear_sel | query_sel3 | update_read3 | update_write3),
                .read(query_sel3 | update_read3), .write(clear_sel | update_write3),
                .dataout(copy3_data[bank*NUM_SMS +: NUM_SMS]));
        end
    endgenerate

    always @(posedge clk) begin
        if (reset) begin
            state <= S_IDLE;
            query_rsp_valid <= 1'b0;
            query_rsp_data0 <= {NUM_SMS{1'b0}};
            query_rsp_data1 <= {NUM_SMS{1'b0}};
            query_rsp_data2 <= {NUM_SMS{1'b0}};
            query_rsp_data3 <= {NUM_SMS{1'b0}};
            update_row0_r <= {ROW_W{1'b0}};
            update_row1_r <= {ROW_W{1'b0}};
            update_row2_r <= {ROW_W{1'b0}};
            update_row3_r <= {ROW_W{1'b0}};
            update_mask_r <= {NUM_SMS{1'b0}};
            query_bank0_r <= {BANK_W{1'b0}};
            query_bank1_r <= {BANK_W{1'b0}};
            query_bank2_r <= {BANK_W{1'b0}};
            query_bank3_r <= {BANK_W{1'b0}};
        end else begin
            if (query_rsp_valid && query_rsp_ready)
                query_rsp_valid <= 1'b0;

            if (write_fire) begin
                update_row0_r <= write_row0;
                update_row1_r <= write_row1;
                update_row2_r <= write_row2;
                update_row3_r <= write_row3;
                update_mask_r <= write_mask;
                state <= S_UPDATE_WRITE;
            end else if (query_fire) begin
                query_bank0_r <= query_bank0;
                query_bank1_r <= query_bank1;
                query_bank2_r <= query_bank2;
                query_bank3_r <= query_bank3;
                state <= S_QUERY_WAIT;
            end else if (state == S_UPDATE_WRITE) begin
                state <= S_IDLE;
            end else if (state == S_QUERY_WAIT) begin
                query_rsp_data0 <= query_data0;
                query_rsp_data1 <= query_data1;
                query_rsp_data2 <= query_data2;
                query_rsp_data3 <= query_data3;
                query_rsp_valid <= 1'b1;
                state <= S_QUERY_HOLD;
            end else if ((state == S_QUERY_HOLD) && query_rsp_valid && query_rsp_ready) begin
                state <= S_IDLE;
            end
        end
    end

    initial begin
        if (NUM_SMS != 64 || TOTAL_ROWS != 5120 || ROW_W != 13)
            $error("ASAP7 Snapshot adapter is fixed at 5120x64 rows");
        if (BANKS_PER_COPY != 5)
            $error("ASAP7 Snapshot adapter expects five 1024-row macros per copy");
    end
endmodule
