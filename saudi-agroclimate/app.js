const SB_URL='https://klwzkmfzxrikqslkclik.supabase.co';
const SB_KEY='sb_publishable_PeoU1Z8jnXXptuck9Zb_Jg_QEeBLZKm';
const sb=window.supabase.createClient(SB_URL,SB_KEY);
const $=id=>document.getElementById(id);

const cropProfiles={
'date-palm':{name:'Date palm',heatOpt:[25,42],heatCritical:46,humidDisease:68,soilLow:.08,etoHigh:.36,diseases:[
{name:'Black scorch',note:'Warm, humid conditions can increase fungal suitability; field symptoms require confirmation.',rh:65,t:[20,38],rain:true},
{name:'Inflorescence rot',note:'Moisture and humidity around flowering structures can favor fungal infection windows.',rh:72,t:[18,32],rain:true},
{name:'Red palm weevil climate pressure',note:'Weather suitability indicator only; pheromone trapping and field inspection remain essential.',rh:45,t:[24,38],rain:false}]},
'wheat':{name:'Wheat',heatOpt:[12,28],heatCritical:35,humidDisease:74,soilLow:.12,etoHigh:.32,diseases:[
{name:'Rust weather suitability',note:'Moderate temperatures plus prolonged humidity can favor rust development.',rh:72,t:[10,26],rain:true},
{name:'Powdery mildew suitability',note:'Cool-to-moderate temperatures with elevated humidity can increase suitability.',rh:68,t:[12,24],rain:false},
{name:'Heat stress at grain filling',note:'High temperature during reproductive development can reduce performance.',rh:0,t:[32,50],rain:false,abiotic:true}]},
'barley':{name:'Barley',heatOpt:[12,30],heatCritical:37,humidDisease:72,soilLow:.11,etoHigh:.33,diseases:[
{name:'Leaf blotch suitability',note:'Moist leaf surfaces and moderate temperatures can favor foliar disease.',rh:72,t:[12,27],rain:true},
{name:'Rust suitability',note:'Humidity and mild temperatures can support rust infection windows.',rh:70,t:[10,26],rain:true}]},
'alfalfa':{name:'Alfalfa',heatOpt:[18,35],heatCritical:42,humidDisease:74,soilLow:.13,etoHigh:.40,diseases:[
{name:'Foliar disease pressure',note:'High humidity can raise general foliar-disease suitability.',rh:74,t:[18,32],rain:true},
{name:'Heat / water stress',note:'High evaporative demand with low soil moisture increases crop stress.',rh:0,t:[38,50],rain:false,abiotic:true}]},
'tomato':{name:'Tomato',heatOpt:[18,30],heatCritical:36,humidDisease:75,soilLow:.14,etoHigh:.34,diseases:[
{name:'Early/late blight weather window',note:'Leaf wetness proxies, humidity and moderate temperatures increase disease suitability.',rh:78,t:[16,28],rain:true},
{name:'Powdery mildew suitability',note:'Warm conditions with elevated humidity can increase canopy risk.',rh:70,t:[20,31],rain:false},
{name:'Heat-set stress',note:'High temperature can impair flowering and fruit set.',rh:0,t:[34,50],rain:false,abiotic:true}]},
'cucumber':{name:'Cucumber',heatOpt:[20,30],heatCritical:36,humidDisease:78,soilLow:.16,etoHigh:.34,diseases:[
{name:'Downy mildew suitability',note:'High humidity and wet-canopy conditions favor disease development.',rh:80,t:[16,27],rain:true},
{name:'Powdery mildew suitability',note:'Warm humid conditions can increase disease pressure.',rh:70,t:[20,31],rain:false}]},
'potato':{name:'Potato',heatOpt:[15,26],heatCritical:33,humidDisease:78,soilLow:.16,etoHigh:.31,diseases:[
{name:'Late blight weather suitability',note:'Cool-to-moderate temperatures with high humidity are a classic risk combination.',rh:80,t:[10,24],rain:true},
{name:'Heat/tuber stress',note:'Sustained heat can reduce tuber development and quality.',rh:0,t:[30,50],rain:false,abiotic:true}]},
'onion':{name:'Onion',heatOpt:[13,28],heatCritical:36,humidDisease:76,soilLow:.12,etoHigh:.33,diseases:[
{name:'Downy mildew suitability',note:'Cool humid conditions can favor foliar disease.',rh:80,t:[10,24],rain:true},
{name:'Heat / bulb stress',note:'High temperature and water deficit can increase crop stress.',rh:0,t:[35,50],rain:false,abiotic:true}]},
'citrus':{name:'Citrus',heatOpt:[18,34],heatCritical:43,humidDisease:72,soilLow:.13,etoHigh:.38,diseases:[
{name:'Citrus fungal pressure',note:'Warm humid weather and rainfall can elevate general fungal suitability.',rh:75,t:[18,32],rain:true},
{name:'Heat / sunburn stress',note:'Extreme heat and high evaporative demand can injure exposed fruit and canopy.',rh:0,t:[41,50],rain:false,abiotic:true}]},
'grape':{name:'Grape',heatOpt:[18,32],heatCritical:40,humidDisease:72,soilLow:.12,etoHigh:.36,diseases:[
{name:'Powdery mildew suitability',note:'Mild-to-warm humid conditions can support disease development.',rh:65,t:[18,30],rain:false},
{name:'Downy mildew suitability',note:'Rainfall and high humidity increase risk windows.',rh:78,t:[12,28],rain:true}]},
'olive':{name:'Olive',heatOpt:[15,34],heatCritical:43,humidDisease:72,soilLow:.09,etoHigh:.38,diseases:[
{name:'Peacock spot suitability',note:'Cooler wet periods increase environmental suitability.',rh:78,t:[10,24],rain:true},
{name:'Verticillium surveillance',note:'Field history and soil evidence are more important than weather alone.',rh:55,t:[18,30],rain:false}]},
'mango':{name:'Mango',heatOpt:[24,35],heatCritical:43,humidDisease:75,soilLow:.13,etoHigh:.38,diseases:[
{name:'Anthracnose weather suitability',note:'Warm, wet and humid periods are important environmental drivers.',rh:80,t:[22,32],rain:true},
{name:'Powdery mildew suitability',note:'Moderate temperatures with elevated humidity can favor infection.',rh:70,t:[18,30],rain:false}]},
'banana':{name:'Banana',heatOpt:[24,32],heatCritical:39,humidDisease:80,soilLow:.18,etoHigh:.36,diseases:[
{name:'Leaf-spot weather suitability',note:'Warm, humid environments can support foliar disease pressure.',rh:82,t:[22,31],rain:true},
{name:'Heat / water stress',note:'Banana is sensitive to high evaporative demand and moisture deficit.',rh:0,t:[37,50],rain:false,abiotic:true}]},
'coffee':{name:'Arabian coffee',heatOpt:[18,27],heatCritical:34,humidDisease:75,soilLow:.16,etoHigh:.30,diseases:[
{name:'Coffee leaf rust suitability',note:'Humidity, leaf wetness and mild temperatures can increase suitability.',rh:78,t:[18,26],rain:true},
{name:'Heat / drought stress',note:'High temperature and water deficit can stress coffee in mountain systems.',rh:0,t:[31,50],rain:false,abiotic:true}]},
'pomegranate':{name:'Pomegranate',heatOpt:[18,34],heatCritical:42,humidDisease:72,soilLow:.11,etoHigh:.37,diseases:[
{name:'Fruit rot weather pressure',note:'Humidity and rainfall can increase fruit-rot suitability.',rh:76,t:[18,31],rain:true},
{name:'Heat / fruit-cracking stress',note:'Rapid water-status changes and heat can elevate physiological stress.',rh:0,t:[39,50],rain:false,abiotic:true}]},
'fig':{name:'Fig',heatOpt:[18,35],heatCritical:43,humidDisease:72,soilLow:.10,etoHigh:.37,diseases:[
{name:'Fruit rot suitability',note:'Humidity and rainfall around ripening can increase spoilage pressure.',rh:78,t:[18,32],rain:true},
{name:'Heat / water stress',note:'High evaporative demand can increase physiological stress.',rh:0,t:[40,50],rain:false,abiotic:true}]},
'apple':{name:'Apple',heatOpt:[12,28],heatCritical:36,humidDisease:75,soilLow:.14,etoHigh:.32,diseases:[
{name:'Apple scab weather suitability',note:'Mild temperatures and wet foliage favor infection windows.',rh:78,t:[10,24],rain:true},
{name:'Heat stress',note:'High temperatures can reduce fruit quality and increase sunburn risk.',rh:0,t:[34,50],rain:false,abiotic:true}]},
'watermelon':{name:'Watermelon',heatOpt:[22,34],heatCritical:42,humidDisease:72,soilLow:.12,etoHigh:.39,diseases:[
{name:'Foliar disease pressure',note:'Warm humid periods can increase general foliar-disease suitability.',rh:76,t:[20,32],rain:true},
{name:'Heat / water stress',note:'High evaporative demand and dry soil elevate crop stress.',rh:0,t:[40,50],rain:false,abiotic:true}]},
'maize':{name:'Maize / sorghum',heatOpt:[20,34],heatCritical:42,humidDisease:74,soilLow:.13,etoHigh:.39,diseases:[
{name:'Foliar disease suitability',note:'Warm humid conditions can support several foliar pathogens.',rh:76,t:[20,32],rain:true},
{name:'Heat / drought stress',note:'High temperatures and low soil moisture increase reproductive stress.',rh:0,t:[39,50],rain:false,abiotic:true}]},
'sesame':{name:'Sesame',heatOpt:[24,35],heatCritical:43,humidDisease:72,soilLow:.09,etoHigh:.38,diseases:[
{name:'Leaf / stem disease pressure',note:'Wet and humid periods increase general fungal suitability.',rh:76,t:[22,32],rain:true},
{name:'Waterlogging sensitivity',note:'Rainfall and saturated soil can create stress in poorly drained fields.',rh:0,t:[0,50],rain:true,abiotic:true}]}
};

