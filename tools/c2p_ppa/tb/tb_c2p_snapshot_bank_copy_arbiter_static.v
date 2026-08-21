`timescale 1ns/1ps

// Exercise the paper geometry, which selects the static 8x16 priority tree
// rather than the small-parameter generic arbiter used by unit tests.
module tb_c2p_snapshot_bank_copy_arbiter_static;
    localparam integer ROW_W = 13;
    reg [127:0] lane_valid;
    reg [127:0] lane_need;
    reg [128*ROW_W-1:0] lane_row;
    reg [128*6-1:0] lane_bank;
    reg [63:0] bank_ready;
    wire [63:0] bank_req_valid;
    wire [64*7-1:0] bank_req_owner;
    wire [64*ROW_W-1:0] bank_req_row;
    wire [127:0] lane_grant;

    c2p_snapshot_bank_copy_arbiter dut (
        .lane_valid(lane_valid), .lane_need(lane_need),
        .lane_row(lane_row), .lane_bank(lane_bank), .bank_ready(bank_ready),
        .bank_req_valid(bank_req_valid), .bank_req_owner(bank_req_owner),
        .bank_req_row(bank_req_row), .lane_grant(lane_grant)
    );

    task set_lane;
        input integer lane;
        input [5:0] bank;
        input [ROW_W-1:0] row;
        begin
            lane_valid[lane] = 1'b1;
            lane_need[lane] = 1'b1;
            lane_bank[lane*6 +: 6] = bank;
            lane_row[lane*ROW_W +: ROW_W] = row;
        end
    endtask

    initial begin
        lane_valid = 128'b0;
        lane_need = 128'b0;
        lane_row = {(128*ROW_W){1'b0}};
        lane_bank = {(128*6){1'b0}};
        bank_ready = 64'hffff_ffff_ffff_ffff;

        // Lanes 0, 16, and 127 contend for bank 6.  The static two-level
        // selector must preserve low-engine fixed priority across groups.
        set_lane(0,   6'd6,  13'd100);
        set_lane(16,  6'd6,  13'd200);
        set_lane(127, 6'd6,  13'd300);
        set_lane(65,  6'd11, 13'd400);
        set_lane(3,   6'd19, 13'd500);
        #1;
        if (!bank_req_valid[6] || bank_req_owner[6*7 +: 7] != 7'd0 ||
            bank_req_row[6*ROW_W +: ROW_W] != 13'd100 ||
            lane_grant != (128'b1 << 0 | 128'b1 << 65 | 128'b1 << 3))
            $fatal(1, "static priority/grant mismatch");

        // A blocked bank is neither issued nor granted; unrelated banks
        // continue to progress in the same cycle.
        bank_ready[11] = 1'b0;
        #1;
        if (bank_req_valid[11] || lane_grant[65] || !bank_req_valid[19] ||
            !lane_grant[3])
            $fatal(1, "bank_ready did not isolate the blocked bank");
        $display("PASS tb_c2p_snapshot_bank_copy_arbiter_static");
        $finish;
    end
endmodule
