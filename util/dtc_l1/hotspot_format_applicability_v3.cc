// CPU-only, read-only memory-format screening. No geometry, ISA, body hashing,
// address correction, simulator execution or admission logic. Reuses r0 identity
// inventory; deliberately excludes Hotspot. C++17; one sequential reader.
#include <algorithm>
#include <charconv>
#include <cctype>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>
using namespace std;
vector<string_view> split(const string &s, char separator = ' ') {
  vector<string_view> t;
  size_t p = 0;
  while (p < s.size()) {
    if (separator == ' ') { while (p < s.size() && isspace((unsigned char)s[p])) ++p; }
    if (p == s.size()) break;
    size_t e = p;
    while (e < s.size() && (separator == ' ' ? !isspace((unsigned char)s[e]) : s[e] != separator)) ++e;
    t.emplace_back(s.data()+p, e-p); p = e+1;
  }
  return t;
}
long long number(string_view s, int base=10) {
  long long v=0;
  auto r=from_chars(s.data(),s.data()+s.size(),v,base);
  if (r.ec!=errc() || r.ptr!=s.data()+s.size()) throw runtime_error("Invalid integer");
  return v;
}
int main(int argc, char **argv) {
 try {
  if (argc!=4) throw runtime_error("usage: reader INVENTORY NEW_COUNTS_TSV NEW_WITNESSES_TSV");
  if (filesystem::exists(argv[2]) || filesystem::exists(argv[3])) throw runtime_error("Outputs must be new");
  ifstream inventory(argv[1]); if (!inventory) throw runtime_error("Missing inventory");
  ofstream out(argv[2]), witness(argv[3]); if (!out || !witness) throw runtime_error("Cannot open outputs");
  vector<string> keys={"memory_records","mode0","mode1","mode2","zero_mask","mode0_excess","mode0_short","mode1_sparse","mode1_nonzero_first_nonzero_stride","mode1_nonzero_first_zero_stride","mode1_bad_payload","mode2_excess","mode2_short","unknown_mode"};
  out<<"workload\tordinal\tpath\ttrace_version"; for(auto &k:keys)out<<'\t'<<k; out<<'\n';
  witness<<"workload\tordinal\tflag\tline\traw_record\n";
  string row; getline(inventory,row); size_t members=0;
  while(getline(inventory,row)) {
   auto r=split(row,'\t'); if(r.size()<8)throw runtime_error("Inventory columns");
   if(r[0]=="hotspot1")continue;
   string workload(r[0]), ordinal(r[1]), path(r[3]);
   ifstream input(path); if(!input)throw runtime_error("Missing input: "+path);
   if(filesystem::file_size(path)!=(uint64_t)number(r[4]))throw runtime_error("Input size differs");
   map<string,uint64_t> counts; map<string,int> examples;
   int version=0; size_t n=0; string line;
   while(getline(input,line)) {
    ++n;
    if(line.rfind("-accelsim tracer version = ",0)==0){version=number(string_view(line).substr(27));continue;}
    if(line.empty() || string("0123456789abcdef").find(line[0])==string::npos)continue;
    auto t=split(line); if(t.empty())continue;
    size_t offset=version>=3?0:4;
    if(t.size()<offset+4)throw runtime_error("Short instruction");
    auto j=offset+3+number(t[offset+2]); auto w=j+2+number(t.at(j+1));
    if(number(t.at(w))==0)continue;
    ++counts["memory_records"];
    auto mask=(uint32_t)number(t[offset+1],16); int active=__builtin_popcount(mask);
    if(!mask)++counts["zero_mask"];
    int mode=number(t.at(w+1)); size_t payload=t.size()-(w+2);
    auto flag=[&](const string &key){
     ++counts[key];
     if(examples[key]++<2){
      // TSV quoting preserves original trailing spaces without adding trailing
      // whitespace to the review table itself. Double quotes use CSV escaping.
      witness<<workload<<'\t'<<ordinal<<'\t'<<key<<'\t'<<n<<"\t\"";
      for(char c:line){if(c=='"')witness<<'"';witness<<c;}
      witness<<"\"\n";
     }
    };
    if(mode==0){++counts["mode0"];if(payload>(size_t)active)flag("mode0_excess");if(payload<(size_t)active)flag("mode0_short");}
    else if(mode==1){
     ++counts["mode1"];
     if(payload!=2){flag("mode1_bad_payload");continue;}
     auto stride=number(t[w+3]);
     if(mask){
      int first=__builtin_ctz(mask),last=31-__builtin_clz(mask);
      if(last-first+1!=active)flag("mode1_sparse");
      if(first)flag(stride?"mode1_nonzero_first_nonzero_stride":"mode1_nonzero_first_zero_stride");
     }
    }
    else if(mode==2){++counts["mode2"];size_t expected=max(active,1);if(payload>expected)flag("mode2_excess");if(payload<expected)flag("mode2_short");}
    else flag("unknown_mode");
   }
   if(!input.eof())throw runtime_error("Read error");
   out<<workload<<'\t'<<ordinal<<'\t'<<path<<'\t'<<version;
   for(auto &k:keys)out<<'\t'<<counts[k];
   out<<'\n';
   if(++members%50==0)cerr<<"format-only members "<<members<<'\n';
  }
  cerr<<"format-only complete "<<members<<'\n';
 } catch(const exception &e){cerr<<e.what()<<'\n';return 1;}
}
