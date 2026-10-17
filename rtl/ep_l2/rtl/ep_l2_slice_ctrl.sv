// Single-slice finite WB changed-path prototype. Traditional Tag lookup/LRU,
// byte-dirty bookkeeping and Line-MSHR policy are explicit upstream boundaries.
// MODE: 0=B16, 1=Unified, 2=S64. No Ideal, TVD, RO or P2 implementation.
module ep_l2_slice_ctrl #(
    parameter integer MODE=0, N_TAG=1024, N_PAYLOAD=1168,
    parameter integer STATIC_WB=(MODE==2 ? 64 : 16), N_WAD=128,
    parameter integer GEN_W=32, ADDR_W=64,
    parameter integer TAG_W=$clog2(N_TAG), PID_W=$clog2(N_PAYLOAD),
    parameter integer WAD_W=$clog2(N_WAD), ROW_W=$clog2(N_PAYLOAD/4)
)(
    input wire clk, rst_n,
    // ops: 0=install/replace, 1=resident read, 2=resident byte write, 3=clean invalidate
    input wire req_valid, output wire req_ready,
    input wire [1:0] req_op, input wire [31:0] req_id,
    input wire [TAG_W-1:0] req_tag,
    input wire [ADDR_W-1:0] req_addr, req_victim_addr,
    input wire [1023:0] req_data,
    input wire [127:0] req_be, req_victim_be,
    input wire [3:0] req_ready_sectors, req_pending_sectors,
    input wire req_install_dirty, req_resources_ready,
    // Approval is a reservation/precheck, NOT the Tag commit handshake.
    // The upstream Tag changes only on native_commit, using captured native_tag.
    input wire native_ready, native_abort,
    output wire native_commit,
    output wire [TAG_W-1:0] native_tag,
    output wire [PID_W-1:0] native_pid,
    output wire [GEN_W-1:0] native_gen,
    output wire rsp_valid, input wire rsp_ready,
    output wire [31:0] rsp_id, output wire rsp_retry,
    output wire [PID_W-1:0] rsp_pid,
    output wire [GEN_W-1:0] rsp_gen,
    output reg [1023:0] rsp_data,
    // Real lower-fill identity. Dirty byte protection comes from the reused
    // native Tag byte mask; the AND/byte write path is implemented here.
    input wire fill_valid, output wire fill_ready,
    input wire [TAG_W-1:0] fill_tag,
    input wire [PID_W-1:0] fill_pid,
    input wire [GEN_W-1:0] fill_gen,
    input wire [3:0] fill_sectors,
    input wire [1023:0] fill_data,
    input wire [127:0] fill_be, fill_protect_be,
    output wire fill_dropped,
    // One finite descriptor-reference operation per cycle. Global max512,
    // per physical line max32. Internal read snapshots share this accounting.
    input wire pin_valid, output wire pin_ready, input wire pin_increment,
    input wire [PID_W-1:0] pin_pid, input wire [GEN_W-1:0] pin_gen,
    output wire wb_valid, input wire wb_ready,
    output reg [1023:0] wb_data,
    output wire [127:0] wb_be,
    output wire [ADDR_W-1:0] wb_addr,
    output wire [WAD_W-1:0] wb_ticket,
    output wire [GEN_W-1:0] wb_ticket_gen,
    input wire done_valid, output wire done_ready,
    input wire [WAD_W-1:0] done_ticket,
    input wire [GEN_W-1:0] done_gen,
    output wire done_dropped,
    output wire module_drained, output wire generation_blocked,
    output reg [WAD_W:0] wad_count, wb_count,
    output reg [9:0] reference_count,
    output wire [3:0] ram_enable, ram_write,
    output wire [4*ROW_W-1:0] ram_row,
    output wire [511:0] ram_be,
    output wire [4095:0] ram_wdata,
    input wire [4095:0] ram_rdata
);
    localparam [2:0] FREE=0, RESIDENT=1, WB=2, RESERVE_R=3, RESERVE_W=4;
    localparam [3:0] IDLE=0, HIT_READ=1, READ_RETURN=2, COPY_READ=3,
                     COPY_RETURN=4, COPY_WRITE=5, COMMIT=6, RESPONSE=7;
    localparam [2:0] W_IDLE=0, W_RETURN=1, W_BUFFER=2, W_SEND=3;
    localparam [1:0] L_NONE=0, L_COPY=1, L_WB=2;
    localparam [GEN_W-1:0] GMAX={GEN_W{1'b1}};
    localparam integer WB_BEGIN=N_PAYLOAD-STATIC_WB;
    reg [2:0] role [0:N_PAYLOAD-1];
    reg [GEN_W-1:0] generation [0:N_PAYLOAD-1];
    reg [TAG_W-1:0] owner_tag [0:N_PAYLOAD-1];
    reg [5:0] pins [0:N_PAYLOAD-1];
    reg [3:0] sectors_ready [0:N_PAYLOAD-1], sectors_pending [0:N_PAYLOAD-1], dirty [0:N_PAYLOAD-1];
    reg [PID_W-1:0] tag_map [0:N_TAG-1];
    reg [N_TAG-1:0] tag_live;
    reg [N_WAD-1:0] wad_live, wad_sent;
    reg [ADDR_W-1:0] wad_addr [0:N_WAD-1];
    reg [GEN_W-1:0] wad_generation [0:N_WAD-1], wad_payload_gen [0:N_WAD-1];
    reg [PID_W-1:0] wad_payload [0:N_WAD-1];
    reg [127:0] wad_bytes [0:N_WAD-1];
    reg [WAD_W-1:0] wb_fifo [0:N_WAD-1];
    reg [WAD_W-1:0] wb_head, wb_tail, active_wad;
    reg [3:0] state;
    reg [2:0] wb_state;
    reg [1:0] latch_owner;
    // Shared, REAL 128B copy/read-return latch in every organization. In U it
    // carries WB read returns; B/S additionally use it for static source copies.
    reg [1023:0] copy_latch;
    reg [1:0] p_op;
    reg [31:0] p_id;
    reg [TAG_W-1:0] p_tag;
    reg [PID_W-1:0] p_old, p_landing, p_staging;
    reg [GEN_W-1:0] p_result_gen;
    reg [WAD_W-1:0] p_wad;
    reg p_old_live, p_dirty, p_new_reserved, p_has_wad, p_retry;
    reg [1023:0] p_data;
    reg [127:0] p_be;
    reg [3:0] p_ready, p_pending;
    reg p_install_dirty;
    reg [15:0] pending_sector_count;
    wire old_live = req_tag < N_TAG && tag_live[req_tag];
    wire [PID_W-1:0] old_pid = old_live ? tag_map[req_tag] : req_tag;
    wire evict_dirty = req_op==0 && old_live && |dirty[old_pid];
    function automatic [3:0] byte_sectors(input [127:0] be);
        integer s; begin
            for (s=0;s<4;s=s+1) byte_sectors[s]=|be[s*32 +:32];
        end
    endfunction
    function automatic [2:0] pop4(input [3:0] v);
        begin pop4={2'b0,v[0]}+v[1]+v[2]+v[3]; end
    endfunction
    reg hazard, have_wad, have_landing, have_staging, free_bank_exists;
    reg [WAD_W-1:0] free_wad;
    reg [PID_W-1:0] free_landing, free_staging;
    integer a;
    // These are real combinational CAM/priority encoders, included in mapped
    // cost and timing. They are not free C++ searches or inferred SRAM ports.
    always @* begin
        hazard=0; have_wad=0; free_wad=0;
        for (integer i=0;i<N_WAD;i=i+1) begin
            if (wad_live[i] && wad_addr[i]==req_addr) hazard=1;
            if (!have_wad && !wad_live[i] && wad_generation[i]!=GMAX) begin
                free_wad=i; have_wad=1;
            end
        end
        have_landing=0; have_staging=0; free_landing=0; free_staging=0; free_bank_exists=0;
        for (integer j=0;j<N_PAYLOAD;j=j+1) begin
            if (role[j]==FREE && (j%4)==(req_tag%4)) free_bank_exists=1;
            if (role[j]==FREE && generation[j] < GMAX-1) begin
                if (MODE==1 && !have_landing && (j%4)==(req_tag%4)) begin
                    have_landing=1; free_landing=j;
                end
                if (MODE!=1 && !have_staging && j>=WB_BEGIN) begin
                    have_staging=1; free_staging=j;
                end
            end
        end
    end
    wire old_unpinned = !old_live || (pins[old_pid]==0 && sectors_pending[old_pid]==0);
    wire reuse_ok = !old_live ? generation[old_pid]<GMAX-1 : generation[old_pid]<GMAX-2;
    wire install_ok = old_unpinned && (!evict_dirty || (have_wad && (MODE==1 || have_staging))) &&
        (MODE==1 && (evict_dirty || !old_live) ? have_landing : reuse_ok);
    wire read_ok = old_live && role[old_pid]==RESIDENT &&
        pins[old_pid]<32 && reference_count<512 && req_ready_sectors!=0 &&
        (req_ready_sectors & ~sectors_ready[old_pid])==0;
    wire write_ok = old_live && old_unpinned;
    wire invalidate_ok = old_live && old_unpinned && dirty[old_pid]==0 && generation[old_pid]!=GMAX;
    assign generation_blocked = state==IDLE && req_valid &&
        (req_op==0 && !install_ok && old_unpinned &&
         ((MODE!=1 && !reuse_ok) || (MODE==1 && !have_landing && free_bank_exists)));
    assign req_ready = rst_n && state==IDLE && req_resources_ready && !hazard &&
        req_tag<N_TAG && (req_op==0 ? install_ok : req_op==1 ? read_ok : req_op==2 ? write_ok : invalidate_ok);
    wire req_fire=req_valid && req_ready;
    wire abort_fire=native_abort && state!=IDLE && state!=RESPONSE && p_op!=1;
    wire [GEN_W-1:0] landing_generation = p_new_reserved ? generation[p_landing] :
        generation[p_landing]+(p_old_live ? 2 : 1);
    wire fill_identity=fill_pid<N_PAYLOAD && role[fill_pid]==RESIDENT &&
        generation[fill_pid]==fill_gen && owner_tag[fill_pid]==fill_tag &&
        fill_sectors!=0 && (fill_sectors & ~sectors_pending[fill_pid])==0;
    wire [WAD_W-1:0] head_wad=wb_fifo[wb_head];
    wire [PID_W-1:0] head_pid=wad_payload[head_wad];
    reg fe_request, fe_write;
    reg [PID_W-1:0] fe_pid;
    reg [127:0] fe_bytes;
    reg [1023:0] fe_data;
    always @* begin
        fe_request=0; fe_write=0; fe_pid=p_old; fe_bytes=p_be; fe_data=p_data;
        if (!abort_fire) begin
            if (state==HIT_READ) fe_request=1;
            if (state==COPY_READ && latch_owner==L_NONE) fe_request=1;
            if (state==COPY_WRITE && latch_owner==L_COPY) begin
                fe_request=1; fe_pid=p_staging; fe_write=1;
                fe_bytes={128{1'b1}}; fe_data=copy_latch;
            end
            if (state==COMMIT && native_ready && p_op!=3 && |p_be) begin
                fe_request=1; fe_pid=p_landing; fe_write=1;
            end
        end
    end
    wire wb_request=wb_state==W_IDLE && wb_count!=0 && latch_owner==L_NONE &&
        state!=COPY_READ && state!=COPY_RETURN && state!=COPY_WRITE;
    wire [2:0] requests={wb_request,fe_request,(fill_valid && fill_identity)};
    wire [5:0] request_banks={head_pid[1:0],fe_pid[1:0],fill_pid[1:0]};
    wire [2:0] grants;
    ep_l2_bank_arbiter arbiter(clk,rst_n,requests,request_banks,grants);
    wire gf=grants[0] && rst_n, ge=grants[1] && rst_n, gw=grants[2] && rst_n;
    reg [3:0] bank_enable, bank_write;
    reg [4*ROW_W-1:0] bank_row;
    reg [511:0] bank_bytes;
    reg [4095:0] bank_data;
    always @* begin
        bank_enable=0; bank_write=0; bank_row=0; bank_bytes=0; bank_data=0;
        if (gf) begin
            bank_enable[fill_pid[1:0]]=1; bank_write[fill_pid[1:0]]=1;
            bank_row[fill_pid[1:0]*ROW_W +: ROW_W]=fill_pid>>2;
            bank_bytes[fill_pid[1:0]*128 +:128]=fill_be & ~fill_protect_be;
            bank_data[fill_pid[1:0]*1024 +:1024]=fill_data;
        end
        if (ge) begin
            bank_enable[fe_pid[1:0]]=1; bank_write[fe_pid[1:0]]=fe_write;
            bank_row[fe_pid[1:0]*ROW_W +:ROW_W]=fe_pid>>2;
            bank_bytes[fe_pid[1:0]*128 +:128]=fe_bytes;
            bank_data[fe_pid[1:0]*1024 +:1024]=fe_data;
        end
        if (gw) begin
            bank_enable[head_pid[1:0]]=1; bank_write[head_pid[1:0]]=0;
            bank_row[head_pid[1:0]*ROW_W +:ROW_W]=head_pid>>2;
        end
    end
    assign ram_enable=bank_enable; assign ram_write=bank_write;
    assign ram_row=bank_row; assign ram_be=bank_bytes; assign ram_wdata=bank_data;
    assign fill_ready=rst_n && (!fill_identity || gf);
    assign fill_dropped=fill_valid && fill_ready && !fill_identity;
    wire fill_fire=fill_valid && fill_ready && fill_identity;
    assign native_commit=state==COMMIT && native_ready && !abort_fire &&
        (p_op==3 || p_be==0 || ge);
    assign native_tag=p_tag; assign native_pid=p_landing;
    assign native_gen=p_op==0 ? landing_generation : generation[p_landing];
    assign rsp_valid=state==RESPONSE; assign rsp_retry=p_retry;
    assign rsp_id=p_id; assign rsp_pid=p_landing; assign rsp_gen=p_result_gen;
    wire rsp_fire=rsp_valid && rsp_ready;
    wire internal_pin_add=req_fire && req_op==1;
    wire internal_pin_sub=rsp_fire && p_op==1;
    assign pin_ready=rst_n && pin_pid<N_PAYLOAD && role[pin_pid]==RESIDENT && generation[pin_pid]==pin_gen &&
        !internal_pin_add && !internal_pin_sub &&
        !(state!=IDLE && state!=RESPONSE && p_old_live && pin_pid==p_old) &&
        (pin_increment ? pins[pin_pid]<32 && reference_count<512 : pins[pin_pid]!=0);
    wire pin_fire=pin_valid && pin_ready;
    assign wb_valid=wb_state==W_SEND;
    assign wb_be=wad_bytes[active_wad]; assign wb_addr=wad_addr[active_wad];
    assign wb_ticket=active_wad; assign wb_ticket_gen=wad_generation[active_wad];
    wire lower_accept=wb_valid && wb_ready;
    wire done_identity=done_ticket<N_WAD && wad_live[done_ticket] && wad_generation[done_ticket]==done_gen;
    assign done_ready=rst_n && (!done_identity || wad_sent[done_ticket]);
    assign done_dropped=done_valid && done_ready && !done_identity;
    wire done_fire=done_valid && done_ready && done_identity;
    wire wad_allocate=req_fire && evict_dirty;
    wire wad_rollback=abort_fire && p_has_wad;
    wire wb_enqueue=native_commit && p_dirty;
    assign module_drained=state==IDLE && wb_state==W_IDLE && wad_count==0 &&
        wb_count==0 && reference_count==0 && pending_sector_count==0;
    always @(posedge clk) begin
        if (!rst_n) begin
            state<=IDLE; wb_state<=W_IDLE; latch_owner<=L_NONE;
            tag_live<=0; wad_live<=0; wad_sent<=0;
            wad_count<=0; wb_count<=0; reference_count<=0; pending_sector_count<=0;
            wb_head<=0; wb_tail<=0; active_wad<=0;
            p_op<=0; p_id<=0; p_tag<=0; p_old<=0; p_landing<=0; p_staging<=0;
            p_result_gen<=0; p_wad<=0; p_old_live<=0; p_dirty<=0;
            p_new_reserved<=0; p_has_wad<=0; p_retry<=0;
            p_data<=0; p_be<=0; p_ready<=0; p_pending<=0; p_install_dirty<=0;
            // No reset of 1024-bit data holding registers is required: valid
            // bits guard them. SRAM contents likewise are never reset to DFFs.
            for (integer i=0;i<N_PAYLOAD;i=i+1) begin
                role[i]<=FREE; generation[i]<=0; owner_tag[i]<=0; pins[i]<=0;
                sectors_ready[i]<=0; sectors_pending[i]<=0; dirty[i]<=0;
            end
            for (integer t=0;t<N_TAG;t=t+1) tag_map[t]<=0;
            for (integer w=0;w<N_WAD;w=w+1) begin
                wad_generation[w]<=0; wad_addr[w]<=0; wad_payload[w]<=0;
                wad_payload_gen[w]<=0; wad_bytes[w]<=0; wb_fifo[w]<=0;
            end
        end else begin
            wad_count<=wad_count+wad_allocate-wad_rollback-done_fire;
            wb_count<=wb_count+wb_enqueue-lower_accept;
            reference_count<=reference_count+internal_pin_add-internal_pin_sub+
                (pin_fire && pin_increment)-(pin_fire && !pin_increment);
            pending_sector_count<=pending_sector_count+
                ((native_commit && p_op==0) ? pop4(p_pending) : 0)-
                (fill_fire ? pop4(fill_sectors) : 0);
            if (pin_fire) pins[pin_pid]<=pin_increment ? pins[pin_pid]+1 : pins[pin_pid]-1;
            if (fill_fire) begin
                sectors_ready[fill_pid]<=sectors_ready[fill_pid] | fill_sectors;
                sectors_pending[fill_pid]<=sectors_pending[fill_pid] & ~fill_sectors;
            end
            if (done_fire) begin wad_live[done_ticket]<=0; wad_sent[done_ticket]<=0; end
            if (req_fire) begin
                p_op<=req_op; p_id<=req_id; p_tag<=req_tag; p_old<=old_pid;
                p_old_live<=old_live; p_dirty<=evict_dirty; p_has_wad<=evict_dirty;
                p_retry<=0; p_data<=req_data; p_be<=req_be;
                p_ready<=req_ready_sectors; p_pending<=req_pending_sectors;
                p_install_dirty<=req_install_dirty; p_new_reserved<=0;
                p_landing<=old_pid;
                p_result_gen<=old_live ? generation[old_pid] : 0;
                if (req_op==1) begin pins[old_pid]<=pins[old_pid]+1; state<=HIT_READ; end
                else begin
                    state<=COMMIT;
                    if (req_op==0) begin
                        if (MODE==1 && (evict_dirty || !old_live)) begin
                            p_landing<=free_landing; p_new_reserved<=1;
                            role[free_landing]<=RESERVE_R;
                            generation[free_landing]<=generation[free_landing]+1;
                            owner_tag[free_landing]<=req_tag;
                        end
                        if (evict_dirty) begin
                            p_wad<=free_wad; wad_live[free_wad]<=1; wad_sent[free_wad]<=0;
                            wad_generation[free_wad]<=wad_generation[free_wad]+1;
                            wad_addr[free_wad]<=req_victim_addr; wad_bytes[free_wad]<=req_victim_be;
                            if (MODE==1) begin
                                p_staging<=old_pid; wad_payload[free_wad]<=old_pid;
                                wad_payload_gen[free_wad]<=generation[old_pid];
                            end else begin
                                p_staging<=free_staging; wad_payload[free_wad]<=free_staging;
                                generation[free_staging]<=generation[free_staging]+1;
                                role[free_staging]<=RESERVE_W;
                                wad_payload_gen[free_wad]<=generation[free_staging]+1;
                                state<=COPY_READ;
                            end
                        end
                    end
                end
            end
            if (ge && state==HIT_READ) state<=READ_RETURN;
            if (state==READ_RETURN) begin
                rsp_data<=ram_rdata[p_old[1:0]*1024 +:1024]; state<=RESPONSE;
                p_result_gen<=generation[p_old];
            end
            if (ge && state==COPY_READ) begin state<=COPY_RETURN; latch_owner<=L_COPY; end
            if (state==COPY_RETURN) begin
                copy_latch<=ram_rdata[p_old[1:0]*1024 +:1024]; state<=COPY_WRITE;
            end
            if (ge && state==COPY_WRITE) begin latch_owner<=L_NONE; state<=COMMIT; end
            if (native_commit) begin
                if (p_op==0) begin
                    if (p_dirty) begin
                        role[p_staging]<=WB; wb_fifo[wb_tail]<=p_wad; wb_tail<=wb_tail+1;
                    end
                    if (!p_new_reserved) generation[p_landing]<=landing_generation;
                    role[p_landing]<=RESIDENT; owner_tag[p_landing]<=p_tag;
                    sectors_ready[p_landing]<=p_ready; sectors_pending[p_landing]<=p_pending;
                    dirty[p_landing]<=p_install_dirty ? byte_sectors(p_be) : 0;
                    tag_map[p_tag]<=p_landing; tag_live[p_tag]<=1; p_result_gen<=landing_generation;
                end else if (p_op==2) begin
                    dirty[p_landing]<=dirty[p_landing] | byte_sectors(p_be);
                    sectors_ready[p_landing]<=sectors_ready[p_landing] | p_ready;
                end else if (p_op==3) begin
                    role[p_landing]<=FREE; generation[p_landing]<=generation[p_landing]+1;
                    tag_live[p_tag]<=0; sectors_ready[p_landing]<=0; dirty[p_landing]<=0;
                end
                state<=RESPONSE;
            end
            if (abort_fire) begin
                if (p_has_wad) wad_live[p_wad]<=0;
                if (p_new_reserved) begin
                    role[p_landing]<=FREE; generation[p_landing]<=generation[p_landing]+1;
                end
                if (p_dirty && MODE!=1) begin
                    role[p_staging]<=FREE; generation[p_staging]<=generation[p_staging]+1;
                    if (latch_owner==L_COPY) latch_owner<=L_NONE;
                end
                p_retry<=1; state<=RESPONSE;
            end
            if (rsp_fire) begin
                if (p_op==1) pins[p_landing]<=pins[p_landing]-1;
                state<=IDLE;
            end
            if (gw) begin active_wad<=head_wad; wb_state<=W_RETURN; latch_owner<=L_WB; end
            if (wb_state==W_RETURN) begin
                copy_latch<=ram_rdata[wad_payload[active_wad][1:0]*1024 +:1024]; wb_state<=W_BUFFER;
            end
            if (wb_state==W_BUFFER) begin wb_data<=copy_latch; latch_owner<=L_NONE; wb_state<=W_SEND; end
            if (lower_accept) begin
                role[wad_payload[active_wad]]<=FREE;
                generation[wad_payload[active_wad]]<=generation[wad_payload[active_wad]]+1;
                sectors_ready[wad_payload[active_wad]]<=0; dirty[wad_payload[active_wad]]<=0;
                wad_sent[active_wad]<=1; wb_head<=wb_head+1; wb_state<=W_IDLE;
            end
        end
    end
`ifndef SYNTHESIS
    initial begin
        if (N_PAYLOAD%4 || N_TAG%4 || N_PAYLOAD<=N_TAG+STATIC_WB ||
            N_WAD!=(1<<WAD_W) || GEN_W<3 || MODE<0 || MODE>2) $fatal(1,"invalid RTL parameters");
    end
    always @(posedge clk) if (rst_n) begin
        if (wad_count>N_WAD || wb_count>wad_count || reference_count>512) $fatal(1,"resource overflow");
        if ((gf && ge && fill_pid[1:0]==fe_pid[1:0]) ||
            (gf && gw && fill_pid[1:0]==head_pid[1:0]) ||
            (ge && gw && fe_pid[1:0]==head_pid[1:0])) $fatal(1,"P1 bank oversubscription");
        if (gw && (role[head_pid]!=WB || generation[head_pid]!=wad_payload_gen[head_wad])) $fatal(1,"stale WB handle");
        if (lower_accept && generation[wad_payload[active_wad]]==GMAX) $fatal(1,"generation wrap");
    end
`endif
endmodule
