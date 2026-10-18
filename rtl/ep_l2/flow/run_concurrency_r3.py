#!/usr/bin/env python3
"""Full production RTL GEN writer overlap, byte snapshots and victim rollback.
Caller holds central lease. Testbench helpers/reference are frozen R2 fixture.
"""
from pathlib import Path
import subprocess,json,hashlib,gzip,argparse
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);repo=Path(__file__).resolve().parents[3];original=(repo/'rtl/ep_l2/tb/ep_l2_slice_tb.sv').read_text();prefix=original.split('    reg [127:0] mask;')[0].replace('module ep_l2_slice_tb;','module ep_l2_concurrency_r3_tb;');extra='''
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
''';tb=a.out/'concurrent_tb.sv';tb.write_text(prefix+extra);fl=repo/'rtl/ep_l2/flow/full_slice_filelist.f';rows=[]
for mode,label in ((0,'B16'),(1,'UNIFIED'),(2,'S64')):
 vvp=a.out/(label+'.vvp');cmd=['iverilog','-g2012','-s','ep_l2_concurrency_r3_tb','-P','ep_l2_concurrency_r3_tb.MODE='+str(mode),'-DEP_L2_FULL_TOP','-f',str(fl),'-o',str(vvp),str(tb)]
 with (a.out/(label+'-compile.log')).open('w') as f:subprocess.run(cmd,cwd=repo,stdout=f,stderr=subprocess.STDOUT,check=True)
 with (a.out/(label+'-run.log')).open('w') as f:subprocess.run(['vvp',str(vvp)],cwd=repo,stdout=f,stderr=subprocess.STDOUT,timeout=900,check=True)
 text=(a.out/(label+'-run.log')).read_text();assert 'R3_ACTUAL_GEN_CONCURRENCY_FULL_CAPACITY' in text and text.count('R3_ACTUAL_CONCURRENT_GEN case')==3
 blob=vvp.read_bytes();archive=vvp.with_suffix('.vvp.gz');archive.write_bytes(gzip.compress(blob,6,mtime=0));assert gzip.decompress(archive.read_bytes())==blob;vvp.unlink();rows.append({'mode':label,'status':'ACTUAL_RTL_THREE_TWO_WRITER_CASES_BYTE_WB_ROLLBACK_DRAIN_PASS','binary_sha256':hashlib.sha256(blob).hexdigest(),'archive':str(archive),'compile_command':cmd});(a.out/'CONCURRENT_GEN_RECEIPT.json').write_text(json.dumps({'rows':rows,'fixture_sha256':hashlib.sha256(tb.read_bytes()).hexdigest(),'source_RTL_sha256':{x:hashlib.sha256((repo/x).read_bytes()).hexdigest() for x in fl.read_text().splitlines() if x},'scope':'full production data/banks; actual concurrent reservation/commit/rollback each with lower release; independent GEN FF targets, immutable WB3 bytes/masks and two preserved victims, full drain'},indent=2)+'\n');print(label,'actual GEN concurrency PASS',flush=True)
