module equiv(input [15:0] eligible,output equal);
 wire found;wire [3:0] index;reg expected_found;reg [3:0] expected_index;
 ep_l2_first_one #(.N(16),.W(4)) dut(eligible,found,index);
 always @* begin expected_found=0;expected_index=0;
 for(integer j=0;j<16;j=j+1)if(!expected_found&&eligible[j])begin expected_found=1;expected_index=j;end end
 assign equal=(found==expected_found)&&(index==expected_index);endmodule
