`timescale 1ns/1ps
module ep_l2_owner_r3_tb;
    parameter integer MODE=0, GEN_W=32, N_TAG=1024, N_PAYLOAD=1168, N_WAD=128,
                      STATIC_WB=(MODE==2?64:16);
    localparam TW=$clog2(N_TAG), PW=$clog2(N_PAYLOAD), WW=$clog2(N_WAD), RW=$clog2(N_PAYLOAD/4);
    reg clk=0; always #5 clk=~clk;
    reg rst_n=0;
    reg req_valid=0; wire req_ready;
    reg [1:0] req_op=0; reg [31:0] req_id=0;
    reg [TW-1:0] req_tag=0;
    reg [63:0] req_addr=0,req_victim_addr=0;
    reg [1023:0] req_data=0; reg [127:0] req_be=0,req_victim_be=0;
    reg [3:0] req_ready_sectors=0,req_pending_sectors=0;
    reg req_install_dirty=0,req_resources_ready=1;
    reg native_ready=1,native_abort=0; wire native_commit;
    wire [TW-1:0] native_tag; wire [PW-1:0] native_pid; wire [GEN_W-1:0] native_gen;
    wire rsp_valid,rsp_retry;reg rsp_ready=1;wire [31:0] rsp_id;
    wire [PW-1:0] rsp_pid;wire [GEN_W-1:0] rsp_gen;wire [1023:0] rsp_data;
    reg fill_valid=0;wire fill_ready,fill_dropped;
    reg [TW-1:0] fill_tag=0;reg [PW-1:0] fill_pid=0;reg [GEN_W-1:0] fill_gen=0;
    reg [3:0] fill_sectors=0;reg [1023:0] fill_data=0;
    reg [127:0] fill_be=0,fill_protect_be=0;
    reg pin_valid=0,pin_increment=0;wire pin_ready;reg [PW-1:0] pin_pid=0;reg [GEN_W-1:0] pin_gen=0;
    wire wb_valid;reg wb_ready=0;wire [1023:0] wb_data;wire [127:0] wb_be;
    wire [63:0] wb_addr;wire [WW-1:0] wb_ticket;wire [GEN_W-1:0] wb_ticket_gen;
    reg done_valid=0;wire done_ready,done_dropped;reg [WW-1:0] done_ticket=0;reg [GEN_W-1:0] done_gen=0;
    wire module_drained,generation_blocked;wire [WW:0] wad_count,wb_count;
    wire [9:0] reference_count;wire [3:0] ram_enable,ram_write;
    wire [4*RW-1:0] ram_row;wire [511:0] ram_be;wire [4095:0] ram_wdata,ram_rdata;
`ifdef EP_L2_FULL_TOP
    ep_l2_slice #(.MODE(MODE),.GEN_W(GEN_W),.N_TAG(N_TAG),.N_PAYLOAD(N_PAYLOAD),.N_WAD(N_WAD),.STATIC_WB(STATIC_WB)) integrated(.*);
    assign ram_enable=integrated.ram_enable;
`define CTRL integrated.controller
`else
    ep_l2_slice_ctrl #(.MODE(MODE),.GEN_W(GEN_W),.N_TAG(N_TAG),.N_PAYLOAD(N_PAYLOAD),.N_WAD(N_WAD),.STATIC_WB(STATIC_WB)) dut(.*);
    ep_l2_payload_banks #(.N_PAYLOAD(N_PAYLOAD)) banks(.*);
