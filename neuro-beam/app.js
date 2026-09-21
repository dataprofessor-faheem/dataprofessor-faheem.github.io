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


function renderValidation(d){
  const f=(x,n=3)=>Number.isFinite(Number(x))?Number(x).toFixed(n):"—";
  document.getElementById("val-ari").textContent=f(d.bootstrap_ari_mean,3);
  document.getElementById("val-gmm").textContent=d.gmm_best_k_bic ?? "—";
  document.getElementById("val-hdb").textContent=d.hdbscan_clusters ?? "—";
  document.getElementById("val-nmi").textContent=f(d.state_class_nmi,3);

  const sroot=document.getElementById("stability-bars");
  const st=d.state_stability||{};
  sroot.innerHTML=Object.entries(st).map(([k,v])=>{
    const mean=Math.max(0,Math.min(1,Number(v.mean_jaccard||0)));
    const lo=Math.max(0,Math.min(1,Number(v.p05||0)));
    const hi=Math.max(0,Math.min(1,Number(v.p95||0)));
    return `<div class="stab-row"><b>${k}</b><div class="stab-track"><div class="stab-fill" style="width:${(mean*100).toFixed(1)}%"></div><div class="stab-band" style="left:${(lo*100).toFixed(1)}%;width:${Math.max(1,(hi-lo)*100).toFixed(1)}%"></div></div><span>${mean.toFixed(3)} · n=${v.n}</span></div>`;
  }).join("");

  const cont=d.contingency||{};
  const states=Object.keys(cont);
  const classes=[...new Set(states.flatMap(s=>Object.keys(cont[s]||{})))];
  const totals={}; classes.forEach(c=>totals[c]=states.reduce((a,s)=>a+(cont[s]?.[c]||0),0));
  let table='<table class="matrix-table"><thead><tr><th>State</th>'+classes.map(c=>`<th>${c}</th>`).join('')+'</tr></thead><tbody>';
  states.forEach(s=>{
    const row=cont[s]||{}; const max=Math.max(...classes.map(c=>row[c]||0),0);
    table+=`<tr><td><b>${s}</b></td>`+classes.map(c=>`<td class="${(row[c]||0)===max&&max>0?'matrix-cell-hi':''}">${row[c]||0}</td>`).join('')+'</tr>';
  });
  table+='</tbody></table>';
  document.getElementById("state-class-table").innerHTML=table;

  const rare=Object.entries(st).filter(([,v])=>Number(v.n)<25).map(([k])=>k);
  let msg=`<b>Validation summary:</b> bootstrap ARI mean ${f(d.bootstrap_ari_mean)}; GMM BIC favors k=${d.gmm_best_k_bic}; HDBSCAN finds ${d.hdbscan_clusters} cluster(s) with ${f((d.hdbscan_noise_fraction||0)*100,1)}% noise. Post hoc state↔class NMI is ${f(d.state_class_nmi)}.`;
  if(rare.length) msg+=` Rare candidate state(s) ${rare.join(", ")} remain provisional because n<25.`;
  msg+=' These metrics describe reproducibility/correspondence, not causality.';
  document.getElementById("validation-interpretation").innerHTML=msg;
}
fetch("data/visual_cortex_stability_validation.json").then(r=>{
  if(!r.ok) throw new Error("not ready");
  return r.json();
}).then(renderValidation).catch(()=>{});


let cbioCatalog=null;
let selectedStudies=[];

function studyLabel(s){
  return s.cancerTypeName && s.cancerTypeName!==s.cancerTypeId ? s.cancerTypeName : (s.cancerTypeId||"Cancer study");
}
function renderSelectedStudies(){
  const root=document.getElementById("selected-diseases");
  const limit=document.getElementById("selected-limit");
  if(!root||!limit)return;
  limit.textContent=`${selectedStudies.length} / 10`;
  root.innerHTML=selectedStudies.map(s=>`<span class="selected-chip" title="${s.name}">${studyLabel(s)}<button data-remove-study="${s.studyId}" aria-label="Remove">×</button></span>`).join("");
  root.querySelectorAll("[data-remove-study]").forEach(b=>b.addEventListener("click",()=>{
    selectedStudies=selectedStudies.filter(s=>s.studyId!==b.dataset.removeStudy);
    renderSelectedStudies(); renderStudyBrowser(); renderDiseaseComparison();
  }));
}
function addStudy(id){
  if(!cbioCatalog||selectedStudies.length>=10||selectedStudies.some(s=>s.studyId===id))return;
  const s=cbioCatalog.studies.find(x=>x.studyId===id); if(!s)return;
  selectedStudies.push(s);
  renderSelectedStudies(); renderStudyBrowser(); renderDiseaseComparison();
}
function renderStudyBrowser(){
  if(!cbioCatalog)return;
  const root=document.getElementById("disease-browser");
  const q=(document.getElementById("disease-search")?.value||"").trim().toLowerCase();
  const rows=cbioCatalog.studies.filter(s=>{
    const hay=[s.studyId,s.name,s.cancerTypeName,s.cancerTypeId,s.description].join(" ").toLowerCase();
    return !q||hay.includes(q);
  }).slice(0,120);
  document.getElementById("disease-count-label").textContent=`${cbioCatalog.generatedStudyCount.toLocaleString()} public studies · showing ${rows.length}`;
  root.innerHTML=rows.map(s=>{
    const chosen=selectedStudies.some(x=>x.studyId===s.studyId);
    const disabled=chosen||selectedStudies.length>=10;
    const desc=(s.description||"").replace(/<[^>]*>/g," ").slice(0,130);
    return `<div class="disease-item"><div><h4>${s.name}</h4><p>${studyLabel(s)} · ${Number(s.sampleCount||0).toLocaleString()} samples · ${s.studyId}<br>${desc}</p></div><button data-add-study="${s.studyId}" ${disabled?"disabled":""} title="Add study">+</button></div>`;
  }).join("");
  root.querySelectorAll("[data-add-study]").forEach(b=>b.addEventListener("click",()=>addStudy(b.dataset.addStudy)));
}
function renderDiseaseComparison(){
  const root=document.getElementById("disease-comparison");
  const bars=document.getElementById("disease-sample-bars");
  if(!root||!bars)return;
  if(!selectedStudies.length){
    root.innerHTML='<p class="micro-note">Choose up to 10 disease/study cohorts.</p>'; bars.innerHTML=""; return;
  }
  root.innerHTML='<table class="disease-table"><thead><tr><th>Disease / study</th><th>Samples</th><th>Genome</th><th>Explore</th></tr></thead><tbody>'+
    selectedStudies.map(s=>`<tr><td><b>${studyLabel(s)}</b><br><span>${s.name}</span></td><td>${Number(s.sampleCount||0).toLocaleString()}</td><td>${s.referenceGenome||"—"}</td><td><a target="_blank" rel="noopener" href="${s.cbioSummaryUrl}">cBioPortal ↗</a></td></tr>`).join("")+
    '</tbody></table>';
  const data={}; selectedStudies.forEach(s=>data[studyLabel(s)]=Number(s.sampleCount||0));
  barChart(bars,data);
}
function openCbioQuery(){
  if(!selectedStudies.length)return;
  const genes=(document.getElementById("gene-query")?.value||"TP53").trim().split(/[\s,;]+/).filter(Boolean).slice(0,20).join(" ");
  const ids=selectedStudies.map(s=>s.studyId).join(",");
  const url="https://www.cbioportal.org/results/oncoprint?cancer_study_list="+encodeURIComponent(ids)+"&case_set_id=all&gene_list="+encodeURIComponent(genes);
  window.open(url,"_blank","noopener");
}
fetch("data/cbioportal_study_catalog.json").then(r=>r.json()).then(d=>{
  cbioCatalog=d;
  selectedStudies=(d.defaultStudyIds||[]).map(id=>d.studies.find(s=>s.studyId===id)).filter(Boolean).slice(0,10);
  renderSelectedStudies(); renderStudyBrowser(); renderDiseaseComparison();
  document.getElementById("disease-search")?.addEventListener("input",renderStudyBrowser);
  document.getElementById("open-cbio-query")?.addEventListener("click",openCbioQuery);
}).catch(err=>{
  console.error("cBioPortal catalog unavailable",err);
  const root=document.getElementById("disease-browser");
  if(root)root.innerHTML='<p class="micro-note">The cBioPortal study catalog is being generated. Refresh after the catalog workflow completes.</p>';
});


