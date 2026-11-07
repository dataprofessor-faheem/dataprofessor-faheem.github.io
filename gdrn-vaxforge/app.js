/* GDRN-VaxForge v0.3 UI. Static, in-browser sequence exploration. */
(function () {
"use strict";
const core = globalThis.VaxForgeCore;
if (!core) throw new Error("VaxForge analysis core not loaded.");
const $ = id => document.getElementById(id);
const state = {report:null,raw:"",source:"manual input"};
const SAMPLE = [
">sample_A | demonstration only","MSTNPKPQRKTKRNTNRRPQDVKFPGG",
">sample_B | demonstration only","MSTNPKPQRKTKRNTNRRPQDVKFPGG",
">sample_C | demonstration only","MSTNPKPQ-KTKRNTNRRPQDVKFPAG",
">sample_D | demonstration only","MSTNPKPQRKTKRNTNRRPQDVKFPAG"
].join("\n");
function status(msg,type="info"){$("status").textContent=msg;$("status").dataset.type=type;}
function compactNumber(n){return n===null||n===undefined?"—":typeof n==="number"?n.toLocaleString(undefined,{maximumFractionDigits:3}):String(n);}
function percent(n){return n===null||n===undefined?"—":(100*n).toFixed(1)+"%";}
function createCell(text,tag="td"){const node=document.createElement(tag);node.textContent=String(text);return node;}
function clear(node){while(node.firstChild)node.removeChild(node.firstChild);}
function download(name,data,mime){const blob=new Blob([data],{type:mime});const u=URL.createObjectURL(blob);const a=document.createElement("a");a.href=u;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),1500);}
async function sha256(value){
  try {if(!crypto?.subtle)return null;const h=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(value));return [...new Uint8Array(h)].map(x=>x.toString(16).padStart(2,"0")).join("");}
  catch{return null;}
}
function chart(cols,threshold){
  const canvas=$("profile");const ctx=canvas.getContext("2d");const w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h);ctx.fillStyle="#ffffff";ctx.fillRect(0,0,w,h);
  const left=50,right=15,top=16,bottom=38,innerW=w-left-right,innerH=h-top-bottom;
  for(let level=0;level<=1;level+=0.25){const y=top+(1-level)*innerH;ctx.strokeStyle="#e1eaf0";ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(w-right,y);ctx.stroke();ctx.fillStyle="#576b80";ctx.font="12px system-ui";ctx.fillText(Math.round(level*100)+"%",8,y+4);}
  const fy=top+(1-threshold)*innerH;ctx.strokeStyle="#d5a04d";ctx.setLineDash([5,4]);ctx.beginPath();ctx.moveTo(left,fy);ctx.lineTo(w-right,fy);ctx.stroke();ctx.setLineDash([]);
  const count=cols.length;if(!count)return;
  const bucket=Math.max(1,Math.ceil(count/innerW));
  const plot=[];
  for(let i=0;i<count;i+=bucket){const slice=cols.slice(i,i+bucket).map(c=>c.modal_fraction).filter(x=>x!==null);plot.push(slice.length?slice.reduce((a,b)=>a+b,0)/slice.length:null);}
  ctx.strokeStyle="#0c827b";ctx.lineWidth=2.5;ctx.beginPath();let active=false;
  for(let i=0;i<plot.length;i++){const v=plot[i];if(v===null){active=false;continue;}const x=left+(plot.length===1?0:i/(plot.length-1))*innerW,y=top+(1-v)*innerH;if(!active){ctx.moveTo(x,y);active=true;}else ctx.lineTo(x,y);}ctx.stroke();
  ctx.fillStyle="#516577";ctx.font="12px system-ui";ctx.fillText("1",left,h-11);ctx.fillText(String(count)+" positions",w-right-100,h-11);
}
function showRows(rows,columns,elementId,limit){
  const host=$(elementId);clear(host);if(!rows?.length){host.append(createCell("No results for these criteria.","p"));return;}
  const table=document.createElement("table");const thead=document.createElement("thead");const header=document.createElement("tr");
  columns.forEach(col=>header.append(createCell(col.label,"th")));thead.append(header);table.append(thead);
  const body=document.createElement("tbody");
  rows.slice(0,limit).forEach(row=>{const tr=document.createElement("tr");columns.forEach(col=>tr.append(createCell(col.show(row))));body.append(tr);});
  table.append(body);host.append(table);
  if(rows.length>limit) {const note=document.createElement("p");note.className="muted";note.textContent="Showing "+limit+" of "+rows.length+". Export CSV for the complete table.";host.append(note);}
}
function showReport(r){
  $("report").hidden=false;
  $("records").textContent=compactNumber(r.qc.n_records);
  $("unique").textContent=compactNumber(r.qc.n_unique_sequences);
  $("alignment-length").textContent=r.parameters.aligned?compactNumber(r.summary.aligned_columns):"Not aligned";
  $("invariant").textContent=r.parameters.aligned?compactNumber(r.summary.completely_covered_invariant_columns):"—";
  $("results-title").textContent=r.parameters.aligned?"Aligned sequence analysis":"FASTA quality control";
  $("results-note").textContent=r.parameters.aligned?
   "Descriptive conservation from the supplied alignment; not a new MSA or epitope prediction.":
   "Sequence QC completed. Select aligned MSA only if the sequences were aligned using an established method.";
  $("qc-report").textContent=[
    "Molecule: "+r.molecule.toUpperCase(),"Sequences: "+r.qc.n_records,
    "Distinct sequences: "+r.qc.n_unique_sequences,
    "Minimum–maximum length: "+r.qc.minimum_length+"–"+r.qc.maximum_length,
    "Residues (including gaps): "+r.qc.total_characters,
    "Gaps: "+r.qc.gap_characters,
    "GC among unambiguous bases: "+(r.qc.gc_fraction_unambiguous===undefined?"Not applicable":percent(r.qc.gc_fraction_unambiguous))
  ].join("\n");
  $("aligned-result").hidden=!r.parameters.aligned;
  if(!r.parameters.aligned)return;
  chart(r.columns,r.parameters.threshold);
  $("summary-detail").textContent="Variable columns: "+r.summary.variable_columns+" • Mean modal residue fraction: "+percent(r.summary.mean_modal_fraction)+" • All-gap columns: "+r.summary.all_gap_columns+" • Candidate conserved windows: "+r.summary.conserved_regions;
  showRows(r.conserved_regions,[
    {label:"Start",show:x=>x.start_1based},{label:"End",show:x=>x.end_1based},{label:"Length",show:x=>x.length},
    {label:"Mean conservation",show:x=>percent(x.mean_modal_fraction)},
    {label:"Consensus (preview)",show:x=>x.consensus.length>100?x.consensus.slice(0,100)+"…":x.consensus}
  ],"regions-table",50);
  showRows(r.columns,[
    {label:"Position",show:x=>x.position},{label:"Consensus",show:x=>x.consensus},
    {label:"Conservation",show:x=>percent(x.modal_fraction)},{label:"Occupancy",show:x=>percent(x.occupancy)},
    {label:"Entropy (bits)",show:x=>x.shannon_bits===null?"—":x.shannon_bits.toFixed(3)},
    {label:"Residue types",show:x=>x.variants}
  ],"columns-table",200);
  if(r.pairwise.skipped){$("pairwise-table").textContent=r.pairwise.reason;}
  else {
    const sorted=[...r.pairwise.pairs].sort((a,b)=>(a.identity??-1)-(b.identity??-1));
    showRows(sorted,[
      {label:"Sequence 1",show:x=>x.id_a},{label:"Sequence 2",show:x=>x.id_b},
      {label:"Identity",show:x=>percent(x.identity)},
      {label:"Compared residues",show:x=>x.compared_sites}
    ],"pairwise-table",40);
  }
}
async function analyze(){
  status("Validating input and running local analysis…");
  $("run").disabled=true;
  try{
    const opts={molecule:$("molecule").value,aligned:$("aligned").checked,
      threshold:Number($("threshold").value)/100,minOccupancy:Number($("occupancy").value)/100,
      minLength:Number($("minlen").value)};
    const input=$("fasta").value;
    const report=core.analyze(input,opts);
    report.generated_at_utc=new Date().toISOString();
    report.input_sha256=await sha256(input);
    report.source_note=state.source;
    state.report=report;state.raw=input;
    showReport(report);
    $("export-json").disabled=false;$("export-columns").disabled=!opts.aligned;
    $("export-regions").disabled=!opts.aligned;
    status("Analysis complete in this browser. "+report.qc.n_records+" sequences processed; no vaccine prediction was performed.","success");
  }catch(err){
    state.report=null;$("report").hidden=true;
    for(const id of ["export-json","export-columns","export-regions"])$(id).disabled=true;
    status("Analysis stopped: "+err.message,"error");
  } finally {$("run").disabled=false;}
}
$("run").addEventListener("click",analyze);
$("example").addEventListener("click",()=>{
  $("fasta").value=SAMPLE;$("molecule").value="protein";$("aligned").checked=true;
  $("threshold").value=95;$("occupancy").value=70;$("minlen").value=3;
  state.source="synthetic demonstration";status("Synthetic test alignment loaded. Select Run analysis to calculate results.");
});
$("reset").addEventListener("click",()=>{
  $("fasta").value="";$("accession").value="";$("file").value="";
  state.report=null;state.source="manual input";$("report").hidden=true;
  for(const id of ["export-json","export-columns","export-regions"])$(id).disabled=true;
  status("Cleared. Data entered into this page remain in your browser.");
});
$("file").addEventListener("change",async evt=>{
  const file=evt.target.files?.[0];if(!file)return;
  if(file.size>3400000){status("Maximum FASTA file size: 3.4 MB.","error");return;}
  try{$("fasta").value=await file.text();state.source="local file: "+file.name;status("File loaded locally: "+file.name+". Select Run analysis.");}
  catch(e){status("Unable to read file: "+e.message,"error");}
});
$("uniprot").addEventListener("click",async()=>{
  const accession=$("accession").value.trim().toUpperCase();
  if(!/^[A-Z0-9]{6,10}(?:-\d{1,3})?$/.test(accession)){status("Enter a valid UniProtKB accession (e.g. P69905).","error");return;}
  $("uniprot").disabled=true;status("Requesting public FASTA from UniProt. No uploaded sequences are sent.");
  try{
    const response=await fetch("https://rest.uniprot.org/uniprotkb/"+encodeURIComponent(accession)+".fasta",{headers:{Accept:"text/plain"},signal:AbortSignal.timeout(12000)});
    if(!response.ok)throw new Error("UniProt returned HTTP "+response.status);
    const text=await response.text();
    if(text.length>200000||!text.trim().startsWith(">"))throw new Error("Unexpected FASTA response");
    const ids=core.parseFasta(text,"protein",false);
    if(ids.length!==1)throw new Error("Expected one UniProtKB entry");
    const existing=$("fasta").value.trim();
    $("fasta").value=existing?existing+"\n"+text.trim():text.trim();
    $("aligned").checked=false;$("molecule").value="protein";
    state.source="UniProt REST accession "+accession+" (mixed with local input if applicable)";
    status("Loaded public accession "+accession+". Run sequence QC. Multiple unaligned entries must be aligned externally before conservation.","success");
  }catch(e){status("UniProt retrieval unavailable: "+e.message+". Paste or upload FASTA instead.","error");}
  finally{$("uniprot").disabled=false;}
});
$("export-json").addEventListener("click",()=>{if(state.report)download("gdrn-vaxforge-report-v0.3.json",JSON.stringify(state.report,null,2)+"\n","application/json");});
$("export-columns").addEventListener("click",()=>{const r=state.report;if(r?.columns?.length)download("gdrn-vaxforge-columns.csv",core.csv(r.columns,["position","consensus","modal_fraction","total_identity_fraction","occupancy","gap_fraction","shannon_bits","variants","non_gap_n"]),"text/csv");});
$("export-regions").addEventListener("click",()=>{const r=state.report;if(r?.columns?.length)download("gdrn-vaxforge-conserved-regions.csv",core.csv(r.conserved_regions,["start_1based","end_1based","length","consensus","mean_modal_fraction"]),"text/csv");});
status("Ready for local analysis. Use a FASTA file, a public UniProtKB accession, or a synthetic demo.");
})();