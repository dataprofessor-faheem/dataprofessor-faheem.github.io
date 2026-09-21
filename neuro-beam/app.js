document.getElementById("year").textContent = new Date().getFullYear();

function barChart(el, data){
  const max=Math.max(...Object.values(data));
  el.innerHTML=Object.entries(data).map(([k,v])=>`
    <div class="bar-row"><span class="bar-label" title="${k}">${k}</span><div class="bar-track"><div class="bar-fill" style="width:${(v/max*100).toFixed(1)}%"></div></div><span class="bar-value">${v.toLocaleString()}</span></div>`).join("");
}
function donut(el,data){
  const entries=Object.entries(data), total=entries.reduce((a,[,v])=>a+v,0);
  let start=0; const palette=["#58dfff","#a57aff","#ff7dbd","#59e5b2"];
  const stops=[];
  entries.forEach(([k,v],i)=>{const p=v/total*100;stops.push(`${palette[i%palette.length]} ${start}% ${start+p}%`);start+=p;});
  el.innerHTML=`<div class="donut" style="background:conic-gradient(${stops.join(",")})"></div><div class="legend">${entries.map(([k,v],i)=>`<div class="legend-row"><span class="swatch" style="background:${palette[i%palette.length]}"></span><span>${k}</span><b>${v.toLocaleString()}</b></div>`).join("")}</div>`;
}
fetch("data/m1_validation_snapshot.json").then(r=>r.json()).then(d=>{
  document.getElementById("k-neurons").textContent=d.metadata_neurons.toLocaleString();
  document.getElementById("k-ephys").textContent=d.matched_meta_ephys.toLocaleString();
  document.getElementById("k-mice").textContent=d.unique_mice.toLocaleString();
  document.getElementById("k-features").textContent=d.ephys_feature_count.toLocaleString();
  barChart(document.getElementById("family-chart"),d.rna_families);
  barChart(document.getElementById("layer-chart"),d.layers);
  donut(document.getElementById("sex-chart"),d.sex);
  document.getElementById("feature-list").innerHTML=d.ephys_features.map(x=>`<span class="feature-chip">${x}</span>`).join("");
}).catch(err=>{
  console.error(err);
  document.getElementById("live-data").insertAdjacentHTML("beforeend","<p>Live snapshot could not be loaded.</p>");
});

const dynPalette=["#58dfff","#a57aff","#ff7dbd","#59e5b2","#ffd36b","#7aa9ff","#ff9c6b","#7ce6d6"];
let dynData=null, pcaPoints=[], animRunning=true, phase=0;

