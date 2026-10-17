module equiv(input [63:0] eligible,output equal);
 wire found;wire [5:0] index;reg expected_found;reg [5:0] expected_index;
 ep_l2_first_one #(.N(64),.W(6)) dut(eligible,found,index);
 always @* begin expected_found=0;expected_index=0;
 for(integer j=0;j<64;j=j+1)if(!expected_found&&eligible[j])begin expected_found=1;expected_index=j;end end
 assign equal=(found==expected_found)&&(index==expected_index);endmodule
