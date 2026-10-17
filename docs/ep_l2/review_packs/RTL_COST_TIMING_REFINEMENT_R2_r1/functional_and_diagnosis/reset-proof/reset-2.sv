module reset_equiv(input rst_n,output equal);localparam MODE=2,N_PAYLOAD=1168,N_TAG=1024,WB_BEGIN=1104;
    localparam integer RESET_LEAF=(N_PAYLOAD+3)/4;
    localparam integer RESET_MID=(RESET_LEAF+15)/16;
    localparam integer RESET_ROOT=(RESET_MID+15)/16;
    wire [RESET_ROOT-1:0] reset_root;
    wire [RESET_MID-1:0] reset_mid;
    wire [RESET_LEAF-1:0] reset_leaf;
    generate for(genvar g=0;g<RESET_ROOT;g=g+1)begin: reset_distribution_root
      (* keep=1,keep_hierarchy=1 *) ep_l2_control_buffer repeater(rst_n,reset_root[g]);
    end
    for(genvar g=0;g<RESET_MID;g=g+1)begin: reset_distribution_mid
      if(MODE==1 || g*64<N_TAG || (g+1)*64>WB_BEGIN)begin: active
        (* keep=1,keep_hierarchy=1 *) ep_l2_control_buffer repeater(reset_root[g/16],reset_mid[g]);
      end else assign reset_mid[g]=rst_n;
    end
    for(genvar g=0;g<RESET_LEAF;g=g+1)begin: reset_distribution_leaf
      if(MODE==1 || g*4<N_TAG || (g+1)*4>WB_BEGIN)begin: active
        (* keep=1,keep_hierarchy=1 *) ep_l2_control_buffer repeater(reset_mid[g/16],reset_leaf[g]);
      end else assign reset_leaf[g]=rst_n;
    end endgenerate
assign equal=reset_leaf=={RESET_LEAF{rst_n}};endmodule
