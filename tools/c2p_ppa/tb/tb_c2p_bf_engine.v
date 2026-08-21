`timescale 1ns/1ps

// Check the pipelined hardware address generator against its mathematical row
// mapping. The reference deliberately uses division; the DUT uses shift/add
// bank formatting and must return the same four rows under backpressure.
module tb_c2p_bf_engine;
    reg clk = 1'b0;
    reg reset = 1'b1;
    reg in_valid = 1'b0;
    wire in_ready;
    reg [63:0] in_tag = 64'b0;
    reg in_aux = 1'b0;
    wire out_valid;
    reg out_ready = 1'b1;
    wire [12:0] out_row0;
    wire [12:0] out_row1;
    wire [12:0] out_row2;
    wire [12:0] out_row3;
    wire out_aux;

    always #5 clk = ~clk;

    c2p_bf_engine dut (
        .clk(clk), .reset(reset),
        .in_valid(in_valid), .in_ready(in_ready),
        .in_tag(in_tag), .in_aux(in_aux),
        .out_valid(out_valid), .out_ready(out_ready),
        .out_row0(out_row0), .out_row1(out_row1),
        .out_row2(out_row2), .out_row3(out_row3), .out_aux(out_aux)
    );

    function [11:0] reference_fold_hash12;
        input [63:0] value;
        input [63:0] salt;
        reg [63:0] x;
        reg [11:0] folded;
        reg [11:0] mixed;
        begin
            x = value ^ salt;
            folded = x[11:0] ^ x[23:12] ^ x[35:24] ^ x[47:36] ^
                     x[59:48] ^ {8'b0, x[63:60]};
            mixed = folded + {folded[6:0], folded[11:7]} + salt[11:0];
            reference_fold_hash12 = mixed ^ {mixed[8:0], mixed[11:9]} ^
                                    {2'b0, mixed[11:2]};
        end
    endfunction

    function [9:0] reference_reverse_low10;
        input [63:0] tag;
        integer i;
        begin
            for (i = 0; i < 10; i = i + 1)
                reference_reverse_low10[9-i] = tag[i];
        end
    endfunction

    function [12:0] reference_row;
        input [63:0] tag;
        input integer row_sel;
        reg [11:0] h1;
        reg [11:0] h2;
        reg [9:0] reversed;
        integer index;
        integer bank;
        integer offset;
        begin
            if (row_sel == 0) begin
                reversed = reference_reverse_low10(tag);
                bank = (reversed / 16) % 64;
                offset = 64 + (reversed % 16);
            end else begin
                h1 = reference_fold_hash12(tag, 64'h243f6a8885a308d3);
                h2 = reference_fold_hash12(tag, 64'h13198a2e03707344);
                index = (row_sel * h1 + h2) & 12'hfff;
                bank = index / 64;
                offset = index % 64;
            end
            reference_row = bank * 80 + offset;
        end
    endfunction

    task push_and_check;
        input [63:0] tag;
        input aux;
        begin
            while (!in_ready) @(negedge clk);
            in_tag = tag;
            in_aux = aux;
            in_valid = 1'b1;
            @(negedge clk);
            in_valid = 1'b0;
            while (!out_valid) @(negedge clk);
            if (out_row0 !== reference_row(tag, 0) ||
                out_row1 !== reference_row(tag, 1) ||
                out_row2 !== reference_row(tag, 2) ||
                out_row3 !== reference_row(tag, 3) || out_aux !== aux)
                $fatal(1, "BF engine row mismatch for tag %h", tag);
        end
    endtask

    initial begin
        repeat (3) @(posedge clk);
        @(negedge clk);
        reset = 1'b0;

        push_and_check(64'h0000000000001234, 1'b0);
        // The output is held as a proper elastic stage, then accepted.
        out_ready = 1'b0;
        repeat (2) @(negedge clk);
        if (!out_valid)
            $fatal(1, "BF engine did not retain a stalled output");
        out_ready = 1'b1;
        @(negedge clk);
        push_and_check(64'hfedcba9876543210, 1'b1);
        @(negedge clk);
        push_and_check(64'h0123456789abcdef, 1'b0);

        $display("PASS tb_c2p_bf_engine");
        $finish;
    end

    initial begin
        #10000;
        $fatal(1, "tb_c2p_bf_engine timeout");
    end
endmodule
