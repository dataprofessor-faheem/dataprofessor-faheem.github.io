'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const candidates = [path.join(__dirname, '..', 'index.html'), path.join(__dirname, '..', 'web', 'index.html')];
const filename = candidates.find(fs.existsSync);
assert(filename, 'Expected a hosted or development HTML workbench');
const html = fs.readFileSync(filename, 'utf8');
for (const id of ['fasta','molecule','aligned','analyze','save','csv','trace','status']) {
  assert(html.includes('id="' + id + '"'), 'Missing control: ' + id);
}
assert(html.includes('gdrn.vaxforge.browser.v2'), 'The v0.2 schema must be present');
const match = html.match(/<script>([\s\S]*?)<\/script>/);
assert(match, 'Expected inline scientific JavaScript');
new vm.Script(match[1], {filename:'gdrn_vaxforge_browser.js'});
const cut = match[1].indexOf("$('file').addEventListener");
assert(cut > 0, 'Could not isolate pure scientific calculations');
const tests = `
const p = parseFasta('>p1\\nACDE\\n>p2\\nAC-E', 'protein', true);
const m = summarize(p, true, 'protein');
if (m.columns.length !== 4 || m.qc.n_records !== 2 || m.columns[2].gap_fraction !== 0.5) throw Error('Conservation QC mismatch');
const dna = parseFasta('>d1\\nACGTN', 'dna', false);
if (dna.length !== 1 || dna[0].sequence !== 'ACGTN') throw Error('DNA FASTA mismatch');
const rna = parseFasta('>r1\\nACGUN', 'rna', false);
if (rna.length !== 1) throw Error('RNA FASTA mismatch');
let rejected = false;
try { parseFasta('>bad\\nACGT-', 'dna', false); } catch (err) { rejected = true; }
if (!rejected) throw Error('Ungapped DNA parser accepted a gap');
`;
vm.runInNewContext(match[1].slice(0,cut)+tests, {console}, {timeout:1000});
console.log('PASS: UI controls, JavaScript compilation, protein QC, DNA/RNA QC, invalid input');
