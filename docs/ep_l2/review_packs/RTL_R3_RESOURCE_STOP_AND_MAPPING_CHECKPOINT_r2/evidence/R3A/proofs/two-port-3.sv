module word_equiv(input [4*3-1:0] old,input [1:0] fp,lp,input reserve,commit,abort,lower,old_live,input [1:0] state,output equal);
 wire r=state==0 && reserve,c=state==1 && commit && !abort,b=state!=0 && abort;
 wire fw=r|c|b;wire st=c&&old_live;wire [3-1:0] fn,ln;
 ep_l2_generation_step #(.GEN_W(3)) fe(old[fp*3 +:3],st,fn);
 ep_l2_generation_step #(.GEN_W(3)) lo(old[lp*3 +:3],1'b0,ln);
 wire [4*3-1:0] a,z;
 genvar i;generate for(i=0;i<4;i=i+1)begin
 wire [3-1:0] x=old[i*3 +:3];
 assign a[i*3 +:3]=lower&&lp==i ? x+3'd1 : (r||c||b)&&fp==i ? x+(st?3'd2:3'd1) : x;
 assign z[i*3 +:3]=lower&&lp==i ? ln : fw&&fp==i ? fn : x;
 end endgenerate
 assign equal=a==z;endmodule
