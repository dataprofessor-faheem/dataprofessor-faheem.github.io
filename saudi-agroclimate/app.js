const locations=[
{name:'Al-Qassim — Buraydah',lat:26.3592,lon:43.9818,zone:'Central-Northern Arid Agriculture',tag:'QASSIM',stress:'Heat / water deficit',desc:'Major irrigated agricultural environment with hot, dry summers. Suitable as a pilot zone for date palm, wheat and protected horticulture.'},
{name:'Riyadh',lat:24.7136,lon:46.6753,zone:'Central Hyper-Arid Plateau',tag:'RIYADH',stress:'Extreme heat',desc:'Continental desert climate with very high summer heat and strong evaporative demand. Irrigation efficiency and heat resilience are key decision variables.'},
{name:'Al-Ahsa — Hofuf',lat:25.3830,lon:49.5860,zone:'Eastern Oasis / Gulf Influence',tag:'AL-AHSA',stress:'Heat / salinity / humidity',desc:'Large oasis agriculture influenced by Gulf humidity. Particularly relevant to date palm, salinity management and humidity-linked disease windows.'},
{name:'Madinah',lat:24.5247,lon:39.5692,zone:'Western Inland Oasis',tag:'MADINAH',stress:'Heat / drought',desc:'Hot arid oasis agriculture with major date production. Water demand, heat load and crop phenology are priority monitoring targets.'},
{name:'Jazan',lat:16.8892,lon:42.5511,zone:'Southwestern Coastal Tihamah',tag:'JAZAN',stress:'Humidity / heat',desc:'Warm coastal agricultural zone with higher humidity and rainfall than central Saudi Arabia, creating distinct crop and pathogen pressure.'},
{name:'Abha — Asir Highlands',lat:18.2164,lon:42.5053,zone:'Southwestern Highlands',tag:'ASIR',stress:'Rain / humidity variability',desc:'Higher-elevation agricultural environment with milder temperatures and seasonal rainfall, requiring a different disease-risk baseline from desert zones.'},
{name:'Tabuk',lat:28.3838,lon:36.5550,zone:'Northern Arid / Cool Winter Agriculture',tag:'TABUK',stress:'Cold–heat variability',desc:'Northern agricultural area with larger seasonal temperature ranges and important open-field crop production.'},
{name:'Al-Jouf — Sakaka',lat:29.9697,lon:40.2064,zone:'Northern Interior Agriculture',tag:'AL-JOUF',stress:'Drought / temperature extremes',desc:'Large-scale irrigated agriculture with hot summers, cool winters and high relevance to crop suitability forecasting.'}
];

const cropRules={
'date-palm':{name:'Date palm',heatOpt:[25,42],humidDisease:68,heatCritical:46,soilLow:.08},
'wheat':{name:'Wheat',heatOpt:[12,28],humidDisease:75,heatCritical:35,soilLow:.12},
'potato':{name:'Potato',heatOpt:[15,26],humidDisease:78,heatCritical:33,soilLow:.16},
'tomato':{name:'Tomato / protected crop',heatOpt:[18,30],humidDisease:75,heatCritical:36,soilLow:.14}
};
const $=id=>document.getElementById(id);

function init(){
 $('locationSelect').innerHTML=locations.map((x,i)=>`<option value="${i}">${x.name}</option>`).join('');
 $('locationSelect').value='0';
 ['locationSelect','cropSelect','horizonSelect'].forEach(id=>$(id).addEventListener('change',loadData));
 $('refreshBtn').addEventListener('click',loadData);
 loadData();
}

async function loadData(){
 const loc=locations[+$('locationSelect').value]; const horizon=+$('horizonSelect').value; const crop=cropRules[$('cropSelect').value];
 renderZone(loc,crop,horizon); $('apiStatus').textContent='Connecting live data…';
 const hourly=['temperature_2m','relative_humidity_2m','precipitation','wind_speed_10m','et0_fao_evapotranspiration','soil_moisture_0_to_1cm'].join(',');
 const current=['temperature_2m','relative_humidity_2m','precipitation','wind_speed_10m'].join(',');
 const url=`https://api.open-meteo.com/v1/forecast?latitude=${loc.lat}&longitude=${loc.lon}&current=${current}&hourly=${hourly}&forecast_days=7&timezone=Asia%2FRiyadh`;
 try{
   const r=await fetch(url); if(!r.ok) throw new Error('Weather API unavailable'); const d=await r.json();
   $('apiStatus').textContent='Live weather connected';
   renderCurrent(d); analyze(d,crop,horizon);
 }catch(e){
   $('apiStatus').textContent='Live feed unavailable';
   $('riskTitle').textContent='Weather feed temporarily unavailable'; $('riskExplanation').textContent='The interface is operational, but live weather data could not be retrieved. Try refreshing the intelligence feed.';
 }
}

function renderZone(loc,crop,horizon){
 $('zoneName').textContent=loc.zone; $('zoneTag').textContent=loc.tag; $('zoneDescription').textContent=loc.desc; $('coords').textContent=`${loc.lat.toFixed(3)}°, ${loc.lon.toFixed(3)}°`; $('primaryStress').textContent=loc.stress; $('selectedCrop').textContent=crop.name; $('forecastPeriod').textContent=`${horizon} h`;
}

