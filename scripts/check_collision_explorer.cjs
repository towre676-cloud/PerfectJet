#!/usr/bin/env node
"use strict";
// Replay the pure arithmetic shipped in the offline HTML, without a browser or dependency.
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm"),assert=require("node:assert/strict");
const html=fs.readFileSync(path.join(__dirname,"../research/collision_pell/explorer.html"),"utf8");
const block=html.match(/<script id="collision-core">([\s\S]*?)<\/script>/);
assert.ok(block,"Self-contained arithmetic block is present");
const sandbox={};vm.runInNewContext(block[1],sandbox,{timeout:5000});const C=sandbox.CollisionPell;
const plain=value=>JSON.parse(JSON.stringify(value,(_,v)=>typeof v==="bigint"?v.toString():v));
let checks=0;
function equal(a,b){assert.deepEqual(plain(a),plain(b));checks++;}
function trueCheck(v){assert.ok(v);checks++;}

// Compare affine-block lookup with a separate term-by-term construction.
for(let L=1;L<=16;L++)for(let n=0;n<=240;n++){
 const histogram=Array(L).fill(0n);for(let j=0;j<=n;j++)histogram[j*(n-j)%L]++;
 equal(C.remoteHistogram(BigInt(n),L),histogram);
 equal(histogram.reduce((a,b)=>a+b,0n),BigInt(n+1));
 if(L===2)equal(histogram[0]-histogram[1],n%2?BigInt(n+1):1n);
}
equal(C.cyclotomic(1),[-1n,1n]);equal(C.cyclotomic(2),[1n,1n]);equal(C.cyclotomic(12),[1n,0n,-1n,0n,1n]);
// Verify Φ_d products reconstruct x^L−1 rather than merely trusting a lookup table.
function multiply(a,b){const p=Array(a.length+b.length-1).fill(0n);a.forEach((x,i)=>b.forEach((y,j)=>p[i+j]+=x*y));return p;}
for(let L=1;L<=16;L++){let p=[1n];for(let d=1;d<=L;d++)if(L%d===0)p=multiply(p,C.cyclotomic(d));const want=Array(L+1).fill(0n);want[0]=-1n;want[L]=1n;equal(p,want);}

// Compare prime convolution with explicit enumeration of every ordered factor pair.
const families=[[],[[2,4]],[[2,3],[3,2]],[[2,2],[3,2],[5,1]]];
for(const factors of families)for(let L=1;L<=16;L++){
 const direct=Array(L).fill(0n);
 function visit(i,kappa){if(i===factors.length){direct[kappa%L]++;return;}const e=factors[i][1];for(let a=0;a<=e;a++)visit(i+1,kappa+a*(e-a));}
 visit(0,0);const result=C.factorHistogram(factors,L);equal(result.histogram,direct);equal(result.total,direct.reduce((a,b)=>a+b,0n));
}
equal(C.parseFactors("2^3 × 3^2 * 2"),[[2,4],[3,2]]);equal(C.parseFactors("1"),[]);
for(const bad of ["4^2","2^-1","2^1001","0","1^2","2^2;3^2","2^1000*2"]){assert.throws(()=>C.parseFactors(bad));checks++;}

// Independent Pell recurrence, quadratic norm, and reciprocal-numerator identity.
let A=1n,B=0n,previousPell=0n,pell=1n,reciprocal=[];
for(let n=0;n<=200;n++){
 equal(C.pellPair(BigInt(n)),[A,B]);equal(A*A-2n*B*B,n%2?-1n:1n);
 const coefficient=n===0?1n:n===1?-2n:-2n*reciprocal[n-1]+reciprocal[n-2];reciprocal.push(coefficient);
 equal(coefficient,(n%2?-1n:1n)*pell);[previousPell,pell]=[pell,2n*pell+previousPell];[A,B]=[A+2n*B,A+B];
}
// A separately represented 2×2 matrix checks huge modular exponentiation.
function matrixMultiply(a,b,m){return[[0,0],[0,0]].map((row,i)=>row.map((_,j)=>(a[i][0]*b[0][j]+a[i][1]*b[1][j])%m));}
function matrixPower(n,m){let out=[[1n,0n],[0n,1n]],base=[[1n,2n],[1n,1n]];while(n){if(n%2n)out=matrixMultiply(out,base,m);base=matrixMultiply(base,base,m);n/=2n;}return[out[0][0],out[1][0]];}
const huge=10n**100n+12345n,modulus=1000000007n;
equal(C.pellPair(huge,modulus),matrixPower(huge,modulus));
equal(C.conductorTwo(huge),huge+1n);equal(C.conductorTwo(huge+1n),1n);
for(let L=1;L<=16;L++)equal(C.remoteHistogram(huge,L).reduce((a,b)=>a+b,0n),huge+1n);
assert.throws(()=>C.pellPair(10001n));checks++;assert.throws(()=>C.pellPair(10n,1n));checks++;
equal(C.formatExact([0n,-1n,2n]),"−ζ + 2ζ^2");equal(C.reduce([1n,1n,1n],3),[0n,0n]);
equal(C.serial({value:huge}),{value:huge.toString()});
trueCheck(!/<script[^>]+src=|<link[^>]+href=/i.test(html));
for(const script of html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g))new vm.Script(script[1]);

