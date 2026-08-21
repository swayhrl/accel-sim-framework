// Two-cycle C2P Bloom/tag-mask address generator.
//
// C2P correctness does not depend on a particular Bloom hash: updates and
// queries must use the same mapping, while every candidate remains subject to
// an exact remote-L1 probe. This hardware-oriented folded hash intentionally
// replaces the simulator's expensive 64-bit splitmix reference hash. It
// avoids a full-width multiplier on the SRAM address path and matches the
// paper's two-cycle BF-engine budget.
module c2p_bf_engine #(
    parameter integer TAG_W = 64,
    parameter integer ROW_W = 13,
    parameter integer NUM_BANKS = 64,
    parameter integer BF_ROWS_PER_BANK = 64,
    parameter integer TAG_MASK_ROWS_PER_BANK = 16,
    parameter integer AUX_W = 1
) (
    input  wire                 clk,
    input  wire                 reset,
    input  wire                 in_valid,
    output wire                 in_ready,
    input  wire [TAG_W-1:0]     in_tag,
    input  wire [AUX_W-1:0]     in_aux,
    output wire                 out_valid,
    input  wire                 out_ready,
    output wire [ROW_W-1:0]     out_row0,
    output wire [ROW_W-1:0]     out_row1,
    output wire [ROW_W-1:0]     out_row2,
    output wire [ROW_W-1:0]     out_row3,
    output wire [5:0]           out_bank0,
    output wire [5:0]           out_bank1,
    output wire [5:0]           out_bank2,
    output wire [5:0]           out_bank3,
    output wire [AUX_W-1:0]     out_aux
);

    reg [1:0] valid_r;
    reg [TAG_W-1:0] tag_r [0:1];
    reg [AUX_W-1:0] aux_r [0:1];
    reg [11:0] h1_r [0:1];
    reg [11:0] h2_r [0:1];

    // A single elastic enable freezes both stages when the selected Snapshot
    // port is busy, preserving valid/data association without a ready loop.
    wire advance = !valid_r[1] || out_ready;
    assign in_ready = advance;
    assign out_valid = valid_r[1];
    assign out_aux = aux_r[1];

    function [11:0] folded_hash12;
        input [TAG_W-1:0] tag;
        input [TAG_W-1:0] salt;
        reg [TAG_W-1:0] x;
        reg [11:0] folded;
        reg [11:0] mixed;
        begin
            x = tag ^ salt;
            folded = x[11:0] ^ x[23:12] ^ x[35:24] ^ x[47:36] ^
                     x[59:48] ^ {8'b0, x[63:60]};
            // This 12-bit add introduces carry-based nonlinearity, so the
            // two salted hashes are not merely fixed XOR translations of one
            // another. The rotations then diffuse each bit without a
            // multiplier-sized timing cone.
            mixed = folded + {folded[6:0], folded[11:7]} + salt[11:0];
            folded_hash12 = mixed ^ {mixed[8:0], mixed[11:9]} ^
                            {2'b0, mixed[11:2]};
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

    // The 64-bank layout has 64 Bloom rows and 16 tag-mask rows per bank.
    // The shift/add form makes the 80-row bank stride explicit.
    function [ROW_W-1:0] bf_row;
        input [11:0] index;
        reg [5:0] bank;
        reg [ROW_W-1:0] base;
        begin
            bank = index[11:6];
            base = {1'b0, bank, 6'b0} + {3'b0, bank, 4'b0};
            bf_row = base + index[5:0];
        end
    endfunction

    function [ROW_W-1:0] tag_row;
        input [TAG_W-1:0] tag;
        reg [9:0] reversed;
        reg [5:0] bank;
        reg [ROW_W-1:0] base;
        begin
            reversed = reverse_low10(tag);
            bank = reversed[9:4];
            base = {1'b0, bank, 6'b0} + {3'b0, bank, 4'b0};
            tag_row = base + BF_ROWS_PER_BANK + reversed[3:0];
        end
    endfunction

    wire [9:0] tag_index = reverse_low10(tag_r[1]);
    wire [11:0] bf_index1 = h1_r[1] + h2_r[1];
    wire [11:0] bf_index2 = (h1_r[1] << 1) + h2_r[1];
    wire [11:0] bf_index3 = h1_r[1] + (h1_r[1] << 1) + h2_r[1];
    assign out_row0 = tag_row(tag_r[1]);
    assign out_row1 = bf_row(bf_index1);
    assign out_row2 = bf_row(bf_index2);
    assign out_row3 = bf_row(bf_index3);
    // Export bank IDs with the rows so a scalable Snapshot front end never
    // has to re-divide a physical row address by the 80-row bank stride.
    assign out_bank0 = tag_index[9:4];
    assign out_bank1 = bf_index1[11:6];
    assign out_bank2 = bf_index2[11:6];
    assign out_bank3 = bf_index3[11:6];

    always @(posedge clk) begin
        if (reset) begin
            valid_r <= 2'b0;
            tag_r[0] <= {TAG_W{1'b0}};
            tag_r[1] <= {TAG_W{1'b0}};
            aux_r[0] <= {AUX_W{1'b0}};
            aux_r[1] <= {AUX_W{1'b0}};
            h1_r[0] <= 12'b0;
            h1_r[1] <= 12'b0;
            h2_r[0] <= 12'b0;
            h2_r[1] <= 12'b0;
        end else if (advance) begin
            valid_r[1] <= valid_r[0];
            valid_r[0] <= in_valid;

            tag_r[1] <= tag_r[0];
            aux_r[1] <= aux_r[0];
            h1_r[1] <= h1_r[0];
            h2_r[1] <= h2_r[0];

            tag_r[0] <= in_tag;
            aux_r[0] <= in_aux;
            h1_r[0] <= folded_hash12(in_tag, 64'h243f6a8885a308d3);
            h2_r[0] <= folded_hash12(in_tag, 64'h13198a2e03707344);
        end
    end

    initial begin
        if (TAG_W != 64 || ROW_W != 13 || NUM_BANKS != 64 ||
            BF_ROWS_PER_BANK != 64 || TAG_MASK_ROWS_PER_BANK != 16)
            $error("c2p_bf_engine implements the paper default 64-bank geometry");
    end
endmodule
