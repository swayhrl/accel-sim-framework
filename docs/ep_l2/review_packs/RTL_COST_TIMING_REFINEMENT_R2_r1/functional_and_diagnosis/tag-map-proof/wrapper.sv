module equiv(input clk,rst_n,native_commit,input [1:0] p_op,input [9:0] p_tag,word_tag,input [10:0] p_landing,output equal);
localparam META_GROUP=16,PID_W=11;
wire write=native_commit && p_op==0 && p_tag==word_tag;
wire [10:0] masked=p_landing & {PID_W{p_tag/META_GROUP==(word_tag/META_GROUP)}};wire [10:0] a,b;
ep_l2_tag_map_word old_word(clk,rst_n,write,p_landing,a);
ep_l2_tag_map_word new_word(clk,rst_n,write,masked,b);
assign equal=a==b;endmodule
