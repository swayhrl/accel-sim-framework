`timescale 1ns/1ps
module ep_l2_slice_tb;
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
    reg [127:0] mask;reg [1023:0] data;
    integer prev,cap,initial_expected;reg [PW-1:0] old_handle;reg [GEN_W-1:0] old_gen;
    initial begin
        for(integer i=0;i<N_TAG;i=i+1)begin reference[i]=0;dirty_bytes[i]=0;address[i]=0;handle_pid[i]=0;handle_gen[i]=0;end
        repeat(3)tick();rst_n=1;tick();
        if(GEN_W<8)begin
            // Small-width proof is exhaustion/refusal, never modulo wrap.
            install(0,64'h1000,pattern(1),{128{1'b1}},15,0,0);
            install(0,64'h2000,pattern(2),{128{1'b1}},15,0,0);
            install(0,64'h3000,pattern(3),{128{1'b1}},15,0,0);
            prepare(0,0,64'h4000,pattern(4),{128{1'b1}},15,0,0);
            repeat(6)tick();if(req_ready || !generation_blocked)$fatal(1,"generation wrap not refused");
            req_valid=0;$display("CASE generation exhaustion, no wrap PASS mode%0d G%0d",MODE,GEN_W);$finish;
        end
        // 1. Whole physical line / boundary addresses at full dimensions.
        install(N_TAG-1,64'h1000,pattern(1),{128{1'b1}},15,0,0);read_check(N_TAG-1);
        // Last static resident ID1023, and full SRAM last row exercised below
        // with an isolated wrapper boundary fixture.
        $display("CASE1 full-line byte data/mapping/bank-compatible handle PASS mode%0d",MODE);
        // 2. Legal 32/64-bit writes to disjoint bytes of the same sector.
        mask=0;mask[4 +:4]=15;write_bytes(N_TAG-1,pattern(2),mask);
        mask=0;mask[16 +:8]=255;write_bytes(N_TAG-1,pattern(3),mask);read_check(N_TAG-1);
        $display("CASE2 32/64-bit byte merge and untouched bytes PASS");
        // 3. Partial data + delayed fill, protected dirty-byte snapshot.
        mask=0;mask[0 +:4]=15;
        install(1,64'h5000,pattern(4),mask,0,15,1);
        @(negedge clk);fill_valid=1;fill_tag=1;fill_pid=handle_pid[1];fill_gen=handle_gen[1];fill_sectors=15;
        fill_be={128{1'b1}};fill_protect_be=mask;fill_data=pattern(5);#1;
        while(!fill_ready)@(negedge clk);tick();fill_valid=0;
        data=pattern(5);for(integer j=0;j<4;j=j+1)data[8*j +:8]=reference[1][8*j +:8];reference[1]=data;
        read_check(1);$display("CASE3 dirty bytes survive delayed fill PASS");
        // Additional controlled same-bank and independent-bank real traffic.
        for(integer bankcase=0;bankcase<2;bankcase=bankcase+1)begin
            install(3+bankcase,64'h8000+128*bankcase,0,{128{1'b1}},0,15,0);
            prev=replies+aborted;prepare(1,N_TAG-1,address[N_TAG-1],0,0,15,0,0);admit();
            @(negedge clk);fill_valid=1;fill_tag=3+bankcase;fill_pid=handle_pid[3+bankcase];
            fill_gen=handle_gen[3+bankcase];fill_sectors=15;fill_be={128{1'b1}};fill_protect_be=0;fill_data=pattern(40+bankcase);#1;
            while(!fill_ready)@(negedge clk);tick();fill_valid=0;
            reference[3+bankcase]=pattern(40+bankcase);wait_replies(prev);
            if(last_rsp_data!==reference[N_TAG-1])$fatal(1,"contended read snapshot changed");
            read_check(3+bankcase);
        end
        if(conflicts==0 || parallel_banks==0)$fatal(1,"bank contention/independence not exercised");
        $display("CASE3b actual same-bank contention and cross-bank parallel grants PASS");
        // 4. Descriptor pin stops replacement; read response holds snapshot.
        force_rsp_block=1;prev=replies+aborted;prepare(1,1,address[1],0,0,15,0,0);admit();
        repeat(6)tick();if(!rsp_valid || reference_count!=1 || rsp_data!==reference[1])$fatal(1,"read snapshot/pin missing");
        @(negedge clk);pin_valid=1;pin_increment=1;pin_pid=handle_pid[1];pin_gen=handle_gen[1];#1;
        while(!pin_ready)@(negedge clk);tick();pin_valid=0;
        force_rsp_block=0;wait_replies(prev);
        prepare(0,1,64'h6000,pattern(6),{128{1'b1}},15,0,1);
        repeat(5)tick();if(req_ready || wad_count!=0)$fatal(1,"pin allowed partial replacement");req_valid=0;
        @(negedge clk);pin_valid=1;pin_increment=0;#1;while(!pin_ready)@(negedge clk);tick();pin_valid=0;
        $display("CASE4 response snapshot/backpressure and real pins PASS");
        // 4b. Acquisition and a conflicting descriptor pin must not both fire
        // on the IDLE admission edge. Cover dirty/clean replace, write, and
        // invalidate; abort before native commit preserves independent bytes.
        for(integer race=0;race<4;race=race+1)begin
            prev=replies+aborted;native_ready=0;
            prepare(race<2?0:race==2?2:3,race==0 || race==2?1:3,
                    64'hb000+128*race,pattern(60+race),{128{1'b1}},15,0,1);
            pin_valid=1;pin_increment=1;pin_pid=handle_pid[req_tag];pin_gen=handle_gen[req_tag];#1;
            if(!req_ready || pin_ready)$fatal(1,"PIN_ADMISSION_RACE op%0d req_ready%0b pin_ready%0b",req_op,req_ready,pin_ready);
            admit();pin_valid=0;repeat(8)tick();
            if(reference_count!=0)$fatal(1,"conflicting pin admitted with destructive acquisition");
            native_abort=1;tick();native_abort=0;wait_replies(prev);native_ready=1;
            if(!last_rsp_retry || wad_count!=0 || wb_count!=0)$fatal(1,"race rollback leaked reservation");
        end
        // No global pin block: independent resident reference can be granted
        // concurrently with the selected victim's acquisition and then released.
        prev=replies+aborted;native_ready=0;
        prepare(0,1,64'hc000,pattern(64),{128{1'b1}},15,0,1);
        pin_valid=1;pin_increment=1;pin_pid=handle_pid[N_TAG-1];pin_gen=handle_gen[N_TAG-1];#1;
        if(!req_ready || !pin_ready)$fatal(1,"unrelated pin unnecessarily serialized");
        admit();pin_valid=0;if(reference_count!=1)$fatal(1,"independent pin lost");
        @(negedge clk);pin_valid=1;pin_increment=0;#1;
        if(!pin_ready)$fatal(1,"independent pin release blocked");tick();pin_valid=0;
        repeat(8)tick();native_abort=1;tick();native_abort=0;wait_replies(prev);native_ready=1;
        if(reference_count!=0 || wad_count!=0 || wb_count!=0)$fatal(1,"independent pin/abort leak");
        read_check(1);read_check(3);
        $display("CASE4b same-edge destructive acquisition/pin exclusion and unrelated-pin parallelism PASS");
`ifdef EP_L2_PIN_ADMISSION_ONLY
        $finish;