function renderCurrent(d){
 const c=d.current||{}; const h=d.hourly||{}; const ix=Math.max(0,(h.time||[]).findIndex(t=>t.startsWith((c.time||'').slice(0,13))));
 $('temp').textContent=num(c.temperature_2m,'°C'); $('humidity').textContent=num(c.relative_humidity_2m,'%'); $('precip').textContent=num(c.precipitation,' mm'); $('wind').textContent=num(c.wind_speed_10m,' km/h');
 $('eto').textContent=num((h.et0_fao_evapotranspiration||[])[ix],' mm/h'); $('soil').textContent=num((h.soil_moisture_0_to_1cm||[])[ix],' m³/m³',3);
 $('updatedAt').textContent=`Updated ${new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}`;
}
function num(v,u,d=1){return Number.isFinite(v)?`${v.toFixed(d)}${u}`:'—'}

function analyze(d,crop,horizon){
 const h=d.hourly, n=Math.min(horizon,h.time.length); let biotic=[],abiotic=[],combined=[];
 for(let i=0;i<n;i++){
   const t=h.temperature_2m[i],rh=h.relative_humidity_2m[i],p=h.precipitation[i],eto=h.et0_fao_evapotranspiration[i]||0,sm=h.soil_moisture_0_to_1cm[i];
   let b=8;
   if(rh>=crop.humidDisease)b+=35; else if(rh>=60)b+=18;
   if(p>0)b+=18;
   if(t>=crop.heatOpt[0]&&t<=crop.heatOpt[1])b+=18;
   if(rh>80&&t>18)b+=12;
   b=Math.min(100,b);
   let a=10;
   if(t>crop.heatOpt[1])a+=Math.min(45,(t-crop.heatOpt[1])*7);
   if(t>=crop.heatCritical)a+=20;
   if(Number.isFinite(sm)&&sm<crop.soilLow)a+=25;
   if(eto>.35)a+=15;
   a=Math.min(100,a);
   biotic.push(b);abiotic.push(a);combined.push(Math.round(.52*a+.48*b));
 }
 const avg=a=>a.reduce((x,y)=>x+y,0)/Math.max(1,a.length); const peak=Math.max(...combined); const score=Math.round(.65*peak+.35*avg(combined));
 const bscore=Math.round(Math.max(...biotic)); const ascore=Math.round(Math.max(...abiotic));
 renderRisk(score,bscore,ascore,h,n,crop,combined);
}

function renderRisk(score,bscore,ascore,h,n,crop,series){
 let level='LOW',title='Conditions are comparatively favorable';
 if(score>=75){level='CRITICAL';title='Critical environmental stress/disease window detected'} else if(score>=55){level='HIGH';title='High crop-health risk window detected'} else if(score>=35){level='MODERATE';title='Moderate environmental risk — monitor closely'};
 $('riskScore').textContent=`${score}%`; $('riskLevel').textContent=level; $('riskTitle').textContent=title;
 $('gaugeFill').style.background=`conic-gradient(var(--accent) 0deg,var(--warn) ${score*2.4}deg,var(--danger) ${score*3.6}deg,#183945 ${score*3.6}deg)`;
 const maxT=Math.max(...h.temperature_2m.slice(0,n)); const maxRH=Math.max(...h.relative_humidity_2m.slice(0,n)); const rain=h.precipitation.slice(0,n).reduce((a,b)=>a+b,0); const minSM=Math.min(...h.soil_moisture_0_to_1cm.slice(0,n).filter(Number.isFinite));
 const drivers=[]; if(maxT>crop.heatOpt[1])drivers.push(`Heat ${maxT.toFixed(1)}°C`); if(maxRH>crop.humidDisease)drivers.push(`RH ${maxRH.toFixed(0)}%`); if(rain>0)drivers.push(`Rain ${rain.toFixed(1)} mm`); if(Number.isFinite(minSM)&&minSM<crop.soilLow)drivers.push('Low surface soil moisture'); if(!drivers.length)drivers.push('No dominant severe driver');
 $('drivers').innerHTML=drivers.map(x=>`<span>${x}</span>`).join('');
 $('riskExplanation').textContent=`For ${crop.name}, the MVP combines the strongest forecasted biotic and abiotic environmental signals. Current score reflects environmental suitability and stress, not confirmed infection.`;
 $('bioticScore').textContent=`Peak biotic suitability: ${bscore}%`; $('abioticScore').textContent=`Peak abiotic stress: ${ascore}%`; $('bioticBar').style.width=`${bscore}%`; $('abioticBar').style.width=`${ascore}%`;
 renderChart(h.time.slice(0,n),series);
}

function renderChart(times,values){
 const step=values.length>100?3:values.length>48?2:1; let html='';
 for(let i=0;i<values.length;i+=step){const v=values[i]; const label=new Date(times[i]).toLocaleString([], {weekday:'short',hour:'2-digit'}); html+=`<div class="bar" style="height:${Math.max(8,v*1.7)}px" data-tip="${label} • ${v}% risk"></div>`;}
 $('forecastChart').innerHTML=html;
}

document.addEventListener('DOMContentLoaded',init);