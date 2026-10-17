// Repeated, bounded standard-cell word. Separate module avoids constructing
// thousands of procedural writers to one giant packed vector in EDA frontends.
// SUPPORT_RES=0 is a static staging slot: resident-only fields are constants.
module ep_l2_metadata_word #(
    parameter integer GEN_W=32,TAG_W=10,SUPPORT_RES=1
)(
    input wire clk,rst_n,
    input wire reserve_resident,reserve_wb,
    input wire [TAG_W-1:0] new_owner,
    input wire pin_update,pin_increment,read_pin_add,read_pin_release,
    input wire fill_update,input wire [3:0] fill_sectors,
    input wire become_wb,install,already_reserved,
    input wire [GEN_W-1:0] install_generation,
    input wire [3:0] install_ready,install_pending,install_dirty,
    input wire hit_write,input wire [3:0] write_ready,write_dirty,
    input wire invalidate,rollback_release,lower_release,
    output reg [2:0] role,
    output reg [GEN_W-1:0] generation,
    output reg [TAG_W-1:0] owner_tag,
    output reg [5:0] pins,
    output reg [3:0] sectors_ready,sectors_pending,dirty
);
    always @(posedge clk) begin
        if(!rst_n)begin
            role<=0;generation<=0;owner_tag<=0;pins<=0;
            sectors_ready<=0;sectors_pending<=0;dirty<=0;
        end else begin
            if(SUPPORT_RES)begin
                if(pin_update)pins<=pin_increment?pins+1:pins-1;
                if(fill_update)begin sectors_ready<=sectors_ready|fill_sectors;sectors_pending<=sectors_pending&~fill_sectors;end
                if(read_pin_add)pins<=pins+1;
                if(reserve_resident)begin role<=3;generation<=generation+1;owner_tag<=new_owner;end
            end
            if(reserve_wb)begin role<=4;generation<=generation+1;end
            if(become_wb)role<=2;
            if(SUPPORT_RES)begin
                if(install)begin
                    if(!already_reserved)generation<=install_generation;
                    role<=1;owner_tag<=new_owner;sectors_ready<=install_ready;sectors_pending<=install_pending;dirty<=install_dirty;
                end
                if(hit_write)begin dirty<=dirty|write_dirty;sectors_ready<=sectors_ready|write_ready;end
                if(invalidate)begin role<=0;generation<=generation+1;sectors_ready<=0;dirty<=0;end
            end
            if(rollback_release)begin role<=0;generation<=generation+1;end
            if(SUPPORT_RES && read_pin_release)pins<=pins-1;
            if(lower_release)begin role<=0;generation<=generation+1;sectors_ready<=0;dirty<=0;end
        end
    end
endmodule
module ep_l2_tag_map_word #(parameter integer PID_W=11)(
    input wire clk,rst_n,write,input wire [PID_W-1:0] data,output reg [PID_W-1:0] payload
);
    always @(posedge clk)begin
        if(!rst_n)payload<=0;else if(write)payload<=data;
    end
endmodule
