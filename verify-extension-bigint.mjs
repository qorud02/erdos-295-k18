import {readFileSync} from 'node:fs';
const pack=JSON.parse(readFileSync(new URL('./certificates-extension.json',import.meta.url),'utf8'));
const gcd=(a,b)=>{while(b){[a,b]=[b,a%b];}return a;};
const out=[];
for(const r of pack.records){
 const ds=r.denominators.map(BigInt);
 if(ds.length!==r.terms||ds[0]!==BigInt(r.minimum)||ds.some((d,i)=>i&&d<=ds[i-1]))throw Error('shape');
 let L=1n;for(const d of ds)L=L/gcd(L,d)*d;
 let S=ds.reduce((s,d)=>s+L/d,0n);
 if(S!==L||L.toString()!==r.lcm||S.toString()!==r.scaled_sum)throw Error('identity');
 out.push({N:r.minimum,terms:r.terms,lcm:L.toString(),scaled_sum:S.toString(),status:'verified'});
}
console.log(JSON.stringify({status:'passed',arithmetic:'JavaScript BigInt independent integer LCM sum',records:out},null,2));