// Execute the shipped UI against a minimal DOM contract. This catches handler,
// validation, and export faults; it makes no screenshot/layout assertion.
class Element {
 constructor(tag="div"){this.tag=tag;this.children=[];this.style={};this.events={};this.value="";this._text="";this.hidden=false;}
 set textContent(value){this._text=String(value);this.children=[];}
 get textContent(){return this._text+this.children.map(c=>c.textContent).join("");}
 append(...nodes){for(const node of nodes){this.children.push(node);if(this.tag==="select"&&node.selected)this.value=node.value;}}
 replaceChildren(...nodes){this._text="";this.children=[];this.append(...nodes);}
 addEventListener(name,handler){(this.events[name]??=[]).push(handler);}
 setAttribute(name,value){this[name]=String(value);}
 dispatch(name,extra={}){for(const fn of this.events[name]||[])fn({target:this,...extra});}
 click(){this.dispatch("click");}
 remove(){}
}
const nodes=new Map();for(const tag of html.matchAll(/<(\w+)\b[^>]*\bid="([^"]+)"[^>]*>/g)){const el=new Element(tag[1]);el.value=tag[0].match(/\bvalue="([^"]*)"/)?.[1]??"";nodes.set(tag[2],el);}
let lastBlob=null;
const domSandbox={document:{getElementById:id=>nodes.get(id),createElement:tag=>new Element(tag),createElementNS:(_,tag)=>new Element(tag),createTextNode:text=>{const el=new Element("text");el.textContent=text;return el;},body:new Element("body")},URL:{createObjectURL:blob=>{lastBlob=blob;return"blob:test";},revokeObjectURL:()=>{}},Blob:class{constructor(parts){this.content=parts.join("");}},setTimeout:()=>0};
vm.runInNewContext(block[1],domSandbox,{timeout:5000});
const ui=html.match(/<script id="collision-ui">([\s\S]*?)<\/script>/);vm.runInNewContext(ui[1],domSandbox,{timeout:5000});
equal(nodes.get("split-answer").textContent,"1");equal(nodes.get("factor-count").textContent,"162");
nodes.get("split-range").value="13";nodes.get("split-range").dispatch("input");equal(nodes.get("split-answer").textContent,"14");equal(nodes.get("split-grid").children.length,14);
nodes.get("conductor").value="3";nodes.get("conductor").dispatch("change");trueCheck(nodes.get("remote-conductor").textContent.includes("L = 3"));
nodes.get("factor-input").value="4^2";nodes.get("factor-go").click();trueCheck(nodes.get("factor-error").textContent.includes("prime"));
nodes.get("export").click();equal(lastBlob,null);
nodes.get("factor-input").value="2^3 * 3^2";nodes.get("factor-go").click();equal(nodes.get("factor-error").textContent,"");equal(nodes.get("factor-count").textContent,"12");
nodes.get("pell-exponent").value="5001";nodes.get("export").click();equal(lastBlob,null);trueCheck(nodes.get("pell-basic-error").textContent.includes("5,000"));
nodes.get("pell-exponent").value="12";nodes.get("export").click();trueCheck(lastBlob!==null);const evidence=JSON.parse(lastBlob.content);equal(evidence.schema,"perfectjet.collision-pell-explorer/1");equal(evidence.factors.total,"12");equal(evidence.pell.norm,"1");equal(evidence.split.n,13);
console.log(JSON.stringify({status:"PASS",checks,scope:"Exact arithmetic, syntax, UI handlers, validation and JSON export from the offline HTML; no screenshot, global analytic or physical claim"},null,2));
