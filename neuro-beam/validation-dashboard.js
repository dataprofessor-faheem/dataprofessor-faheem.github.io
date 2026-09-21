/* NEURO-BEAM predictive + external validation dashboard */
function vdFmt(v,d=3){
  if(v===null||v===undefined||!Number.isFinite(Number(v)))return "NA";
  return Number(v).toFixed(d);
}
function vdBarRows(rows,valueKey,labelKey,positiveNegative=false){
  if(!rows.length)return '<p class="micro-note">No results available.</p>';
  const vals=rows.map(r=>Number(r[valueKey])).filter(Number.isFinite);
  const mx=Math.max(.001,...vals.map(Math.abs));
  return rows.map(r=>{
    const v=Number(r[valueKey]),pct=Math.min(100,Math.abs(v)/mx*100);
    const col=v<0?"linear-gradient(90deg,#ff7dbd,#a57aff)":"linear-gradient(90deg,#59e5b2,#58dfff)";
    return `<div class="mini-bar-row"><span title="${r[labelKey]}">${String(r[labelKey]).replaceAll("_"," ").slice(0,24)}</span><div class="mini-bar"><span style="width:${pct.toFixed(1)}%;background:${col}"></span></div><b>${vdFmt(v,3)}</b></div>`;
  }).join("");
}
Promise.all([
  fetch("data/predictive_benchmark.json").then(r=>r.ok?r.json():Promise.reject()),
  fetch("data/external_m1_validation.json").then(r=>r.ok?r.json():Promise.reject())
]).then(([internal,external])=>{
  const models=(internal.models||[]).slice().sort((a,b)=>(b.mean_trait_r2||-999)-(a.mean_trait_r2||-999));
  const best=models[0];
  document.getElementById("ml-best-model").textContent=best?.model?.replaceAll("_"," ")||"—";
  document.getElementById("ml-best-r2").textContent=best?`mean trait R² ${vdFmt(best.mean_trait_r2,3)}`:"—";
  document.getElementById("ml-internal-rho").textContent=best?vdFmt(best.mean_trait_spearman,3):"—";
  document.getElementById("ml-model-bars").innerHTML=vdBarRows(models,"mean_trait_r2","model");

  const extModels=external.models||[];
  const cbe=extModels.find(x=>x.model==="ridge_cbe_top500")||extModels[0];
  document.getElementById("ml-external-rho").textContent=cbe?vdFmt(cbe.mean_external_spearman,3):"—";
  const traitRows=(external.perTrait||[]).filter(x=>x.model===(cbe?.model||""));
  const ordered=traitRows.slice().sort((a,b)=>Math.abs(b.external_spearman||0)-Math.abs(a.external_spearman||0));
  const top=ordered[0];
  document.getElementById("ml-external-best").textContent=top?top.v1_trait.replaceAll("_"," "):"—";
  document.getElementById("ml-external-best-rho").textContent=top?`external ρ ${vdFmt(top.external_spearman,3)} · n=${top.n_external}`:"—";
  document.getElementById("ml-external-bars").innerHTML=vdBarRows(ordered,"external_spearman","v1_trait",true);
}).catch(err=>console.error("Validation summary unavailable",err));

fetch("data/cbef_sensitivity_summary.json").then(r=>r.ok?r.json():Promise.reject()).then(d=>{
  const root=document.getElementById("ml-cbef-stability");if(!root)return;
  const w=d.weightSensitivity||{},b=d.cohortBootstrap||{},p=d.permutationNegativeControl||{};
  root.innerHTML=[
    ["Weight-grid median rank ρ",vdFmt(w.medianRankSpearman,3)],
    ["Weight-grid median Top-50 Jaccard",vdFmt(w.medianTop50Jaccard,3)],
    ["Cohort-bootstrap Top-50 Jaccard",vdFmt(b.meanTop50Jaccard,3)],
    ["Permutation empirical p",p.empiricalP!=null?Number(p.empiricalP).toExponential(2):"NA"]
  ].map(([k,v])=>`<article><span>${k}</span><b>${v}</b></article>`).join("");
}).catch(()=>{});
