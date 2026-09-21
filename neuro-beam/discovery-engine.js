/* NEURO-BEAM CBEF Top-500 Discovery Engine + counterfactual neuron simulator */
let cbeCatalog=null, cbeModels=null, cbeSelectedGene=null, cbeAnimRunning=true, cbeAnimT=0, cbeLastSim=null;

function cbeClamp(x,a,b){return Math.max(a,Math.min(b,x))}
function cbeFmt(v,d=3){
  if(v===null||v===undefined||!Number.isFinite(Number(v))) return "NA";
  const n=Number(v);
  if(Math.abs(n)>0 && Math.abs(n)<1e-4) return n.toExponential(2);
  return n.toFixed(d);
}
function cbeGeneByName(name){
  if(!cbeCatalog)return null;
  const q=String(name||"").trim().toUpperCase();
  return cbeCatalog.genes.find(g=>String(g.gene).toUpperCase()===q || String(g.mouseGene).toUpperCase()===q) || null;
}
function cbeModelFor(gene){
  if(!cbeModels)return null;
  return cbeModels.models.find(x=>x.gene===gene)||null;
}
function cbeSetGene(gene){
  const g=cbeGeneByName(gene);
  if(!g)return;
  cbeSelectedGene=g;
  const input=document.getElementById("cbe-gene-search");
  if(input)input.value=g.gene;
  cbeRenderAll();
}
function cbeRenderRankedList(){
  if(!cbeCatalog)return;
  const root=document.getElementById("cbe-ranked-list"); if(!root)return;
  const limit=Number(document.getElementById("cbe-rank-window")?.value||500);
  const q=String(document.getElementById("cbe-gene-search")?.value||"").trim().toUpperCase();
  let genes=cbeCatalog.genes.slice(0,limit);
  if(q && !cbeGeneByName(q)){
    genes=genes.filter(g=>(g.gene+" "+g.mouseGene+" "+g.bestElectricalFeature).toUpperCase().includes(q));
  }
  root.innerHTML=genes.map(g=>`<button class="discovery-gene-row ${cbeSelectedGene?.gene===g.gene?'active':''}" data-cbe-gene="${g.gene}">
      <span>#${g.rank}</span><b>${g.gene}</b>
      <span class="score-chip">${cbeFmt(g.discoveryScore,3)}</span>
      <span>${cbeFmt(g.bioelectricEvidenceScore,3)}</span>
      <span>${cbeFmt(g.cancerEvidenceScore,3)}</span>
      <span class="trait-chip" title="${g.bestElectricalFeature}">${g.bestElectricalFeature.replaceAll("_"," ")}</span>
    </button>`).join("");
  root.querySelectorAll("[data-cbe-gene]").forEach(b=>b.addEventListener("click",()=>cbeSetGene(b.dataset.cbeGene)));
}
function cbeRenderSummary(){
  const g=cbeSelectedGene, m=cbeModelFor(g?.gene); if(!g)return;
  const rank=document.getElementById("cbe-selected-rank"); if(rank)rank.textContent=`rank #${g.rank} · ${g.gene}`;
  const mode=m?.modelMode||"phenotype-constrained";
  document.getElementById("cbe-model-mode").textContent=mode==="conductance-aware"?"conductance-aware":"phenotype";
  const root=document.getElementById("cbe-selected-summary");
  root.innerHTML=[
    ["Human gene",g.gene],["Mouse ortholog",g.mouseGene],
    ["Best electrical trait",g.bestElectricalFeature.replaceAll("_"," ")],
    ["Best ρ",(Number(g.bestRho)>=0?"+":"")+cbeFmt(g.bestRho,3)],
    ["Best FDR q",cbeFmt(g.bestQ,3)],["Significant traits",g.significantTraitCount],
    ["Mean cancer mutation",cbeFmt(g.meanMutationPercent,2)+"%"],
    ["Max cancer mutation",cbeFmt(g.maxMutationPercent,2)+"%"]
  ].map(([k,v])=>`<div><span>${k}</span><b>${v}</b></div>`).join("");
  const ev=document.getElementById("cbe-evidence-bars");
  const vals=[
    ["CBEF",g.discoveryScore],["Bioelectric",g.bioelectricEvidenceScore],
    ["Cancer",g.cancerEvidenceScore],["Synergy",g.crossDomainSynergy]
  ];
  ev.innerHTML=vals.map(([k,v])=>`<div class="evidence-row"><span>${k}</span><div class="evidence-track"><div class="evidence-fill" style="width:${cbeClamp(Number(v)*100,0,100).toFixed(1)}%"></div></div><b>${cbeFmt(v,3)}</b></div>`).join("");
  const simLabel=document.getElementById("cbe-sim-label");
  if(simLabel)simLabel.textContent=`${g.gene} · ${mode} · normalized counterfactual`;
}
function cbeRenderElectricalProfile(){
  const g=cbeSelectedGene;if(!g)return;
  const root=document.getElementById("cbe-electrical-profile");
  const rows=(g.electricalAssociations||[]).slice().sort((a,b)=>Math.abs(Number(b.rho))-Math.abs(Number(a.rho)));
  const mx=Math.max(.001,...rows.map(x=>Math.abs(Number(x.rho)||0)));
  root.innerHTML=rows.map(r=>{
    const v=Number(r.rho)||0,pct=cbeClamp(Math.abs(v)/mx*50,0,50);
    const style=v>=0?`left:50%;width:${pct}%`:`right:50%;width:${pct}%`;
    return `<div class="fingerprint-row"><span class="fingerprint-label" title="${r.feature}">${r.feature.replaceAll("_"," ")}</span><div class="fingerprint-axis"><span class="fingerprint-seg ${v>=0?'pos':'neg'}" style="${style}"></span></div><span class="fingerprint-value ${v>=0?'rho-pos':'rho-neg'}">${v>=0?'+':''}${v.toFixed(3)}</span></div>`;
  }).join("");
}
function cbeRenderCancerProfile(){
  const g=cbeSelectedGene;if(!g)return;
  const root=document.getElementById("cbe-cancer-profile");
  const studies=cbeCatalog.studies||[];
  const rows=studies.map(s=>({s,v:g.mutations?.[s.studyId]})).filter(x=>x.v!==null&&x.v!==undefined).sort((a,b)=>b.v-a.v);
  const mx=Math.max(1,...rows.map(x=>Number(x.v)||0));
  root.innerHTML=rows.map(({s,v})=>`<div class="mini-bar-row"><span title="${s.name}">${(s.cancerTypeName||s.studyId).slice(0,20)}</span><div class="mini-bar"><span style="width:${(Number(v)/mx*100).toFixed(1)}%"></span></div><b>${cbeFmt(v,1)}</b></div>`).join("");
}
function cbeStrength(){
  return Number(document.getElementById("cbe-strength")?.value||0)/100;
}
function cbeDrive(){
  return Number(document.getElementById("cbe-drive")?.value||60)/100;
}
function cbeModelParams(){
  const m=cbeModelFor(cbeSelectedGene?.gene);
  const p=m?.parameters||{};
  const s=cbeStrength();
  const pow=(x)=>Math.pow(Number(x||1),s);
  return {
    mode:m?.modelMode||"phenotype-constrained",
    EL:-65 + s*Number(p.vRestShift_mV||0),
    tau:20*pow(p.tauMultiplier),
    R:100*pow(p.inputResistanceMultiplier),
    fi:pow(p.fiGainMultiplier),
    adapt:0.75*pow(p.adaptationMultiplier),
    tauW:150,
    latencyScale:pow(p.latencyMultiplier),
    sag:pow(p.sagMultiplier),
    thresholdCurrent:pow(p.thresholdCurrentMultiplier),
    Vth:-50 + s*Number(p.thresholdVoltageShift_mV||0),
    Vreset:-68,
    kinetics:pow(p.spikeKineticsMultiplier)
  };
}
function cbeCurrent(t,params){
  const drive=cbeDrive();
  if(t>=120 && t<300) return -0.055*params.sag; // hyperpolarizing probe
  if(t>=420 && t<1750){
    const base=0.22*drive;
    return base*params.fi/Math.max(.35,params.thresholdCurrent);
  }
  return 0;
}
function cbeSimulate(params){
  const dt=.5,T=2000,n=Math.floor(T/dt);
  let V=params.EL,w=0,spikes=[];
  const trace=new Float32Array(n);
  for(let i=0;i<n;i++){
    const t=i*dt;
    const I=cbeCurrent(t,params);
    // Adaptive LIF: units are normalized but displayed in mV-scale coordinates.
    const drive=params.R*I;
    const dV=((-(V-params.EL)+drive-w)/Math.max(5,params.tau))*dt;
    const dw=((0.03*(V-params.EL)-w)/params.tauW)*dt;
    V+=dV;w+=dw;
    if(V>=params.Vth){
      trace[i]=30;
      spikes.push(t);
      V=params.Vreset;
      w+=params.adapt;
    }else trace[i]=V;
  }
  return {trace,spikes,dt,T,params};
}
function cbeBaselineParams(){
  return {mode:"baseline",EL:-65,tau:20,R:100,fi:1,adapt:.75,tauW:150,latencyScale:1,sag:1,thresholdCurrent:1,Vth:-50,Vreset:-68,kinetics:1};
}
function cbeDrawMembrane(){
  const canvas=document.getElementById("cbe-membrane-canvas");if(!canvas||!cbeSelectedGene)return;
  const ctx=canvas.getContext("2d"),w=canvas.width,h=canvas.height;
  const base=cbeSimulate(cbeBaselineParams()), model=cbeSimulate(cbeModelParams()); cbeLastSim=model;
  ctx.clearRect(0,0,w,h);ctx.fillStyle="#06131c";ctx.fillRect(0,0,w,h);
  ctx.strokeStyle="#17303e";ctx.lineWidth=1;
  for(let y=40;y<h-25;y+=50){ctx.beginPath();ctx.moveTo(48,y);ctx.lineTo(w-16,y);ctx.stroke();}
  for(let x=48;x<w-16;x+=150){ctx.beginPath();ctx.moveTo(x,20);ctx.lineTo(x,h-28);ctx.stroke();}
  const minV=-90,maxV=35;
  const draw=(sim,color,width,alpha)=>{
    ctx.strokeStyle=color;ctx.globalAlpha=alpha;ctx.lineWidth=width;ctx.beginPath();
    const stride=Math.max(1,Math.floor(sim.trace.length/(w-64)));
    let px=48;
    for(let i=0;i<sim.trace.length;i+=stride){
      const x=48+i/(sim.trace.length-1)*(w-64);
      const v=sim.trace[i]; const y=20+(maxV-v)/(maxV-minV)*(h-48);
      if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);px=x;
    }ctx.stroke();ctx.globalAlpha=1;
  };
  draw(base,"#71899a",1.6,.8); draw(model,"#58dfff",2.2,1);
  // current protocol
  ctx.strokeStyle="#a57aff";ctx.lineWidth=1.3;ctx.beginPath();
  for(let x=48;x<w-16;x++){
    const t=(x-48)/(w-64)*2000;const I=cbeCurrent(t,cbeModelParams());
    const y=h-15-I*120;
    if(x===48)ctx.moveTo(x,y);else ctx.lineTo(x,y);
  }ctx.stroke();
  ctx.fillStyle="#829aa8";ctx.font="11px system-ui";ctx.fillText("Vm (mV)",6,18);ctx.fillText("0 ms",45,h-3);ctx.fillText("2000 ms",w-65,h-3);
  cbeRenderModelReadout(base,model);
}
function cbeRenderModelReadout(base,model){
  const root=document.getElementById("cbe-model-readout");if(!root)return;
  const first=(x)=>x.spikes.length?x.spikes[0]:null;
  const hz=(x)=>x.spikes.length/(x.T/1000);
  const p=model.params;
  root.innerHTML=[
    ["Model mode",p.mode],["Resting set-point",cbeFmt(p.EL,2)+" mV"],
    ["Threshold",cbeFmt(p.Vth,2)+" mV"],["Membrane τ",cbeFmt(p.tau,2)+" ms"],
    ["Input resistance proxy",cbeFmt(p.R,1)],["Spike rate",cbeFmt(hz(model),2)+" Hz"],
    ["First spike",first(model)==null?"none":cbeFmt(first(model),1)+" ms"],["Δ spike rate",cbeFmt(hz(model)-hz(base),2)+" Hz"],
    ["Counterfactual strength",(cbeStrength()>=0?"+":"")+cbeFmt(cbeStrength(),2)],["Drive",Math.round(cbeDrive()*100)+"%"]
  ].map(([k,v])=>`<div><b>${v}</b><span>${k}</span></div>`).join("");
}
function cbeDrawNeuron(){
  const canvas=document.getElementById("cbe-neuron-canvas");if(!canvas||!cbeSelectedGene)return;
  const ctx=canvas.getContext("2d"),w=canvas.width,h=canvas.height;ctx.clearRect(0,0,w,h);ctx.fillStyle="#06131c";ctx.fillRect(0,0,w,h);
  const sim=cbeLastSim||cbeSimulate(cbeModelParams());
  const period=sim.T;
  const t=(cbeAnimT*16)%period;
  const recent=sim.spikes.some(s=>Math.abs(s-t)<35);
  const g=cbeSelectedGene;
  const cx=w*.48,cy=h*.48;
  const col=recent?"#ffffff":"#58dfff";
  const glow=recent?.75:.22+.13*Math.sin(cbeAnimT*.13);
  const grad=ctx.createRadialGradient(cx,cy,5,cx,cy,115);grad.addColorStop(0,recent?"rgba(255,255,255,.9)":"rgba(88,223,255,.65)");grad.addColorStop(1,"rgba(88,223,255,0)");
  ctx.globalAlpha=glow;ctx.fillStyle=grad;ctx.beginPath();ctx.arc(cx,cy,115,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;
  ctx.strokeStyle=col;ctx.fillStyle=col;ctx.lineWidth=3;ctx.lineCap="round";
  ctx.beginPath();ctx.arc(cx,cy,21,0,Math.PI*2);ctx.fill();
  const branches=[[-165,-72],[-185,38],[-96,-132],[132,-110],[171,-15],[143,95],[27,145],[-86,126]];
  branches.forEach(([dx,dy],i)=>{ctx.beginPath();ctx.moveTo(cx,cy);ctx.quadraticCurveTo(cx+dx*.52,cy+dy*.52,cx+dx,cy+dy);ctx.stroke();ctx.beginPath();ctx.arc(cx+dx,cy+dy,recent?6:3.5,0,Math.PI*2);ctx.fill();});
  ctx.fillStyle="#dff7ff";ctx.font="600 18px system-ui";ctx.fillText(g.gene,20,h-44);
  ctx.fillStyle="#7f99a8";ctx.font="11px system-ui";ctx.fillText(`CBEF rank #${g.rank} · ${cbeModelFor(g.gene)?.modelMode||"phenotype"}`,20,h-23);
  const status=document.getElementById("cbe-live-status");if(status)status.textContent=recent?"spike event":"membrane integration";
}
function cbeExportSelectedGeneReport(){
  if(!cbeSelectedGene)return;
  const model=cbeModelFor(cbeSelectedGene.gene);
  const report={
    generatedAt:new Date().toISOString(),
    method:cbeCatalog?.method||"CBEF v1.0",
    gene:cbeSelectedGene,
    dynamicModel:model,
    interpretation:{
      ranking:"Cross-domain evidence-fusion prioritization; not a causal disease mechanism.",
      simulation:"Correlation-informed normalized counterfactual; not a physical gene-effect estimate.",
      cancer:"Somatic mutation prevalence is an independent disease-genomic evidence layer."
    },
    sources:{
      portal:window.location.href.split("#")[0],
      top500Catalog:"data/top500_discovery_catalog.json",
      dynamicModels:"data/top500_dynamic_models.json"
    }
  };
  const blob=new Blob([JSON.stringify(report,null,2)],{type:"application/json"});
  const url=URL.createObjectURL(blob),a=document.createElement("a");
  a.href=url;a.download=`NEURO_BEAM_${cbeSelectedGene.gene}_research_report.json`;a.click();
  setTimeout(()=>URL.revokeObjectURL(url),500);
}
function cbeAnimate(){
  if(cbeAnimRunning){cbeAnimT++;cbeDrawNeuron();}
  requestAnimationFrame(cbeAnimate);
}
function cbeRenderAll(){
  if(!cbeSelectedGene)return;
  cbeRenderRankedList();cbeRenderSummary();cbeRenderElectricalProfile();cbeRenderCancerProfile();cbeDrawMembrane();cbeDrawNeuron();
}
Promise.all([
  fetch("data/top500_discovery_catalog.json").then(r=>{if(!r.ok)throw new Error("Top500 catalog not ready");return r.json()}),
  fetch("data/top500_dynamic_models.json").then(r=>{if(!r.ok)throw new Error("Dynamic models not ready");return r.json()})
]).then(([cat,mods])=>{
  cbeCatalog=cat;cbeModels=mods;
  document.getElementById("cbe-top-count").textContent=cat.nRankedGenes||cat.genes.length;
  document.getElementById("cbe-mapped-count").textContent=cat.nMappedGenes||"—";
  document.getElementById("cbe-cohort-count").textContent=(cat.studies||[]).length;
  const dl=document.getElementById("cbe-gene-options");
  dl.innerHTML=cat.genes.map(g=>`<option value="${g.gene}">#${g.rank} · ${g.bestElectricalFeature}</option>`).join("");
  cbeSelectedGene=cat.genes[0]||null;
  const search=document.getElementById("cbe-gene-search");if(search&&cbeSelectedGene)search.value=cbeSelectedGene.gene;
  search?.addEventListener("change",()=>cbeSetGene(search.value));
  search?.addEventListener("input",()=>cbeRenderRankedList());
  document.getElementById("cbe-rank-window")?.addEventListener("change",cbeRenderRankedList);
  document.getElementById("cbe-strength")?.addEventListener("input",e=>{
    const v=Number(e.target.value)/100;document.getElementById("cbe-strength-label").textContent=`${v>=0?"+":""}${v.toFixed(2)} normalized units`;cbeDrawMembrane();
  });
  document.getElementById("cbe-drive")?.addEventListener("input",e=>{
    document.getElementById("cbe-drive-label").textContent=`${e.target.value}%`;cbeDrawMembrane();
  });
  document.getElementById("cbe-export-gene-report")?.addEventListener("click",cbeExportSelectedGeneReport);
  cbeRenderAll();cbeAnimate();
}).catch(err=>{
  console.error("CBEF discovery engine unavailable",err);
  const root=document.getElementById("cbe-ranked-list");
  if(root)root.innerHTML='<div class="data-note warning-note"><b>Discovery computation in progress:</b> Top-500 CBEF outputs have not been published yet. The portal will populate automatically when the reproducible GitHub workflow completes.</div>';
});
