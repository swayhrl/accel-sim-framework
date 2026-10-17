module equiv(input [1168*32-1:0] words,input [10:0] index,output equal);
 wire [31:0] data;ep_l2_index_mux #(.N(1168),.W(32),.IW(11)) dut(words,index,data);
 wire [31:0] reference=index<1168 ? words[index*32 +:32] : 32'b0;
 assign equal=data==reference;endmodule