const regions=[
{slug:'riyadh',name:'Riyadh',lat:24.7136,lon:46.6753,x:65,y:50,climate:'Central hyper-arid plateau and irrigated production systems.',stress:'Extreme heat, evapotranspiration, water deficit',desc:'Large central agricultural systems around Riyadh, Al-Kharj and Wadi Al-Dawasir.',crops:['date-palm','wheat','barley','alfalfa','tomato','cucumber','grape']},
{slug:'makkah',name:'Makkah',lat:21.2854,lon:40.4158,x:31,y:59,climate:'Western coastal-to-highland gradient including Taif agricultural environments.',stress:'Heat, water availability, highland variability',desc:'Diverse environments support fruit, vegetables and selected date-palm systems.',crops:['grape','pomegranate','fig','mango','date-palm','tomato']},
{slug:'madinah',name:'Madinah',lat:24.5247,lon:39.5692,x:32,y:45,climate:'Western inland oasis agriculture with hot arid conditions.',stress:'Heat, drought, irrigation demand',desc:'Internationally recognized date-growing environment with additional fruit and vegetable production.',crops:['date-palm','grape','mango','tomato','watermelon']},
{slug:'qassim',name:'Al-Qassim',lat:26.3592,lon:43.9818,x:53,y:38,climate:'Central-northern irrigated arid agriculture.',stress:'Heat, water deficit, protected-crop humidity',desc:'One of the Kingdom’s leading date-palm regions with cereals, fruits and extensive greenhouse production.',crops:['date-palm','wheat','barley','alfalfa','tomato','cucumber','grape','pomegranate']},
{slug:'eastern',name:'Eastern Province',lat:25.3830,lon:49.5860,x:83,y:48,climate:'Gulf-influenced oasis and coastal agriculture including Al-Ahsa and Qatif.',stress:'Heat, humidity, salinity, water quality',desc:'Major oasis date production with humid coastal influence and salinity-management importance.',crops:['date-palm','citrus','tomato','cucumber','mango','alfalfa']},
{slug:'asir',name:'Asir',lat:18.2164,lon:42.5053,x:42,y:75,climate:'Southwestern highlands with milder temperatures and seasonal rainfall.',stress:'Rain variability, humidity, erosion, localized heat',desc:'Highland agriculture supports coffee, fruits, cereals and vegetables.',crops:['coffee','grape','pomegranate','fig','olive','mango','maize']},
{slug:'tabuk',name:'Tabuk',lat:28.3838,lon:36.5550,x:25,y:25,climate:'Northern arid agriculture with cool winters and large seasonal range.',stress:'Cold–heat variability, drought, wind',desc:'Large commercial crop production with grapes, olives, fruits, cereals and vegetables.',crops:['wheat','potato','grape','olive','apple','pomegranate','fig','mango','date-palm']},
{slug:'hail',name:'Hail',lat:27.5114,lon:41.7208,x:45,y:31,climate:'Northern-central continental arid environment.',stress:'Temperature extremes, drought, wind',desc:'Important cereal, date and northern-fruit production environment.',crops:['wheat','barley','date-palm','olive','grape','potato','alfalfa']},
{slug:'northern-borders',name:'Northern Borders',lat:30.9753,lon:41.0381,x:48,y:12,climate:'Northern desert with cold winters and hot dry summers.',stress:'Frost/cold events, drought, wind, heat',desc:'Lower-intensity agriculture with cereals, forage, grapes and protected production in suitable sites.',crops:['wheat','barley','grape','alfalfa','tomato']},
{slug:'jazan',name:'Jazan',lat:16.8892,lon:42.5511,x:40,y:86,climate:'Southwestern Tihamah coastal plain and mountain gradient.',stress:'Humidity, heat, intense rainfall, disease pressure',desc:'Saudi Arabia’s strongest tropical-crop environment, notable for mango, banana and papaya systems.',crops:['mango','banana','maize','sesame','tomato','watermelon','date-palm']},
{slug:'najran',name:'Najran',lat:17.5656,lon:44.2289,x:50,y:82,climate:'Southern interior valley agriculture with hot dry conditions.',stress:'Heat, water deficit, dust and irrigation stress',desc:'Valley agriculture supports dates, cereals, grapes and fruit crops.',crops:['date-palm','wheat','barley','grape','pomegranate','mango','alfalfa']},
{slug:'al-bahah',name:'Al-Bahah',lat:20.0129,lon:41.4677,x:36,y:68,climate:'Southwestern highlands with comparatively mild, wetter conditions.',stress:'Rainfall variability, humidity, slope and erosion',desc:'Mountain agriculture includes fruits, coffee, olives and cereals in suitable elevations.',crops:['coffee','pomegranate','grape','fig','olive','mango','maize']},
{slug:'al-jouf',name:'Al-Jouf',lat:29.9697,lon:40.2064,x:39,y:17,climate:'Northern interior agriculture with Mediterranean influence in winter.',stress:'Drought, frost/heat range, irrigation demand',desc:'Nationally important olive, wheat, date and fruit production environment.',crops:['olive','wheat','date-palm','grape','apple','fig','watermelon','alfalfa']}
];