`endif
        // 5. Native precommit rollback after real staged copy; fixed victim
        // survives changes to raw upstream Tag input after admission.
        prev=replies+aborted;native_ready=0;
        prepare(0,1,64'h6000,pattern(6),{128{1'b1}},15,0,1);admit();
        req_tag=2;repeat(8)tick();
        if(native_tag!=1 || wad_count!=1 || wb_count!=0)$fatal(1,"victim binding/reservation");
        native_abort=1;tick();native_abort=0;wait_replies(prev);native_ready=1;
        if(!last_rsp_retry || wad_count!=0 || wb_count!=0)$fatal(1,"rollback leak");
        read_check(1);$display("CASE5 native rollback/fixed victim/exact-once release PASS");
        // 6. Native dirty commit, REAL static copying versus in-place U.
        install(1,64'h6000,pattern(6),{128{1'b1}},15,0,1);
        repeat(7)tick();if(!wb_valid || wad_count!=1 || wb_count!=1)$fatal(1,"WB not retained");
        force_wb_block=0;wait_lower();if(wad_count!=1)$fatal(1,"WAD freed at lower_accept");
        $display("CASE6 real WB bytes/copy/in-place/lower_accept split PASS");
        // 7. While old payload may be reused, old line is blocked until done.
        prepare(0,2,64'h5000,pattern(7),{128{1'b1}},15,0,0);
        repeat(5)tick();if(req_ready)$fatal(1,"same-line WAD hazard missing");req_valid=0;
        complete_one();install(2,64'h5000,pattern(7),{128{1'b1}},15,0,0);
        $display("CASE7 old-address hazard until set_done PASS");
        // 8. Stale lower event cannot mutate a reused incarnation.
        old_handle=handle_pid[2];old_gen=handle_gen[2];
        install(2,64'h7000,pattern(8),{128{1'b1}},0,15,0);
        @(negedge clk);fill_valid=1;fill_pid=old_handle;fill_gen=old_gen;fill_tag=2;fill_sectors=15;
        fill_data=0;fill_be={128{1'b1}};fill_protect_be=0;#1;
        if(!fill_ready || !fill_dropped)$fatal(1,"stale fill not rejected");tick();fill_valid=0;
        if(`CTRL.sectors_pending_bits[handle_pid[2]*4 +:4]!=15)$fatal(1,"late old generation consumed new fill state");
        @(negedge clk);fill_valid=1;fill_pid=handle_pid[2];fill_gen=handle_gen[2];fill_data=pattern(8);#1;
        if(fill_dropped)$fatal(1,"fresh generation was corrupted by old fill");
        while(!fill_ready)@(negedge clk);tick();fill_valid=0;read_check(2);
        @(negedge clk);done_valid=1;done_ticket=received_ticket[0];done_gen=received_gen[0];#1;
        if(!done_ready || !done_dropped)$fatal(1,"stale set_done accepted");tick();done_valid=0;
        $display("CASE8 late fill/completion identity rejection PASS");
        // 9. Real local WB quota, 16/64 static; U retains >16 without copy.
        force_wb_block=1;tick();cap=MODE==1?20:STATIC_WB;
        install(0,64'h10000,pattern(9),{128{1'b1}},15,0,1);
        for(integer i=0;i<cap;i=i+1)install(0,64'h20000+128*i,pattern(10+i),{128{1'b1}},15,0,1);
        if(wb_count!=cap || wad_count!=cap)$fatal(1,"local WB capacity wrong %0d expected%0d",wb_count,cap);
        if(MODE!=1)begin
            prepare(0,0,64'h90000,pattern(90),{128{1'b1}},15,0,1);
            repeat(10)tick();if(req_ready || wad_count!=cap || wb_count!=cap)$fatal(1,"full quota partially committed");
        end
        @(negedge clk);done_valid=1;done_ticket=received_ticket[0];done_gen=received_gen[0];#1;
        if(!done_ready || !done_dropped)$fatal(1,"old WAD generation aliased reused live entry");
        tick();done_valid=0;if(wad_count!=cap)$fatal(1,"stale done freed reused WAD");
        if(MODE!=1)begin
            // The very same refused requester remains asserted until credit
            // returns. No cancellation/reissue can hide a duplicate reserve.
            prev=replies+aborted;expect_writeback(0);force_wb_block=0;admit();wait_replies(prev);
            reference[0]=pattern(90);dirty_bytes[0]={128{1'b1}};address[0]=64'h90000;
            handle_pid[0]=last_rsp_pid;handle_gen[0]=last_rsp_gen;
        end else force_wb_block=0;
        wait_lower();close_wads();read_check(0);
        $display("CASE9 full-dimension actual WB peak%0d refusal/SAME-request-credit-recovery/versions PASS",cap);
        // WAD can remain full even with every local WB payload already freed.
        for(integer w=0;w<N_WAD;w=w+1)install(0,64'h100000+128*w,pattern(200+w),{128{1'b1}},15,0,1);
        wait_lower();if(wad_count!=N_WAD || wb_count!=0)$fatal(1,"WAD128 lower-sent pressure not reached");
        prepare(0,0,64'h900000,pattern(512),{128{1'b1}},15,0,1);
        repeat(10)tick();if(req_ready || wad_count!=N_WAD)$fatal(1,"WAD129 partial admission");
        prev=replies+aborted;expect_writeback(0);complete_one();admit();wait_replies(prev);
        reference[0]=pattern(512);dirty_bytes[0]={128{1'b1}};address[0]=64'h900000;
        handle_pid[0]=last_rsp_pid;handle_gen[0]=last_rsp_gen;
        wait_lower();close_wads();read_check(0);
        $display("CASE9b WAD128 full after lower accept,129th same-request resume/FIFO-wrap/exact drain PASS");
        // 10. Small reproducible random ready/valid delays and byte masks.
        random_backpressure=1;
        for(integer n=0;n<24;n=n+1)begin
            mask=0;mask[(n%16)*8 +:8]=255;
            write_bytes(0,pattern(n+100),mask);read_check(0);
        end
        random_backpressure=0;repeat(8)tick();
        if(!module_drained || reference_count!=0 || wb_count!=0 || wad_count!=0 || received_wbs!=expected_wbs || accepted!=replies+aborted)
            $fatal(1,"terminal resource/request/WB leak");
        if(MODE==1 && (copy_reads!=0 || copy_writes!=0))$fatal(1,"Unified copied bytes");
        if(MODE!=1 && (copy_reads==0 || copy_reads!=copy_writes))$fatal(1,"static copy optimized/dead");
        $display("CASE10 random backpressure/byte reference/exact-once/drain PASS");
        $display("RTL_RESULT mode=%0d tags=%0d physical=%0d wb_peak=%0d WAD=%0d gen=%0d accepted=%0d replies=%0d rollback=%0d WB=%0d copy_read=%0d copy_write=%0d bank_ops=%0d conflicts=%0d parallel_banks=%0d cycles=%0d PASS",
            MODE,N_TAG,N_PAYLOAD,cap,N_WAD,GEN_W,accepted,replies,aborted,received_wbs,copy_reads,copy_writes,bank_ops,conflicts,parallel_banks,cycles);
        $finish;
    end
endmodule