let advancedDiseaseData=null;
function heatColor(v,max){
  if(v==null||!Number.isFinite(+v)) return "rgba(255,255,255,.02)";
  const t=Math.max(0,Math.min(1,(+v)/(max||1)));
  return `rgba(${Math.round(70+170*t)},${Math.round(110-35*t)},${Math.round(180+40*t)},${0.10+0.70*t})`;
}
function renderAdvancedHeatmap(){
  const d=advancedDiseaseData;if(!d)return;
  const moduleFilter=document.getElementById("heatmap-module-filter")?.value||"ALL";
  const sort=document.getElementById("heatmap-sort")?.value||"mean";
  const modules=d.modules||{};
  const membership={};Object.entries(modules).forEach(([m,gs])=>gs.forEach(g=>membership[g]=m));
  let genes=(d.geneSummary||[]).filter(g=>moduleFilter==="ALL"||g.module===moduleFilter);
  if(sort==="max")genes=genes.slice().sort((a,b)=>(b.maxPercent||0)-(a.maxPercent||0));
  else if(sort==="alpha")genes=genes.slice().sort((a,b)=>a.gene.localeCompare(b.gene));
  else genes=genes.slice().sort((a,b)=>(b.meanPercent||0)-(a.meanPercent||0));
  const studies=d.studies||[];
  const vals=[];genes.forEach(g=>studies.forEach(s=>{const v=d.geneByStudyPercent?.[g.gene]?.[s.studyId];if(v!=null)vals.push(+v)}));const max=Math.max(1,...vals);
  let h='<table class="heatmap-table"><thead><tr><th>Gene</th><th>Module</th>'+studies.map(s=>`<th title="${s.name}">${(s.cancerTypeName||s.studyId).slice(0,14)}</th>`).join('')+'</tr></thead><tbody>';
  genes.forEach(g=>{
    h+=`<tr><td><b>${g.gene}</b></td><td>${g.module.replace(/ \/ .*/,"")}</td>`;
    studies.forEach(s=>{const v=d.geneByStudyPercent?.[g.gene]?.[s.studyId];h+=`<td class="heat-cell" title="${s.name} · ${g.gene}: ${v==null?'NA':(+v).toFixed(2)+'%'}" style="background:${heatColor(v,max)}">${v==null?'—':(+v).toFixed(1)}</td>`;});
    h+='</tr>';
  });h+='</tbody></table>';
  document.getElementById("gene-disease-heatmap").innerHTML=h;
}
function renderAdvancedDisease(d){
  advancedDiseaseData=d;
  const failed=(d.errors||[]).length;
  const total=(d.studies||[]).length;
  const matrixVals=Object.values(d.geneByStudyPercent||{}).flatMap(x=>Object.values(x||{}));
  const validMolecularCells=matrixVals.filter(v=>v!==null && Number.isFinite(Number(v))).length;
  if(total>0 && validMolecularCells===0){
    document.getElementById("adv-study-count").textContent=total;
    document.getElementById("adv-gene-count").textContent=(d.genes||Object.keys(d.geneByStudyPercent||{})).length;
    document.getElementById("adv-top-gene").textContent="NA";
    document.getElementById("adv-errors").textContent=failed;
    const hm=document.getElementById("gene-disease-heatmap");
    if(hm) hm.innerHTML='<div class="data-note warning-note"><b>Data withheld:</b> cBioPortal mutation retrieval failed for all selected studies. Zero values are not displayed because they would be misleading. The backend is being revalidated against the documented API request.</div>';
    const mb=document.getElementById("module-burden-chart"); if(mb) mb.innerHTML='<p class="micro-note">Module burden withheld until successful molecular retrieval.</p>';
    const tg=document.getElementById("top-gene-table"); if(tg) tg.innerHTML='<p class="micro-note">Gene ranking withheld until successful molecular retrieval.</p>';
    const ms=document.getElementById("mutation-spectrum"); if(ms) ms.innerHTML='<p class="micro-note">Mutation spectrum withheld until successful molecular retrieval.</p>';
    const sp=document.getElementById("study-provenance"); if(sp) sp.innerHTML='<p class="micro-note">Study denominators are available, but molecular values are withheld because mutation retrieval failed.</p>';
    return;
  }
  document.getElementById("adv-study-count").textContent=total;
  document.getElementById("adv-gene-count").textContent=(d.genes||Object.keys(d.geneByStudyPercent||{})).length;
  document.getElementById("adv-top-gene").textContent=d.geneSummary?.[0]?.gene||"—";
  document.getElementById("adv-errors").textContent=(d.errors||[]).length;

  const mf=document.getElementById("heatmap-module-filter");
  Object.keys(d.modules||{}).forEach(m=>{const o=document.createElement("option");o.value=m;o.textContent=m;mf.appendChild(o);});
  mf.addEventListener("change",renderAdvancedHeatmap);
  document.getElementById("heatmap-sort").addEventListener("change",renderAdvancedHeatmap);
  renderAdvancedHeatmap();

  const modRoot=document.getElementById("module-burden-chart");
  modRoot.innerHTML=Object.entries(d.moduleByStudyPercent||{}).map(([m,vals])=>{
    const arr=Object.entries(vals).sort((a,b)=>(b[1]||0)-(a[1]||0)); const mx=Math.max(1,...arr.map(x=>x[1]||0));
    return `<div class="module-group"><h4>${m}</h4>${arr.map(([sid,v])=>{const s=d.studies.find(x=>x.studyId===sid);return `<div class="mini-bar-row"><span title="${s?.name||sid}">${(s?.cancerTypeName||sid).slice(0,18)}</span><div class="mini-bar"><span style="width:${((v||0)/mx*100).toFixed(1)}%"></span></div><b>${v==null?'—':(+v).toFixed(1)}</b></div>`;}).join("")}</div>`;
  }).join("");

  document.getElementById("top-gene-table").innerHTML=(d.geneSummary||[]).slice(0,24).map((g,i)=>`<div class="rank-row"><span>#${i+1}</span><b>${g.gene}</b><small>${g.module}</small><span class="rank-score">${g.meanPercent==null?'—':g.meanPercent.toFixed(2)}%</span></div>`).join("");

  const spec=document.getElementById("mutation-spectrum");
  spec.innerHTML=(d.studies||[]).map(s=>{
    const obj=d.mutationTypeCounts?.[s.studyId]||{};const arr=Object.entries(obj).slice(0,6);const mx=Math.max(1,...arr.map(x=>x[1]));
    return `<div class="spectrum-study"><h4>${s.cancerTypeName||s.studyId}</h4>${arr.map(([k,v])=>`<div class="spectrum-line"><span>${k}</span><div class="mini-bar"><span style="width:${(v/mx*100).toFixed(1)}%"></span></div><b>${v}</b></div>`).join("")}</div>`;
  }).join("");

  let p='<table class="matrix-table"><thead><tr><th>Study</th><th>Sequenced n</th><th>Denominator source</th><th>Mutation profile</th><th>Events fetched</th></tr></thead><tbody>';
  (d.studies||[]).forEach(s=>p+=`<tr><td><b>${s.cancerTypeName||s.studyId}</b><br>${s.studyId}</td><td>${s.mutationSequencedDenominator}</td><td>${s.denominatorSource}</td><td>${s.mutationProfileId}</td><td>${Number(s.mutationEventsFetched||0).toLocaleString()}</td></tr>`);
  p+='</tbody></table>';document.getElementById("study-provenance").innerHTML=p;
}
fetch("data/disease_bioelectric_bridge.json").then(r=>r.ok?r.json():Promise.reject()).then(renderAdvancedDisease).catch(()=>{});