let currentRegion=3,lastWeather=null,lastSeries=[],lastSummary=null;

function init(){
  $('locationSelect').innerHTML=regions.map((r,i)=>'<option value="'+i+'">'+r.name+'</option>').join('');
  $('farmZone').innerHTML=regions.map((r,i)=>'<option value="'+i+'">'+r.name+'</option>').join('');
  $('locationSelect').value=String(currentRegion);
  updateCropOptions();
  ['locationSelect','horizonSelect'].forEach(id=>$(id).addEventListener('change',()=>{if(id==='locationSelect'){currentRegion=+$('locationSelect').value;updateCropOptions();}loadData();}));
  $('cropSelect').addEventListener('change',loadData);
  $('refreshBtn').addEventListener('click',loadData);
  $('signInBtn').addEventListener('click',signIn);
  $('signUpBtn').addEventListener('click',signUp);
  $('signOutBtn').addEventListener('click',()=>sb.auth.signOut());
  $('farmForm').addEventListener('submit',saveFarm);
  sb.auth.onAuthStateChange(()=>refreshAuth());
  renderAllRegions();
  refreshAuth();
  loadData();
}

function updateCropOptions(){
  const region=regions[currentRegion];
  const previous=$('cropSelect').value;
  $('cropSelect').innerHTML=region.crops.map(k=>'<option value="'+k+'">'+cropProfiles[k].name+'</option>').join('');
  if(region.crops.includes(previous)) $('cropSelect').value=previous;
  renderRegion(currentRegion);
}

