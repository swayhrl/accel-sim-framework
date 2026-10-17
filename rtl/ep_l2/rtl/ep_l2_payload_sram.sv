// Simulation: true 1024-bit data, byte enables, synchronous one-cycle reads.
// Synthesis: explicit SRAM boundary. NO DFF implementation of payload storage.
// Supply a real macro adapter + Liberty before claiming macro area or timing.
`ifdef SYNTHESIS
(* blackbox *)
`endif
module ep_l2_payload_sram #(
    parameter integer ROWS = 292,
    parameter integer ROW_W = $clog2(ROWS)
) (
    input wire clk, input wire enable, input wire write,
    input wire [ROW_W-1:0] row,
    input wire [127:0] byte_enable,
    input wire [1023:0] write_data,
    output reg [1023:0] read_data
);
`ifndef SYNTHESIS
    reg [1023:0] memory [0:ROWS-1];
    always @(posedge clk) begin
        if (enable) begin
            if (row >= ROWS) $fatal(1, "SRAM row outside physical bank");
            if (write) begin
                for (integer i = 0; i < 128; i = i + 1)
                    if (byte_enable[i]) memory[row][8*i +: 8] <= write_data[8*i +: 8];
            end else read_data <= memory[row];
        end
    end
`endif
endmodule
