// Exact GMP port. No bound on any denominator is used.
#include <gmp.h>
#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
struct Z {
 mpz_t v;
 Z(){mpz_init(v);} Z(int x){mpz_init_set_si(v,x);}
 Z(const Z& x){mpz_init_set(v,x.v);} Z(Z&& x)noexcept{mpz_init(v);mpz_swap(v,x.v);}
 ~Z(){mpz_clear(v);} Z& operator=(const Z& x){mpz_set(v,x.v);return *this;}
 Z& operator=(Z&& x)noexcept{mpz_swap(v,x.v);return *this;}
 Z& operator++(){mpz_add_ui(v,v,1);return *this;}
 std::string str()const{std::string s(mpz_sizeinbase(v,10)+3,'\0');mpz_get_str(&s[0],10,v);s.resize(s.find('\0'));return s;}
 static Z parse(const std::string&s){Z x;if(mpz_set_str(x.v,s.c_str(),10))throw std::invalid_argument("integer");return x;}
};
#define BIN(OP,FN) static Z operator OP(const Z&a,const Z&b){Z r;FN(r.v,a.v,b.v);return r;}
BIN(+,mpz_add) BIN(-,mpz_sub) BIN(*,mpz_mul) BIN(/,mpz_tdiv_q) BIN(%,mpz_tdiv_r)
#undef BIN
static bool operator==(const Z&a,const Z&b){return mpz_cmp(a.v,b.v)==0;}
static bool operator!=(const Z&a,const Z&b){return !(a==b);}
static bool operator<(const Z&a,const Z&b){return mpz_cmp(a.v,b.v)<0;}
static bool operator>(const Z&a,const Z&b){return b<a;}
static bool operator<=(const Z&a,const Z&b){return !(b<a);}
static bool operator>=(const Z&a,const Z&b){return !(a<b);}
static Z gcd(const Z&a,const Z&b){Z r;mpz_gcd(r.v,a.v,b.v);return r;}
static Z isqrt(const Z&a){Z r;mpz_sqrt(r.v,a.v);return r;}
static Z maximum(const Z&a,const Z&b){return a<b?b:a;}
static Z minimum(const Z&a,const Z&b){return a<b?a:b;}
struct ZHash {size_t operator()(const Z&x)const{size_t h=mpz_size(x.v);for(size_t i=0;i<mpz_size(x.v);i++)h=(h*1099511628211ull)^mpz_getlimbn(x.v,i);return h;}};
struct Rat {Z a,b;Rat():a(0),b(1){} Rat(Z x,Z y):a(std::move(x)),b(std::move(y)){Z g=gcd(a,b);a=a/g;b=b/g;}};
static Rat addunit(const Rat&r,const Z&x){return Rat(r.a*x+r.b,r.b*x);}
static Rat subtractunit(const Rat&r,const Z&x){Z h=gcd(r.b,x),c=r.a*(x/h)-r.b/h,j=(h==1?Z(1):gcd(c,h));return Rat(c/j,(r.b/h)*(x/j));}
struct HK {Z d;int t;bool operator==(const HK&x)const{return t==x.t&&d==x.d;}};
struct HH {size_t operator()(const HK&x)const{return ZHash{}(x.d)*37+x.t;}};
struct SK {Z d,a,b;int t;bool operator==(const SK&x)const{return t==x.t&&d==x.d&&a==x.a&&b==x.b;}};
struct SH {size_t operator()(const SK&x)const{return ((ZHash{}(x.d)*37+x.t)*37+ZHash{}(x.a))*37+ZHash{}(x.b);}};
struct Timeout{};
static bool inbase(const Z&x){
 static const unsigned long small[]={18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,38,39,40,43,44,45,46,48,50,52,54,63,275};
 if(mpz_fits_ulong_p(x.v)){unsigned long u=mpz_get_ui(x.v);if(u<=275)return std::binary_search(std::begin(small),std::end(small),u);if(u==14143068ul)return true;}
 static const Z last=Z::parse("10457416992");return x==last;
}
static bool insmall(const Z&x){
 static const Z first=Z::parse("14143068"),last=Z::parse("10457416992");
 return inbase(x)&&x!=first&&x!=last;
}
class Search {
 using Clock=std::chrono::steady_clock;
 Clock::time_point start=Clock::now();double seconds,next_report=15;bool prime,joint;size_t memo_limit;
 std::unordered_map<HK,Rat,HH> harmonics,quota_harmonics;
 std::unordered_map<Z,std::vector<int>,ZHash> factors;
 std::unordered_set<SK,SH> failed;
 std::ofstream log;
 public:
 int base_selected=0,small_selected=0;unsigned long long quota_prunes=0;
 unsigned long long nodes=0,hprunes=0,pprunes=0,jprunes=0,mhits=0,two_prunes=0,two_candidates=0;
 std::vector<Z> path;
 Search(double s,bool p=true,bool j=false,size_t memo=200000,const std::string& output=""):seconds(s),prime(p),joint(j),memo_limit(memo){if(!output.empty())log.open(output);}
 double elapsed()const{return std::chrono::duration<double>(Clock::now()-start).count();}
 void emit(const std::string&s){std::cout<<s<<std::endl;if(log){log<<s<<std::endl;}}
 std::string list(const std::vector<Z>&v)const{std::string s="[";for(size_t i=0;i<v.size();i++){if(i)s+=",";s+=v[i].str();}return s+"]";}
 void tick(){double e=elapsed();if(e>=seconds)throw Timeout{};if(e>=next_report){emit("{\"event\":\"progress\",\"elapsed_seconds\":"+std::to_string(e)+",\"nodes\":"+std::to_string(nodes)+",\"prime_prunes\":"+std::to_string(pprunes)+",\"joint_prunes\":"+std::to_string(jprunes)+",\"quadratic_two_prunes\":"+std::to_string(two_prunes)+",\"current_prefix\":"+list(path)+"}");next_report=e+15;}}
 Rat harmonic(const Z&d,int t){HK key{d,t};auto it=harmonics.find(key);if(it!=harmonics.end())return it->second;Rat h;for(int j=0;j<t;j++)h=addunit(h,d+j);if(harmonics.size()<250000)harmonics.emplace(std::move(key),h);return h;}
 Rat quota_harmonic(const Z&d,int t,int q,int qs){
  if(q>=t&&qs>=t)return harmonic(d,t);
  HK key{d,t*35*35+q*35+qs};auto it=quota_harmonics.find(key);if(it!=quota_harmonics.end())return it->second;
  Rat h;Z x=d;int chosen=0;while(chosen<t){bool ba=inbase(x),sm=insmall(x);if((ba&&q==0)||(sm&&qs==0)){++x;continue;}if(ba)--q;if(sm)--qs;h=addunit(h,x);++chosen;++x;}
  if(quota_harmonics.size()<100000)quota_harmonics.emplace(std::move(key),h);return h;
 }
 bool quota_enough(const Z&d,int t,const Z&a,const Z&b){if(base_selected>28||small_selected>27)return false;Rat h=quota_harmonic(d,t,28-base_selected,27-small_selected);return h.a*b>=a*h.b;}
 bool enough(const Z&d,int t,const Z&a,const Z&b){Rat h=harmonic(d,t);return h.a*b>=a*h.b;}
 Z upper(const Z&d,int t,const Z&a,const Z&b){Z lo=d-1,hi=t*b/a;while(lo<hi){Z mid=(lo+hi+1)/2;if(quota_enough(mid,t,a,b))lo=mid;else hi=mid-1;}return lo;}
 std::vector<int> factor(const Z&n){auto it=factors.find(n);if(it!=factors.end())return it->second;Z r=n;std::vector<int> out;int d=2;while(Z(d)*d<=r&&d<=10000){if(r%d==0){out.push_back(d);while(r%d==0)r=r/d;}d=(d==2?3:d+2);}if(r>1&&Z(d)*d>r)out.push_back((int)mpz_get_ui(r.v));if(factors.size()<100000)factors.emplace(n,out);return out;}
 std::vector<int> merge(const std::vector<int>&a,const std::vector<int>&b){std::vector<int>v=a;v.insert(v.end(),b.begin(),b.end());std::sort(v.begin(),v.end());v.erase(std::unique(v.begin(),v.end()),v.end());return v;}
 Z inverse(const Z&a,int p){Z r;if(!mpz_invert(r.v,a.v,Z(p).v))throw std::runtime_error("noninvertible");return r;}
 bool joint_obstruction(const Z&d,int t,const Z&a,const Z&b,const std::vector<int>&primes){
  if(!joint||t<3||t>8)return false;Rat h=harmonic(d,t-1);if(h.a*b>=a*h.b)return false;
  std::vector<Z>powers;for(int p:primes){Z v=b,pe=1;while(v%p==0){pe=pe*p;v=v/p;}if(pe>1)powers.push_back(pe);}
  if(powers.size()<2)return false;
  std::sort(powers.begin(),powers.end(),[&](const Z&x,const Z&y){return ((d+x-1)/x)*x>((d+y-1)/y)*y;});if(powers.size()>4)powers.resize(4);
  int n=(int)powers.size();std::vector<Z>q(1<<n,Z(1));for(int mask=1;mask<(1<<n);mask++){Z product=1;for(int i=0;i<n;i++)if(mask&(1<<i))product=product*powers[i];q[mask]=((d+product-1)/product)*product;}
  Z all=q.back();if((h.a*all+h.b)*b>=a*h.b*all)return false;
  std::vector<int>blocks;bool possible=false;
  auto visit=[&](auto&&self,int i)->void{
   if(possible)return;
   if(i==n){if(blocks.size()>(size_t)t)return;Rat h0=harmonic(d,t-(int)blocks.size());Z num=h0.a,den=h0.b,prev=d+t-(int)blocks.size()-1;std::vector<Z>bounds;for(int mask:blocks)bounds.push_back(q[mask]);std::sort(bounds.begin(),bounds.end());for(const Z&bound:bounds){prev=maximum(bound,prev+1);num=num*prev+den;den=den*prev;}if(num*b>=a*den)possible=true;return;}
   size_t size=blocks.size();for(size_t j=0;j<size;j++){int old=blocks[j];blocks[j]|=1<<i;self(self,i+1);blocks[j]=old;}blocks.push_back(1<<i);self(self,i+1);blocks.pop_back();
  };visit(visit,0);if(!possible){jprunes++;return true;}return false;
 }
 bool obstruction(const Z&d,int t,const Z&a,const Z&b,const std::vector<int>&primes){if(!prime||b==1||t<=1)return false;for(int p:primes){Z v=b,pe=1;while(v%p==0){pe=pe*p;v=v/p;}if(pe==1)continue;Z q1=((d+pe-1)/pe)*pe,q2=q1+pe;if(q2<d+t)continue;Rat h2=q1<d+t-1?addunit(harmonic(d,t-1),q2):addunit(addunit(harmonic(d,t-2),q1),q2);if(h2.a*b>=a*h2.b)continue;Z unit=(v*inverse(a,p))%p,mod=pe*p,q=pe*unit;if(q<d)q=q+((d-q+mod-1)/mod)*mod;if(q<d+t)continue;Rat h1=addunit(harmonic(d,t-1),q);if(h1.a*b<a*h1.b)return true;}return joint_obstruction(d,t,a,b,primes);}
 bool two(const Z&d,const Z&a,const Z&b,std::vector<Z>&out){Z lo=maximum(d,b/a+1),hi=(2*b-1)/a;if(hi<lo){two_prunes++;return false;}if(lo*lo-a*lo+b<0){two_prunes++;return false;}if(!quota_enough(d,2,a,b)){quota_prunes++;return false;}Z delta=a*a-4*b;if(delta>0){Z s=isqrt(delta);if(s*s<delta)++s;hi=minimum(hi,(a-s)/2);}if(hi<lo){two_prunes++;return false;}for(Z x=lo;x<=hi;++x){two_candidates++;if((two_candidates&1023)==0)tick();Z rem,num=b*x,den=a*x-b,y;mpz_tdiv_qr(y.v,rem.v,num.v,den.v);if(rem==0&&y>x&&base_selected+(int)inbase(x)+(int)inbase(y)<=28&&small_selected+(int)insmall(x)+(int)insmall(y)<=27){out={x,y};return true;}}return false;}
 bool dfs(const Z&d,int t,const Z&a,const Z&b,const std::vector<int>&primes,std::vector<Z>&out){
  nodes++;if((nodes&1023)==0)tick();if(t==0){out.clear();return a==0;}if(a<=0)return false;if(base_selected>28||small_selected>27){quota_prunes++;return false;}
  if(t==1){if(b%a==0&&b/a>=d&&base_selected+(int)inbase(b/a)<=28&&small_selected+(int)insmall(b/a)<=27){out={b/a};return true;}return false;}if(t==2)return two(d,a,b,out);
  if(!enough(d,t,a,b)){hprunes++;return false;}if(!quota_enough(d,t,a,b)){quota_prunes++;return false;}SK key{d,a,b,t*35*35+base_selected*35+small_selected};if(failed.find(key)!=failed.end()){mhits++;return false;}if(obstruction(d,t,a,b,primes)){pprunes++;return false;}
  Z lo=maximum(d,b/a+1),hi=upper(lo,t,a,b);
  for(Z x=lo;x<=hi;++x){Z h=gcd(b,x),c=a*(x/h)-b/h,j=h==1?Z(1):gcd(c,h);Z na=c/j,nb=(b/h)*(x/j);if(na<=0)continue;auto next=t>3?merge(primes,factor(x)):primes;path.push_back(x);base_selected+=(int)inbase(x);small_selected+=(int)insmall(x);bool ok=dfs(x+1,t-1,na,nb,next,out);base_selected-=(int)inbase(x);small_selected-=(int)insmall(x);path.pop_back();if(ok){out.insert(out.begin(),x);return true;}}
  if(failed.size()<memo_limit)failed.insert(std::move(key));return false;
 }
 std::string result(const std::string&status,int n,int t,const std::vector<Z>&prefix,const std::vector<Z>&out){return "{\"event\":\"result\",\"status\":\""+status+"\",\"minimum\":"+std::to_string(n)+",\"terms\":"+std::to_string(t)+",\"prefix\":"+list(prefix)+",\"max_denominator\":null,\"denominators\":"+(status=="witness"?list(out):"null")+",\"elapsed_seconds\":"+std::to_string(elapsed())+",\"nodes\":"+std::to_string(nodes)+",\"prime_prunes\":"+std::to_string(pprunes)+",\"joint_prunes\":"+std::to_string(jprunes)+",\"harmonic_prunes\":"+std::to_string(hprunes)+",\"memo_hits\":"+std::to_string(mhits)+",\"quadratic_two_prunes\":"+std::to_string(two_prunes)+",\"two_candidates\":"+std::to_string(two_candidates)+",\"failed_states\":"+std::to_string(failed.size())+",\"checkpoint_prefix\":"+list(path)+",\"base_quota\":28,\"small_reference_quota\":27,\"base_quota_prunes\":"+std::to_string(quota_prunes)+"}";}
};
static void require(bool value,const char*message){if(!value)throw std::runtime_error(message);}
static void verify(){std::mt19937 rng(2951810);for(int i=0;i<10000;i++){Z n=(int)(rng()%1000000),m=(int)(rng()%1000000);n=n*m;Z q=isqrt(n);require(q*q<=n&&(q+1)*(q+1)>n,"sqrt");Rat r((int)(rng()%100000+1),(int)(rng()%100000+1));Z x=(int)(rng()%100000+1);Rat fast=subtractunit(r,x),old(r.a*x-r.b,r.b*x);require(fast.a==old.a&&fast.b==old.b,"reduction");}
 for(int i=0;i<1000;i++){Rat r((int)(rng()%500+1),(int)(rng()%2000+2));Z d=(int)(rng()%50+2),lo=maximum(d,r.b/r.a+1),hi=(2*r.b-1)/r.a;bool expected=false;for(Z x=lo;x<=hi;++x){Z q=r.a*x-r.b;if((r.b*x)%q==0&&(r.b*x)/q>x){expected=true;break;}}Search s(120,false);std::vector<Z>out;require(s.two(d,r.a,r.b,out)==expected,"two oracle");}
 for(int i=0;i<10000;i++){int t=(int)(rng()%7+2);std::vector<int>ds;while(ds.size()<(size_t)t){int x=(int)(rng()%298+2);if(std::find(ds.begin(),ds.end(),x)==ds.end())ds.push_back(x);}std::sort(ds.begin(),ds.end());Rat r;Search s(120,true,true);std::vector<int>primes;for(int x:ds){r=addunit(r,x);primes=s.merge(primes,s.factor(x));}require(!s.obstruction(ds[0],t,r.a,r.b,primes),"known valid prime cover");}
 for(int i=0;i<100;i++){Rat r((int)(rng()%20+1),(int)(rng()%30+2));Z d=(int)(rng()%12+2);int t=(int)(rng()%2+2);Search s0(120,false,false,2000),s1(120,true,true,2000);std::vector<Z>o0,o1;require(s0.dfs(d,t,r.a,r.b,s0.factor(r.b),o0)==s1.dfs(d,t,r.a,r.b,s1.factor(r.b),o1),"full residual oracle");}
 std::cout<<"{\"event\":\"validation\",\"status\":\"passed\",\"square_roots\":10000,\"reductions\":10000,\"two_oracles\":1000,\"valid_prime_covers\":10000,\"full_on_off\":100}"<<std::endl;
}
static void laminar_probe(){
 Search s(120);std::vector<Z> starts;for(int d=2;d<=80;d++)starts.emplace_back(d);
 for(const char* v:{"14143066","14143067","14143068","14143069","10457416990","10457416991","10457416992","10457416993"})starts.push_back(Z::parse(v));
 for(const Z&d:starts)for(int t=1;t<=6;t++)for(int q=0;q<=6;q++)for(int qs=0;qs<=6;qs++){
  Rat r=s.quota_harmonic(d,t,q,qs);std::cout<<d.str()<<" "<<t<<" "<<q<<" "<<qs<<" "<<r.a.str()<<" "<<r.b.str()<<"\n";
 }
}
int main(int argc,char**argv){try{int n=18,t=33;double seconds=300;bool prime=true,joint=false;std::string pref,output;for(int i=1;i<argc;i++){std::string x=argv[i];if(x=="--laminar-bounds"){laminar_probe();return 0;}if(x=="--verify"){verify();return 0;}if(x=="--minimum")n=std::stoi(argv[++i]);else if(x=="--terms")t=std::stoi(argv[++i]);else if(x=="--seconds")seconds=std::stod(argv[++i]);else if(x=="--prefix")pref=argv[++i];else if(x=="--output")output=argv[++i];else if(x=="--no-prime-prune")prime=false;else if(x=="--joint")joint=true;else throw std::invalid_argument("unknown argument");}
 Search s(seconds,prime,joint,200000,output);Z a=1,b=1,d=n;std::vector<Z>prefix,out;while(!pref.empty()){size_t comma=pref.find(',');Z x=Z::parse(pref.substr(0,comma));require(x>=d,"prefix order");Z na=a*x-b,nb=b*x,g=gcd(na,nb);a=na/g;b=nb/g;d=x+1;prefix.push_back(x);s.path.push_back(x);s.base_selected+=(int)inbase(x);s.small_selected+=(int)insmall(x);if(comma==std::string::npos)break;pref=pref.substr(comma+1);}require(t==33,"certified BASE quota applies only to 33-term search");require(prefix.size()<=(size_t)t,"prefix length");std::string status="exhausted";try{if(s.dfs(d,t-(int)prefix.size(),a,b,s.factor(b),out)){status="witness";out.insert(out.begin(),prefix.begin(),prefix.end());}}catch(Timeout&){status="timeout";}
 if(status=="witness"){require(out.size()==(size_t)t,"witness count");Rat r;Z last=n-1;for(const Z&x:out){require(x>last,"witness order");r=addunit(r,x);last=x;}require(r.a==r.b,"witness sum");}s.emit(s.result(status,n,t,prefix,out));return 0;
 }catch(std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
