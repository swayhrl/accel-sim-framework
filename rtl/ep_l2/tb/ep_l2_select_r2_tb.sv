`timescale 1ns/1ps
module check_first #(parameter integer N=292,W=$clog2(N)) (output reg done=0);
 reg [N-1:0] eligible=0;wire found;wire [W-1:0] index;
 ep_l2_first_one #(.N(N),.W(W)) dut(eligible,found,index);
 integer expected;reg expected_found;reg [31:0] seed=32'h96341a8d;
 task check;begin
   #1;expected=0;expected_found=0;
   for(integer j=0;j<N;j=j+1)if(eligible[j]&&!expected_found)begin expected=j;expected_found=1;end
   if(found!==expected_found || index!==W'(expected))$fatal(1,"first-one mismatch N%0d",N);
 end endtask
 initial begin
  check();eligible='1;check();
  for(integer j=0;j<N;j=j+1)begin eligible=0;eligible[j]=1;check();end
  for(integer trial=0;trial<512;trial=trial+1)begin
   for(integer j=0;j<N;j=j+1)begin seed={seed[30:0],seed[31]^seed[21]^seed[1]^seed[0]};eligible[j]=seed[0]&&(trial%3!=0 || j>trial%N);end
   check();
  end
  $display("FIRST_ONE N%0d all_singletons+empty+full+512patterns PASS",N);done=1;
 end
endmodule
module ep_l2_select_r2_tb;
 wire a,b,c,d;check_first #(292) fa(a);check_first #(128) fb(b);check_first #(16) fc(c);check_first #(64) fd(d);
 reg [1168*32-1:0] words;reg [10:0] index;wire [31:0] data;
 ep_l2_index_mux mux(words,index,data);
 initial begin
  for(integer j=0;j<1168;j=j+1)words[j*32 +:32]=32'h96341a8d^(j*65537);
  for(integer j=0;j<2048;j=j+1)begin index=j;#1;
   if(data!==(j<1168 ? (32'h96341a8d^(j*65537)) : 32'b0))$fatal(1,"mux index%0d mismatch",j);
  end
  wait(a&&b&&c&&d);$display("R2 SELECT FULL1168/INVALID2048 PASS");$finish;
 end
endmodule
