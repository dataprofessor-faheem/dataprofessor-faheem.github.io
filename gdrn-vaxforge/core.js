/* GDRN-VaxForge v0.3.0 — browser-only exploratory sequence analysis.
   No epitope, immunogenicity, protection, or pangenome prediction is made. */
(function (root, factory) {
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.VaxForgeCore = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const VERSION = "0.3.0";
  const ALPHABETS = Object.freeze({
    protein: "ACDEFGHIKLMNPQRSTVWYBXZJUO",
    dna: "ACGTRYSWKMBDHVN",
    rna: "ACGURYSWKMBDHVN"
  });
  const MAX_RECORDS = 500;
  const MAX_RESIDUES = 3000000;
  const MAX_HEADER = 400;
  function checkType(type) {
    if (!Object.prototype.hasOwnProperty.call(ALPHABETS, type)) throw new Error("Choose protein, DNA, or RNA.");
    return type;
  }
  function parseFasta(input, molecule, aligned) {
    checkType(molecule);
    if (typeof input !== "string" || !input.trim()) throw new Error("Paste or upload a FASTA file first.");
    if (input.length > MAX_RESIDUES + 300000) throw new Error("Input exceeds the 3 million-residue browser limit.");
    const allowed = new Set((ALPHABETS[molecule] + (aligned ? "-" : "")).split(""));
    const seen = new Set();
    const records = [];
    let active = null, total = 0;
    for (const [lineIndex, raw] of input.split(/\r?\n/).entries()) {
      const line = raw.trim();
      if (!line) continue;
      if (line[0] === ">") {
        const header = line.slice(1).trim();
        const id = header.split(/\s+/)[0];
        if (!id || header.length > MAX_HEADER) throw new Error("Invalid FASTA header on line " + (lineIndex + 1) + ".");
        if (seen.has(id)) throw new Error("Duplicate FASTA identifier: " + id + ".");
        if (records.length >= MAX_RECORDS) throw new Error("Maximum " + MAX_RECORDS + " records per browser analysis.");
        seen.add(id);
        active = { id, header, sequence: "" };
        records.push(active);
      } else {
        if (!active) throw new Error("Sequence found before FASTA header on line " + (lineIndex + 1) + ".");
        if (/\s/.test(line)) throw new Error("Whitespace inside sequence at line " + (lineIndex + 1) + ".");
        const upper = line.toUpperCase();
        for (const ch of upper) if (!allowed.has(ch)) throw new Error("Invalid " + molecule + " residue '" + ch + "' on line " + (lineIndex + 1) + ".");
        active.sequence += upper;
        total += upper.length;
        if (total > MAX_RESIDUES) throw new Error("Maximum " + MAX_RESIDUES + " sequence characters per browser analysis.");
      }
    }
    if (!records.length || records.some(x => !x.sequence.length)) throw new Error("FASTA contains missing or empty sequences.");
    if (aligned) {
      const l = records[0].sequence.length;
      if (records.some(x => x.sequence.length !== l)) throw new Error("Aligned sequences must have exactly equal lengths.");
    }
    return records;
  }
  function shannon(counts, total) {
    if (!total) return null;
    let h = 0;
    for (const n of Object.values(counts)) {
      const p = n / total;
      h -= p * Math.log2(p);
    }
    return h;
  }
  function conservation(records) {
    if (records.length < 2) throw new Error("At least two aligned sequences are required to assess conservation.");
    const n = records.length, l = records[0].sequence.length;
    if (records.some(r => r.sequence.length !== l)) throw new Error("Unequal sequence lengths are not an MSA.");
    const columns = [];
    for (let pos = 0; pos < l; pos++) {
      const counts = Object.create(null);
      let nongap = 0;
      for (let i = 0; i < n; i++) {
        const ch = records[i].sequence[pos];
        if (ch === "-") continue;
        counts[ch] = (counts[ch] || 0) + 1;
        nongap++;
      }
      const ranks = Object.entries(counts).sort((a,b)=>b[1]-a[1] || a[0].localeCompare(b[0]));
      columns.push({
        position: pos + 1,
        consensus: ranks.length ? ranks[0][0] : "-",
        modal_fraction: nongap ? ranks[0][1] / nongap : null,
        total_identity_fraction: ranks.length ? ranks[0][1] / n : 0,
        occupancy: nongap / n,
        gap_fraction: 1 - nongap / n,
        shannon_bits: shannon(counts, nongap),
        variants: ranks.length,
        non_gap_n: nongap
      });
    }
    return columns;
  }
  function conservedRegions(columns, threshold, minOccupancy, minLength) {
    if (!(threshold >= 0.5 && threshold <= 1)) throw new Error("Conservation threshold must be 0.5 to 1.");
    if (!(minOccupancy >= 0 && minOccupancy <= 1)) throw new Error("Minimum occupancy must be 0 to 1.");
    if (!(Number.isSafeInteger(minLength) && minLength >= 1 && minLength <= 10000)) throw new Error("Minimum region length must be 1–10000.");
    const blocks = [];
    let start = -1;
    function emit(end) {
      if (start < 0) return;
      if (end - start >= minLength) {
        const group = columns.slice(start, end);
        const sum = group.reduce((s,x)=>s+x.modal_fraction,0);
        blocks.push({start_1based:start+1,end_1based:end,length:group.length,consensus:group.map(x=>x.consensus).join(""),mean_modal_fraction:sum/group.length});
      }
      start = -1;
    }
    for(let i = 0;i < columns.length;i++) {
      const x = columns[i];
      const eligible = x.modal_fraction !== null && x.modal_fraction >= threshold - 1e-12 && x.occupancy >= minOccupancy - 1e-12;
      if (eligible && start < 0) start = i;
      if (!eligible) emit(i);
    }
    emit(columns.length);
    return blocks.sort((a,b)=>b.length-a.length || a.start_1based-b.start_1based);
  }
  function pairwise(records, maxRecords=24, maxLength=15000) {
    if (records.length > maxRecords || records[0].sequence.length > maxLength) return {skipped:true,reason:"Pairwise comparison limited to "+maxRecords+" records and "+maxLength+" alignment positions."};
    const data = [];
    for (let i=0;i<records.length;i++) for (let j=i+1;j<records.length;j++) {
      const a=records[i].sequence, b=records[j].sequence;
      let matches=0, compared=0, excludedGap=0;
      for (let k=0;k<a.length;k++) {
        if (a[k]==="-" || b[k]==="-") { excludedGap++; continue; }
        compared++;
        if (a[k]===b[k]) matches++;
      }
      data.push({id_a:records[i].id,id_b:records[j].id,identity:compared?matches/compared:null,compared_sites:compared,gap_excluded_sites:excludedGap});
    }
    return {skipped:false,pairs:data};
  }
  function analyze(input, params={}) {
    const molecule = checkType(params.molecule || "protein");
    const aligned = !!params.aligned;
    const threshold = params.threshold === undefined ? 0.95 : Number(params.threshold);
    const minOccupancy = params.minOccupancy === undefined ? 0.9 : Number(params.minOccupancy);
    const minLength = params.minLength === undefined ? 6 : Number(params.minLength);
    // Validate user options even without MSA for consistent manifests.
    if (!(threshold>=0.5 && threshold<=1) || !(minOccupancy>=0 && minOccupancy<=1) || !(Number.isSafeInteger(minLength)&&minLength>=1&&minLength<=10000)) throw new Error("Invalid conservation filter parameters.");
    const records = parseFasta(input,molecule,aligned);
    const lens = records.map(r=>r.sequence.length);
    const uniq = new Set(records.map(r=>r.sequence)).size;
    const total = lens.reduce((a,b)=>a+b,0);
    const gapCount = records.reduce((sum,r)=>sum+(r.sequence.match(/-/g)||[]).length,0);
    const qc = {
      n_records: records.length,n_unique_sequences:uniq,
      total_characters:total,minimum_length:Math.min(...lens),maximum_length:Math.max(...lens),
      equal_length: lens.every(l=>l===lens[0]),gap_characters:gapCount,
      sequence_ids:records.map(r=>r.id)
    };
    if(molecule!=="protein"){
      let gc=0,acgtu=0;
      for(const r of records)for(const c of r.sequence){if("ACGTU".includes(c)){acgtu++;if(c==="G"||c==="C")gc++;}}
      qc.gc_fraction_unambiguous = acgtu ? gc/acgtu : null;
    }
    const result = {
      schema:"gdrn.vaxforge.exploration.v3",version:VERSION,
      molecule,analysis:aligned?"verified_input_msa_exploration":"sequence_qc",
      parameters:{aligned,threshold,minOccupancy,minLength},
      qc,warning:"Computational exploratory results only. Equal length does not validate homology or alignment. No epitope, vaccine or statistical-efficacy prediction performed.",
      methods:{alignment:"User-provided; no alignment was generated",conservation:"Highest residue frequency among nongap residues",entropy:"Shannon entropy in bits over nongap residues",pairwise:"Identical residues / nongap-overlap positions"},
      columns:[],conserved_regions:[],pairwise:{skipped:true,reason:"Requires aligned sequences"},summary:{}
    };
    if (aligned) {
      const columns = conservation(records);
      const blocks = conservedRegions(columns,threshold,minOccupancy,minLength);
      const all = columns.filter(x=>x.non_gap_n>0);
      result.columns=columns; result.conserved_regions=blocks;
      result.pairwise=pairwise(records);
      result.summary={
        aligned_columns: columns.length,
        completely_covered_invariant_columns: columns.filter(x=>x.modal_fraction===1 && x.occupancy===1).length,
        variable_columns:columns.filter(x=>x.variants>1).length,
        all_gap_columns:columns.length-all.length,
        mean_modal_fraction: all.length?all.reduce((sum,x)=>sum+x.modal_fraction,0)/all.length:null,
        conserved_regions:blocks.length
      };
    }
    return result;
  }
  function csv(rows,keys) {
    const esc = value => {
      const s = String(value===null || value===undefined?"":value);
      return /[",\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;
    };
    return [keys.join(","),...rows.map(row=>keys.map(k=>esc(row[k])).join(","))].join("\n")+"\n";
  }
  return {VERSION,parseFasta,conservation,conservedRegions,pairwise,analyze,csv};
});
