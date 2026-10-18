`timescale 1ns/1ps
module ep_l2_concurrency_r3_tb;
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

    integer previous,pairs=0,fp,lp,steps;reg [GEN_W-1:0] fg,lg;
    task wait_send;begin steps=0;while(!wb_valid&&steps<10000)begin tick();steps=steps+1;end if(!wb_valid)$fatal(1,"WB send did not arrive");end endtask
    task pair_check(input integer which,input integer delta);begin
        #1;if(!`CTRL.fe_gen_write || !`CTRL.lower_accept)$fatal(1,"required concurrent GEN writers absent case%0d",which);
        fp=`CTRL.frontend_generation_pid;lp=`CTRL.active_pid;
        if(fp==lp)$fatal(1,"directed independent GEN targets unexpectedly alias");
        fg=`CTRL.generation_bits[fp*GEN_W +:GEN_W];lg=`CTRL.generation_bits[lp*GEN_W +:GEN_W];
        tick();if(`CTRL.generation_bits[fp*GEN_W +:GEN_W]!==fg+GEN_W'(delta) || `CTRL.generation_bits[lp*GEN_W +:GEN_W]!==lg+GEN_W'(1))$fatal(1,"two actual GEN FF writes incorrect case%0d",which);
        pairs=pairs+1;$display("R3_ACTUAL_CONCURRENT_GEN case%0d frontendPID%0d +%0d lowerPID%0d +1 PASS",which,fp,delta,lp);
    end endtask
    initial begin
        for(integer i=0;i<N_TAG;i=i+1)begin reference[i]=0;dirty_bytes[i]=0;address[i]=0;handle_pid[i]=0;handle_gen[i]=0;end
        repeat(3)tick();rst_n=1;tick();
        install(0,64'h1000,pattern(1),{128{1'b1}},15,0,1);
        install(0,64'h2000,pattern(2),{128{1'b1}},15,0,1);
        install(2,64'h3000,pattern(3),{128{1'b1}},15,0,0);wait_send();
        // Same edge: clean resident install+2 and independent WB physical release+1.
        native_ready=0;previous=replies+aborted;
        prepare(0,2,64'h4000,pattern(4),{128{1'b1}},15,0,0);admit();
        force_wb_block=0;@(negedge clk);#1;native_ready=1;pair_check(1,2);
        wait_replies(previous);if(last_rsp_retry)$fatal(1,"commit pair retried");
        reference[2]=pattern(4);address[2]=64'h4000;handle_pid[2]=last_rsp_pid;handle_gen[2]=last_rsp_gen;
        read_check(2);close_wads();
        // Same edge: frontend dirty reservation+1 and independent WB release+1.
        force_wb_block=1;install(0,64'h5000,pattern(5),{128{1'b1}},15,0,1);wait_send();
        native_ready=0;previous=replies+aborted;
        prepare(0,0,64'h6000,pattern(6),{128{1'b1}},15,0,1);
        force_wb_block=0;wb_ready=1;#1;if(!req_ready)$fatal(1,"reservation precheck blocked");pair_check(2,1);req_valid=0;
        native_abort=1;tick();native_abort=0;native_ready=1;wait_replies(previous);
        if(!last_rsp_retry)$fatal(1,"reservation rollback response missing");read_check(0);close_wads();
        // Same edge: abort of a newly reserved payload+1 and old WB release+1.
        force_wb_block=1;install(0,64'h7000,pattern(7),{128{1'b1}},15,0,1);wait_send();
        native_ready=0;previous=replies+aborted;
        prepare(0,0,64'h8000,pattern(8),{128{1'b1}},15,0,1);admit();
        force_wb_block=0;@(negedge clk);#1;native_abort=1;pair_check(3,1);
        native_abort=0;native_ready=1;wait_replies(previous);
        if(!last_rsp_retry)$fatal(1,"concurrent abort/release retry missing");read_check(0);close_wads();
        if(pairs!=3 || !module_drained || received_wbs!=3 || completed_wbs!=3 || aborted!=2)$fatal(1,"concurrent fixture failed exact drain");
        $display("R3_ACTUAL_GEN_CONCURRENCY_FULL_CAPACITY mode%0d 3pairs byteWB3 rollback2 drain PASS cycles%0d",MODE,cycles);$finish;
    end
endmodule
