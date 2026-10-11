#define main preserved_search_main
#include "quota-search.cpp"
#undef main
int main(){
 Search s(120);
 std::vector<Z> starts;for(int d=2;d<=80;d++)starts.emplace_back(d);
 for(const char* v:{"14143066","14143067","14143068","14143069","10457416990","10457416991","10457416992","10457416993"})starts.push_back(Z::parse(v));
 for(const Z&d:starts)for(int t=1;t<=6;t++)for(int q=0;q<=6;q++){
  Rat r=s.quota_harmonic(d,t,q);std::cout<<d.str()<<" "<<t<<" "<<q<<" "<<r.a.str()<<" "<<r.b.str()<<"\n";
 }
}