`define CTRL dut
`endif
    // Independent byte merge and immutable WB snapshots. Never consult the
    // RTL SRAM array, selector, versions or mapping to construct expected data.
    reg [1023:0] reference [0:N_TAG-1];
    reg [127:0] dirty_bytes [0:N_TAG-1];
    reg [63:0] address [0:N_TAG-1];
    reg [PW-1:0] handle_pid [0:N_TAG-1];
    reg [GEN_W-1:0] handle_gen [0:N_TAG-1];
    reg [1023:0] expected_wb_data [0:1023];
    reg [127:0] expected_wb_be [0:1023];
    reg [63:0] expected_wb_addr [0:1023];
    reg [WW-1:0] received_ticket [0:1023];
    reg [GEN_W-1:0] received_gen [0:1023];
    integer expected_wbs=0,received_wbs=0,completed_wbs=0,cycles=0,copy_reads=0,copy_writes=0,bank_ops=0;
    integer replies=0,accepted=0,aborted=0,conflicts=0,parallel_banks=0;reg [31:0] prng=32'h31d2c0de;
    reg random_backpressure=0;reg force_wb_block=1;reg force_rsp_block=0;
    reg [31:0] last_rsp_uid=0;reg [1023:0] last_rsp_data;
    reg last_rsp_retry;reg [PW-1:0] last_rsp_pid;reg [GEN_W-1:0] last_rsp_gen;
    reg [63:0] held_wb_addr;reg [1023:0] held_wb_data;reg [127:0] held_wb_be;
    reg wb_was_blocked=0;
    always @(negedge clk) begin
        if (rst_n) begin
            prng<={prng[30:0],prng[31]^prng[21]^prng[1]^prng[0]};
            wb_ready<=!force_wb_block && (!random_backpressure || prng[0]);
            rsp_ready<=!force_rsp_block && (!random_backpressure || prng[1]);
        end
    end
    always @(posedge clk) if (rst_n) begin
        cycles=cycles+1;
        if (cycles>30000) $fatal(1,"bounded fixture watchdog");
        for (integer b=0;b<4;b=b+1) if(ram_enable[b])bank_ops=bank_ops+1;
        if(`CTRL.ge && `CTRL.state==3)copy_reads=copy_reads+1;
        if(`CTRL.ge && `CTRL.state==5)copy_writes=copy_writes+1;
        if((`CTRL.requests[0] && `CTRL.requests[1] && `CTRL.request_banks[1:0]==`CTRL.request_banks[3:2]) ||
           (`CTRL.requests[1] && `CTRL.requests[2] && `CTRL.request_banks[3:2]==`CTRL.request_banks[5:4]))conflicts=conflicts+1;
        if((`CTRL.gf && `CTRL.ge) || (`CTRL.gf && `CTRL.gw) || (`CTRL.ge && `CTRL.gw))parallel_banks=parallel_banks+1;
        if(req_valid && req_ready)accepted=accepted+1;
        if(rsp_valid && rsp_ready) begin
            if(rsp_id<=last_rsp_uid) $fatal(1,"duplicate/reordered frontend completion");
            last_rsp_uid=rsp_id;last_rsp_data=rsp_data;last_rsp_retry=rsp_retry;
            last_rsp_pid=rsp_pid;last_rsp_gen=rsp_gen;
            if(rsp_retry)aborted=aborted+1;else replies=replies+1;
        end
        if(wb_was_blocked && (!wb_valid || wb_data!==held_wb_data || wb_addr!==held_wb_addr || wb_be!==held_wb_be))
            $fatal(1,"lower data snapshot changed while stalled");
        wb_was_blocked=wb_valid && !wb_ready;
        if(wb_was_blocked)begin held_wb_data=wb_data;held_wb_addr=wb_addr;held_wb_be=wb_be;end
        if(wb_valid && wb_ready) begin
            if(received_wbs>=expected_wbs || wb_addr!==expected_wb_addr[received_wbs] || wb_be!==expected_wb_be[received_wbs])
                $fatal(1,"WB identity/byte mask mismatch got addr%h expected%h",wb_addr,expected_wb_addr[received_wbs]);
            for(integer j=0;j<128;j=j+1)
                if(wb_be[j] && wb_data[8*j +:8]!==expected_wb_data[received_wbs][8*j +:8])
                    $fatal(1,"WB byte mismatch packet%0d byte%0d got%h expected%h",received_wbs,j,wb_data[8*j +:8],expected_wb_data[received_wbs][8*j +:8]);
            received_ticket[received_wbs]=wb_ticket;received_gen[received_wbs]=wb_ticket_gen;received_wbs=received_wbs+1;
        end
    end
    task tick;begin @(posedge clk);#1;end endtask
    task wait_replies(input integer previous);integer n;begin
        n=0;while(replies+aborted==previous && n<3000)begin tick();n=n+1;end
        if(n==3000)$fatal(1,"frontend progress timeout state%0d",`CTRL.state);
    end endtask
    task prepare(input integer op,input integer tag,input [63:0] addr,input [1023:0] data,input [127:0] be,input [3:0] readysec,input [3:0] pendingsec,input integer isdirty);
        begin
            @(negedge clk);req_op=op;req_tag=tag;req_addr=addr;req_victim_addr=address[tag];
            req_data=data;req_be=be;req_ready_sectors=readysec;req_pending_sectors=pendingsec;
            req_install_dirty=isdirty;req_victim_be=dirty_bytes[tag];req_id=req_id+1;req_valid=1;#1;
        end
    endtask
    task admit;integer n;begin
        n=0;while(!req_ready && n<3000)begin @(negedge clk);n=n+1;end
        if(!req_ready)$fatal(1,"request precheck timeout tag%0d op%0d WAD%0d WB%0d",req_tag,req_op,wad_count,wb_count);
        tick();req_valid=0;
    end endtask
    task merge_reference(input integer tag,input [1023:0] data,input [127:0] be);
        begin for(integer i=0;i<128;i=i+1)if(be[i])reference[tag][8*i +:8]=data[8*i +:8];end
    endtask
    task expect_writeback(input integer tag);begin
        expected_wb_data[expected_wbs]=reference[tag];expected_wb_be[expected_wbs]=dirty_bytes[tag];
        expected_wb_addr[expected_wbs]=address[tag];expected_wbs=expected_wbs+1;
    end endtask
    task install(input integer tag,input [63:0] addr,input [1023:0] data,input [127:0] be,input [3:0] rsec,input [3:0] psec,input integer dirty_input);
        integer previous;begin
            previous=replies+aborted;
            if(|dirty_bytes[tag])expect_writeback(tag);
            prepare(0,tag,addr,data,be,rsec,psec,dirty_input);admit();wait_replies(previous);
            if(last_rsp_retry)$fatal(1,"unexpected rollback");
            reference[tag]=0;merge_reference(tag,data,be);address[tag]=addr;
            dirty_bytes[tag]=dirty_input?be:0;handle_pid[tag]=last_rsp_pid;handle_gen[tag]=last_rsp_gen;
            if(handle_pid[tag]%4!=tag%4)$fatal(1,"landing bank class changed");
        end
    endtask
    task write_bytes(input integer tag,input [1023:0] data,input [127:0] be);
        integer previous;begin
            previous=replies+aborted;prepare(2,tag,address[tag],data,be,0,0,0);admit();wait_replies(previous);
            merge_reference(tag,data,be);dirty_bytes[tag]=dirty_bytes[tag]|be;
        end
    endtask
    task read_check(input integer tag);
        integer previous;begin
            previous=replies+aborted;prepare(1,tag,address[tag],0,0,15,0,0);admit();wait_replies(previous);
            if(last_rsp_data!==reference[tag])$fatal(1,"read byte reference mismatch tag%0d",tag);
        end
    endtask
    task wait_lower;integer n;begin
        n=0;while(received_wbs<expected_wbs && n<5000)begin tick();n=n+1;end
        if(received_wbs!=expected_wbs || wb_count!=0)$fatal(1,"lower drain timeout");
    end endtask
    task complete_one;integer n;begin
        if(completed_wbs>=received_wbs)$fatal(1,"completion before lower accept");
        @(negedge clk);done_ticket=received_ticket[completed_wbs];done_gen=received_gen[completed_wbs];done_valid=1;
        n=0;while(!done_ready && n<100)begin @(negedge clk);n=n+1;end
        if(!done_ready)$fatal(1,"set_done stuck");tick();done_valid=0;completed_wbs=completed_wbs+1;
    end endtask
    task close_wads;begin while(completed_wbs<received_wbs)complete_one();end endtask
    function automatic [1023:0] pattern(input integer seed);
        begin for(integer i=0;i<128;i=i+1)pattern[8*i +:8]=(seed*37+i*13) & 255;end
    endfunction

    integer previous,steps,drops=0,same_tag,fpair,lpair;reg [GEN_W-1:0] fgpair,lgpair;reg [PW-1:0] saved_pid;reg [GEN_W-1:0] saved_gen;
    reg [1023:0] old_snapshot,merge_line;reg [127:0] bmask;
    task reject_fill(input integer tag,input [PW-1:0] pid,input [GEN_W-1:0] gen,input [3:0] sectors);begin
      @(negedge clk);fill_valid=1;fill_tag=tag;fill_pid=pid;fill_gen=gen;fill_sectors=sectors;
      fill_be={128{1'b1}};fill_protect_be=0;fill_data=pattern(230);#1;
      if(!fill_ready || !fill_dropped || `CTRL.gf)$fatal(1,"wrong-owner/stale fill accepted tag%0d pid%0d",tag,pid);
      tick();fill_valid=0;drops=drops+1;
    end endtask
    initial begin
      for(integer i=0;i<N_TAG;i=i+1)begin reference[i]=0;dirty_bytes[i]=0;address[i]=0;handle_pid[i]=0;handle_gen[i]=0;end
      repeat(3)tick();rst_n=1;tick();
      install(1,64'h1000,pattern(1),{128{1'b1}},1,14,0);
      install(5,64'h5000,pattern(5),{128{1'b1}},15,0,0);
      install(4,64'h4400,pattern(44),{128{1'b1}},15,0,0);
      // Resident5 is live in the same bank. Match PID1/current GEN, wrong Tag5.
      reject_fill(5,handle_pid[1],handle_gen[1],14);
      // Hold a real read snapshot and an independent descriptor pin while fill
      // updates other sectors; the forward map must neither rebind nor mutate it.
      force_rsp_block=1;previous=replies+aborted;old_snapshot=reference[1];
      prepare(1,1,address[1],0,0,1,0,0);admit();repeat(6)tick();
      if(!rsp_valid || rsp_data!==old_snapshot || reference_count!=1)$fatal(1,"partial-sector read snapshot missing");
      @(negedge clk);pin_valid=1;pin_increment=1;pin_pid=handle_pid[1];pin_gen=handle_gen[1];#1;
      if(!pin_ready)$fatal(1,"descriptor pin blocked for held response");tick();pin_valid=0;
      reject_fill(5,handle_pid[1],handle_gen[1],14);
      @(negedge clk);fill_valid=1;fill_tag=1;fill_pid=handle_pid[1];fill_gen=handle_gen[1];
      fill_sectors=14;fill_be={128{1'b1}}<<32;fill_protect_be=0;fill_data=pattern(6);#1;
      steps=0;while(!fill_ready&&steps<100)begin @(negedge clk);steps=steps+1;end
      if(!fill_ready || fill_dropped)$fatal(1,"right-owner concurrent fill dropped");tick();fill_valid=0;
      merge_line=pattern(6);for(integer j=32;j<128;j=j+1)reference[1][j*8 +:8]=merge_line[j*8 +:8];
      if(!rsp_valid || rsp_data!==old_snapshot || reference_count!=2)$fatal(1,"fill mutated pinned response snapshot");
      force_rsp_block=0;wait_replies(previous);
      prepare(0,1,64'h1100,pattern(11),{128{1'b1}},15,0,0);repeat(4)tick();
      if(req_ready || reference_count!=1)$fatal(1,"descriptor pin allowed Tag rebind");req_valid=0;
      @(negedge clk);pin_valid=1;pin_increment=0;#1;if(!pin_ready)$fatal(1,"descriptor release lost");tick();pin_valid=0;
      read_check(1);saved_pid=handle_pid[1];saved_gen=handle_gen[1];
      install(1,64'h1200,pattern(12),{128{1'b1}},15,0,0);
      reject_fill(1,saved_pid,saved_gen,15); // stale GEN after clean reuse
      bmask=0;bmask[8 +:8]=255;write_bytes(1,pattern(13),bmask);
      saved_pid=handle_pid[1];saved_gen=handle_gen[1];
      install(1,64'h1300,pattern(14),{128{1'b1}},15,0,0);
      reject_fill(1,saved_pid,saved_gen,15); // Unified old WB-role, static old GEN
      // Same bank, DIFFERENT rows: P1 DATA service does not serialize two
      // GEN metadata writes (frontend clean replace + lower WB release).
      steps=0;while(!wb_valid&&steps<1000)begin tick();steps=steps+1;end
      if(!wb_valid)$fatal(1,"same-bank lower did not reach SEND");
      same_tag=MODE==1?5:4;native_ready=0;previous=replies+aborted;
      prepare(0,same_tag,64'h4500,pattern(45),{128{1'b1}},15,0,0);admit();
      force_wb_block=0;@(negedge clk);#1;native_ready=1;#1;
      fpair=`CTRL.frontend_generation_pid;lpair=`CTRL.active_pid;
      fgpair=`CTRL.generation_bits[fpair*GEN_W +:GEN_W];lgpair=`CTRL.generation_bits[lpair*GEN_W +:GEN_W];
      if(!`CTRL.fe_gen_write || !`CTRL.lower_accept || fpair==lpair || (fpair%4)!=(lpair%4))$fatal(1,"same-bank independent GEN pair absent");
      tick();if(`CTRL.generation_bits[fpair*GEN_W +:GEN_W]!==fgpair+GEN_W'(2) || `CTRL.generation_bits[lpair*GEN_W +:GEN_W]!==lgpair+GEN_W'(1))$fatal(1,"same-bank GEN pair incorrect");
      wait_replies(previous);reference[same_tag]=pattern(45);address[same_tag]=64'h4500;handle_pid[same_tag]=last_rsp_pid;handle_gen[same_tag]=last_rsp_gen;
      $display("R3_SAME_BANK_INDEPENDENT_GEN frontendPID%0d lowerPID%0d bank%0d PASS",fpair,lpair,fpair%4);
      wait_lower();close_wads();
      install(9,64'h9000,pattern(9),{128{1'b1}},0,15,0);
      if(MODE==1 && handle_pid[9]!=saved_pid)$fatal(1,"real cross-Tag physical reuse not reached");
      // Even a forged matching CURRENT GEN cannot make old Tag1 own Tag9's PID.
      reject_fill(1,handle_pid[9],handle_gen[9],15);
      reject_fill(9,handle_pid[9],saved_gen,15); // stale generation to current Tag
      @(negedge clk);fill_valid=1;fill_tag=9;fill_pid=handle_pid[9];fill_gen=handle_gen[9];
      fill_sectors=15;fill_be={128{1'b1}};fill_protect_be=0;fill_data=pattern(10);#1;
      steps=0;while(!fill_ready&&steps<100)begin @(negedge clk);steps=steps+1;end
      if(!fill_ready || fill_dropped)$fatal(1,"current forward-identity fill rejected");tick();fill_valid=0;reference[9]=pattern(10);
      read_check(9);read_check(1);read_check(5);read_check(4);
      if(drops!=6 || !module_drained || received_wbs!=1 || completed_wbs!=1 || reference_count!=0)$fatal(1,"owner stress exact drain failed");
      $display("R3_ACTUAL_OWNER_STRESS mode%0d drops6 snapshot-pin-fill rebind same-bank-double-GEN byteWB1 full-drain PASS cycles%0d",MODE,cycles);$finish;
    end
endmodule