async function loadData(){
  const region=regions[currentRegion],crop=cropProfiles[$('cropSelect').value],horizon=+$('horizonSelect').value;
  $('apiStatus').innerHTML='<i class="live-dot"></i> Connecting live data';
  $('statusRegion').textContent=region.name;$('statusCrop').textContent=crop.name;$('statusHorizon').textContent=horizon===24?'24 hours':horizon===72?'72 hours':'7 days';
  renderRegion(currentRegion);
  const hourly=['temperature_2m','relative_humidity_2m','precipitation','wind_speed_10m','et0_fao_evapotranspiration','soil_moisture_0_to_1cm'].join(',');
  const current=['temperature_2m','relative_humidity_2m','precipitation','wind_speed_10m'].join(',');
  const url='https://api.open-meteo.com/v1/forecast?latitude='+region.lat+'&longitude='+region.lon+'&current='+current+'&hourly='+hourly+'&forecast_days=7&timezone=Asia%2FRiyadh';
  try{
    const res=await fetch(url);if(!res.ok) throw new Error('Weather feed unavailable');
    const d=await res.json();lastWeather=d;
    $('apiStatus').innerHTML='<i class="live-dot"></i> Live weather connected';$('statusWeather').textContent='Operational';
    renderCurrent(d);analyze(d,crop,horizon);renderAllRegions();
  }catch(err){
    $('apiStatus').textContent='Weather feed unavailable';$('statusWeather').textContent='Temporarily unavailable';
    $('decisionHeadline').textContent='Live meteorological data could not be retrieved';
    $('farmerDecision').textContent='Retry the live feed before taking a weather-dependent decision.';
    $('researchDecision').textContent='No forecast inference is generated when required weather inputs are unavailable.';
  }
}

