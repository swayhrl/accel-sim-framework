// One-copy, 64-bank C2P Snapshot request arbiter.
//
// Each bank selects one pending BF engine.  Arbitration is deliberately
// independent for the four physical Snapshot copies: a request can obtain a
// tag-mask row and its three Bloom rows in different cycles, and the response
// joiner uses bank_req_owner to reassemble them.  This removes the 128-entry
// all-copy matching cone from the address path.
//
// A 16-engine local selector followed by an 8-way group selector keeps the
// priority depth bounded for the paper's 128-engine configuration.  Priority
// is fixed low index; fairness rotation belongs at the request-queue layer.
module c2p_snapshot_bank_copy_arbiter #(
    parameter integer ENGINES = 128,
    parameter integer NUM_BANKS = 64,
    parameter integer ROW_W = 13,
    parameter integer GROUP_SIZE = (ENGINES < 16) ? ENGINES : 16,
    parameter integer ENGINE_W = (ENGINES <= 1) ? 1 : $clog2(ENGINES),
    parameter integer GROUPS = ENGINES / GROUP_SIZE
) (
    input  wire [ENGINES-1:0]               lane_valid,
    input  wire [ENGINES-1:0]               lane_need,
    input  wire [ENGINES*ROW_W-1:0]         lane_row,
    input  wire [ENGINES*6-1:0]             lane_bank,
    input  wire [NUM_BANKS-1:0]             bank_ready,

    output reg  [NUM_BANKS-1:0]             bank_req_valid,
    output reg  [NUM_BANKS*ENGINE_W-1:0]    bank_req_owner,
    output reg  [NUM_BANKS*ROW_W-1:0]       bank_req_row,
    output reg  [ENGINES-1:0]               lane_grant
);

    genvar bank_g;
    genvar group_g;
    generate
        for (bank_g = 0; bank_g < NUM_BANKS; bank_g = bank_g + 1) begin : g_bank
            wire [GROUPS-1:0] group_valid;
            wire [GROUPS*ENGINE_W-1:0] group_owner;
            wire [GROUPS*ROW_W-1:0] group_row;

            for (group_g = 0; group_g < GROUPS; group_g = group_g + 1) begin : g_group
                reg group_valid_r;
                reg [ENGINE_W-1:0] group_owner_r;
                reg [ROW_W-1:0] group_row_r;
                integer lane_i;

                always @* begin
                    group_valid_r = 1'b0;
                    group_owner_r = {ENGINE_W{1'b0}};
                    group_row_r = {ROW_W{1'b0}};
                    for (lane_i = group_g*GROUP_SIZE;
                         lane_i < (group_g + 1)*GROUP_SIZE;
                         lane_i = lane_i + 1) begin
                        if (!group_valid_r && lane_valid[lane_i] &&
                            lane_need[lane_i] &&
                            (lane_bank[lane_i*6 +: 6] == bank_g)) begin
                            group_valid_r = 1'b1;
                            group_owner_r = lane_i;
                            group_row_r = lane_row[lane_i*ROW_W +: ROW_W];
                        end
                    end
                end

                assign group_valid[group_g] = group_valid_r;
                assign group_owner[group_g*ENGINE_W +: ENGINE_W] = group_owner_r;
                assign group_row[group_g*ROW_W +: ROW_W] = group_row_r;
            end

            integer select_group_i;
            reg selected_r;
            reg [ENGINE_W-1:0] selected_owner_r;
            reg [ROW_W-1:0] selected_row_r;
            always @* begin
                selected_r = 1'b0;
                selected_owner_r = {ENGINE_W{1'b0}};
                selected_row_r = {ROW_W{1'b0}};
                for (select_group_i = 0; select_group_i < GROUPS;
                     select_group_i = select_group_i + 1) begin
                    if (!selected_r && group_valid[select_group_i]) begin
                        selected_r = 1'b1;
                        selected_owner_r =
                            group_owner[select_group_i*ENGINE_W +: ENGINE_W];
                        selected_row_r = group_row[select_group_i*ROW_W +: ROW_W];
                    end
                end
                bank_req_valid[bank_g] = selected_r && bank_ready[bank_g];
                bank_req_owner[bank_g*ENGINE_W +: ENGINE_W] = selected_owner_r;
                bank_req_row[bank_g*ROW_W +: ROW_W] = selected_row_r;
            end
        end
    endgenerate

    integer grant_bank_i;
    integer grant_owner_i;
    always @* begin
        lane_grant = {ENGINES{1'b0}};
        for (grant_bank_i = 0; grant_bank_i < NUM_BANKS;
             grant_bank_i = grant_bank_i + 1) begin
            grant_owner_i = bank_req_owner[grant_bank_i*ENGINE_W +: ENGINE_W];
            if (bank_req_valid[grant_bank_i])
                lane_grant[grant_owner_i] = 1'b1;
        end
    end

    initial begin
        if (NUM_BANKS != 64 || GROUP_SIZE < 1 || GROUP_SIZE > 16 ||
            (ENGINES % GROUP_SIZE) != 0)
            $error("C2P bank arbiter expects 64 banks and integral groups of at most 16 engines");
    end
endmodule
