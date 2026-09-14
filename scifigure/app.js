const palettes={
 biomedical:[['Deep Navy','#123A63'],['Clinical Blue','#3D7EA6'],['Teal','#2A8C82'],['Soft Aqua','#A8DADC'],['Warm White','#F7FAFC']],
 molecular:[['Indigo','#344EAD'],['Violet','#7A5AF8'],['Cyan','#2FB7C4'],['Soft Gray','#E9EEF5'],['Ink','#1F2937']],
 immune:[['Deep Blue','#214E7A'],['T Cell Teal','#1F8A70'],['Signal Gold','#D9A441'],['Cytokine Rose','#C96A7B'],['Background','#F8FAFC']],
 cancer:[['Charcoal','#2B2D42'],['Tumor Red','#B84A62'],['Mutation Plum','#7B4F8C'],['Stroma Sand','#D6B98C'],['Pale Gray','#F3F4F6']],
 eco:[['Forest','#2F6B4F'],['Leaf','#67A65B'],['Earth','#9B7653'],['Water','#4C93B6'],['Pale Green','#EFF6EE']],
 data:[['Midnight','#23395B'],['Azure','#3D77A8'],['Cyan','#3EA7A3'],['Signal Orange','#D98C3F'],['Canvas','#F6F8FB']]
};

const typeLayouts={
 'Graphical Abstract':['Problem / biological context','Core mechanism or experimental intervention','Main outcome / conclusion'],
 'Mechanism Figure':['Trigger / upstream factor','Molecular or cellular mechanism','Downstream biological effect'],
 'Experimental Workflow':['Samples / inputs','Methods / assays / computational analysis','Results / validation'],
 'Bioinformatics Pipeline':['Data acquisition','Preprocessing + analysis','Models / interpretation / validation'],
 'Clinical Pathway':['Patient / cohort','Assessment / intervention','Outcome / decision'],
 'Poster Figure':['Research question','Methods + central visual','Key result + take-home message']
};

function tokens(text){return [...new Set(text.toLowerCase().replace(/[^a-z0-9\s-]/g,' ').split(/\s+/).filter(x=>x.length>3))].slice(0,10)}
function renderPalette(name){
 const p=palettes[name]||palettes.biomedical;
 document.querySelector('#paletteOutput').innerHTML=p.map(([n,h])=>`<div class="swatch"><div class="swatch-color" style="background:${h}"></div><div class="swatch-meta"><strong>${n}</strong>${h}</div></div>`).join('');
 return p.map(x=>x[1]).join(', ');
}

document.querySelector('#suggestPalette').addEventListener('click',()=>renderPalette(document.querySelector('#paletteType').value));
renderPalette('biomedical');

document.querySelector('#generatePlan').addEventListener('click',()=>{
 const topic=document.querySelector('#topic').value.trim();
 const type=document.querySelector('#figureType').value;
 const field=document.querySelector('#field').value;
 if(!topic){document.querySelector('#topic').focus();return;}
 const keys=tokens(topic);
 let paletteKey='biomedical';
 if(field.includes('Bioinformatics')) paletteKey='data';
 else if(field.includes('Immunology')) paletteKey='immune';
 else if(field.includes('Cancer')) paletteKey='cancer';
 else if(field.includes('Plant')) paletteKey='eco';
 else if(field.includes('Molecular')) paletteKey='molecular';
 const steps=typeLayouts[type]||typeLayouts['Graphical Abstract'];
 const iconHints=[...keys.slice(0,6),'arrow','cell','molecule'].filter((v,i,a)=>a.indexOf(v)===i).slice(0,8);
 const colors=palettes[paletteKey];
 document.querySelector('#planResult').innerHTML=`<div class="plan-box"><span class="eyebrow">RECOMMENDED PLAN</span><h3>${type} • ${field}</h3><p><strong>Visual story:</strong> Keep one clear left-to-right scientific narrative with a single visual emphasis per stage.</p><ol>${steps.map(s=>`<li>${s}</li>`).join('')}</ol><p><strong>Suggested icon searches</strong></p><div class="tag-row">${iconHints.map(k=>`<span class="tag">${k}</span>`).join('')}</div><p><strong>Professional palette</strong></p><div class="tag-row">${colors.map(([n,h])=>`<span class="tag"><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${h};margin-right:5px"></i>${n} ${h}</span>`).join('')}</div><p><strong>Design rules:</strong> Use 1 main message, 2–3 accent colors, short labels, consistent arrow style, generous spacing, and avoid decorative elements that do not communicate science.</p></div>`;
});

document.querySelector('#searchIcons').addEventListener('click',()=>{
 const q=document.querySelector('#iconQuery').value.trim()||'scientific icon';
 const e=encodeURIComponent(q);
 document.querySelector('#iconResults').innerHTML=`
 <article><span class="license cc0">MULTIPLE OPEN LICENSES</span><h3>Bioicons</h3><p>Search Bioicons for <strong>${q}</strong>. Check the license shown for each individual icon.</p><a target="_blank" rel="noopener" href="https://bioicons.com/">Search Bioicons →</a></article>
 <article><span class="license ccby">CC BY 4.0</span><h3>Servier Medical Art</h3><p>Search medical and biomedical artwork for <strong>${q}</strong>. Attribution is required for reused artwork.</p><a target="_blank" rel="noopener" href="https://smart.servier.com/?s=${e}">Search Servier →</a></article>`;
});