let bioeBridgeData=null;
function renderBioeFeatureGenes(){
  const d=bioeBridgeData;if(!d)return;
  const feature=document.getElementById("bioelectric-feature-select")?.value;
  const root=document.getElementById("bioe-feature-gene-table");
  let rows=(d.topAssociations||[]).filter(x=>x.feature===feature && Number.isFinite(+x.rho));
  rows=rows.sort((a,b)=>Math.abs(+b.rho)-Math.abs(+a.rho)).slice(0,30);
  root.innerHTML=rows.map((r,i)=>`<div class="rank-row"><span>#${i+1}</span><b>${r.gene}</b><small>${r.q<=0.05?'<span class="sig-badge">FDR</span>':''} q=${Number(r.q).toExponential(1)}</small><span class="rank-score ${r.rho>=0?'rho-pos':'rho-neg'}">${r.rho>=0?'+':''}${Number(r.rho).toFixed(3)}</span></div>`).join("")||'<p class="micro-note">No associations available for this trait.</p>';
}
function renderBioeContributors(){
  const d=bioeBridgeData;if(!d)return;
  const sid=document.getElementById("bioe-disease-select")?.value;
  const row=(d.diseaseBioelectricScores||[]).find(x=>x.studyId===sid);
  const root=document.getElementById("bioe-contributor-table");
  root.innerHTML=(row?.topContributors||[]).map((x,i)=>`<div class="rank-row"><span>#${i+1}</span><b>${x.gene}</b><small>${x.bestFeature} · mut ${Number(x.mutationPercent).toFixed(1)}%</small><span class="rank-score ${x.rho>=0?'rho-pos':'rho-neg'}">${x.rho>=0?'+':''}${Number(x.rho).toFixed(3)}</span></div>`).join("")||'<p class="micro-note">No contributor data.</p>';
}
function renderBioelectricDisease(d){
  bioeBridgeData=d;
  document.getElementById("bioe-cells").textContent=Number(d.nMatchedCells||0).toLocaleString();
  document.getElementById("bioe-genes").textContent=Number(d.nGenesTested||0).toLocaleString();
  document.getElementById("bioe-features").textContent=(d.electricalFeatures||[]).length;
  document.getElementById("bioe-shared").textContent=(d.candidatePanelSharedGenes||[]).length;

  const fs=document.getElementById("bioelectric-feature-select");
  fs.innerHTML=(d.electricalFeatures||[]).map(x=>`<option value="${x}">${x.replaceAll("_"," ")}</option>`).join("");
  fs.addEventListener("change",renderBioeFeatureGenes);renderBioeFeatureGenes();

  const gs=(d.geneBioelectricScores||[]).slice(0,30), mx=Math.max(.001,...gs.map(x=>x.bioelectricCouplingScore||0));
  document.getElementById("bioe-bcs-chart").innerHTML=gs.map(x=>`<div class="bioe-score-row"><span>${x.gene}</span><div class="mini-bar"><span style="width:${(x.bioelectricCouplingScore/mx*100).toFixed(1)}%"></span></div><b>${x.bioelectricCouplingScore.toFixed(3)}</b></div>`).join("");

  const diseases=d.diseaseBioelectricScores||[];
  const dsel=document.getElementById("bioe-disease-select");
  dsel.innerHTML=diseases.map(x=>`<option value="${x.studyId}">${x.cancerTypeName||x.name}</option>`).join("");
  dsel.addEventListener("change",renderBioeContributors);renderBioeContributors();

  const ds=diseases.filter(x=>x.exploratoryBioelectricAlterationIndex!=null);
  const dmax=Math.max(.001,...ds.map(x=>x.exploratoryBioelectricAlterationIndex||0));
  document.getElementById("bioe-disease-score-chart").innerHTML=ds.map(x=>`<div class="mini-bar-row"><span title="${x.name}">${(x.cancerTypeName||x.name).slice(0,20)}</span><div class="mini-bar"><span style="width:${(x.exploratoryBioelectricAlterationIndex/dmax*100).toFixed(1)}%"></span></div><b>${x.exploratoryBioelectricAlterationIndex.toFixed(2)}</b></div>`).join("");

  const genes=(d.geneBioelectricScores||[]).slice(0,30);
  let h='<table class="heatmap-table"><thead><tr><th>Gene</th><th>Best electrical trait</th>'+diseases.map(x=>`<th title="${x.name}">${(x.cancerTypeName||x.studyId).slice(0,13)}</th>`).join('')+'</tr></thead><tbody>';
  const maxContrib=Math.max(.001,...genes.flatMap(g=>diseases.map(ds=>{const c=(ds.topContributors||[]).find(x=>x.gene===g.gene);return c?c.contribution:0;})));
  genes.forEach(g=>{
    h+=`<tr><td><b>${g.gene}</b></td><td>${g.bestFeature.replaceAll("_"," ")}</td>`;
    diseases.forEach(ds=>{const c=(ds.topContributors||[]).find(x=>x.gene===g.gene);const v=c?c.contribution:null;h+=`<td class="heat-cell" style="background:${heatColor(v,maxContrib)}" title="${v==null?'Not among top contributors':'weighted contribution '+v.toFixed(4)}">${v==null?'—':v.toFixed(3)}</td>`;});
    h+='</tr>';
  });h+='</tbody></table>';
  document.getElementById("bioe-disease-matrix").innerHTML=h;
}
fetch("data/bioelectric_disease_bridge.json").then(r=>r.ok?r.json():Promise.reject()).then(renderBioelectricDisease).catch(()=>{});


