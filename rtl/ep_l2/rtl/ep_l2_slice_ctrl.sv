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
    wire [N_TAG*PID_W-1:0] tag_map_bits;
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
    wire [N_PAYLOAD*3-1:0] role_bits;
    wire [N_PAYLOAD*GEN_W-1:0] generation_bits;
    wire [N_PAYLOAD*TAG_W-1:0] owner_tag_bits;
    wire [N_PAYLOAD*6-1:0] pins_bits;
    wire [N_PAYLOAD*4-1:0] sectors_ready_bits;
    wire [N_PAYLOAD*4-1:0] sectors_pending_bits;
    wire [N_PAYLOAD*4-1:0] dirty_bits;
    wire [3-1:0] role_old_pid;
    wire [3-1:0] role_fill_pid;
    wire [3-1:0] role_pin_pid;
    wire [3-1:0] role_head_pid;
    wire [GEN_W-1:0] generation_old_pid;
    wire [GEN_W-1:0] frontend_generation_old,frontend_generation_next,lower_generation_next;
    wire [GEN_W-1:0] generation_p_landing;
    wire [GEN_W-1:0] generation_fill_pid;
    wire [GEN_W-1:0] generation_pin_pid;
    wire [GEN_W-1:0] generation_free_staging;
    wire [GEN_W-1:0] generation_p_old;
    wire [GEN_W-1:0] generation_head_pid;
    wire [GEN_W-1:0] generation_active_pid;
    wire [PID_W-1:0] fill_mapped_pid;
    wire [6-1:0] pins_old_pid;
    wire [6-1:0] pins_pin_pid;
    wire [4-1:0] sectors_ready_old_pid;
    wire [4-1:0] sectors_pending_old_pid;
    wire [4-1:0] sectors_pending_fill_pid;
    wire [4-1:0] dirty_old_pid;
    wire old_live = req_tag < N_TAG && tag_live[req_tag];
    wire [PID_W-1:0] old_pid;
    generate if(MODE==1)begin
        assign old_pid=old_live ? tag_map_bits[req_tag*PID_W +:PID_W] : req_tag;
    end else begin
        assign old_pid=req_tag; // static resident handle invariant, see R2 proof
    end endgenerate
    wire evict_dirty = req_op==0 && old_live && |dirty_old_pid;
    function automatic [3:0] byte_sectors(input [127:0] be);
        integer s; begin
            for (s=0;s<4;s=s+1) byte_sectors[s]=|be[s*32 +:32];
        end
    endfunction
    function automatic [2:0] pop4(input [3:0] v);
        begin pop4={2'b0,v[0]}+v[1]+v[2]+v[3]; end
    endfunction
    wire hazard, have_wad, have_landing, have_staging, free_bank_exists;
    wire [WAD_W-1:0] free_wad;
    wire [PID_W-1:0] free_landing, free_staging;
    wire [N_WAD-1:0] wad_hazards, wad_eligible;
    generate for(genvar w=0;w<N_WAD;w=w+1)begin: wad_search
        assign wad_hazards[w]=wad_live[w] && wad_addr[w]==req_addr;
        assign wad_eligible[w]=!wad_live[w] && wad_generation[w]!=GMAX;
    end endgenerate
    assign hazard=|wad_hazards;
    ep_l2_first_one #(.N(N_WAD),.W(WAD_W)) wad_encoder(wad_eligible,have_wad,free_wad);
    wire [3:0] bank_found, bank_free;
    wire [4*ROW_W-1:0] bank_first;
    generate for(genvar b=0;b<4;b=b+1)begin: allocation_bank
        wire [N_PAYLOAD/4-1:0] eligible,free_slots;
        for(genvar row=0;row<N_PAYLOAD/4;row=row+1)begin: candidate
            localparam integer ID=4*row+b;
            assign free_slots[row]=role_bits[ID*3 +:3]==FREE;
            assign eligible[row]=free_slots[row] && generation_bits[ID*GEN_W +:GEN_W]<GMAX-1;
        end
        assign bank_free[b]=|free_slots;
        ep_l2_first_one #(.N(N_PAYLOAD/4),.W(ROW_W)) encoder(eligible,bank_found[b],bank_first[b*ROW_W +:ROW_W]);
    end endgenerate
    assign have_landing=MODE==1 && bank_found[req_tag[1:0]];
    assign free_bank_exists=bank_free[req_tag[1:0]];
    assign free_landing=have_landing ? {bank_first[req_tag[1:0]*ROW_W +:ROW_W],req_tag[1:0]} : {PID_W{1'b0}};
    wire [STATIC_WB-1:0] staging_eligible;
    wire [$clog2(STATIC_WB)-1:0] staging_index;
    wire staging_found;
    generate for(genvar w=0;w<STATIC_WB;w=w+1)begin: staging_search
        localparam integer ID=WB_BEGIN+w;
        assign staging_eligible[w]=role_bits[ID*3 +:3]==FREE && generation_bits[ID*GEN_W +:GEN_W]<GMAX-1;
    end endgenerate
    ep_l2_first_one #(.N(STATIC_WB)) staging_encoder(staging_eligible,staging_found,staging_index);
    assign have_staging=MODE!=1 && staging_found;
    assign free_staging=have_staging ? PID_W'(WB_BEGIN)+staging_index : {PID_W{1'b0}};
    wire old_unpinned = !old_live || (pins_old_pid==0 && sectors_pending_old_pid==0);
    wire reuse_ok = !old_live ? generation_old_pid<GMAX-1 : generation_old_pid<GMAX-2;
    wire install_ok = old_unpinned && (!evict_dirty || (have_wad && (MODE==1 || have_staging))) &&
        (MODE==1 && (evict_dirty || !old_live) ? have_landing : reuse_ok);
    wire read_ok = old_live && role_old_pid==RESIDENT &&
        pins_old_pid<32 && reference_count<512 && req_ready_sectors!=0 &&
        (req_ready_sectors & ~sectors_ready_old_pid)==0;
    wire write_ok = old_live && old_unpinned;
    wire invalidate_ok = old_live && old_unpinned && dirty_old_pid==0 && generation_old_pid!=GMAX;
    assign generation_blocked = state==IDLE && req_valid &&
        (req_op==0 && !install_ok && old_unpinned &&
         ((MODE!=1 && !reuse_ok) || (MODE==1 && !have_landing && free_bank_exists)));
    assign req_ready = rst_n && state==IDLE && req_resources_ready && !hazard &&
        req_tag<N_TAG && (req_op==0 ? install_ok : req_op==1 ? read_ok : req_op==2 ? write_ok : invalidate_ok);
    wire req_fire=req_valid && req_ready;
    wire abort_fire=native_abort && state!=IDLE && state!=RESPONSE && p_op!=1;
    wire [GEN_W-1:0] landing_generation = p_new_reserved ? generation_p_landing :
        frontend_generation_next;
    wire fill_identity=fill_pid<N_PAYLOAD && role_fill_pid==RESIDENT &&
        generation_fill_pid==fill_gen && fill_tag<N_TAG && tag_live[fill_tag] && fill_mapped_pid==fill_pid &&
        fill_sectors!=0 && (fill_sectors & ~sectors_pending_fill_pid)==0;
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
            if (MODE!=1 && state==COPY_READ && latch_owner==L_NONE) fe_request=1;
            if (MODE!=1 && state==COPY_WRITE && latch_owner==L_COPY) begin
                fe_request=1; fe_pid=p_staging; fe_write=1;
                fe_bytes={128{1'b1}}; fe_data=copy_latch;
            end
            if (state==COMMIT && native_ready && p_op!=3 && |p_be) begin
                fe_request=1; fe_pid=p_landing; fe_write=1;
            end
        end
    end
    wire wb_request=wb_state==W_IDLE && wb_count!=0 && latch_owner==L_NONE &&
        (MODE==1 || (state!=COPY_READ && state!=COPY_RETURN && state!=COPY_WRITE));
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
    assign native_gen=p_op==0 ? landing_generation : generation_p_landing;
    assign rsp_valid=state==RESPONSE; assign rsp_retry=p_retry;
    assign rsp_id=p_id; assign rsp_pid=p_landing; assign rsp_gen=p_result_gen;
    wire rsp_fire=rsp_valid && rsp_ready;
    wire internal_pin_add=req_fire && req_op==1;
    wire internal_pin_sub=rsp_fire && p_op==1;
    assign pin_ready=rst_n && pin_pid<N_PAYLOAD && role_pin_pid==RESIDENT && generation_pin_pid==pin_gen &&
        !internal_pin_add && !internal_pin_sub &&
        // On the admission edge state is still IDLE. A destructive request
        // acquiring this victim wins over a new external descriptor pin.
        // Gate only a real req_fire: a blocked request must still let an
        // existing pin decrement, and unrelated payloads remain independent.
        !(req_fire && req_op!=1 && old_live && pin_pid==old_pid) &&
        !(state!=IDLE && state!=RESPONSE && p_old_live && pin_pid==p_old) &&
        (pin_increment ? pins_pin_pid<32 && reference_count<512 : pins_pin_pid!=0);
    wire pin_fire=pin_valid && pin_ready;
    assign wb_valid=wb_state==W_SEND;
    assign wb_be=wad_bytes[active_wad]; assign wb_addr=wad_addr[active_wad];
    assign wb_ticket=active_wad; assign wb_ticket_gen=wad_generation[active_wad];
    wire lower_accept=wb_valid && wb_ready;
    wire [PID_W-1:0] active_pid=wad_payload[active_wad];
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
            if (done_fire) begin wad_live[done_ticket]<=0; wad_sent[done_ticket]<=0; end
            if (req_fire) begin
                p_op<=req_op; p_id<=req_id; p_tag<=req_tag; p_old<=old_pid;
                p_old_live<=old_live; p_dirty<=evict_dirty; p_has_wad<=evict_dirty;
                p_retry<=0; p_data<=req_data; p_be<=req_be;
                p_ready<=req_ready_sectors; p_pending<=req_pending_sectors;
                p_install_dirty<=req_install_dirty; p_new_reserved<=0;
                p_landing<=old_pid;
                p_result_gen<=old_live ? generation_old_pid : 0;
                if (req_op==1) begin state<=HIT_READ; end
                else begin
                    state<=COMMIT;
                    if (req_op==0) begin
                        if (MODE==1 && (evict_dirty || !old_live)) begin
                            p_landing<=free_landing; p_new_reserved<=1;
                        end
                        if (evict_dirty) begin
                            p_wad<=free_wad; wad_live[free_wad]<=1; wad_sent[free_wad]<=0;
                            wad_generation[free_wad]<=wad_generation[free_wad]+1;
                            wad_addr[free_wad]<=req_victim_addr; wad_bytes[free_wad]<=req_victim_be;
                            if (MODE==1) begin
                                p_staging<=old_pid; wad_payload[free_wad]<=old_pid;
                                wad_payload_gen[free_wad]<=generation_old_pid;
                            end else begin
                                p_staging<=free_staging; wad_payload[free_wad]<=free_staging;
                                wad_payload_gen[free_wad]<=generation_free_staging+1;
                                state<=COPY_READ;
                            end
                        end
                    end
                end
            end
            if (ge && state==HIT_READ) state<=READ_RETURN;
            if (state==READ_RETURN) begin
                rsp_data<=ram_rdata[p_old[1:0]*1024 +:1024]; state<=RESPONSE;
                p_result_gen<=generation_p_old;
            end
            if (MODE!=1 && ge && state==COPY_READ) begin state<=COPY_RETURN; latch_owner<=L_COPY; end
            if (MODE!=1 && state==COPY_RETURN) begin
                copy_latch<=ram_rdata[p_old[1:0]*1024 +:1024]; state<=COPY_WRITE;
            end
            if (MODE!=1 && ge && state==COPY_WRITE) begin latch_owner<=L_NONE; state<=COMMIT; end
            if (native_commit) begin
                if (p_op==0) begin
                    if (p_dirty) begin
                        wb_fifo[wb_tail]<=p_wad; wb_tail<=wb_tail+1;
                    end
                    tag_live[p_tag]<=1; p_result_gen<=landing_generation;
                end else if (p_op==3) begin
                    tag_live[p_tag]<=0;
                end
                state<=RESPONSE;
            end
            if (abort_fire) begin
                if (p_has_wad) wad_live[p_wad]<=0;
                if (p_dirty && MODE!=1) begin
                    if (latch_owner==L_COPY) latch_owner<=L_NONE;
                end
                p_retry<=1; state<=RESPONSE;
            end
            if (rsp_fire) begin
                state<=IDLE;
            end
            if (gw) begin active_wad<=head_wad; wb_state<=W_RETURN; latch_owner<=L_WB; end
            if (wb_state==W_RETURN) begin
                copy_latch<=ram_rdata[wad_payload[active_wad][1:0]*1024 +:1024]; wb_state<=W_BUFFER;
            end
            if (wb_state==W_BUFFER) begin wb_data<=copy_latch; latch_owner<=L_NONE; wb_state<=W_SEND; end
            if (lower_accept) begin
                wad_sent[active_wad]<=1; wb_head<=wb_head+1; wb_state<=W_IDLE;
            end
        end
    end


    // R3: one frontend event and an independent lower release may coexist.
    wire fe_gen_reserve=req_fire && req_op==0 &&
        ((MODE==1 && (evict_dirty || !old_live)) || (MODE!=1 && evict_dirty));
    wire fe_gen_commit=native_commit && ((p_op==0 && !p_new_reserved) || p_op==3);
    wire fe_gen_abort=abort_fire && (p_new_reserved || (p_dirty && MODE!=1));
    wire fe_gen_write=fe_gen_reserve || fe_gen_commit || fe_gen_abort;
    wire [PID_W-1:0] frontend_generation_pid=state==IDLE ?
        (MODE==1 ? free_landing : free_staging) :
        (fe_gen_abort && MODE!=1 ? p_staging : p_landing);
    wire frontend_generation_step_two=p_op==0 && p_old_live && !p_new_reserved && state!=IDLE && !fe_gen_abort;
    ep_l2_generation_step #(.GEN_W(GEN_W)) frontend_generation_engine(
        frontend_generation_old,frontend_generation_step_two,frontend_generation_next);
    ep_l2_generation_step #(.GEN_W(GEN_W)) lower_generation_engine(
        generation_active_pid,1'b0,lower_generation_next);
    assign generation_p_landing=frontend_generation_old;
    assign generation_p_old=frontend_generation_old; // op1 captures p_old==p_landing
    assign generation_free_staging=frontend_generation_old; // static req allocation, IDLE
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(GEN_W),.IW(PID_W)) select_generation_frontend(
        generation_bits,frontend_generation_pid,frontend_generation_old);

    // R2 explicit local metadata read ports; same information/cycles as R1.
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(3),.IW(PID_W)) select_role_old_pid(role_bits,old_pid,role_old_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(3),.IW(PID_W)) select_role_fill_pid(role_bits,fill_pid,role_fill_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(3),.IW(PID_W)) select_role_pin_pid(role_bits,pin_pid,role_pin_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(3),.IW(PID_W)) select_role_head_pid(role_bits,head_pid,role_head_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(GEN_W),.IW(PID_W)) select_generation_old_pid(generation_bits,old_pid,generation_old_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(GEN_W),.IW(PID_W)) select_generation_fill_pid(generation_bits,fill_pid,generation_fill_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(GEN_W),.IW(PID_W)) select_generation_pin_pid(generation_bits,pin_pid,generation_pin_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(GEN_W),.IW(PID_W)) select_generation_head_pid(generation_bits,head_pid,generation_head_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(GEN_W),.IW(PID_W)) select_generation_active_pid(generation_bits,active_pid,generation_active_pid);
    // R3B proven role/live/forward-map invariant replaces reverse owner.
    ep_l2_index_mux #(.N(N_TAG),.W(PID_W),.IW(TAG_W)) select_fill_tag_map(tag_map_bits,fill_tag,fill_mapped_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(6),.IW(PID_W)) select_pins_old_pid(pins_bits,old_pid,pins_old_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(6),.IW(PID_W)) select_pins_pin_pid(pins_bits,pin_pid,pins_pin_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(4),.IW(PID_W)) select_sectors_ready_old_pid(sectors_ready_bits,old_pid,sectors_ready_old_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(4),.IW(PID_W)) select_sectors_pending_old_pid(sectors_pending_bits,old_pid,sectors_pending_old_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(4),.IW(PID_W)) select_sectors_pending_fill_pid(sectors_pending_bits,fill_pid,sectors_pending_fill_pid);
    ep_l2_index_mux #(.N(N_PAYLOAD),.W(4),.IW(PID_W)) select_dirty_old_pid(dirty_bits,old_pid,dirty_old_pid);

    // Direct vector slices keep every combinational dependency explicit.
    // Constant slot classes at elaboration; data SRAM is still full1168.
    // WB-only static bypass slots have no active owner in this finite path.
    // R2 control/data distribution in16-slot groups. Values outside a
    // word's update group are unobservable by its qualified write enables.
    // Group masks are real charged gates; no buffer/timing exception magic.
    localparam integer META_GROUP=16,META_GROUPS=(N_PAYLOAD+META_GROUP-1)/META_GROUP;
    wire [META_GROUPS-1:0] group_landing,group_fill,group_pin,group_owner;
    wire [META_GROUPS*4-1:0] group_ready,group_pending,group_dirty,group_install_dirty,group_fill_sectors;
    wire [META_GROUPS*TAG_W-1:0] group_new_owner;
    wire [META_GROUPS-1:0] group_old_live,group_reserved,group_pin_increment;
    generate for(genvar g=0;g<META_GROUPS;g=g+1)begin: metadata_distribution
        assign group_landing[g]=p_landing/META_GROUP==g;
        assign group_fill[g]=fill_pid/META_GROUP==g;
        assign group_pin[g]=pin_pid/META_GROUP==g;
        assign group_owner[g]=req_fire ? free_landing/META_GROUP==g : group_landing[g];
        assign group_ready[g*4 +:4]=p_ready & {4{group_landing[g]}};
        assign group_pending[g*4 +:4]=p_pending & {4{group_landing[g]}};
        assign group_dirty[g*4 +:4]=byte_sectors(p_be) & {4{group_landing[g]}};
        assign group_install_dirty[g*4 +:4]=group_dirty[g*4 +:4] & {4{p_install_dirty}};
        assign group_fill_sectors[g*4 +:4]=fill_sectors & {4{group_fill[g]}};
        assign group_new_owner[g*TAG_W +:TAG_W]=(req_fire?req_tag:p_tag) & {TAG_W{group_owner[g]}};
        assign group_old_live[g]=p_old_live && group_landing[g];
        assign group_reserved[g]=p_new_reserved && group_landing[g];
        assign group_pin_increment[g]=pin_increment && group_pin[g];
    end endgenerate
    wire [META_GROUPS*GEN_W-1:0] group_frontend_gen,group_lower_gen;
    generate for(genvar g=0;g<META_GROUPS;g=g+1)begin: generation_distribution
        assign group_frontend_gen[g*GEN_W +:GEN_W]=frontend_generation_next &
            {GEN_W{frontend_generation_pid/META_GROUP==g}};
        assign group_lower_gen[g*GEN_W +:GEN_W]=lower_generation_next &
            {GEN_W{active_pid/META_GROUP==g}};
    end endgenerate
    // Three real buffer levels, fanout<=16 between levels, four words/leaf.
    // All active metadata and Unified Tag-map resets use this network.
    // No flop, reset-cycle extension or timing exception is introduced.
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
    genvar m;
    generate for(m=0;m<N_PAYLOAD;m=m+1)begin: metadata
        if(MODE!=1 && m>=N_TAG && m<WB_BEGIN)begin: unused_static_bypass
            assign role_bits[m*3 +:3]=FREE;
            assign generation_bits[m*GEN_W +:GEN_W]=0;
            assign owner_tag_bits[m*TAG_W +:TAG_W]=0;
            assign pins_bits[m*6 +:6]=0;
            assign sectors_ready_bits[m*4 +:4]=0;
            assign sectors_pending_bits[m*4 +:4]=0;
            assign dirty_bits[m*4 +:4]=0;
        end else begin: active
            wire [TAG_W-1:0] word_owner;
            assign owner_tag_bits[m*TAG_W +:TAG_W]=(MODE!=1 && m<N_TAG)?TAG_W'(m):word_owner;
            ep_l2_metadata_word #(.GEN_W(GEN_W),.TAG_W(TAG_W),.SUPPORT_RES(MODE==1 || m<N_TAG),.DYNAMIC_OWNER(0),.STATIC_RESIDENT(MODE!=1 && m<N_TAG)) word_state(
                .clk(clk),.rst_n(reset_leaf[m/4]),
                .generation_write((fe_gen_write && frontend_generation_pid==m) || (lower_accept && active_pid==m)),
                .generation_value(lower_accept && active_pid==m ? group_lower_gen[(m/META_GROUP)*GEN_W +:GEN_W] : group_frontend_gen[(m/META_GROUP)*GEN_W +:GEN_W]),
                .reserve_resident(req_fire && req_op==0 && MODE==1 && (evict_dirty || !old_live) && free_landing==m),
                .reserve_wb(req_fire && req_op==0 && evict_dirty && MODE!=1 && free_staging==m),
                .new_owner(group_new_owner[(m/META_GROUP)*TAG_W +:TAG_W]),
                .pin_update(pin_fire && pin_pid==m),.pin_increment(group_pin_increment[m/META_GROUP]),
                .read_pin_add(req_fire && req_op==1 && old_pid==m),
                .read_pin_release(rsp_fire && p_op==1 && p_landing==m),
                .fill_update(fill_fire && fill_pid==m),.fill_sectors(group_fill_sectors[(m/META_GROUP)*4 +:4]),
                .become_wb(native_commit && p_op==0 && p_dirty && p_staging==m),
                .install(native_commit && p_op==0 && p_landing==m),.already_reserved(group_reserved[m/META_GROUP]),
                .install_old_live(group_old_live[m/META_GROUP]),.install_ready(group_ready[(m/META_GROUP)*4 +:4]),.install_pending(group_pending[(m/META_GROUP)*4 +:4]),
                .install_dirty(group_install_dirty[(m/META_GROUP)*4 +:4]),
                .hit_write(native_commit && p_op==2 && p_landing==m),.write_ready(group_ready[(m/META_GROUP)*4 +:4]),.write_dirty(group_dirty[(m/META_GROUP)*4 +:4]),
                .invalidate(native_commit && p_op==3 && p_landing==m),
                .rollback_release(abort_fire && ((p_new_reserved && p_landing==m) || (p_dirty && MODE!=1 && p_staging==m))),
                .lower_release(lower_accept && active_pid==m),
                .role(role_bits[m*3 +:3]),.generation(generation_bits[m*GEN_W +:GEN_W]),
                .owner_tag(word_owner),.pins(pins_bits[m*6 +:6]),
                .sectors_ready(sectors_ready_bits[m*4 +:4]),.sectors_pending(sectors_pending_bits[m*4 +:4]),.dirty(dirty_bits[m*4 +:4]));
        end
    end endgenerate
    localparam integer TAG_MAP_GROUPS=(N_TAG+META_GROUP-1)/META_GROUP;
    wire [TAG_MAP_GROUPS*PID_W-1:0] group_tag_map_data;
    generate for(genvar g=0;g<TAG_MAP_GROUPS;g=g+1)begin: tag_map_distribution
      assign group_tag_map_data[g*PID_W +:PID_W]=p_landing & {PID_W{p_tag/META_GROUP==g}};
    end endgenerate
    genvar t;
    generate for(t=0;t<N_TAG;t=t+1)begin: mapping
        if(MODE!=1)begin: fixed_mapping
            assign tag_map_bits[t*PID_W +:PID_W]=PID_W'(t);
        end else begin: dynamic_mapping
        ep_l2_tag_map_word #(.PID_W(PID_W)) word_state(.clk(clk),.rst_n(reset_leaf[t/4]),
            .write(native_commit && p_op==0 && p_tag==t),.data(group_tag_map_data[(t/META_GROUP)*PID_W +:PID_W]),.payload(tag_map_bits[t*PID_W +:PID_W]));
        end
    end endgenerate
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
        if (gw && (role_head_pid!=WB || generation_head_pid!=wad_payload_gen[head_wad])) $fatal(1,"stale WB handle");
        if (lower_accept && generation_active_pid==GMAX) $fatal(1,"generation wrap");
    end
`endif
endmodule
