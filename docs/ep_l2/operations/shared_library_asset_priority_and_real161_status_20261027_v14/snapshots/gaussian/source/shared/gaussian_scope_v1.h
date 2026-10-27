#pragma once
#include <cstdint>
#include <cctype>
#include <vector>
#include <string>
#include <sstream>
#include <fstream>
#include <algorithm>
#include <stdexcept>
#include <unistd.h>
namespace gaussian16 {
static const char* profile="GAUSSIAN16_DIRECT_RETPAIR_INPUT_OBSERVER_V2_CANDIDATE";
static const char* binary="50fad6fdc65b005af1384c83a1b825df405f7b894ed649b98ee145a0b7cd01d1";
static const char* cubin="690c2d76dff5785f9d5d253a04b3ccd725db59f94d2893077e456fa8de35a5a1";
static const char* mapsha="09a8918db2494e8a498fdafb84125a79bfde9ea7c871315220dd72ae38b9099b";
static const char* fan1="_Z4Fan1PfS_ii";
static const char* fan2="_Z4Fan2PfS_S_iii";
inline void require(bool ok,const char*why){if(!ok)throw std::runtime_error(std::string("GAUSSIAN16_SCOPE_REJECT:")+why);}
inline uint32_t rr(uint32_t x,unsigned n){return(x>>n)|(x<<(32-n));}
inline std::string sha256(const std::vector<unsigned char>&input){
 static const uint32_t k[64]={0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
 uint32_t h[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
 auto b=input;uint64_t bits=uint64_t(b.size())*8;b.push_back(0x80);while(b.size()%64!=56)b.push_back(0);for(int i=7;i>=0;i--)b.push_back((bits>>(8*i))&255);
 for(size_t off=0;off<b.size();off+=64){uint32_t w[64];for(int i=0;i<16;i++)w[i]=(uint32_t(b[off+4*i])<<24)|(uint32_t(b[off+4*i+1])<<16)|(uint32_t(b[off+4*i+2])<<8)|b[off+4*i+3];for(int i=16;i<64;i++){auto a=w[i-15],c=w[i-2];w[i]=w[i-16]+(rr(a,7)^rr(a,18)^(a>>3))+w[i-7]+(rr(c,17)^rr(c,19)^(c>>10));}
 uint32_t a=h[0],c=h[1],d=h[2],e=h[3],f=h[4],g=h[5],j=h[6],l=h[7];for(int i=0;i<64;i++){uint32_t t1=l+(rr(f,6)^rr(f,11)^rr(f,25))+((f&g)^((~f)&j))+k[i]+w[i],t2=(rr(a,2)^rr(a,13)^rr(a,22))+((a&c)^(a&d)^(c&d));l=j;j=g;g=f;f=e+t1;e=d;d=c;c=a;a=t1+t2;}h[0]+=a;h[1]+=c;h[2]+=d;h[3]+=e;h[4]+=f;h[5]+=g;h[6]+=j;h[7]+=l;}
 std::ostringstream o;o<<std::hex;for(auto x:h){o.width(8);o.fill('0');o<<x;}return o.str();
}
inline std::string file_sha(const std::string&p){std::ifstream in(p,std::ios::binary);require(bool(in),"missing pinned file");std::vector<unsigned char>b;char c;while(in.get(c)){require(b.size()<32u*1024*1024,"pinned file32MiB");b.push_back((unsigned char)c);}require(in.eof(),"pinned read failure");return sha256(b);}
inline std::string compact(std::string x){x.erase(std::remove_if(x.begin(),x.end(),[](unsigned char c){return std::isspace(c)||c==';';}),x.end());return x;}
inline bool owner_ok(const std::string&fn){return fn==fan1||fn==fan2;}
inline void runtime_identity(const char*map){
 char exe[4096];ssize_t n=readlink("/proc/self/exe",exe,sizeof(exe)-1);require(n>0&&n<ssize_t(sizeof(exe)-1),"executable path");exe[n]=0;
 require(file_sha(exe)==binary,"executable SHA");require(map&&file_sha(map)==mapsha,"semantic map SHA");
 std::ifstream c("/proc/self/cmdline",std::ios::binary);std::vector<std::string>argv;std::string v;while(std::getline(c,v,'\0'))argv.push_back(v);
 require(argv.size()==3&&argv[1]=="-s"&&argv[2]=="16","exact argv Gaussian16");
}
inline void loaded_identity(const std::string&path,const std::string&fn,int sm){require(owner_ok(fn),"unexpected related owner");require(sm==89,"actual binaryVersion");require(file_sha(path)==cubin,"actual loaded cubin SHA");}
inline int static_site(const std::string&fn,uint64_t rel,const std::string&sass,const std::vector<int>&src,const std::vector<int>&dst){
 auto s=compact(sass);
 bool control=s.find("CALL")!=std::string::npos||s.find("RET")!=std::string::npos||s.find("BRX")!=std::string::npos||s.find("JMX")!=std::string::npos;
 if(!control)return 0;
 require(fn==fan1,"control wrong owner");
 if(s=="CALL.REL.NOINC0x2f0"){require(rel==0x280,"CALL exact PC");return 1;}
 if(s=="RET.REL.NODECR60x0"){require(rel==0x960&&src==std::vector<int>({6,7})&&dst.empty(),"RET exact PC/pair");return 2;}
 throw std::runtime_error("GAUSSIAN16_SCOPE_REJECT:indirect/predicated/unknown control");
}
inline uint64_t add(uint64_t a,uint64_t b){require(UINT64_MAX-a>=b,"full64 target overflow");return a+b;}
inline void record(const std::string&fn,uint64_t rel,int kind,const std::string&op,unsigned ns,const unsigned*src,unsigned nd,unsigned active,unsigned mask,const uint64_t*targets){
 require((mask&~active)==0,"record mask");require(fn==fan1,"record owner");
 if(kind==1){require(rel==0x280&&op=="CALL.REL.NOINC"&&ns==0&&nd==0,"CALL record grammar/deps");for(unsigned l=0;l<32;l++)if(mask&(1u<<l))require(targets[l]==0x2f0,"CALL target mismatch");}
 else if(kind==2){require(rel==0x960&&op=="RET.REL.NODEC"&&ns==2&&src[0]==6&&src[1]==7&&nd==0,"RET record pair");}
 else require(kind==0&&op.rfind("CALL",0)!=0&&op.rfind("RET",0)!=0,"control kind outside exact Gaussian subset");
}
}
