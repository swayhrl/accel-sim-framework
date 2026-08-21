// Four-copy C2P Snapshot request arbiter.
//
// The four Snapshot replicas are independent 64-bank memories. Every copy
// arbitrates its own pending rows, while the engine-side sent mask in
// c2p_snapshot_banked_frontend prevents a row from being issued twice. A
// response router joins the four owner-tagged replies before candidate
// evaluation; no atomic four-bank grant or global conflict scoreboard exists
// on this request path.
module c2p_snapshot_bank_arbiter #(
    parameter integer ENGINES = 128,
    parameter integer NUM_BANKS = 64,
    parameter integer ROW_W = 13,
    parameter integer ENGINE_W = (ENGINES <= 1) ? 1 : $clog2(ENGINES)
) (
    input  wire [ENGINES-1:0]               lane_valid,
    input  wire [ENGINES-1:0]               lane_need0,
    input  wire [ENGINES-1:0]               lane_need1,
    input  wire [ENGINES-1:0]               lane_need2,
    input  wire [ENGINES-1:0]               lane_need3,
    input  wire [ENGINES*ROW_W-1:0]         lane_row0,
    input  wire [ENGINES*ROW_W-1:0]         lane_row1,
    input  wire [ENGINES*ROW_W-1:0]         lane_row2,
    input  wire [ENGINES*ROW_W-1:0]         lane_row3,
    input  wire [ENGINES*6-1:0]             lane_bank0,
    input  wire [ENGINES*6-1:0]             lane_bank1,
    input  wire [ENGINES*6-1:0]             lane_bank2,
    input  wire [ENGINES*6-1:0]             lane_bank3,

    output wire [4*NUM_BANKS-1:0]           bank_req_valid,
    output wire [4*NUM_BANKS*ENGINE_W-1:0]  bank_req_owner,
    output wire [4*NUM_BANKS*ROW_W-1:0]     bank_req_row,
    output wire [ENGINES-1:0]               lane_grant0,
    output wire [ENGINES-1:0]               lane_grant1,
    output wire [ENGINES-1:0]               lane_grant2,
    output wire [ENGINES-1:0]               lane_grant3
);

    c2p_snapshot_bank_copy_arbiter #(
        .ENGINES(ENGINES), .NUM_BANKS(NUM_BANKS), .ROW_W(ROW_W),
        .ENGINE_W(ENGINE_W)
    ) copy0 (
        .lane_valid(lane_valid), .lane_need(lane_need0), .lane_row(lane_row0),
        .lane_bank(lane_bank0),
        .bank_req_valid(bank_req_valid[0*NUM_BANKS +: NUM_BANKS]),
        .bank_req_owner(bank_req_owner[0*NUM_BANKS*ENGINE_W +: NUM_BANKS*ENGINE_W]),
        .bank_req_row(bank_req_row[0*NUM_BANKS*ROW_W +: NUM_BANKS*ROW_W]),
        .lane_grant(lane_grant0)
    );
    c2p_snapshot_bank_copy_arbiter #(
        .ENGINES(ENGINES), .NUM_BANKS(NUM_BANKS), .ROW_W(ROW_W),
        .ENGINE_W(ENGINE_W)
    ) copy1 (
        .lane_valid(lane_valid), .lane_need(lane_need1), .lane_row(lane_row1),
        .lane_bank(lane_bank1),
        .bank_req_valid(bank_req_valid[1*NUM_BANKS +: NUM_BANKS]),
        .bank_req_owner(bank_req_owner[1*NUM_BANKS*ENGINE_W +: NUM_BANKS*ENGINE_W]),
        .bank_req_row(bank_req_row[1*NUM_BANKS*ROW_W +: NUM_BANKS*ROW_W]),
        .lane_grant(lane_grant1)
    );
    c2p_snapshot_bank_copy_arbiter #(
        .ENGINES(ENGINES), .NUM_BANKS(NUM_BANKS), .ROW_W(ROW_W),
        .ENGINE_W(ENGINE_W)
    ) copy2 (
        .lane_valid(lane_valid), .lane_need(lane_need2), .lane_row(lane_row2),
        .lane_bank(lane_bank2),
        .bank_req_valid(bank_req_valid[2*NUM_BANKS +: NUM_BANKS]),
        .bank_req_owner(bank_req_owner[2*NUM_BANKS*ENGINE_W +: NUM_BANKS*ENGINE_W]),
        .bank_req_row(bank_req_row[2*NUM_BANKS*ROW_W +: NUM_BANKS*ROW_W]),
        .lane_grant(lane_grant2)
    );
    c2p_snapshot_bank_copy_arbiter #(
        .ENGINES(ENGINES), .NUM_BANKS(NUM_BANKS), .ROW_W(ROW_W),
        .ENGINE_W(ENGINE_W)
    ) copy3 (
        .lane_valid(lane_valid), .lane_need(lane_need3), .lane_row(lane_row3),
        .lane_bank(lane_bank3),
        .bank_req_valid(bank_req_valid[3*NUM_BANKS +: NUM_BANKS]),
        .bank_req_owner(bank_req_owner[3*NUM_BANKS*ENGINE_W +: NUM_BANKS*ENGINE_W]),
        .bank_req_row(bank_req_row[3*NUM_BANKS*ROW_W +: NUM_BANKS*ROW_W]),
        .lane_grant(lane_grant3)
    );
endmodule
