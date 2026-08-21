`timescale 1ns/1ps

module tb_c2p_snapshot_response_fabric;
    localparam integer ENGINES = 8;
    localparam integer NUM_BANKS = 4;
    localparam integer ENGINE_W = 3;
    reg clk = 1'b0;
    reg reset = 1'b1;
    reg [NUM_BANKS-1:0] bank_rsp_valid = 0;
    wire [NUM_BANKS-1:0] bank_rsp_ready;
    reg [NUM_BANKS*ENGINE_W-1:0] bank_rsp_owner = 0;
    reg [NUM_BANKS*64-1:0] bank_rsp_data = 0;
    wire [ENGINES-1:0] out_valid;
    reg [ENGINES-1:0] out_ready = {ENGINES{1'b1}};
    wire [ENGINES*64-1:0] out_data;
    reg [ENGINES-1:0] seen = 0;
    integer bank_i;

    always #5 clk = ~clk;

    c2p_snapshot_response_fabric #(
        .ENGINES(ENGINES), .NUM_BANKS(NUM_BANKS), .DATA_W(64)
    ) dut (
        .clk(clk), .reset(reset),
        .bank_rsp_valid(bank_rsp_valid), .bank_rsp_ready(bank_rsp_ready),
        .bank_rsp_owner(bank_rsp_owner), .bank_rsp_data(bank_rsp_data),
        .out_valid(out_valid), .out_ready(out_ready), .out_data(out_data)
    );

    always @(posedge clk)
        if (reset) seen <= 0;
        else seen <= seen | out_valid;

    initial begin
        repeat (3) @(posedge clk);
        @(negedge clk);
        reset = 1'b0;
        // Owners 1 and 5 initially contend in the first routing switch;
        // neither may be lost while the other advances.
        bank_rsp_owner[0*ENGINE_W +: ENGINE_W] = 3'd1;
        bank_rsp_owner[1*ENGINE_W +: ENGINE_W] = 3'd5;
        bank_rsp_owner[2*ENGINE_W +: ENGINE_W] = 3'd2;
        bank_rsp_owner[3*ENGINE_W +: ENGINE_W] = 3'd7;
        bank_rsp_data[0*64 +: 64] = 64'h11;
        bank_rsp_data[1*64 +: 64] = 64'h55;
        bank_rsp_data[2*64 +: 64] = 64'h22;
        bank_rsp_data[3*64 +: 64] = 64'h77;
        bank_rsp_valid = 4'b1111;
        while (bank_rsp_valid != 0) begin
            @(negedge clk);
            for (bank_i = 0; bank_i < NUM_BANKS; bank_i = bank_i + 1)
                if (bank_rsp_ready[bank_i]) bank_rsp_valid[bank_i] = 1'b0;
        end
        repeat (20) @(negedge clk);
        if (seen !== 8'b10100110)
            $fatal(1, "fabric lost or misrouted packets: %b", seen);
        if (out_data[1*64 +: 64] !== 64'h11 ||
            out_data[2*64 +: 64] !== 64'h22 ||
            out_data[5*64 +: 64] !== 64'h55 ||
            out_data[7*64 +: 64] !== 64'h77)
            $fatal(1, "fabric data mismatch");
        $display("PASS tb_c2p_snapshot_response_fabric");
        $finish;
    end

    initial begin
        #10000;
        $fatal(1, "tb_c2p_snapshot_response_fabric timeout");
    end
endmodule
