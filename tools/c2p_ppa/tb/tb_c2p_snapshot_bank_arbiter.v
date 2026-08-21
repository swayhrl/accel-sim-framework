`timescale 1ns/1ps

module tb_c2p_snapshot_bank_arbiter;
    localparam integer ENGINES = 4;
    localparam integer ROW_W = 13;
    localparam integer ENGINE_W = 2;
    reg [ENGINES-1:0] lane_valid;
    reg [ENGINES-1:0] lane_need0;
    reg [ENGINES-1:0] lane_need1;
    reg [ENGINES-1:0] lane_need2;
    reg [ENGINES-1:0] lane_need3;
    reg [ENGINES*ROW_W-1:0] lane_row0;
    reg [ENGINES*ROW_W-1:0] lane_row1;
    reg [ENGINES*ROW_W-1:0] lane_row2;
    reg [ENGINES*ROW_W-1:0] lane_row3;
    reg [ENGINES*6-1:0] lane_bank0;
    reg [ENGINES*6-1:0] lane_bank1;
    reg [ENGINES*6-1:0] lane_bank2;
    reg [ENGINES*6-1:0] lane_bank3;
    wire [255:0] bank_req_valid;
    wire [4*64*ENGINE_W-1:0] bank_req_owner;
    wire [4*64*ROW_W-1:0] bank_req_row;
    wire [ENGINES-1:0] lane_grant0;
    wire [ENGINES-1:0] lane_grant1;
    wire [ENGINES-1:0] lane_grant2;
    wire [ENGINES-1:0] lane_grant3;

    c2p_snapshot_bank_arbiter #(.ENGINES(ENGINES)) dut (
        .lane_valid(lane_valid),
        .lane_need0(lane_need0), .lane_need1(lane_need1),
        .lane_need2(lane_need2), .lane_need3(lane_need3),
        .lane_row0(lane_row0), .lane_row1(lane_row1),
        .lane_row2(lane_row2), .lane_row3(lane_row3),
        .lane_bank0(lane_bank0), .lane_bank1(lane_bank1),
        .lane_bank2(lane_bank2), .lane_bank3(lane_bank3),
        .bank_req_valid(bank_req_valid), .bank_req_owner(bank_req_owner),
        .bank_req_row(bank_req_row),
        .lane_grant0(lane_grant0), .lane_grant1(lane_grant1),
        .lane_grant2(lane_grant2), .lane_grant3(lane_grant3)
    );

    task set_lane;
        input integer lane;
        input [5:0] bank0;
        input [5:0] bank1;
        input [5:0] bank2;
        input [5:0] bank3;
        input [ROW_W-1:0] row0;
        input [ROW_W-1:0] row1;
        input [ROW_W-1:0] row2;
        input [ROW_W-1:0] row3;
        begin
            lane_valid[lane] = 1'b1;
            lane_bank0[lane*6 +: 6] = bank0;
            lane_bank1[lane*6 +: 6] = bank1;
            lane_bank2[lane*6 +: 6] = bank2;
            lane_bank3[lane*6 +: 6] = bank3;
            lane_row0[lane*ROW_W +: ROW_W] = row0;
            lane_row1[lane*ROW_W +: ROW_W] = row1;
            lane_row2[lane*ROW_W +: ROW_W] = row2;
            lane_row3[lane*ROW_W +: ROW_W] = row3;
        end
    endtask

    initial begin
        lane_valid = 4'b0;
        lane_need0 = 4'b1111;
        lane_need1 = 4'b1111;
        lane_need2 = 4'b1111;
        lane_need3 = 4'b1111;
        lane_row0 = 0;
        lane_row1 = 0;
        lane_row2 = 0;
        lane_row3 = 0;
        lane_bank0 = 0;
        lane_bank1 = 0;
        lane_bank2 = 0;
        lane_bank3 = 0;

        // Lanes 2 and 3 conflict in exactly one physical copy. Independent
        // bank queues must make useful partial request progress, tagging every
        // request with its owner so the response joiner can complete the row
        // set without issuing any row twice.
        set_lane(0, 6'd1, 6'd2, 6'd3, 6'd4,
                 13'd81, 13'd162, 13'd243, 13'd324);
        set_lane(1, 6'd5, 6'd6, 6'd7, 6'd8,
                 13'd405, 13'd486, 13'd567, 13'd648);
        set_lane(2, 6'd1, 6'd9, 6'd10, 6'd11,
                 13'd80, 13'd720, 13'd800, 13'd880);
        set_lane(3, 6'd12, 6'd13, 6'd7, 6'd14,
                 13'd960, 13'd1040, 13'd560, 13'd1120);
        #1;
        if (lane_grant0 !== 4'b1011 || lane_grant1 !== 4'b1111 ||
            lane_grant2 !== 4'b0111 || lane_grant3 !== 4'b1111)
            $fatal(1, "unexpected independent grants: %b %b %b %b",
                   lane_grant3, lane_grant2, lane_grant1, lane_grant0);
        if (!bank_req_valid[1] || !bank_req_valid[64+2] ||
            !bank_req_valid[128+3] || !bank_req_valid[192+4] ||
            !bank_req_valid[5] || !bank_req_valid[64+6] ||
            !bank_req_valid[128+7] || !bank_req_valid[192+8])
            $fatal(1, "missing bank requests for independently granted rows");
        if (bank_req_owner[1*ENGINE_W +: ENGINE_W] !== 0 ||
            bank_req_owner[5*ENGINE_W +: ENGINE_W] !== 1 ||
            bank_req_row[(64+6)*ROW_W +: ROW_W] !== 13'd486)
            $fatal(1, "bank request owner or row mismatch");
        $display("PASS tb_c2p_snapshot_bank_arbiter");
        $finish;
    end
endmodule
