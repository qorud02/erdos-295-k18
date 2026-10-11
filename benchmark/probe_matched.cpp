// Test-only entry point for the frozen matched-search.cpp engine.
// The production engine is included unchanged. This probe is not a general API.
#define main matched_production_main
#include "matched-search.cpp"
#undef main
#include <sstream>

static std::string quoted(const std::string& s) {
 std::string out="\"";
 for(char c:s){if(c=='\\'||c=='\"')out+='\\'; if(c=='\n'){out+="\\n";continue;}out+=c;}
 return out+"\"";
}
static std::string exact_list(const std::vector<Z>& values) {
 std::string s="[";for(size_t i=0;i<values.size();++i){if(i)s+=",";s+=quoted(values[i].str());}return s+"]";
}
int main() {
 std::string line;size_t index=0;
 while(std::getline(std::cin,line)){
  if(line.empty())continue;
  ++index;
  try {
   std::istringstream input(line);std::string mode_text,ds,as,bs,extra;
   int t,base_count,small_count;
   if(!(input>>mode_text>>ds>>t>>as>>bs>>base_count>>small_count)||(input>>extra))throw std::invalid_argument("expected mode d t a b base_selected small_selected");
   int mode=-1;
   if(mode_text=="off"||mode_text=="0")mode=0;
   if(mode_text=="single"||mode_text=="1")mode=1;
   if(mode_text=="nested"||mode_text=="2")mode=2;
   Z d=Z::parse(ds),a=Z::parse(as),b=Z::parse(bs);
   if(mode<0||d<1||t<1||t>3||a<0||b<=0||base_count<0||small_count<0||small_count>base_count)throw std::invalid_argument("probe scope: mode 0..2, d>=1, 1<=t<=3, a>=0, b>0, 0<=small_selected<=base_selected");
   Rat r(a,b);
   Search search(30,true,true,200000,"",mode);
   search.base_selected=base_count;search.small_selected=small_count;
   std::vector<Z> witness;
   std::string status;
   try {status=search.dfs(d,t,r.a,r.b,search.factor(r.b),witness)?"witness":"exhausted";}
   catch(const Timeout&){status="timeout";}
   std::cout<<"{\"index\":"<<index<<",\"status\":"<<quoted(status)<<",\"mode\":"<<mode
    <<",\"d\":"<<quoted(d.str())<<",\"t\":"<<t<<",\"a\":"<<quoted(r.a.str())<<",\"b\":"<<quoted(r.b.str())
    <<",\"base_selected\":"<<base_count<<",\"small_selected\":"<<small_count
    <<",\"denominators\":"<<(status=="witness"?exact_list(witness):"null")
    <<",\"nodes\":"<<search.nodes<<",\"prime_prunes\":"<<search.pprunes<<",\"joint_prunes\":"<<search.jprunes
    <<",\"harmonic_prunes\":"<<search.hprunes<<",\"quota_prunes\":"<<search.quota_prunes
    <<",\"two_candidates\":"<<search.two_candidates<<",\"quadratic_two_prunes\":"<<search.two_prunes<<"}\n";
  }catch(const std::exception& error){std::cout<<"{\"index\":"<<index<<",\"status\":\"error\",\"error\":"<<quoted(error.what())<<"}\n";}
 }
 return 0;
}
