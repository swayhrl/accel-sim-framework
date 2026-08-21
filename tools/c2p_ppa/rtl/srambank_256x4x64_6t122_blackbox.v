// Physical black box for the BSD-3-Clause OpenROAD ASAP7 SRAM macro.
// Functional tests use the upstream behavioural Verilog fetched by
// fetch_asap7_sram.sh; PPA reads this black box plus the matching LEF/Liberty.
(* blackbox *)
module srambank_256x4x64_6t122 (
    input wire clk,
    input wire [9:0] ADDRESS,
    input wire [63:0] wd,
    input wire banksel,
    input wire read,
    input wire write,
    output wire [63:0] dataout
);
endmodule
