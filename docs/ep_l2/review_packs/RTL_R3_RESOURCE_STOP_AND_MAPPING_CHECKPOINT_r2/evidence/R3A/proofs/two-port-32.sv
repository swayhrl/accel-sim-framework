module word_equiv(input [4*32-1:0] old,input [1:0] fp,lp,input reserve,commit,abort,lower,old_live,input [1:0] state,output equal);
 wire r=state==0 && reserve,c=state==1 && commit && !abort,b=state!=0 && abort;
 wire fw=r|c|b;wire st=c&&old_live;wire [32-1:0] fn,ln;
 ep_l2_generation_step #(.GEN_W(32)) fe(old[fp*32 +:32],st,fn);
 ep_l2_generation_step #(.GEN_W(32)) lo(old[lp*32 +:32],1'b0,ln);
 wire [4*32-1:0] a,z;
 genvar i;generate for(i=0;i<4;i=i+1)begin
 wire [32-1:0] x=old[i*32 +:32];
 assign a[i*32 +:32]=lower&&lp==i ? x+32'd1 : (r||c||b)&&fp==i ? x+(st?32'd2:32'd1) : x;
 assign z[i*32 +:32]=lower&&lp==i ? ln : fw&&fp==i ? fn : x;
 end endgenerate
 assign equal=a==z;endmodule