function renderCurrent(d){
  const c=d.current||{},h=d.hourly||{};
  const ix=Math.max(0,(h.time||[]).findIndex(t=>t.startsWith((c.time||'').slice(0,13))));
  $('temp').textContent=num(c.temperature_2m,'°C');$('humidity').textContent=num(c.relative_humidity_2m,'%');
  $('precip').textContent=num(c.precipitation,' mm');$('wind').textContent=num(c.wind_speed_10m,' km/h');
  $('eto').textContent=num((h.et0_fao_evapotranspiration||[])[ix],' mm/h',2);$('soil').textContent=num((h.soil_moisture_0_to_1cm||[])[ix],' m³/m³',3);
  $('updatedAt').textContent='Updated '+new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
}
function num(v,u,d=1){return Number.isFinite(v)?v.toFixed(d)+u:'—'}

function analyze(d,crop,horizon){
  const h=d.hourly,n=Math.min(horizon,h.time.length);const biotic=[],abiotic=[],combined=[];
  for(let i=0;i<n;i++){
    const t=h.temperature_2m[i],rh=h.relative_humidity_2m[i],p=h.precipitation[i]||0,wind=h.wind_speed_10m[i]||0,eto=h.et0_fao_evapotranspiration[i]||0,sm=h.soil_moisture_0_to_1cm[i];
    let b=6;
    if(rh>=crop.humidDisease)b+=32;else if(rh>=crop.humidDisease-12)b+=16;
    if(p>0)b+=14;if(t>=crop.heatOpt[0]&&t<=crop.heatOpt[1])b+=16;if(rh>82&&t>15)b+=10;if(wind<7&&rh>75)b+=6;b=Math.min(100,b);
    let a=7;if(t>crop.heatOpt[1])a+=Math.min(42,(t-crop.heatOpt[1])*6);if(t>=crop.heatCritical)a+=18;
    if(Number.isFinite(sm)&&sm<crop.soilLow)a+=25;if(eto>crop.etoHigh)a+=16;if(wind>32)a+=9;a=Math.min(100,a);
    biotic.push(Math.round(b));abiotic.push(Math.round(a));combined.push(Math.round(.48*b+.52*a));
  }
  const mean=a=>a.reduce((x,y)=>x+y,0)/Math.max(a.length,1),peak=Math.max(...combined),score=Math.round(.62*peak+.38*mean(combined));
  const bscore=Math.round(Math.max(...biotic)),ascore=Math.round(Math.max(...abiotic));
  const available=[h.temperature_2m,h.relative_humidity_2m,h.precipitation,h.wind_speed_10m,h.et0_fao_evapotranspiration,h.soil_moisture_0_to_1cm].filter(a=>Array.isArray(a)&&a.slice(0,n).some(Number.isFinite)).length;
  const horizonPenalty=horizon===24?0:horizon===72?5:12;const confidence=Math.max(45,Math.min(94,Math.round(60+available*6-horizonPenalty)));
  lastSeries=combined;lastSummary={score,bscore,ascore,confidence};
  renderRisk(score,bscore,ascore,confidence,h,n,crop,combined);renderDiseases(h,n,crop);renderChart(h.time.slice(0,n),combined);
}

