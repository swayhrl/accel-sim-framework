#!/usr/bin/env python3
"""Full production RTL GEN writer overlap, byte snapshots and victim rollback.
Caller holds central lease. Testbench helpers/reference are frozen R2 fixture.
"""
from pathlib import Path
import subprocess,json,hashlib,gzip,argparse
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--resume',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=a.resume);repo=Path(__file__).resolve().parents[3];original=(repo/'rtl/ep_l2/tb/ep_l2_slice_tb.sv').read_text();prefix=original.split('    reg [127:0] mask;')[0].replace('module ep_l2_slice_tb;','module ep_l2_owner_r3_tb;');extra='''
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
''';tb=a.out/'owner_stress_tb.sv';tb.write_text(prefix+extra);fl=repo/'rtl/ep_l2/flow/full_slice_filelist.f';rows=[]
if a.resume:
 prior=json.loads((a.out/'OWNER_STRESS_RECEIPT.json').read_text());assert prior['fixture_sha256']==hashlib.sha256(tb.read_bytes()).hexdigest();assert prior['source_RTL_sha256']=={x:hashlib.sha256((repo/x).read_bytes()).hexdigest() for x in fl.read_text().splitlines() if x};rows=prior['rows']
for mode,label in ((0,'B16'),(1,'UNIFIED'),(2,'S64')):
 if any(row['mode']==label for row in rows):continue
 vvp=a.out/(label+'.vvp');cmd=['iverilog','-g2012','-s','ep_l2_owner_r3_tb','-P','ep_l2_owner_r3_tb.MODE='+str(mode),'-DEP_L2_FULL_TOP','-f',str(fl),'-o',str(vvp),str(tb)]
 with (a.out/(label+'-compile.log')).open('w') as f:subprocess.run(cmd,cwd=repo,stdout=f,stderr=subprocess.STDOUT,check=True)
 with (a.out/(label+'-run.log')).open('w') as f:subprocess.run(['vvp',str(vvp)],cwd=repo,stdout=f,stderr=subprocess.STDOUT,timeout=900,check=True)
 text=(a.out/(label+'-run.log')).read_text();assert 'R3_ACTUAL_OWNER_STRESS' in text and 'full-drain PASS' in text
 blob=vvp.read_bytes();archive=vvp.with_suffix('.vvp.gz');archive.write_bytes(gzip.compress(blob,6,mtime=0));assert gzip.decompress(archive.read_bytes())==blob;vvp.unlink();rows.append({'mode':label,'status':'ACTUAL_RTL_OWNER_REBIND_LATE_FILL_PIN_SNAPSHOT_BYTES_DRAIN_PASS','binary_sha256':hashlib.sha256(blob).hexdigest(),'archive':str(archive),'compile_command':cmd});(a.out/'OWNER_STRESS_RECEIPT.json').write_text(json.dumps({'rows':rows,'fixture_sha256':hashlib.sha256(tb.read_bytes()).hexdigest(),'source_RTL_sha256':{x:hashlib.sha256((repo/x).read_bytes()).hexdigest() for x in fl.read_text().splitlines() if x},'scope':'full production data/banks: live wrong Tag with current GEN, held snapshot+descriptor pin+other-sector fill, pin prevents rebind, stale GEN, WB role, cross-Tag Unified PID reuse, forged current GEN wrong owner, byte WB and full drain'},indent=2)+'\n');print(label,'actual owner stress PASS',flush=True)
