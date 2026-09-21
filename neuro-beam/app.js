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