function renderRisk(score,bscore,ascore,confidence,h,n,crop,series){
  const level=riskLevel(score),title=score>=75?'Critical environmental risk window':score>=50?'High-priority crop-health watch':score>=25?'Moderate crop-health pressure':'Low current environmental pressure';
  $('riskScore').textContent=score+'%';$('riskLevel').textContent=level;$('riskTitle').textContent=title;
  $('scoreRing').style.background='conic-gradient('+riskColor(score)+' '+(score*3.6)+'deg,#e8ece9 '+(score*3.6)+'deg)';
  $('bioticScore').textContent=bscore+'%';$('abioticScore').textContent=ascore+'%';$('confidenceScore').textContent=confidence+'%';
  $('bioticBar').style.width=bscore+'%';$('abioticBar').style.width=ascore+'%';$('confidenceBar').style.width=confidence+'%';
  const temps=h.temperature_2m.slice(0,n),rhs=h.relative_humidity_2m.slice(0,n),rain=h.precipitation.slice(0,n),etos=h.et0_fao_evapotranspiration.slice(0,n),sms=h.soil_moisture_0_to_1cm.slice(0,n).filter(Number.isFinite);
  const maxT=Math.max(...temps),maxRH=Math.max(...rhs),rainSum=rain.reduce((a,b)=>a+(b||0),0),maxEto=Math.max(...etos.map(x=>x||0)),minSM=sms.length?Math.min(...sms):NaN;
  const drivers=[];if(maxT>crop.heatOpt[1])drivers.push('Heat '+maxT.toFixed(1)+'°C');if(maxRH>=crop.humidDisease)drivers.push('Humidity '+maxRH.toFixed(0)+'%');if(rainSum>0)drivers.push('Rain '+rainSum.toFixed(1)+' mm');if(maxEto>crop.etoHigh)drivers.push('High ET₀');if(Number.isFinite(minSM)&&minSM<crop.soilLow)drivers.push('Low surface soil moisture');if(!drivers.length)drivers.push('No dominant severe driver');
  $('drivers').innerHTML=drivers.map(x=>'<span>'+x+'</span>').join('');
  $('riskExplanation').textContent='For '+crop.name+', the index integrates crop-specific thermal range, humidity, precipitation, wind, ET₀ and surface soil-moisture signals across the selected forecast horizon.';
  const peakIndex=series.indexOf(Math.max(...series)),peakTime=new Date(h.time[peakIndex]);
  $('peakTiming').textContent=peakTime.toLocaleString([],{weekday:'short',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'})+' • '+series[peakIndex]+'% modeled risk';
  const q=Math.max(1,Math.floor(series.length/3)),early=avg(series.slice(0,q)),late=avg(series.slice(-q)),delta=late-early;
  $('riskTrend').textContent=delta>8?'Increasing across the forecast window (+'+Math.round(delta)+' points).':delta<-8?'Decreasing across the forecast window ('+Math.round(delta)+' points).':'Broadly stable across the forecast window.';
  $('decisionHeadline').textContent=level+' risk • '+crop.name+' • '+regions[currentRegion].name;
  $('farmerDecision').textContent=farmerAdvice(score,drivers,crop.name);
  $('researchDecision').textContent='Peak biotic suitability '+bscore+'%, peak abiotic stress '+ascore+'%, model confidence '+confidence+'%. Dominant modeled drivers: '+drivers.join(', ')+'. Validate against field observations before causal interpretation.';
}

function farmerAdvice(score,drivers,cropName){
  if(score>=75)return 'Prioritise field inspection for '+cropName+' during the identified peak window. Review irrigation, canopy condition and disease/pest scouting immediately; consult locally approved agronomic guidance before treatment decisions.';
  if(score>=50)return 'Increase scouting frequency for '+cropName+', verify irrigation and crop water status, and inspect areas with prior disease or pest history before the peak-risk period.';
  if(score>=25)return 'Maintain closer-than-routine monitoring. Check crop water status and inspect representative plants after meaningful humidity, rainfall or heat changes.';
  return 'Continue routine crop monitoring and irrigation scheduling. No strong environmental hazard signal is present in the selected forecast window.';
}
function avg(a){return a.length?a.reduce((x,y)=>x+y,0)/a.length:0}
function riskLevel(v){return v>=75?'CRITICAL':v>=50?'HIGH':v>=25?'MODERATE':'LOW'}
function riskColor(v){return v>=75?'#9f3f3f':v>=50?'#b96d2e':v>=25?'#a87c2b':'#3c7a63'}

function renderChart(times,values){
  const step=values.length>100?3:values.length>48?2:1;let out='';
  for(let i=0;i<values.length;i+=step){const v=values[i],label=new Date(times[i]).toLocaleString([],{weekday:'short',hour:'2-digit'});out+='<div class="bar" style="height:'+Math.max(8,v*1.85)+'px;background:'+riskColor(v)+'" data-tip="'+label+' • '+v+'%"></div>'}
  $('forecastChart').innerHTML=out;
}

function renderRegion(index){
  const r=regions[index];$('regionTitle').textContent=r.name;$('regionDescription').textContent=r.desc;$('regionClimate').textContent=r.climate;$('regionStress').textContent=r.stress;$('regionCrops').textContent=r.crops.map(k=>cropProfiles[k].name).join(' • ');
}
function renderAllRegions(){
  $('regionMap').innerHTML=regions.map((r,i)=>'<button class="map-node" style="left:'+r.x+'%;top:'+r.y+'%" data-label="'+r.name+'" onclick="selectRegion('+i+')" aria-label="Select '+r.name+'"></button>').join('');
  $('regionCards').innerHTML=regions.map((r,i)=>'<article class="region-card" onclick="selectRegion('+i+')"><strong>'+r.name+'</strong><span>'+r.climate+'</span><p>'+r.crops.slice(0,5).map(k=>cropProfiles[k].name).join(' • ')+(r.crops.length>5?' • +'+(r.crops.length-5)+' more':'')+'</p></article>').join('');
}
window.selectRegion=i=>{currentRegion=i;$('locationSelect').value=String(i);updateCropOptions();renderRegion(i);document.getElementById('regions').scrollIntoView({behavior:'smooth',block:'start'});loadData()};

function renderDiseases(h,n,crop){
  const temps=h.temperature_2m.slice(0,n),rhs=h.relative_humidity_2m.slice(0,n),rain=h.precipitation.slice(0,n),avgT=avg(temps),maxRH=Math.max(...rhs),rainSum=rain.reduce((a,b)=>a+(b||0),0);
  $('diseaseGrid').innerHTML=crop.diseases.map(d=>{
    let s=10;
    if(d.abiotic){
      if(avgT>=d.t[0]&&avgT<=d.t[1])s+=45;if(d.rain&&rainSum>0)s+=18;
    }else{
      if(maxRH>=d.rh)s+=35;else if(maxRH>=d.rh-10)s+=18;if(avgT>=d.t[0]&&avgT<=d.t[1])s+=30;if(d.rain&&rainSum>0)s+=18;
    }
    s=Math.min(95,s);
    return '<article class="disease-card"><span class="label">'+(d.abiotic?'ABIOTIC WATCH':'ENVIRONMENTAL SUITABILITY')+'</span><h3>'+d.name+'</h3><p>'+d.note+'</p><strong>'+s+'%</strong><div class="meter"><i style="width:'+s+'%;background:'+riskColor(s)+'"></i></div><small>'+riskLevel(s)+' modeled suitability • not a diagnosis</small></article>';
  }).join('');
}

async function refreshAuth(){
  const {data:{user}}=await sb.auth.getUser();$('authLoggedOut').hidden=!!user;$('authLoggedIn').hidden=!user;
  if(user){$('userEmail').textContent=user.email;await loadFarms()}else{$('farmList').innerHTML='<p class="muted">Sign in to load your registered sites.</p>';$('farmCount').textContent='0 sites'}
}
async function signIn(){const email=$('authEmail').value.trim(),password=$('authPassword').value;const {error}=await sb.auth.signInWithPassword({email,password});$('authMessage').textContent=error?error.message:'Signed in successfully.'}
async function signUp(){const email=$('authEmail').value.trim(),password=$('authPassword').value;if(password.length<6){$('authMessage').textContent='Use at least 6 characters for the password.';return}const {error}=await sb.auth.signUp({email,password});$('authMessage').textContent=error?error.message:'Account created. Check email confirmation if enabled.'}
async function saveFarm(e){
  e.preventDefault();const {data:{user}}=await sb.auth.getUser();if(!user){$('farmMessage').textContent='Please sign in before saving a site.';return}
  const r=regions[+$('farmZone').value],payload={user_id:user.id,name:$('farmName').value.trim(),latitude:r.lat,longitude:r.lon,area_hectares:$('farmArea').value?+$('farmArea').value:null,irrigation_type:$('irrigation').value};
  const {data:z}=await sb.from('agro_zones').select('id').eq('slug',r.slug).maybeSingle();if(z)payload.zone_id=z.id;
  const {error}=await sb.from('agro_farms').insert(payload);$('farmMessage').textContent=error?error.message:'Site saved securely.';if(!error){e.target.reset();await loadFarms()}
}
async function loadFarms(){
  const {data,error}=await sb.from('agro_farms').select('id,name,area_hectares,irrigation_type,latitude,longitude,created_at').order('created_at',{ascending:false});
  if(error){$('farmList').innerHTML='<p class="muted">'+error.message+'</p>';return}
  $('farmCount').textContent=data.length+' site'+(data.length===1?'':'s');
  $('farmList').innerHTML=data.length?data.map(f=>'<article class="farm-card"><strong>'+escapeHtml(f.name)+'</strong><span>'+(f.area_hectares??'—')+' ha • '+(f.irrigation_type??'unspecified')+'</span><span>'+Number(f.latitude).toFixed(3)+'°, '+Number(f.longitude).toFixed(3)+'°</span></article>').join(''):'<p class="muted">No registered sites yet.</p>';
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]))}
document.addEventListener('DOMContentLoaded',init);