function parseCSV(text){
  const lines=text.trim().split(/\r?\n/); if(lines.length<2)return[];
  const h=lines[0].split(",");
  return lines.slice(1).map(line=>{const a=line.split(",");const o={};h.forEach((k,i)=>o[k]=a[i]);return o;});
}
function getStateProfile(state){
  return dynData?.cluster_profiles?.[state]||{};
}
function stateParams(state){
  const p=getStateProfile(state);
  const vrest=Number(p.vrest ?? -68);
  const slope=Math.max(.05,Math.abs(Number(p.f_i_curve_slope ?? .25)));
  const adapt=Math.max(0,Number(p.adaptation ?? .03));
  const latency=Math.max(.005,Number(p.latency ?? .03));
  const threshI=Math.max(20,Math.abs(Number(p.threshold_i_long_square ?? 80)));
  return {vrest,slope,adapt,latency,threshI};
}
function renderReadout(state){
  const p=stateParams(state);
  const root=document.getElementById("state-readout");
  root.innerHTML=[
    ["Resting Vm",p.vrest.toFixed(1)+" mV"],
    ["F-I slope",p.slope.toFixed(3)],
    ["Adaptation",p.adapt.toFixed(3)],
    ["Latency",(p.latency*1000).toFixed(1)+" ms"],
    ["Threshold current",p.threshI.toFixed(0)+" pA"],
    ["Cluster n",(dynData.cluster_sizes?.[state]??"—").toLocaleString?.() || dynData.cluster_sizes?.[state] || "—"]
  ].map(([k,v])=>`<div><b>${v}</b><span>${k}</span></div>`).join("");
}
function drawNeuron(){
  const canvas=document.getElementById("neuron-canvas"); if(!canvas)return;
  const ctx=canvas.getContext("2d"); const w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h); ctx.fillStyle="#07131c";ctx.fillRect(0,0,w,h);
  const state=document.getElementById("state-select")?.value||"E1";
  const p=stateParams(state); const drive=Number(document.getElementById("drive-slider")?.value||55)/100;
  const idx=Math.max(0,Object.keys(dynData?.cluster_sizes||{}).indexOf(state)); const col=dynPalette[idx%dynPalette.length];
  const cx=w*.48,cy=h*.50;
  const firing=Math.min(1.2,drive*(.35+p.slope*1.4));
  const glow=.18+.45*Math.max(0,Math.sin(phase*firing*2.5));
  const grad=ctx.createRadialGradient(cx,cy,10,cx,cy,120);grad.addColorStop(0,col);grad.addColorStop(1,"rgba(0,0,0,0)");
  ctx.globalAlpha=glow;ctx.fillStyle=grad;ctx.beginPath();ctx.arc(cx,cy,120,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;
  ctx.strokeStyle=col;ctx.lineWidth=3;ctx.lineCap="round";ctx.fillStyle=col;
  ctx.beginPath();ctx.arc(cx,cy,22,0,Math.PI*2);ctx.fill();
  const branches=[[-170,-80],[-190,40],[-95,-145],[135,-120],[175,-20],[150,105],[30,155],[-90,135]];
  branches.forEach(([dx,dy],i)=>{ctx.beginPath();ctx.moveTo(cx,cy);const bx=cx+dx*.55,by=cy+dy*.55;ctx.quadraticCurveTo(bx,by,cx+dx,cy+dy);ctx.stroke();ctx.beginPath();ctx.arc(cx+dx,cy+dy,4+3*Math.max(0,Math.sin(phase*3+i)),0,Math.PI*2);ctx.fill();});
  ctx.strokeStyle="rgba(140,220,255,.22)";ctx.lineWidth=1;
  for(let i=0;i<5;i++){const r=42+i*22+8*Math.sin(phase*1.4-i);ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();}
  document.getElementById("activity-state").textContent=`${state} · drive ${Math.round(drive*100)}%`;
}
function spikeWave(t,p,drive){
  const base=p.vrest;
  const freq=Math.max(0.7,2+drive*10*p.slope);
  const period=1/freq;
  const tt=(t-p.latency)%period;
  if(t<p.latency||tt<0)return base;
  const width=.035+Math.min(.03,p.adapt*.25);
  if(tt<width*.18)return base+(tt/(width*.18))*95;
  if(tt<width*.45)return 27-((tt-width*.18)/(width*.27))*85;
  if(tt<width)return -58-((tt-width*.45)/(width*.55))*10;
  return base+2*Math.exp(-(tt-width)*20);
}
function drawTrace(){
  const canvas=document.getElementById("trace-canvas");if(!canvas)return;const ctx=canvas.getContext("2d"),w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h);ctx.fillStyle="#08151e";ctx.fillRect(0,0,w,h);
  ctx.strokeStyle="#183344";ctx.lineWidth=1;for(let y=40;y<h;y+=45){ctx.beginPath();ctx.moveTo(45,y);ctx.lineTo(w-15,y);ctx.stroke();}
  const state=document.getElementById("state-select")?.value||"E1",p=stateParams(state),drive=Number(document.getElementById("drive-slider")?.value||55)/100;
  const idx=Math.max(0,Object.keys(dynData?.cluster_sizes||{}).indexOf(state));ctx.strokeStyle=dynPalette[idx%dynPalette.length];ctx.lineWidth=2.4;ctx.beginPath();
  for(let x=45;x<w-15;x++){const t=(x-45)/(w-60)*1.2;const v=spikeWave(t,p,drive);const y=35+(35-v)/120*(h-70);if(x===45)ctx.moveTo(x,y);else ctx.lineTo(x,y);}ctx.stroke();
  ctx.fillStyle="#7f98a7";ctx.font="11px system-ui";ctx.fillText("mV",12,28);ctx.fillText("0",42,h-16);ctx.fillText("1.2 s",w-48,h-16);
}
function drawPCA(){
  const canvas=document.getElementById("pca-canvas"); if(!canvas||!pcaPoints.length)return; const ctx=canvas.getContext("2d"),w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h);ctx.fillStyle="#08151e";ctx.fillRect(0,0,w,h);
  const xs=pcaPoints.map(d=>+d.PC1).filter(Number.isFinite),ys=pcaPoints.map(d=>+d.PC2).filter(Number.isFinite);
  const minx=Math.min(...xs),maxx=Math.max(...xs),miny=Math.min(...ys),maxy=Math.max(...ys);
  const states=[...new Set(pcaPoints.map(d=>d.state))].sort();
  pcaPoints.forEach(d=>{const x=35+(+d.PC1-minx)/(maxx-minx||1)*(w-60),y=h-30-(+d.PC2-miny)/(maxy-miny||1)*(h-55);const i=states.indexOf(d.state);ctx.fillStyle=dynPalette[i%dynPalette.length];ctx.globalAlpha=.65;ctx.beginPath();ctx.arc(x,y,2.4,0,Math.PI*2);ctx.fill();});ctx.globalAlpha=1;
  document.getElementById("pca-legend").innerHTML=states.map((s,i)=>`<span><i class="legend-dot" style="background:${dynPalette[i%dynPalette.length]}"></i>${s}</span>`).join("");
}
function drawClusterDiagnostics(){
  const root=document.getElementById("cluster-diagnostic-chart");if(!root||!dynData)return;
  const rows=dynData.cluster_diagnostics||[];const max=Math.max(...rows.map(r=>r.silhouette));
  root.innerHTML=rows.map(r=>`<div class="metric-row"><b>k=${r.k}</b><div class="metric-track"><div class="metric-fill" style="width:${(r.silhouette/max*100).toFixed(1)}%"></div></div><span>${r.silhouette.toFixed(3)}</span></div>`).join("");
}
function animate(){
  if(animRunning){phase+=.035;drawNeuron();drawTrace();}
  requestAnimationFrame(animate);
}
Promise.all([
  fetch("data/visual_cortex_discovery.json").then(r=>r.json()),
  fetch("data/visual_cortex_pca_sample.csv").then(r=>r.text())
]).then(([d,csv])=>{
  dynData=d;pcaPoints=parseCSV(csv);
  const sel=document.getElementById("state-select");
  const states=Object.keys(d.cluster_sizes||{});sel.innerHTML=states.map(s=>`<option value="${s}">${s}</option>`).join("");
  sel.addEventListener("change",()=>{renderReadout(sel.value);drawNeuron();drawTrace();});
  document.getElementById("drive-slider").addEventListener("input",()=>{drawNeuron();drawTrace();});
  document.getElementById("pause-neuron").addEventListener("click",e=>{animRunning=!animRunning;e.target.textContent=animRunning?"Pause":"Resume";});
  renderReadout(states[0]||"E1");drawPCA();drawClusterDiagnostics();animate();
}).catch(err=>console.error("Dynamic discovery data unavailable",err));
