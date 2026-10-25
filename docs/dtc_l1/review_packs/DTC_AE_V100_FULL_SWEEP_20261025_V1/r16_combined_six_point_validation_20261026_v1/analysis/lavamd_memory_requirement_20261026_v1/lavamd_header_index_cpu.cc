#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <thread>
#include <unordered_set>
#include <vector>
struct Event {unsigned long long offset;int kind;std::string value;};
int main(int argc,char **argv){
 if(argc!=4)return 2;FILE *f=strcmp(argv[1],"-")==0?stdin:fopen(argv[1],"rb");if(!f)return 3;FILE *out=fopen(argv[2],"wx");if(!out)return 4;
 const size_t block=8*1024*1024;std::vector<char>buf(block);std::string carry;unsigned long long bytes=0;std::unordered_set<unsigned long long>seen;auto began=std::chrono::steady_clock::now();unsigned step=0;
 while(size_t n=fread(buf.data(),1,buf.size(),f)){
  std::string text=carry+std::string(buf.data(),n);unsigned long long base=bytes-carry.size();bytes+=n;std::vector<Event>events;
  const char *keys[]={"\nthread block = ","\nwarp = ","\ninsts = "};
  for(int k=0;k<3;++k){size_t at=0;while((at=text.find(keys[k],at))!=std::string::npos){size_t value=at+strlen(keys[k]),end=text.find('\n',value);if(end==std::string::npos)break;unsigned long long pos=base+at;if(seen.insert(pos).second)events.push_back({pos,k,text.substr(value,end-value)});at=value;}}
  std::sort(events.begin(),events.end(),[](const auto&a,const auto&b){return a.offset<b.offset;});for(const auto&e:events)fprintf(out,"%llu\t%d\t%s\n",e.offset,e.kind,e.value.c_str());carry=text.substr(text.size()>256?text.size()-256:0);
  double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-began).count();double target=double(bytes)/(256.0*1024*1024);if(target>elapsed)std::this_thread::sleep_for(std::chrono::duration<double>(target-elapsed));
  if(++step%64==0){FILE *p=fopen(argv[3],"w");if(p){fprintf(p,"{\"bytes\":%llu,\"elapsed_seconds\":%.3f,\"CPU_only\":true,\"models_started\":0}\n",bytes,elapsed);fclose(p);}}
 }
 if(ferror(f))return 5;fclose(f);fclose(out);double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-began).count();printf("{\"bytes\":%llu,\"elapsed_seconds\":%.3f,\"events\":%zu,\"CPU_only\":true,\"models_started\":0}\n",bytes,elapsed,seen.size());return 0;
}
