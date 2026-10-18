module owner_invariant(input clk,input [2:0] op,input [1:0] tag,input [2:0] landing,lower_pid,fill_pid,input [1:0] fill_tag,input dirty,lower,output legal,invariant,owner_property);
 localparam NT=4,NP=8;
 wire [NP*3-1:0] roles;wire [NP*2-1:0] owners;wire [NT*3-1:0] maps;
 reg [NT-1:0] live;
 wire [2:0] oldpid=maps[tag*3 +:3];wire oldlive=live[tag];
 wire commit=op==2||op==3;
 assign legal=(op==0 || (op==1&&roles[landing*3 +:3]==0) ||
 (op==2&&oldlive&&landing==oldpid&&!dirty) ||
 (op==3&&roles[landing*3 +:3]==3&&owners[landing*2 +:2]==tag&&(!oldlive||dirty)) ||
 (op==4&&oldlive) || (op==5&&roles[landing*3 +:3]==3)) &&
 (!lower || roles[lower_pid*3 +:3]==2);
 always @(posedge clk) begin
  if(commit)live[tag]<=1;
  if(op==4)live[tag]<=0;
 end
 genvar t,m;
 generate for(t=0;t<NT;t=t+1)begin: tag_word
 ep_l2_tag_map_word #(.PID_W(3)) map_state(.clk(clk),.rst_n(1'b1),.write(commit&&tag==t),.data(landing),.payload(maps[t*3 +:3]));
 end
 for(m=0;m<NP;m=m+1)begin: word
 ep_l2_metadata_word #(.GEN_W(3),.TAG_W(2)) s(.clk(clk),.rst_n(1'b1),
 .reserve_resident(op==1&&landing==m),.reserve_wb(1'b0),.new_owner(tag),
 .pin_update(1'b0),.pin_increment(1'b0),.read_pin_add(1'b0),.read_pin_release(1'b0),
 .fill_update(1'b0),.fill_sectors(4'b0),.become_wb(op==3&&oldlive&&dirty&&oldpid==m),
 .install(commit&&landing==m),.already_reserved(op==3),.install_old_live(oldlive),
 .generation_write(1'b0),.generation_value(3'b0),.install_ready(4'b0),.install_pending(4'b0),.install_dirty(4'b0),
 .hit_write(1'b0),.write_ready(4'b0),.write_dirty(4'b0),.invalidate(op==4&&oldpid==m),
 .rollback_release(op==5&&landing==m),.lower_release(lower&&lower_pid==m),
 .role(roles[m*3 +:3]),.owner_tag(owners[m*2 +:2]),.generation(),.pins(),.sectors_ready(),.sectors_pending(),.dirty());
 end endgenerate
 wire [NT-1:0] tag_ok;wire [NP-1:0] payload_ok;
 generate for(t=0;t<NT;t=t+1)begin
 wire [2:0] p=maps[t*3 +:3];
 assign tag_ok[t]=!live[t] || (roles[p*3 +:3]==1 && owners[p*2 +:2]==t);
 end
 for(m=0;m<NP;m=m+1)begin
 wire [1:0] own=owners[m*2 +:2];
 assign payload_ok[m]=roles[m*3 +:3]!=1 || (live[own] && maps[own*3 +:3]==m);
 end endgenerate
 assign invariant=(&tag_ok)&&(&payload_ok);
 wire a=roles[fill_pid*3 +:3]==1 && owners[fill_pid*2 +:2]==fill_tag;
 wire b=roles[fill_pid*3 +:3]==1 && live[fill_tag] && maps[fill_tag*3 +:3]==fill_pid;
 assign owner_property=invariant&&(a==b);
endmodule