/* === Cancer × Gene × Bioelectric Signature Explorer === */
let signatureCube=null;
let signatureSelectedStudies=new Set();

function sigFmt(v,d=4){
  if(v===null||v===undefined||Number.isNaN(Number(v))) return "NA";
  const n=Number(v);
  if(Math.abs(n)>0 && Math.abs(n)<0.0001) return n.toExponential(3);
  return n.toFixed(d);
}
function sigCsvEscape(v){
  if(v===null||v===undefined)return "";
  const s=String(v);
  return /[",\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;
}
function signatureRowsFiltered(){
  if(!signatureCube)return[];
  const gene=document.getElementById("signature-gene-select")?.value;
  const signal=document.getElementById("signature-signal-select")?.value;
  return signatureCube.rows.filter(r=>r.gene===gene && r.electrical_feature===signal && signatureSelectedStudies.has(r.study_id));
}
function exportCurrentSignatureCsv(){
  const rows=signatureRowsFiltered();
  if(!rows.length)return;
  const cols=Object.keys(rows[0]);
  const csv=[cols.join(","),...rows.map(r=>cols.map(c=>sigCsvEscape(r[c])).join(","))].join("\n");
  const blob=new Blob([csv],{type:"text/csv;charset=utf-8"});
  const url=URL.createObjectURL(blob);
  const a=document.createElement("a");
  const gene=document.getElementById("signature-gene-select").value;
  const sig=document.getElementById("signature-signal-select").value;
  a.href=url;a.download=`NEURO_BEAM_${gene}_${sig}_selected_cohorts.csv`;a.click();
  setTimeout(()=>URL.revokeObjectURL(url),500);
}
function renderSignatureCohorts(){
  const root=document.getElementById("signature-cohort-selector");
  root.innerHTML=signatureCube.studies.map(s=>{
    const active=signatureSelectedStudies.has(s.studyId);
    return `<button class="cohort-pill ${active?'active':''}" data-sig-study="${s.studyId}" title="${s.name} · mutation n=${s.mutationSequencedDenominator}">${s.cancerTypeName}</button>`;
  }).join("");
  root.querySelectorAll("[data-sig-study]").forEach(b=>b.addEventListener("click",()=>{
    const id=b.dataset.sigStudy;
    if(signatureSelectedStudies.has(id))signatureSelectedStudies.delete(id);
    else if(signatureSelectedStudies.size<10)signatureSelectedStudies.add(id);
    document.getElementById("signature-cohort-count").textContent=`${signatureSelectedStudies.size} / 10`;
    renderSignatureCohorts();renderSignatureExplorer();
  }));
}
function renderSignatureBars(rows,metric){
  const root=document.getElementById("signature-cohort-bars");
  const values=rows.map(r=>Number(r[metric])).filter(Number.isFinite);
  const mx=Math.max(.000001,...values.map(Math.abs));
  const labels={
    mutation_percent:"Mutation prevalence (%)",
    spearman_rho:"Spearman rho",
    signed_mutation_bioelectric_score:"Signed mutation × bioelectric score",
    absolute_mutation_bioelectric_score:"Absolute mutation × bioelectric score"
  };
  document.getElementById("signature-chart-label").textContent=labels[metric]||metric;
  const studyMap=Object.fromEntries(signatureCube.studies.map(s=>[s.studyId,s]));
  root.innerHTML=rows.sort((a,b)=>Math.abs(Number(b[metric]))-Math.abs(Number(a[metric]))).map(r=>{
    const v=Number(r[metric]),pct=Math.min(100,Math.abs(v)/mx*100);
    const s=studyMap[r.study_id];
    return `<div class="signature-bar-row"><span class="signature-bar-label" title="${r.study_name}">${s?.cancerTypeName||r.cancer_type}</span><div class="signature-bar-track"><div class="signature-bar-fill ${v<0?'negative':''}" style="width:${pct.toFixed(1)}%"></div></div><span class="signature-bar-value ${v<0?'rho-neg':'rho-pos'}">${sigFmt(v,metric==='mutation_percent'?2:5)}</span></div>`;
  }).join("");
}
function renderGeneFingerprint(gene){
  const root=document.getElementById("gene-electrical-fingerprint");
  const unique=new Map();
  signatureCube.rows.filter(r=>r.gene===gene).forEach(r=>{if(!unique.has(r.electrical_feature))unique.set(r.electrical_feature,r)});
  const rows=[...unique.values()].sort((a,b)=>Math.abs(b.spearman_rho)-Math.abs(a.spearman_rho));
  const mx=Math.max(.001,...rows.map(r=>Math.abs(Number(r.spearman_rho))));
  root.innerHTML=rows.map(r=>{
    const v=Number(r.spearman_rho),pct=Math.min(50,Math.abs(v)/mx*50);
    const style=v>=0?`left:50%;width:${pct}%`:`right:50%;width:${pct}%`;
    return `<div class="fingerprint-row"><span class="fingerprint-label" title="${r.electrical_feature}">${r.electrical_feature.replaceAll("_"," ")}</span><div class="fingerprint-axis"><span class="fingerprint-seg ${v>=0?'pos':'neg'}" style="${style}"></span></div><span class="fingerprint-value ${v>=0?'rho-pos':'rho-neg'}">${v>=0?'+':''}${v.toFixed(3)}</span></div>`;
  }).join("");
}
function renderSignatureMatrix(gene){
  const signals=signatureCube.electricalFeatures;
  const studies=signatureCube.studies.filter(s=>signatureSelectedStudies.has(s.studyId));
  const lookup=new Map(signatureCube.rows.filter(r=>r.gene===gene).map(r=>[`${r.study_id}|${r.electrical_feature}`,r]));
  const vals=[];
  lookup.forEach(r=>{if(signatureSelectedStudies.has(r.study_id)&&r.signed_mutation_bioelectric_score!=null)vals.push(Math.abs(Number(r.signed_mutation_bioelectric_score)))});
  const mx=Math.max(.000001,...vals);
  let h='<table class="heatmap-table"><thead><tr><th>Electrical signal</th>'+studies.map(s=>`<th title="${s.name}">${s.cancerTypeName.slice(0,13)}</th>`).join('')+'</tr></thead><tbody>';
  signals.forEach(sig=>{
    h+=`<tr><td>${sig.replaceAll("_"," ")}</td>`;
    studies.forEach(s=>{
      const r=lookup.get(`${s.studyId}|${sig}`);
      const v=r?.signed_mutation_bioelectric_score;
      let bg="rgba(255,255,255,.02)";
      if(v!==null&&v!==undefined){
        const t=Math.min(1,Math.abs(Number(v))/mx);
        bg=Number(v)>=0?`rgba(88,223,255,${.08+.72*t})`:`rgba(255,125,189,${.08+.72*t})`;
      }
      h+=`<td class="heat-cell" style="background:${bg}" title="${r?gene+' · '+sig+' · '+s.cancerTypeName+'\nmutation '+sigFmt(r.mutation_percent,3)+'%\nrho '+sigFmt(r.spearman_rho,5)+'\nq '+sigFmt(r.bh_fdr_q,5)+'\nsigned '+sigFmt(v,6):'NA'}">${v==null||v===undefined?'—':sigFmt(v,4)}</td>`;
    });
    h+='</tr>';
  });
  h+='</tbody></table>';
  document.getElementById("signature-signal-matrix").innerHTML=h;
}
function renderSignatureExactTable(rows){
  const root=document.getElementById("signature-exact-table");
  let h='<table class="matrix-table"><thead><tr><th>Cohort</th><th>Mutation n</th><th>Mutation %</th><th>ρ</th><th>p</th><th>BH q</th><th>Neuron n</th><th>Signed</th><th>Absolute</th><th>BCS</th></tr></thead><tbody>';
  rows.forEach(r=>{
    h+=`<tr><td><b>${r.cancer_type}</b><br><small>${r.study_id}</small></td><td>${r.mutation_sequenced_n}</td><td>${sigFmt(r.mutation_percent,4)}</td><td class="${Number(r.spearman_rho)>=0?'rho-pos':'rho-neg'}">${sigFmt(r.spearman_rho,6)}</td><td>${sigFmt(r.p_value,6)}</td><td>${sigFmt(r.bh_fdr_q,6)}</td><td>${r.matched_neuron_n}</td><td>${sigFmt(r.signed_mutation_bioelectric_score,7)}</td><td>${sigFmt(r.absolute_mutation_bioelectric_score,7)}</td><td>${sigFmt(r.bioelectric_coupling_score,5)}</td></tr>`;
  });
  h+='</tbody></table>';root.innerHTML=h;
}
function renderSignatureExplorer(){
  if(!signatureCube)return;
  const gene=document.getElementById("signature-gene-select").value;
  const signal=document.getElementById("signature-signal-select").value;
  const metric=document.getElementById("signature-metric-select").value;
  const rows=signatureRowsFiltered();
  if(!rows.length)return;

  const ref=rows[0];
  document.getElementById("sig-kpi-gene").textContent=gene;
  document.getElementById("sig-kpi-mouse").textContent=`mouse ortholog: ${ref.mouse_gene}`;
  document.getElementById("sig-kpi-signal").textContent=signal.replaceAll("_"," ");
  document.getElementById("sig-kpi-rho").textContent=(Number(ref.spearman_rho)>=0?"+":"")+sigFmt(ref.spearman_rho,4);
  document.getElementById("sig-kpi-direction").textContent=Number(ref.spearman_rho)>=0?"positive neuronal association":"negative neuronal association";
  document.getElementById("sig-kpi-q").textContent=sigFmt(ref.bh_fdr_q,4);
  document.getElementById("sig-kpi-n").textContent=`matched neuronal n=${ref.matched_neuron_n}`;
  document.getElementById("sig-kpi-bcs").textContent=sigFmt(ref.bioelectric_coupling_score,3);
  document.getElementById("sig-kpi-consistency").textContent=`direction consistency ${sigFmt((ref.same_direction_fraction_across_classes||0)*100,0)}% across ${ref.classes_tested} classes`;

  renderSignatureBars(rows,metric);
  renderGeneFingerprint(gene);
  renderSignatureMatrix(gene);
  renderSignatureExactTable(rows);

  const d=document.getElementById("signature-detail-card");
  d.innerHTML=[
    ["Gene",gene],["Mouse gene",ref.mouse_gene],["Electrical trait",signal.replaceAll("_"," ")],
    ["Spearman ρ",(Number(ref.spearman_rho)>=0?"+":"")+sigFmt(ref.spearman_rho,6)],
    ["p-value",sigFmt(ref.p_value,6)],["BH-FDR q",sigFmt(ref.bh_fdr_q,6)],
    ["Matched neurons",ref.matched_neuron_n],["Best gene-level trait",ref.best_electrical_feature.replaceAll("_"," ")],
    ["BCS",sigFmt(ref.bioelectric_coupling_score,5)],["Class direction consistency",sigFmt((ref.same_direction_fraction_across_classes||0)*100,1)+"%"]
  ].map(([k,v])=>`<div><span>${k}</span><b>${v}</b></div>`).join("");
}
fetch("data/cancer_gene_bioelectric_signature_cube.json").then(r=>r.json()).then(d=>{
  signatureCube=d;
  d.studies.forEach(s=>signatureSelectedStudies.add(s.studyId));
  const gs=document.getElementById("signature-gene-select");
  const ss=document.getElementById("signature-signal-select");
  gs.innerHTML=d.genes.map(g=>`<option value="${g}">${g}</option>`).join("");
  ss.innerHTML=d.electricalFeatures.map(s=>`<option value="${s}">${s.replaceAll("_"," ")}</option>`).join("");
  // Start with a strongly interpretable ion-channel gene and threshold-current phenotype.
  if(d.genes.includes("SCN1A"))gs.value="SCN1A";
  if(d.electricalFeatures.includes("threshold_i_long_square"))ss.value="threshold_i_long_square";
  renderSignatureCohorts();
  [gs,ss,document.getElementById("signature-metric-select")].forEach(x=>x.addEventListener("change",renderSignatureExplorer));
  document.getElementById("download-filtered-signature").addEventListener("click",exportCurrentSignatureCsv);
  renderSignatureExplorer();
}).catch(err=>{
  console.error("Signature cube unavailable",err);
  const el=document.getElementById("signature-exact-table");
  if(el)el.innerHTML='<div class="data-note warning-note"><b>Signature cube unavailable:</b> the analysis file could not be loaded.</div>';
});

document.getElementById("copy-platform-citation")?.addEventListener("click",async e=>{
  const citation="Khan MF, Ahmad K. NEURO-BEAM: Neuronal BioElectricity–Activity–Molecular Atlas. GDRN Network. Available at: https://www.gdrnetwork.org/neuro-beam/";
  try{await navigator.clipboard.writeText(citation);e.target.textContent="Citation copied";setTimeout(()=>e.target.textContent="Copy citation",1600);}catch(_){}
});


/* === NEURO-BEAM Top-500 Discovery Studio === */
let nbTop500=null, nbCancerRows=[], nbBioRows=[], nbModelLib=null;
let nbSelectedGene=null, nbLatestSim=null, nbGeneAnimPhase=0;

function nbParseCSV(text){
  const lines=text.trim().split(/\r?\n/); if(lines.length<2)return[];
  function split(line){let a=[],c="",q=false;for(let i=0;i<line.length;i++){let ch=line[i];if(ch==='"'){if(q&&line[i+1]==='"'){c+='"';i++;}else q=!q;}else if(ch===','&&!q){a.push(c);c="";}else c+=ch;}a.push(c);return a;}
  const h=split(lines[0]);
  return lines.slice(1).filter(Boolean).map(line=>{const a=split(line),o={};h.forEach((k,i)=>o[k]=a[i]??"");return o;});
}
function nbNum(v){const n=Number(v);return Number.isFinite(n)?n:null;}
function nbInterpolate(base,target,strength){
  const out={};Object.keys(base).forEach(k=>{const b=Number(base[k]);const t=Number(target[k]??b);out[k]=b+(t-b)*strength;});return out;
}
function nbSimulate(params,currentPA){
  const dt=.1,T=1000,n=Math.round(T/dt),Vtrace=new Float32Array(n),spikes=[];
  let V=params.E_L_mV,w=0,h=.15,refr=0;
  const tauh=120,Eh=params.E_h_mV??-35;
  const stepStart=Math.max(30,100+(params.latency_bias_ms||0)),stepEnd=900;
  for(let i=0;i<n;i++){
    const t=i*dt;
    const I=(t>=stepStart&&t<=stepEnd)?currentPA*(params.input_gain||1):0;
    const hinf=1/(1+Math.exp((V+75)/5.5));
    h+=(hinf-h)/tauh*dt;
    const Ih=(params.g_h_relative||0)*80*h*((Eh-V)/40);
    w+=(-w/(params.tau_w_ms||120))*dt;
    if(refr>0){refr-=dt;V=params.V_reset_mV;}
    else{
      const drive=(params.R_MOhm||100)*(I-w+Ih)/1000;
      V+=(-(V-params.E_L_mV)+drive)/(params.tau_m_ms||20)*dt;
      if(V>=params.V_threshold_mV){
        spikes.push(t);Vtrace[i]=30;V=params.V_reset_mV;
        w+=(params.adaptation_b_pA||0);refr=params.refractory_ms||2;continue;
      }
    }
    Vtrace[i]=V;
  }
  const active=spikes.filter(x=>x>=stepStart&&x<=stepEnd);
  const isi=active.slice(1).map((x,i)=>x-active[i]);
  let sum=0,min=Infinity,max=-Infinity;
  for(const v of Vtrace){sum+=v;if(v<min)min=v;if(v>max)max=v;}
  return {
    dt,T,trace:Vtrace,spikes,stepStart,stepEnd,
    stats:{
      spikeCount:active.length,
      firingRateHz:active.length/((stepEnd-stepStart)/1000),
      firstSpikeLatencyMs:active.length?active[0]-stepStart:null,
      meanISI:isi.length?isi.reduce((a,b)=>a+b,0)/isi.length:null,
      meanVm:sum/Vtrace.length,minVm:min,maxVm:max
    }
  };
}
function nbGetGeneModel(gene){
  return nbModelLib?.genes?.find(x=>x.gene===gene)||null;
}
function nbConditionParams(model){
  const cond=document.getElementById("dynamic-condition")?.value||"baseline";
  const strength=Number(document.getElementById("dynamic-strength")?.value||100)/100;
  if(cond==="baseline")return {...model.baseline};
  const target=cond==="high"?model.highExpressionLike:model.lowExpressionLike;
  return nbInterpolate(model.baseline,target,strength);
}
function nbRenderTopTable(){
  const root=document.getElementById("top500-table");if(!root||!nbTop500)return;
  const rows=nbTop500.top500.slice(0,500);
  let h='<table class="top500-table"><thead><tr><th>Rank / gene</th><th>DPS</th><th>BioE</th><th>Cancer</th><th>Best ρ</th></tr></thead><tbody>';
  rows.forEach(r=>{
    h+=`<tr data-topgene="${r.gene}" class="${r.gene===nbSelectedGene?'selected':''}"><td><b>#${r.rank} ${r.gene}</b><br><small>${r.mouse_gene||''}</small></td><td>${Number(r.discovery_priority_score).toFixed(3)}</td><td>${Number(r.bioelectric_score).toFixed(3)}</td><td>${Number(r.cancer_score).toFixed(3)}</td><td class="${Number(r.best_rho)>=0?'rho-pos':'rho-neg'}">${Number(r.best_rho)>=0?'+':''}${Number(r.best_rho).toFixed(3)}</td></tr>`;
  });
  h+='</tbody></table>';root.innerHTML=h;
  root.querySelectorAll("[data-topgene]").forEach(tr=>tr.addEventListener("click",()=>nbSelectGene(tr.dataset.topgene)));
}
function nbRenderCancer(gene){
  const rows=nbCancerRows.filter(r=>r.gene===gene);
  const root=document.getElementById("top500-cancer-profile");if(!root)return;
  const mx=Math.max(.01,...rows.map(r=>nbNum(r.mutation_percent)||0));
  root.innerHTML=rows.sort((a,b)=>(nbNum(b.mutation_percent)||0)-(nbNum(a.mutation_percent)||0)).map(r=>{
    const v=nbNum(r.mutation_percent)||0;
    return `<div class="signature-bar-row"><span class="signature-bar-label" title="${r.study_name}">${r.cancer_type}</span><div class="signature-bar-track"><div class="signature-bar-fill" style="width:${(v/mx*100).toFixed(1)}%"></div></div><span class="signature-bar-value">${v.toFixed(2)}%</span></div>`;
  }).join("");
}
function nbRenderFingerprint(gene){
  const rows=nbBioRows.filter(r=>r.gene===gene);
  const root=document.getElementById("top500-electrical-fingerprint");if(!root)return;
  const mx=Math.max(.001,...rows.map(r=>Math.abs(nbNum(r.rho)||0)));
  root.innerHTML=rows.sort((a,b)=>Math.abs(nbNum(b.rho)||0)-Math.abs(nbNum(a.rho)||0)).map(r=>{
    const v=nbNum(r.rho)||0,pct=Math.min(50,Math.abs(v)/mx*50);
    const style=v>=0?`left:50%;width:${pct}%`:`right:50%;width:${pct}%`;
    return `<div class="fingerprint-row"><span class="fingerprint-label" title="${r.feature}">${r.feature.replaceAll("_"," ")}</span><div class="fingerprint-axis"><span class="fingerprint-seg ${v>=0?'pos':'neg'}" style="${style}"></span></div><span class="fingerprint-value ${v>=0?'rho-pos':'rho-neg'}">${v>=0?'+':''}${v.toFixed(3)}</span></div>`;
  }).join("");
}
function nbDrawVoltage(baseSim,condSim){
  const c=document.getElementById("gene-voltage-canvas");if(!c)return;const ctx=c.getContext("2d"),w=c.width,h=c.height;
  ctx.clearRect(0,0,w,h);ctx.fillStyle="#07131c";ctx.fillRect(0,0,w,h);
  ctx.strokeStyle="#173140";ctx.lineWidth=1;
  for(let y=45;y<h-30;y+=55){ctx.beginPath();ctx.moveTo(55,y);ctx.lineTo(w-20,y);ctx.stroke();}
  const minV=-90,maxV=35;
  function yof(v){return 28+(maxV-v)/(maxV-minV)*(h-65)}
  function draw(sim,color){
    ctx.strokeStyle=color;ctx.lineWidth=2;ctx.beginPath();
    const step=Math.max(1,Math.floor(sim.trace.length/(w-75)));
    let px=0;
    for(let i=0;i<sim.trace.length;i+=step){
      const x=55+i/(sim.trace.length-1)*(w-75),y=yof(sim.trace[i]);
      if(px++===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
    }ctx.stroke();
  }
  draw(baseSim,"#9baeb9");draw(condSim,"#58dfff");
  ctx.fillStyle="#7f98a7";ctx.font="11px system-ui";ctx.fillText("Vm (mV)",8,22);ctx.fillText("0",52,h-12);ctx.fillText("1000 ms",w-65,h-12);
  const sx=55+baseSim.stepStart/baseSim.T*(w-75),ex=55+baseSim.stepEnd/baseSim.T*(w-75);
  ctx.strokeStyle="rgba(89,229,178,.5)";ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(sx,h-22);ctx.lineTo(ex,h-22);ctx.stroke();
}
function nbRenderStats(baseSim,condSim){
  const root=document.getElementById("dynamic-output-grid");if(!root)return;
  const B=baseSim.stats,C=condSim.stats;
  const f=(v,d=2)=>v==null?"NA":Number(v).toFixed(d);
  const rows=[
    ["Spike count",B.spikeCount,C.spikeCount],
    ["Firing rate",f(B.firingRateHz)+" Hz",f(C.firingRateHz)+" Hz"],
    ["First-spike latency",f(B.firstSpikeLatencyMs)+" ms",f(C.firstSpikeLatencyMs)+" ms"],
    ["Mean ISI",f(B.meanISI)+" ms",f(C.meanISI)+" ms"],
    ["Mean Vm",f(B.meanVm)+" mV",f(C.meanVm)+" mV"],
    ["Minimum Vm",f(B.minVm)+" mV",f(C.minVm)+" mV"]
  ];
  root.innerHTML=rows.map(([k,b,c])=>`<div><span>${k}</span><b>${c}</b><small>baseline: ${b}</small></div>`).join("");
}
function nbRenderParams(model,params){
  const root=document.getElementById("dynamic-parameter-table");if(!root)return;
  const keys=["E_L_mV","V_threshold_mV","V_reset_mV","tau_m_ms","R_MOhm","adaptation_b_pA","g_h_relative","input_gain","latency_bias_ms","refractory_ms"];
  let h='<table class="matrix-table"><thead><tr><th>Parameter</th><th>Baseline</th><th>Conditioned</th><th>Δ</th></tr></thead><tbody>';
  keys.forEach(k=>{const b=Number(model.baseline[k]),v=Number(params[k]);h+=`<tr><td>${k}</td><td>${b.toFixed(3)}</td><td>${v.toFixed(3)}</td><td class="${v-b>=0?'rho-pos':'rho-neg'}">${v-b>=0?'+':''}${(v-b).toFixed(3)}</td></tr>`;});
  h+='</tbody></table>';root.innerHTML=h;
}
function nbDrawNeuronAnim(){
  const c=document.getElementById("gene-neuron-canvas");if(!c||!nbLatestSim){requestAnimationFrame(nbDrawNeuronAnim);return;}
  const ctx=c.getContext("2d"),w=c.width,h=c.height;ctx.clearRect(0,0,w,h);ctx.fillStyle="#07131c";ctx.fillRect(0,0,w,h);
  nbGeneAnimPhase=(nbGeneAnimPhase+3)%1000;
  const sim=nbLatestSim.conditioned;
  const near=sim.spikes.some(t=>Math.abs(t-nbGeneAnimPhase)<15);
  const col=near?"#ffffff":"#58dfff",cx=w*.5,cy=h*.5;
  const glow=ctx.createRadialGradient(cx,cy,5,cx,cy,near?120:70);glow.addColorStop(0,near?"rgba(255,255,255,.9)":"rgba(88,223,255,.6)");glow.addColorStop(1,"rgba(88,223,255,0)");ctx.fillStyle=glow;ctx.beginPath();ctx.arc(cx,cy,near?120:70,0,Math.PI*2);ctx.fill();
  ctx.strokeStyle=col;ctx.fillStyle=col;ctx.lineWidth=3;ctx.lineCap="round";ctx.beginPath();ctx.arc(cx,cy,21,0,Math.PI*2);ctx.fill();
  const br=[[-190,-85],[-190,60],[-100,-145],[155,-125],[190,-30],[165,105],[35,155],[-105,140]];
  br.forEach(([dx,dy],i)=>{ctx.beginPath();ctx.moveTo(cx,cy);ctx.quadraticCurveTo(cx+dx*.5,cy+dy*.5,cx+dx,cy+dy);ctx.stroke();if(near||((nbGeneAnimPhase/30+i)%10<1)){ctx.beginPath();ctx.arc(cx+dx,cy+dy,5,0,Math.PI*2);ctx.fill();}});
  ctx.fillStyle="#8da6b5";ctx.font="12px system-ui";ctx.fillText(`${nbSelectedGene||''} · t=${Math.round(nbGeneAnimPhase)} ms`,18,24);
  requestAnimationFrame(nbDrawNeuronAnim);
}
function nbRunDynamic(){
  if(!nbSelectedGene||!nbModelLib)return;
  const model=nbGetGeneModel(nbSelectedGene);if(!model)return;
  const strength=Number(document.getElementById("dynamic-strength").value)/100;
  const cond=document.getElementById("dynamic-condition").value;
  let params={...model.baseline};
  if(cond!=="baseline"){
    const target=cond==="high"?model.highExpressionLike:model.lowExpressionLike;
    params=nbInterpolate(model.baseline,target,strength);
  }
  const current=Number(document.getElementById("dynamic-current").value);
  const base=nbSimulate(model.baseline,current), conditioned=nbSimulate(params,current);
  nbLatestSim={base,conditioned};
  nbDrawVoltage(base,conditioned);nbRenderStats(base,conditioned);nbRenderParams(model,params);
  document.getElementById("gene-sim-status").textContent=`${nbSelectedGene} · ${cond} · ${current} pA`;
}
function nbSelectGene(gene){
  if(!nbTop500?.top500.some(r=>r.gene===gene))return;
  nbSelectedGene=gene;document.getElementById("top500-gene-search").value=gene;
  const r=nbTop500.top500.find(x=>x.gene===gene);
  document.getElementById("disc-rank").textContent="#"+r.rank;
  document.getElementById("disc-score").textContent=Number(r.discovery_priority_score).toFixed(3);
  document.getElementById("disc-components").textContent=`cancer ${Number(r.cancer_score).toFixed(3)} · bioelectric ${Number(r.bioelectric_score).toFixed(3)}`;
  document.getElementById("disc-best-trait").textContent=String(r.best_feature).replaceAll("_"," ");
  document.getElementById("disc-best-rho").textContent=`ρ ${Number(r.best_rho)>=0?'+':''}${Number(r.best_rho).toFixed(3)} · q ${Number(r.best_q).toExponential(1)}`;
  document.getElementById("disc-cancer-mean").textContent=Number(r.mean_mutation_percent).toFixed(2)+"%";
  document.getElementById("disc-cancer-max").textContent=`max ${Number(r.max_mutation_percent).toFixed(2)}% · ${r.cohorts_with_mutation}/10 cohorts`;
  document.getElementById("disc-sig-traits").textContent=`${r.significant_trait_count}/${r.n_traits_tested}`;
  nbRenderTopTable();nbRenderCancer(gene);nbRenderFingerprint(gene);nbRunDynamic();
}
Promise.all([
  fetch("data/top500_cancer_bioelectric_genes.json").then(r=>r.json()),
  fetch("data/top500_cancer_matrix.csv").then(r=>r.text()).then(nbParseCSV),
  fetch("data/top500_bioelectric_matrix.csv").then(r=>r.text()).then(nbParseCSV),
  fetch("data/top500_dynamic_model_library.json").then(r=>r.json())
]).then(([top,cancer,bio,models])=>{
  nbTop500=top;nbCancerRows=cancer;nbBioRows=bio;nbModelLib=models;
  const dl=document.getElementById("top500-gene-list");
  dl.innerHTML=top.top500.map(r=>`<option value="${r.gene}">#${r.rank} · DPS ${Number(r.discovery_priority_score).toFixed(3)}</option>`).join("");
  const search=document.getElementById("top500-gene-search");
  search.addEventListener("change",()=>nbSelectGene(search.value.trim().toUpperCase()));
  search.addEventListener("keydown",e=>{if(e.key==="Enter")nbSelectGene(search.value.trim().toUpperCase());});
  document.getElementById("dynamic-condition").addEventListener("change",nbRunDynamic);
  document.getElementById("dynamic-strength").addEventListener("input",e=>{document.getElementById("dynamic-strength-label").textContent=e.target.value+"%";nbRunDynamic();});
  document.getElementById("dynamic-current").addEventListener("input",e=>{document.getElementById("dynamic-current-label").textContent=e.target.value+" pA";nbRunDynamic();});
  nbRenderTopTable();
  nbSelectGene(top.top500[0]?.gene||"SCN1A");
  requestAnimationFrame(nbDrawNeuronAnim);
}).catch(err=>{
  console.error("Top500 Discovery Studio unavailable",err);
  const el=document.getElementById("top500-table");if(el)el.innerHTML='<div class="data-note warning-note"><b>Discovery data unavailable:</b> the Top-500 build pipeline has not completed successfully.</div>';
});


/* === Predictive validation === */
function nbRenderMLBars(rootId,rows,key,labelKey,external=false){
  const root=document.getElementById(rootId);if(!root)return;
  const good=rows.filter(r=>Number.isFinite(Number(r[key]))).sort((a,b)=>Number(b[key])-Number(a[key]));
  const mx=Math.max(.001,...good.map(r=>Math.max(0,Number(r[key]))));
  root.innerHTML=good.map(r=>{
    const v=Number(r[key]),pct=Math.max(0,v)/mx*100;
    const lab=r[labelKey]||r.target||r.target_vis||"";
    return `<div class="ml-metric-row"><span title="${lab}">${String(lab).replaceAll("_"," ")}</span><div class="ml-metric-bar ${external?'external':''}"><span style="width:${pct.toFixed(1)}%"></span></div><b>${v.toFixed(3)}</b></div>`;
  }).join("");
}
Promise.all([
  fetch("data/ml_grouped_cv_summary.json").then(r=>r.json()),
  fetch("data/m1_external_validation_summary.json").then(r=>r.ok?r.json():null).catch(()=>null)
]).then(([internal,external])=>{
  document.getElementById("ml-cells").textContent=Number(internal.nCells||0).toLocaleString();
  document.getElementById("ml-subjects").textContent=Number(internal.nSubjects||0).toLocaleString();
  const et=(internal.summary||[]).filter(x=>x.model==="ExtraTrees");
  nbRenderMLBars("ml-internal-chart",et,"spearman_mean","target",false);
  if(external){
    document.getElementById("ml-ext-cells").textContent=Number(external.nExternalM1||0).toLocaleString();
    document.getElementById("ml-shared-genes").textContent=Number(external.nSharedGenes||0).toLocaleString();
    nbRenderMLBars("ml-external-chart",external.metrics||[],"spearman","target_vis",true);
  }else{
    document.getElementById("ml-external-chart").innerHTML='<p class="micro-note">Frozen M1 evaluation is being generated.</p>';
  }
}).catch(err=>console.error("ML validation data unavailable",err));
