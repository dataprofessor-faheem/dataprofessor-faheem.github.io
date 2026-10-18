const SB_URL='https://klwzkmfzxrikqslkclik.supabase.co';
const SB_KEY='sb_publishable_PeoU1Z8jnXXptuck9Zb_Jg_QEeBLZKm';
const sb=window.supabase.createClient(SB_URL,SB_KEY);
const $=id=>document.getElementById(id);

const cropProfiles={
'date-palm':{name:'Date palm',heatOpt:[25,42],heatCritical:46,humidDisease:68,soilLow:.08,etoHigh:.36,diseases:[{name:'Black scorch',note:'Warm, humid conditions can increase fungal suitability; field symptoms require confirmation.',rh:65,t:[20,38],rain:true},{name:'Inflorescence rot',note:'Moisture and humidity around flowering structures can favor fungal infection windows.',rh:72,t:[18,32],rain:true},{name:'Red palm weevil climate pressure',note:'Weather suitability indicator; pheromone trapping and field inspection provide the biological evidence.',rh:45,t:[24,38],rain:false}]},
'wheat':{name:'Wheat',heatOpt:[12,28],heatCritical:35,humidDisease:74,soilLow:.12,etoHigh:.32,diseases:[{name:'Rust weather suitability',note:'Moderate temperatures plus prolonged humidity can favor rust development.',rh:72,t:[10,26],rain:true},{name:'Powdery mildew suitability',note:'Cool-to-moderate temperatures with elevated humidity can increase suitability.',rh:68,t:[12,24],rain:false},{name:'Heat stress at grain filling',note:'High temperature during reproductive development can reduce performance.',rh:0,t:[32,50],rain:false,abiotic:true}]},
'barley':{name:'Barley',heatOpt:[12,30],heatCritical:37,humidDisease:72,soilLow:.11,etoHigh:.33,diseases:[{name:'Leaf blotch suitability',note:'Moist leaf surfaces and moderate temperatures can favor foliar disease.',rh:72,t:[12,27],rain:true},{name:'Rust suitability',note:'Humidity and mild temperatures can support rust infection windows.',rh:70,t:[10,26],rain:true}]},
'alfalfa':{name:'Alfalfa',heatOpt:[18,35],heatCritical:42,humidDisease:74,soilLow:.13,etoHigh:.40,diseases:[{name:'Foliar disease pressure',note:'High humidity can raise general foliar-disease suitability.',rh:74,t:[18,32],rain:true},{name:'Heat / water stress',note:'High evaporative demand with low soil moisture increases crop stress.',rh:0,t:[38,50],rain:false,abiotic:true}]},
'tomato':{name:'Tomato',heatOpt:[18,30],heatCritical:36,humidDisease:75,soilLow:.14,etoHigh:.34,diseases:[{name:'Blight weather window',note:'Leaf-wetness proxies, humidity and moderate temperatures increase disease suitability.',rh:78,t:[16,28],rain:true},{name:'Powdery mildew suitability',note:'Warm conditions with elevated humidity can increase canopy risk.',rh:70,t:[20,31],rain:false},{name:'Heat-set stress',note:'High temperature can impair flowering and fruit set.',rh:0,t:[34,50],rain:false,abiotic:true}]},
'cucumber':{name:'Cucumber',heatOpt:[20,30],heatCritical:36,humidDisease:78,soilLow:.16,etoHigh:.34,diseases:[{name:'Downy mildew suitability',note:'High humidity and wet-canopy conditions favor disease development.',rh:80,t:[16,27],rain:true},{name:'Powdery mildew suitability',note:'Warm humid conditions can increase disease pressure.',rh:70,t:[20,31],rain:false}]},
'potato':{name:'Potato',heatOpt:[15,26],heatCritical:33,humidDisease:78,soilLow:.16,etoHigh:.31,diseases:[{name:'Late blight weather suitability',note:'Cool-to-moderate temperatures with high humidity form a classic risk combination.',rh:80,t:[10,24],rain:true},{name:'Heat / tuber stress',note:'Sustained heat can reduce tuber development and quality.',rh:0,t:[30,50],rain:false,abiotic:true}]},
'onion':{name:'Onion',heatOpt:[13,28],heatCritical:36,humidDisease:76,soilLow:.12,etoHigh:.33,diseases:[{name:'Downy mildew suitability',note:'Cool humid conditions can favor foliar disease.',rh:80,t:[10,24],rain:true},{name:'Heat / bulb stress',note:'High temperature and water deficit can increase crop stress.',rh:0,t:[35,50],rain:false,abiotic:true}]},
'citrus':{name:'Citrus',heatOpt:[18,34],heatCritical:43,humidDisease:72,soilLow:.13,etoHigh:.38,diseases:[{name:'Citrus fungal pressure',note:'Warm humid weather and rainfall can elevate general fungal suitability.',rh:75,t:[18,32],rain:true},{name:'Heat / sunburn stress',note:'Extreme heat and high evaporative demand can injure exposed fruit and canopy.',rh:0,t:[41,50],rain:false,abiotic:true}]},
'grape':{name:'Grape',heatOpt:[18,32],heatCritical:40,humidDisease:72,soilLow:.12,etoHigh:.36,diseases:[{name:'Powdery mildew suitability',note:'Mild-to-warm humid conditions can support disease development.',rh:65,t:[18,30],rain:false},{name:'Downy mildew suitability',note:'Rainfall and high humidity increase risk windows.',rh:78,t:[12,28],rain:true}]},
'olive':{name:'Olive',heatOpt:[15,34],heatCritical:43,humidDisease:72,soilLow:.09,etoHigh:.38,diseases:[{name:'Peacock spot suitability',note:'Cooler wet periods increase environmental suitability.',rh:78,t:[10,24],rain:true},{name:'Verticillium surveillance',note:'Field history and soil evidence are more important than weather alone.',rh:55,t:[18,30],rain:false}]},
'mango':{name:'Mango',heatOpt:[24,35],heatCritical:43,humidDisease:75,soilLow:.13,etoHigh:.38,diseases:[{name:'Anthracnose weather suitability',note:'Warm, wet and humid periods are important environmental drivers.',rh:80,t:[22,32],rain:true},{name:'Powdery mildew suitability',note:'Moderate temperatures with elevated humidity can favor infection.',rh:70,t:[18,30],rain:false}]},
'banana':{name:'Banana',heatOpt:[24,32],heatCritical:39,humidDisease:80,soilLow:.18,etoHigh:.36,diseases:[{name:'Leaf-spot weather suitability',note:'Warm, humid environments can support foliar disease pressure.',rh:82,t:[22,31],rain:true},{name:'Heat / water stress',note:'Banana is sensitive to high evaporative demand and moisture deficit.',rh:0,t:[37,50],rain:false,abiotic:true}]},
'coffee':{name:'Arabian coffee',heatOpt:[18,27],heatCritical:34,humidDisease:75,soilLow:.16,etoHigh:.30,diseases:[{name:'Coffee leaf rust suitability',note:'Humidity, leaf wetness and mild temperatures can increase suitability.',rh:78,t:[18,26],rain:true},{name:'Heat / drought stress',note:'High temperature and water deficit can stress coffee in mountain systems.',rh:0,t:[31,50],rain:false,abiotic:true}]},
'pomegranate':{name:'Pomegranate',heatOpt:[18,34],heatCritical:42,humidDisease:72,soilLow:.11,etoHigh:.37,diseases:[{name:'Fruit rot weather pressure',note:'Humidity and rainfall can increase fruit-rot suitability.',rh:76,t:[18,31],rain:true},{name:'Heat / fruit-cracking stress',note:'Rapid water-status changes and heat can elevate physiological stress.',rh:0,t:[39,50],rain:false,abiotic:true}]},
'fig':{name:'Fig',heatOpt:[18,35],heatCritical:43,humidDisease:72,soilLow:.10,etoHigh:.37,diseases:[{name:'Fruit rot suitability',note:'Humidity and rainfall around ripening can increase spoilage pressure.',rh:78,t:[18,32],rain:true},{name:'Heat / water stress',note:'High evaporative demand can increase physiological stress.',rh:0,t:[40,50],rain:false,abiotic:true}]},
'apple':{name:'Apple',heatOpt:[12,28],heatCritical:36,humidDisease:75,soilLow:.14,etoHigh:.32,diseases:[{name:'Apple scab weather suitability',note:'Mild temperatures and wet foliage favor infection windows.',rh:78,t:[10,24],rain:true},{name:'Heat stress',note:'High temperatures can reduce fruit quality and increase sunburn risk.',rh:0,t:[34,50],rain:false,abiotic:true}]},
'watermelon':{name:'Watermelon',heatOpt:[22,34],heatCritical:42,humidDisease:72,soilLow:.12,etoHigh:.39,diseases:[{name:'Foliar disease pressure',note:'Warm humid periods can increase general foliar-disease suitability.',rh:76,t:[20,32],rain:true},{name:'Heat / water stress',note:'High evaporative demand and dry soil elevate crop stress.',rh:0,t:[40,50],rain:false,abiotic:true}]},
'maize':{name:'Maize / sorghum',heatOpt:[20,34],heatCritical:42,humidDisease:74,soilLow:.13,etoHigh:.39,diseases:[{name:'Foliar disease suitability',note:'Warm humid conditions can support several foliar pathogens.',rh:76,t:[20,32],rain:true},{name:'Heat / drought stress',note:'High temperatures and low soil moisture increase reproductive stress.',rh:0,t:[39,50],rain:false,abiotic:true}]},
'sesame':{name:'Sesame',heatOpt:[24,35],heatCritical:43,humidDisease:72,soilLow:.09,etoHigh:.38,diseases:[{name:'Leaf / stem disease pressure',note:'Wet and humid periods increase general fungal suitability.',rh:76,t:[22,32],rain:true},{name:'Waterlogging sensitivity',note:'Rainfall and saturated soil can create stress in poorly drained fields.',rh:0,t:[0,50],rain:true,abiotic:true}]}
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
{slug:'northern-borders',name:'Northern Borders',lat:30.9753,lon:41.0381,x:48,y:12,climate:'Northern desert with cold winters and hot dry summers.',stress:'Frost/cold events, drought, wind, heat',desc:'Cereal, forage, grape and protected production occur in suitable sites.',crops:['wheat','barley','grape','alfalfa','tomato']},
{slug:'jazan',name:'Jazan',lat:16.8892,lon:42.5511,x:40,y:86,climate:'Southwestern Tihamah coastal plain and mountain gradient.',stress:'Humidity, heat, intense rainfall, disease pressure',desc:'Saudi Arabia’s strongest tropical-crop environment, notable for mango and banana systems.',crops:['mango','banana','maize','sesame','tomato','watermelon','date-palm']},
{slug:'najran',name:'Najran',lat:17.5656,lon:44.2289,x:50,y:82,climate:'Southern interior valley agriculture with hot dry conditions.',stress:'Heat, water deficit, dust and irrigation stress',desc:'Valley agriculture supports dates, cereals, grapes and fruit crops.',crops:['date-palm','wheat','barley','grape','pomegranate','mango','alfalfa','citrus']},
{slug:'al-bahah',name:'Al-Bahah',lat:20.0129,lon:41.4677,x:36,y:68,climate:'Southwestern highlands with comparatively mild, wetter conditions.',stress:'Rainfall variability, humidity, slope and erosion',desc:'Mountain agriculture includes fruits, coffee, olives and cereals at suitable elevations.',crops:['coffee','pomegranate','grape','fig','olive','mango','maize']},
{slug:'al-jouf',name:'Al-Jouf',lat:29.9697,lon:40.2064,x:39,y:17,climate:'Northern interior agriculture with Mediterranean influence in winter.',stress:'Drought, frost/heat range, irrigation demand',desc:'Nationally important olive, wheat, date and fruit production environment.',crops:['olive','wheat','date-palm','grape','apple','fig','watermelon','alfalfa']}
];



const cityProfiles=[
{id:'riyadh-city',region:'riyadh',name:'Riyadh',lat:24.7136,lon:46.6753,crops:['date-palm','tomato','cucumber','alfalfa']},
{id:'al-kharj',region:'riyadh',name:'Al-Kharj',lat:24.1556,lon:47.3120,crops:['date-palm','wheat','alfalfa','tomato','cucumber']},
{id:'wadi-dawasir',region:'riyadh',name:'Wadi Al-Dawasir',lat:20.4607,lon:44.7871,crops:['date-palm','wheat','alfalfa','tomato']},
{id:'majmaah',region:'riyadh',name:"Al-Majma'ah",lat:25.9044,lon:45.3566,crops:['wheat','barley','date-palm','alfalfa']},
{id:'zulfi',region:'riyadh',name:'Zulfi',lat:26.2994,lon:44.8154,crops:['date-palm','wheat','barley','alfalfa']},

{id:'makkah-city',region:'makkah',name:'Makkah',lat:21.3891,lon:39.8579,crops:['date-palm','tomato','fig']},
{id:'taif',region:'makkah',name:'Taif',lat:21.2854,lon:40.4158,crops:['grape','pomegranate','fig','tomato','olive']},
{id:'jeddah',region:'makkah',name:'Jeddah',lat:21.5433,lon:39.1728,crops:['tomato','cucumber','date-palm']},
{id:'qunfudhah',region:'makkah',name:'Al-Qunfudhah',lat:19.1264,lon:41.0789,crops:['mango','maize','sesame','tomato','watermelon']},

{id:'madinah-city',region:'madinah',name:'Madinah',lat:24.5247,lon:39.5692,crops:['date-palm','grape','tomato']},
{id:'yanbu',region:'madinah',name:'Yanbu',lat:24.0895,lon:38.0618,crops:['date-palm','mango','tomato','watermelon']},
{id:'khaybar',region:'madinah',name:'Khaybar',lat:25.6980,lon:39.2930,crops:['date-palm','grape','alfalfa']},

{id:'buraydah',region:'qassim',name:'Buraydah',lat:26.3592,lon:43.9818,crops:['date-palm','wheat','barley','tomato','cucumber']},
{id:'unaizah',region:'qassim',name:'Unaizah',lat:26.0843,lon:43.9936,crops:['date-palm','wheat','tomato','grape','pomegranate']},
{id:'al-rass',region:'qassim',name:'Al-Rass',lat:25.8694,lon:43.4973,crops:['wheat','barley','date-palm','alfalfa']},
{id:'bukayriyah',region:'qassim',name:'Al-Bukayriyah',lat:26.1442,lon:43.6578,crops:['date-palm','grape','pomegranate','tomato']},

{id:'hofuf',region:'eastern',name:'Al-Ahsa / Hofuf',lat:25.3830,lon:49.5860,crops:['date-palm','citrus','tomato','cucumber','alfalfa']},
{id:'dammam',region:'eastern',name:'Dammam',lat:26.4207,lon:50.0888,crops:['date-palm','tomato','cucumber']},
{id:'qatif',region:'eastern',name:'Qatif',lat:26.5652,lon:50.0089,crops:['date-palm','citrus','tomato','cucumber']},
{id:'jubail',region:'eastern',name:'Jubail',lat:27.0174,lon:49.6225,crops:['date-palm','tomato','cucumber']},

{id:'abha',region:'asir',name:'Abha',lat:18.2164,lon:42.5053,crops:['coffee','grape','pomegranate','fig','maize']},
{id:'khamis',region:'asir',name:'Khamis Mushait',lat:18.3064,lon:42.7293,crops:['grape','pomegranate','maize','tomato']},
{id:'muhayil',region:'asir',name:'Muhayil Asir',lat:18.5453,lon:42.0535,crops:['mango','maize','sesame','tomato']},
{id:'namas',region:'asir',name:'Al-Namas',lat:19.1217,lon:42.1356,crops:['coffee','grape','fig','olive','apple']},

{id:'tabuk-city',region:'tabuk',name:'Tabuk',lat:28.3838,lon:36.5550,crops:['wheat','potato','grape','olive','apple']},
{id:'tayma',region:'tabuk',name:'Tayma',lat:27.6203,lon:38.5219,crops:['date-palm','grape','olive','wheat']},
{id:'duba',region:'tabuk',name:'Duba',lat:27.3513,lon:35.6901,crops:['date-palm','grape','tomato']},
{id:'haql',region:'tabuk',name:'Haql',lat:29.2833,lon:34.9500,crops:['grape','olive','tomato','apple']},

{id:'hail-city',region:'hail',name:'Hail',lat:27.5114,lon:41.7208,crops:['wheat','barley','date-palm','olive','grape','potato']},
{id:'baqaa',region:'hail',name:"Baqa'a",lat:27.8833,lon:42.4167,crops:['wheat','barley','alfalfa']},
{id:'ghazalah',region:'hail',name:'Al-Ghazalah',lat:26.7850,lon:41.8170,crops:['date-palm','wheat','barley']},

{id:'arar',region:'northern-borders',name:'Arar',lat:30.9753,lon:41.0381,crops:['wheat','barley','alfalfa','tomato']},
{id:'rafha',region:'northern-borders',name:'Rafha',lat:29.6270,lon:43.4940,crops:['wheat','barley','alfalfa']},
{id:'turaif',region:'northern-borders',name:'Turaif',lat:31.6725,lon:38.6637,crops:['wheat','barley','tomato']},

{id:'jazan-city',region:'jazan',name:'Jazan',lat:16.8892,lon:42.5511,crops:['mango','banana','tomato','watermelon']},
{id:'sabya',region:'jazan',name:'Sabya',lat:17.1495,lon:42.6254,crops:['mango','banana','maize','sesame']},
{id:'abu-arish',region:'jazan',name:'Abu Arish',lat:16.9689,lon:42.8325,crops:['mango','banana','maize','sesame','tomato']},
{id:'baish',region:'jazan',name:'Baish',lat:17.3881,lon:42.5241,crops:['mango','banana','maize']},
{id:'samtah',region:'jazan',name:'Samtah',lat:16.5964,lon:42.9444,crops:['mango','banana','sesame','maize']},

{id:'najran-city',region:'najran',name:'Najran',lat:17.5656,lon:44.2289,crops:['date-palm','wheat','barley','grape','pomegranate','mango']},
{id:'sharurah',region:'najran',name:'Sharurah',lat:17.4667,lon:47.1167,crops:['date-palm','wheat','alfalfa']},
{id:'hubuna',region:'najran',name:'Hubuna',lat:17.8370,lon:44.0230,crops:['date-palm','grape','pomegranate']},

{id:'bahah-city',region:'al-bahah',name:'Al-Bahah',lat:20.0129,lon:41.4677,crops:['coffee','pomegranate','grape','fig','olive']},
{id:'makhwah',region:'al-bahah',name:'Al-Makhwah',lat:19.7794,lon:41.4394,crops:['coffee','mango','maize','sesame']},
{id:'mandaq',region:'al-bahah',name:'Al-Mandaq',lat:20.1060,lon:41.2830,crops:['coffee','pomegranate','grape','fig']},
{id:'qilwah',region:'al-bahah',name:'Qilwah',lat:19.7520,lon:41.4300,crops:['coffee','mango','maize']},

{id:'sakaka',region:'al-jouf',name:'Sakaka',lat:29.9697,lon:40.2064,crops:['olive','wheat','date-palm','grape','apple']},
{id:'dumat',region:'al-jouf',name:'Dumat Al-Jandal',lat:29.8158,lon:39.8664,crops:['olive','date-palm','grape','wheat']},
{id:'qurayyat',region:'al-jouf',name:'Al-Qurayyat',lat:31.3318,lon:37.3428,crops:['olive','wheat','grape','apple']},
{id:'tabarjal',region:'al-jouf',name:'Tabarjal',lat:30.5007,lon:38.2143,crops:['wheat','olive','alfalfa']}
];

let currentRegion=3;
let activeCityId='regional';
let activeCoords=null;
let lastWeather=null;
let lastRows=[];
let lastDiseaseScores=[];
const charts={};

function init(){
  $('locationSelect').innerHTML=regions.map((r,i)=>`<option value="${i}">${r.name}</option>`).join('');
  $('farmZone').innerHTML=regions.map((r,i)=>`<option value="${i}">${r.name}</option>`).join('');
  $('locationSelect').value=String(currentRegion);
  populateCityOptions();
  updateCropOptions();
  $('locationSelect').addEventListener('change',()=>{currentRegion=+$('locationSelect').value;activeCityId='regional';activeCoords=null;populateCityOptions();updateCropOptions();updateLocationReadout();loadData();});
  $('citySelect').addEventListener('change',()=>{activeCityId=$('citySelect').value;activeCoords=null;updateCropOptions();updateLocationReadout();loadData();});
  $('cropSelect').addEventListener('change',loadData);
  $('horizonSelect').addEventListener('change',loadData);
  $('refreshBtn').addEventListener('click',loadData);
  $('useGpsBtn').addEventListener('click',useFarmGps);
  $('downloadReportBtn').addEventListener('click',generateNabatReport);
  $('signInBtn').addEventListener('click',signIn);
  $('signUpBtn').addEventListener('click',signUp);
  $('signOutBtn').addEventListener('click',()=>sb.auth.signOut());
  $('farmForm').addEventListener('submit',saveFarm);
  sb.auth.onAuthStateChange(()=>refreshAuth());
  renderAllRegions();
  updateLocationReadout();
  refreshAuth();
  loadData();
}

function citiesForRegion(){return cityProfiles.filter(c=>c.region===regions[currentRegion].slug);}
function getSelectedCity(){return activeCityId==='regional'?null:cityProfiles.find(c=>c.id===activeCityId)||null;}
function populateCityOptions(){
  const cities=citiesForRegion();
  $('citySelect').innerHTML='<option value="regional">Regional analysis</option>'+cities.map(c=>`<option value="${c.id}">${c.name}</option>`).join('');
  if(!cities.some(c=>c.id===activeCityId)) activeCityId='regional';
  $('citySelect').value=activeCityId;
}
function updateCropOptions(){
  const region=regions[currentRegion],city=getSelectedCity(),previous=$('cropSelect').value;
  const cropKeys=city?.crops?.length?city.crops:region.crops;
  $('cropSelect').innerHTML=cropKeys.map(k=>`<option value="${k}">${cropProfiles[k].name}</option>`).join('');
  if(cropKeys.includes(previous)) $('cropSelect').value=previous;
  renderRegion(currentRegion);
}
function updateLocationReadout(){
  const region=regions[currentRegion],city=getSelectedCity();
  if(activeCoords){
    $('locationReadout').textContent=`Farm GPS: ${activeCoords.lat.toFixed(5)}°, ${activeCoords.lon.toFixed(5)}° • ${region.name}`;
    $('statusLocation').textContent='Farm GPS';
    if($('statusCity')) $('statusCity').textContent='GPS';
  }else if(city){
    $('locationReadout').textContent=`${city.name}: ${city.lat.toFixed(4)}°, ${city.lon.toFixed(4)}° • ${region.name}`;
    $('statusLocation').textContent='City';
    if($('statusCity')) $('statusCity').textContent=city.name;
  }else{
    $('locationReadout').textContent=`Regional reference: ${region.lat.toFixed(4)}°, ${region.lon.toFixed(4)}° • ${region.name}`;
    $('statusLocation').textContent='Region';
    if($('statusCity')) $('statusCity').textContent='Regional';
  }
}

function useFarmGps(){
  if(!navigator.geolocation){$('gpsStatus').textContent='Browser geolocation is not available; regional reference mode remains active.';return;}
  $('gpsStatus').textContent='Requesting device location…';
  navigator.geolocation.getCurrentPosition(pos=>{
    const lat=pos.coords.latitude,lon=pos.coords.longitude;
    if(lat<15.5||lat>33.7||lon<34||lon>56.8){activeCoords=null;$('gpsStatus').textContent='Device location is outside the Saudi operating extent; regional reference mode remains active.';updateLocationReadout();return;}
    const nearest=nearestRegion(lat,lon);currentRegion=nearest;activeCityId='regional';$('locationSelect').value=String(nearest);populateCityOptions();activeCoords={lat,lon,accuracy:pos.coords.accuracy};updateCropOptions();updateLocationReadout();$('gpsStatus').textContent=`GPS accepted • estimated accuracy ±${Math.round(pos.coords.accuracy)} m • weather will use the farm coordinate.`;loadData();
  },err=>{$('gpsStatus').textContent=err.code===1?'Location permission was not granted; regional reference mode remains active.':'Location could not be resolved; regional reference mode remains active.';},{enableHighAccuracy:true,timeout:12000,maximumAge:300000});
}

function nearestRegion(lat,lon){let best=0,bestD=Infinity;regions.forEach((r,i)=>{const d=haversine(lat,lon,r.lat,r.lon);if(d<bestD){bestD=d;best=i;}});return best;}
function haversine(a,b,c,d){const R=6371,toRad=x=>x*Math.PI/180;const dLat=toRad(c-a),dLon=toRad(d-b);const q=Math.sin(dLat/2)**2+Math.cos(toRad(a))*Math.cos(toRad(c))*Math.sin(dLon/2)**2;return 2*R*Math.asin(Math.sqrt(q));}

async function loadData(){
  const region=regions[currentRegion],city=getSelectedCity(),crop=cropProfiles[$('cropSelect').value],horizon=+$('horizonSelect').value;
  const coords=activeCoords||(city?{lat:city.lat,lon:city.lon}:{lat:region.lat,lon:region.lon});
  $('apiStatus').innerHTML='<i class="live-dot"></i> Connecting live data';
  $('statusRegion').textContent=region.name;if($('statusCity'))$('statusCity').textContent=activeCoords?'GPS':(city?city.name:'Regional');$('statusCrop').textContent=crop.name;$('statusHorizon').textContent=horizon===24?'24 hours':horizon===72?'72 hours':'7 days';
  renderRegion(currentRegion);updateLocationReadout();
  const hourly=['temperature_2m','relative_humidity_2m','precipitation','wind_speed_10m','et0_fao_evapotranspiration','soil_moisture_0_to_1cm'].join(',');
  const current=['temperature_2m','relative_humidity_2m','precipitation','wind_speed_10m'].join(',');
  const url=`https://api.open-meteo.com/v1/forecast?latitude=${coords.lat}&longitude=${coords.lon}&current=${current}&hourly=${hourly}&forecast_days=7&timezone=Asia%2FRiyadh`;
  try{
    const res=await fetch(url);if(!res.ok)throw new Error('Weather feed unavailable');const d=await res.json();lastWeather=d;
    $('apiStatus').innerHTML='<i class="live-dot"></i> Live weather connected';$('statusWeather').textContent='Operational';
    renderCurrent(d);analyze(d,crop,horizon);renderAllRegions();
  }catch(err){
    $('apiStatus').textContent='Weather feed unavailable';$('statusWeather').textContent='Temporarily unavailable';$('decisionHeadline').textContent='Meteorological feed unavailable';$('researchDecision').textContent='No risk inference is issued when the required forecast variables are unavailable.';$('farmerActions').innerHTML='<li>Refresh the weather feed before using this decision workspace for farm operations.</li>';
  }
}

function renderCurrent(d){
  const c=d.current||{},h=d.hourly||{},ix=Math.max(0,(h.time||[]).findIndex(t=>t.startsWith((c.time||'').slice(0,13))));
  $('temp').textContent=num(c.temperature_2m,'°C');$('humidity').textContent=num(c.relative_humidity_2m,'%');$('precip').textContent=num(c.precipitation,' mm');$('wind').textContent=num(c.wind_speed_10m,' km/h');$('eto').textContent=num((h.et0_fao_evapotranspiration||[])[ix],' mm/h',2);$('soil').textContent=num((h.soil_moisture_0_to_1cm||[])[ix],' m³/m³',3);$('updatedAt').textContent=`Updated ${new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}`;
}
function num(v,u,d=1){return Number.isFinite(v)?`${v.toFixed(d)}${u}`:'—'}

function analyze(d,crop,horizon){
  const h=d.hourly,n=Math.min(horizon,h.time.length),rows=[];
  for(let i=0;i<n;i++){
    const t=h.temperature_2m[i],rh=h.relative_humidity_2m[i],p=h.precipitation[i]||0,wind=h.wind_speed_10m[i]||0,eto=h.et0_fao_evapotranspiration[i]||0,sm=h.soil_moisture_0_to_1cm[i];
    let biotic=6;if(rh>=crop.humidDisease)biotic+=32;else if(rh>=crop.humidDisease-12)biotic+=16;if(p>0)biotic+=14;if(t>=crop.heatOpt[0]&&t<=crop.heatOpt[1])biotic+=16;if(rh>82&&t>15)biotic+=10;if(wind<7&&rh>75)biotic+=6;biotic=Math.min(100,biotic);
    let abiotic=7;if(t>crop.heatOpt[1])abiotic+=Math.min(42,(t-crop.heatOpt[1])*6);if(t>=crop.heatCritical)abiotic+=18;if(Number.isFinite(sm)&&sm<crop.soilLow)abiotic+=25;if(eto>crop.etoHigh)abiotic+=16;if(wind>32)abiotic+=9;abiotic=Math.min(100,abiotic);
    const risk=Math.round(.48*biotic+.52*abiotic);
    rows.push({time:h.time[i],t,rh,p,wind,eto,sm,biotic:Math.round(biotic),abiotic:Math.round(abiotic),risk});
  }
  lastRows=rows;
  const score=Math.round(.62*Math.max(...rows.map(r=>r.risk))+.38*mean(rows.map(r=>r.risk))),bscore=Math.max(...rows.map(r=>r.biotic)),ascore=Math.max(...rows.map(r=>r.abiotic));
  const available=['t','rh','p','wind','eto','sm'].filter(k=>rows.some(r=>Number.isFinite(r[k]))).length,horizonPenalty=horizon===24?0:horizon===72?5:12,confidence=Math.max(45,Math.min(94,Math.round(60+available*6-horizonPenalty)));
  lastDiseaseScores=calculateDiseaseScores(rows,crop);
  renderRisk(score,bscore,ascore,confidence,rows,crop);renderDiseases(crop);renderFarmerActions(rows,crop,score,confidence,lastDiseaseScores);
  try{renderAnalytics(rows,crop,confidence);}catch(err){console.error('NABAT analytics rendering error',err);const note=$('researchAnalyticsText');if(note)note.textContent='Statistical summaries are available; graphical rendering could not be completed in this browser session.';}
}

function renderRisk(score,bscore,ascore,confidence,rows,crop){
  const level=riskLevel(score),title=score>=75?'Critical environmental risk window':score>=50?'High-priority crop-health watch':score>=25?'Moderate crop-health pressure':'Low current environmental pressure';
  $('riskScore').textContent=`${score}%`;$('riskLevel').textContent=level;$('riskTitle').textContent=title;$('scoreRing').style.background=`conic-gradient(${riskColor(score)} ${score*3.6}deg,#e8ece9 ${score*3.6}deg)`;
  $('bioticScore').textContent=`${bscore}%`;$('abioticScore').textContent=`${ascore}%`;$('confidenceScore').textContent=`${confidence}%`;$('bioticBar').style.width=`${bscore}%`;$('abioticBar').style.width=`${ascore}%`;$('confidenceBar').style.width=`${confidence}%`;
  const s=summarizeRows(rows,crop),drivers=[];if(s.maxT>crop.heatOpt[1])drivers.push(`Heat ${s.maxT.toFixed(1)}°C`);if(s.maxRH>=crop.humidDisease)drivers.push(`Humidity ${s.maxRH.toFixed(0)}%`);if(s.rain>0)drivers.push(`Rain ${s.rain.toFixed(1)} mm`);if(s.maxEto>crop.etoHigh)drivers.push('High ET₀');if(Number.isFinite(s.minSM)&&s.minSM<crop.soilLow)drivers.push('Low surface soil moisture');if(s.maxWind>32)drivers.push('Strong wind');if(!drivers.length)drivers.push('No dominant severe driver');$('drivers').innerHTML=drivers.map(x=>`<span>${x}</span>`).join('');
  $('riskExplanation').textContent=`For ${crop.name}, the index combines crop-specific thermal range, atmospheric moisture, rainfall, wind, evapotranspiration and surface soil-moisture signals across the selected forecast period.`;
  const peakRow=rows.reduce((a,b)=>b.risk>a.risk?b:a,rows[0]);$('peakTiming').textContent=`${fmtDateTime(peakRow.time)} • ${peakRow.risk}% modeled risk`;
  const q=Math.max(1,Math.floor(rows.length/3)),delta=mean(rows.slice(-q).map(r=>r.risk))-mean(rows.slice(0,q).map(r=>r.risk));$('riskTrend').textContent=delta>8?`Increasing across the forecast window (+${Math.round(delta)} points).`:delta<-8?`Decreasing across the forecast window (${Math.round(delta)} points).`:'Broadly stable across the forecast window.';
  $('decisionHeadline').textContent=`${level} risk • ${crop.name} • ${regions[currentRegion].name}`;$('researchDecision').textContent=`Peak biotic suitability ${bscore}%, peak abiotic stress ${ascore}%, forecast confidence ${confidence}%. Primary environmental drivers: ${drivers.join(', ')}.`;
}

function summarizeRows(rows,crop){const sms=rows.map(r=>r.sm).filter(Number.isFinite);return{meanT:mean(rows.map(r=>r.t)),maxT:Math.max(...rows.map(r=>r.t)),minT:Math.min(...rows.map(r=>r.t)),maxRH:Math.max(...rows.map(r=>r.rh)),meanRH:mean(rows.map(r=>r.rh)),rain:sum(rows.map(r=>r.p)),eto:sum(rows.map(r=>r.eto)),maxEto:Math.max(...rows.map(r=>r.eto)),minSM:sms.length?Math.min(...sms):NaN,meanSM:sms.length?mean(sms):NaN,maxWind:Math.max(...rows.map(r=>r.wind)),crop};}
function mean(a){const f=a.filter(Number.isFinite);return f.length?f.reduce((x,y)=>x+y,0)/f.length:NaN;}function sum(a){return a.filter(Number.isFinite).reduce((x,y)=>x+y,0);}
function fmtDateTime(t){return new Date(t).toLocaleString([],{weekday:'short',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'});}function riskLevel(v){return v>=75?'CRITICAL':v>=50?'HIGH':v>=25?'MODERATE':'LOW'}function riskColor(v){return v>=75?'#9f3f3f':v>=50?'#b96d2e':v>=25?'#a87c2b':'#3c7a63'}

function calculateDiseaseScores(rows,crop){const s=summarizeRows(rows,crop);return crop.diseases.map(d=>{let score=10;if(d.abiotic){if(s.meanT>=d.t[0]&&s.meanT<=d.t[1])score+=45;if(d.rain&&s.rain>0)score+=18;}else{if(s.maxRH>=d.rh)score+=35;else if(s.maxRH>=d.rh-10)score+=18;if(s.meanT>=d.t[0]&&s.meanT<=d.t[1])score+=30;if(d.rain&&s.rain>0)score+=18;}return{...d,score:Math.min(95,score)};}).sort((a,b)=>b.score-a.score);}
function renderDiseases(crop){$('diseaseGrid').innerHTML=lastDiseaseScores.map(d=>`<article class="disease-card"><span class="label">${d.abiotic?'ABIOTIC WATCH':'ENVIRONMENTAL SUITABILITY'}</span><h3>${d.name}</h3><p>${d.note}</p><strong>${d.score}%</strong><div class="meter"><i style="width:${d.score}%;background:${riskColor(d.score)}"></i></div><small>${riskLevel(d.score)} surveillance priority</small></article>`).join('');}

function renderFarmerActions(rows,crop,score,confidence,diseaseScores){
  const s=summarizeRows(rows,crop),peak=rows.reduce((a,b)=>b.risk>a.risk?b:a,rows[0]),topDisease=diseaseScores[0];
  const actions=[];
  actions.push(score>=75?`Treat ${fmtDateTime(peak.time)} as the priority inspection window: walk the crop before and after this period and document visible stress, pests or disease symptoms.`:score>=50?`Increase field scouting around ${fmtDateTime(peak.time)}, when the combined environmental risk is forecast to peak.`:score>=25?`Add a focused crop inspection around ${fmtDateTime(peak.time)} while maintaining the normal monitoring schedule.`:`Continue routine monitoring; the current forecast does not show a strong combined hazard window for ${crop.name}.`);
  if(Number.isFinite(s.minSM)&&s.minSM<crop.soilLow) actions.push(`Review irrigation timing because modeled surface soil moisture falls to ${s.minSM.toFixed(3)} m³/m³ while cumulative ET₀ is ${s.eto.toFixed(2)} mm. Compare this with the farm’s irrigation plan and root-zone measurements.`); else if(s.eto>crop.etoHigh*rows.length*.65) actions.push(`Evaporative demand is meaningful (cumulative ET₀ ${s.eto.toFixed(2)} mm). Check irrigation uniformity and crop water status before the highest-demand hours.`); else actions.push(`Water-stress indicators are presently limited; keep irrigation aligned with crop stage, soil/root-zone measurements and the farm schedule.`);
  if(topDisease&&!topDisease.abiotic&&topDisease.score>=50) actions.push(`Prioritise scouting for ${topDisease.name}; the weather-suitability score is ${topDisease.score}%. Inspect representative plants and previous problem areas rather than relying on weather alone.`); else actions.push(`No crop-health weather window currently dominates the disease watch; continue routine scouting and record any symptoms for future model calibration.`);
  if(s.maxT>=crop.heatCritical) actions.push(`Prepare for critical heat up to ${s.maxT.toFixed(1)}°C. Check plant water status, exposed fruit/canopy condition and heat-sensitive growth stages during the hottest hours.`); else if(s.maxT>crop.heatOpt[1]) actions.push(`Temperatures rise above the crop’s preferred range to ${s.maxT.toFixed(1)}°C. Inspect for midday heat stress and verify water availability.`); else actions.push(`Forecast temperature remains within or near the crop’s working thermal range; no special heat response is indicated beyond routine observation.`);
  if(s.rain>0||s.maxRH>=crop.humidDisease) actions.push(`Humidity/wetness conditions are relevant (peak RH ${s.maxRH.toFixed(0)}%, forecast rain ${s.rain.toFixed(1)} mm). Inspect canopy ventilation and re-check foliage after wet periods.`); else actions.push(`The forecast remains comparatively dry (peak RH ${s.maxRH.toFixed(0)}%). Give greater attention to heat and water balance than moisture-driven disease conditions.`);
  actions.push(`Re-open the NABAT forecast after a major weather change or within the next 24 hours. Current forecast confidence is ${confidence}%; record field observations so future calibrated models can compare prediction with outcome.`);
  $('farmerActions').innerHTML=actions.slice(0,6).map(a=>`<li>${a}</li>`).join('');
}

function renderAnalytics(rows,crop,confidence){
  const s=summarizeRows(rows,crop);$('statMeanTemp').textContent=`${s.meanT.toFixed(1)}°C`;$('statMaxTemp').textContent=`${s.maxT.toFixed(1)}°C`;$('statRain').textContent=`${s.rain.toFixed(1)} mm`;$('statEto').textContent=`${s.eto.toFixed(2)} mm`;$('statSoil').textContent=Number.isFinite(s.minSM)?s.minSM.toFixed(3):'—';
  const corrs={Temperature:pearson(rows.map(r=>r.t),rows.map(r=>r.risk)),Humidity:pearson(rows.map(r=>r.rh),rows.map(r=>r.risk)),'ET₀':pearson(rows.map(r=>r.eto),rows.map(r=>r.risk)),'Soil moisture':pearson(rows.map(r=>r.sm),rows.map(r=>r.risk)),Wind:pearson(rows.map(r=>r.wind),rows.map(r=>r.risk))};
  const strongest=Object.entries(corrs).filter(([,v])=>Number.isFinite(v)).sort((a,b)=>Math.abs(b[1])-Math.abs(a[1]))[0]||['—',NaN];$('statAssociation').textContent=Number.isFinite(strongest[1])?`${strongest[0]} r=${strongest[1].toFixed(2)}`:'—';
  $('correlationTable').innerHTML=Object.entries(corrs).map(([k,v])=>`<div class="corr-item"><span>${k} vs risk</span><strong>${Number.isFinite(v)?v.toFixed(2):'—'}</strong></div>`).join('');
  $('researchAnalyticsText').textContent=Number.isFinite(strongest[1])?`Across the selected forecast window, ${strongest[0].toLowerCase()} has the strongest linear association with the modeled risk trajectory (Pearson r=${strongest[1].toFixed(2)}). This is an exploratory association within model outputs, not evidence of causality. Forecast confidence is ${confidence}%.`:`The forecast window does not contain enough variable variation for a stable correlation summary. Forecast confidence is ${confidence}%.`;
  $('statAssociation').title='Exploratory Pearson correlation between the hourly variable and modeled risk';
  if(typeof Chart==='undefined'){const note=$('researchAnalyticsText');if(note)note.textContent+=' Interactive chart library is unavailable in this browser session; refresh the page to reload visual analytics.';return;}
  drawClimateChart(rows);drawDailyRiskChart(rows);drawDriverRadar(rows,crop);drawScatter(rows);
}
function pearson(a,b){const pairs=a.map((x,i)=>[x,b[i]]).filter(([x,y])=>Number.isFinite(x)&&Number.isFinite(y));if(pairs.length<3)return NaN;const xs=pairs.map(p=>p[0]),ys=pairs.map(p=>p[1]),mx=mean(xs),my=mean(ys);let num=0,dx=0,dy=0;for(let i=0;i<xs.length;i++){const vx=xs[i]-mx,vy=ys[i]-my;num+=vx*vy;dx+=vx*vx;dy+=vy*vy;}return dx&&dy?num/Math.sqrt(dx*dy):NaN;}
function destroyChart(name){if(charts[name]){charts[name].destroy();charts[name]=null;}}
function sampleRows(rows,max=48){const step=Math.max(1,Math.ceil(rows.length/max));return rows.filter((_,i)=>i%step===0);}
function drawClimateChart(rows){destroyChart('climate');const r=sampleRows(rows,56);charts.climate=new Chart($('climateTrendChart'),{type:'line',data:{labels:r.map(x=>new Date(x.time).toLocaleString([],{weekday:'short',hour:'2-digit'})),datasets:[{label:'Temperature °C',data:r.map(x=>x.t),borderColor:'#b96d2e',backgroundColor:'rgba(185,109,46,.08)',yAxisID:'y',pointRadius:0,tension:.25},{label:'Relative humidity %',data:r.map(x=>x.rh),borderColor:'#527b8b',backgroundColor:'rgba(82,123,139,.08)',yAxisID:'y1',pointRadius:0,tension:.25}]},options:chartOptions({y:{position:'left',title:{display:true,text:'Temperature °C'}},y1:{position:'right',grid:{drawOnChartArea:false},title:{display:true,text:'RH %'}}})});}
function drawDailyRiskChart(rows){destroyChart('daily');const groups={};rows.forEach(r=>{const k=r.time.slice(0,10);(groups[k]??=[]).push(r.risk);});const labels=Object.keys(groups),peak=labels.map(k=>Math.max(...groups[k])),avgRisk=labels.map(k=>mean(groups[k]));charts.daily=new Chart($('dailyRiskChart'),{data:{labels:labels.map(d=>new Date(d+'T12:00:00').toLocaleDateString([],{weekday:'short',day:'numeric'})),datasets:[{type:'bar',label:'Daily peak risk %',data:peak,backgroundColor:peak.map(riskColor),borderWidth:0},{type:'line',label:'Daily mean risk %',data:avgRisk,borderColor:'#285f4c',backgroundColor:'#285f4c',pointRadius:3,tension:.25}]},options:chartOptions({y:{min:0,max:100,title:{display:true,text:'Risk index'}}})});}
function drawDriverRadar(rows,crop){destroyChart('radar');const s=summarizeRows(rows,crop);const heat=clamp(((s.maxT-crop.heatOpt[1])/(Math.max(4,crop.heatCritical-crop.heatOpt[1])))*100,0,100),humidity=clamp(((s.maxRH-(crop.humidDisease-20))/20)*100,0,100),water=Number.isFinite(s.minSM)?clamp(((crop.soilLow-s.minSM)/crop.soilLow)*100+clamp((s.maxEto-crop.etoHigh)*160,0,45),0,100):clamp((s.maxEto-crop.etoHigh)*180,0,100),wetness=clamp((s.rain>0?40+Math.min(45,s.rain*5):0)+(s.maxRH>80?25:0),0,100),wind=clamp((s.maxWind-18)*4,0,100);charts.radar=new Chart($('driverRadarChart'),{type:'radar',data:{labels:['Heat','Humidity','Water deficit','Wetness','Wind'],datasets:[{label:'Relative pressure',data:[heat,humidity,water,wetness,wind],borderColor:'#285f4c',backgroundColor:'rgba(40,95,76,.16)',pointBackgroundColor:'#285f4c',pointRadius:3}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{r:{min:0,max:100,ticks:{display:false},grid:{color:'#dfe6e2'},angleLines:{color:'#dfe6e2'},pointLabels:{font:{size:10},color:'#52645e'}}}}});}
function drawScatter(rows){destroyChart('scatter');const r=sampleRows(rows,80);charts.scatter=new Chart($('riskScatterChart'),{type:'scatter',data:{datasets:[{label:'Forecast hours',data:r.map(x=>({x:x.t,y:x.rh,r:x.risk})),pointBackgroundColor:r.map(x=>riskColor(x.risk)),pointRadius:r.map(x=>3+Math.round(x.risk/35)),pointHoverRadius:7}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>`Temp ${c.raw.x.toFixed(1)}°C • RH ${c.raw.y.toFixed(0)}% • risk ${c.raw.r}%`}}},scales:{x:{title:{display:true,text:'Temperature °C'},grid:{color:'#edf1ee'}},y:{title:{display:true,text:'Relative humidity %'},grid:{color:'#edf1ee'}}}}});}
function chartOptions(scales){return{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},plugins:{legend:{labels:{boxWidth:10,font:{size:10},color:'#52645e'}},tooltip:{titleFont:{size:10},bodyFont:{size:10}}},scales:Object.fromEntries(Object.entries(scales).map(([k,v])=>[k,{grid:{color:'#edf1ee',...(v.grid||{})},ticks:{font:{size:9},color:'#6d7d77'},...v}]))};}
function clamp(v,a,b){return Math.max(a,Math.min(b,v));}

function renderRegion(index){const r=regions[index];$('regionTitle').textContent=r.name;$('regionDescription').textContent=r.desc;$('regionClimate').textContent=r.climate;$('regionStress').textContent=r.stress;$('regionCrops').textContent=r.crops.map(k=>cropProfiles[k].name).join(' • ');}
function renderAllRegions(){$('regionMap').innerHTML=regions.map((r,i)=>`<button class="map-node" style="left:${r.x}%;top:${r.y}%" data-label="${r.name}" onclick="selectRegion(${i})" aria-label="Select ${r.name}"></button>`).join('');$('regionCards').innerHTML=regions.map((r,i)=>`<article class="region-card" onclick="selectRegion(${i})"><strong>${r.name}</strong><span>${r.climate}</span><p>${r.crops.slice(0,5).map(k=>cropProfiles[k].name).join(' • ')}${r.crops.length>5?` • +${r.crops.length-5} more`:''}</p></article>`).join('');}
window.selectRegion=i=>{currentRegion=i;activeCoords=null;$('locationSelect').value=String(i);updateCropOptions();renderRegion(i);updateLocationReadout();document.getElementById('regions').scrollIntoView({behavior:'smooth',block:'start'});loadData();};

async function refreshAuth(){const {data:{user}}=await sb.auth.getUser();$('authLoggedOut').hidden=!!user;$('authLoggedIn').hidden=!user;if(user){$('userEmail').textContent=user.email;await loadFarms();}else{$('farmList').innerHTML='<p class="muted">Sign in to load your registered sites.</p>';$('farmCount').textContent='0 sites';}}
async function signIn(){const email=$('authEmail').value.trim(),password=$('authPassword').value;const {error}=await sb.auth.signInWithPassword({email,password});$('authMessage').textContent=error?error.message:'Signed in successfully.';}
async function signUp(){const email=$('authEmail').value.trim(),password=$('authPassword').value;if(password.length<6){$('authMessage').textContent='Use at least 6 characters for the password.';return;}const {error}=await sb.auth.signUp({email,password});$('authMessage').textContent=error?error.message:'Account created. Check email confirmation if enabled.';}
async function saveFarm(e){e.preventDefault();const {data:{user}}=await sb.auth.getUser();if(!user){$('farmMessage').textContent='Please sign in before saving a site.';return;}const r=regions[+$('farmZone').value],payload={user_id:user.id,name:$('farmName').value.trim(),latitude:r.lat,longitude:r.lon,area_hectares:$('farmArea').value?+$('farmArea').value:null,irrigation_type:$('irrigation').value};const {data:z}=await sb.from('agro_zones').select('id').eq('slug',r.slug).maybeSingle();if(z)payload.zone_id=z.id;const {error}=await sb.from('agro_farms').insert(payload);$('farmMessage').textContent=error?error.message:'Site saved securely.';if(!error){e.target.reset();await loadFarms();}}
async function loadFarms(){const {data,error}=await sb.from('agro_farms').select('id,name,area_hectares,irrigation_type,latitude,longitude,created_at').order('created_at',{ascending:false});if(error){$('farmList').innerHTML=`<p class="muted">${escapeHtml(error.message)}</p>`;return;}$('farmCount').textContent=`${data.length} site${data.length===1?'':'s'}`;$('farmList').innerHTML=data.length?data.map(f=>`<article class="farm-card"><strong>${escapeHtml(f.name)}</strong><span>${f.area_hectares??'—'} ha • ${escapeHtml(f.irrigation_type??'unspecified')}</span><span>${Number(f.latitude).toFixed(3)}°, ${Number(f.longitude).toFixed(3)}°</span></article>`).join(''):'<p class="muted">No registered sites yet.</p>';}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));}

function generateNabatReport(){
  if(!lastRows.length){alert('Run the forecast before exporting a report.');return;}
  if(!window.jspdf||!window.jspdf.jsPDF){alert('PDF engine is not available. Refresh the page and try again.');return;}
  const {jsPDF}=window.jspdf;
  const doc=new jsPDF({unit:'mm',format:'a4',orientation:'portrait'});
  const region=regions[currentRegion],city=getSelectedCity(),crop=cropProfiles[$('cropSelect').value],horizon=+$('horizonSelect').value;
  const s=summarizeRows(lastRows,crop),score=parseInt(($('riskScore').textContent||'0').replace(/\D/g,''),10)||0;
  const confidence=parseInt(($('confidenceScore').textContent||'0').replace(/\D/g,''),10)||0;
  const mode=activeCoords?'Farm GPS':(city?'City':'Regional reference');
  const lat=activeCoords?activeCoords.lat:(city?city.lat:region.lat),lon=activeCoords?activeCoords.lon:(city?city.lon:region.lon);
  const actions=[...document.querySelectorAll('#farmerActions li')].map(x=>x.textContent.trim());
  const corr=[...document.querySelectorAll('#correlationTable .corr-item')].map(x=>x.textContent.replace(/\s+/g,' ').trim());
  const generated=new Date();
  const green=[39,93,75],dark=[23,50,43],muted=[95,112,105],line=[217,225,221],soft=[246,248,246],gold=[168,124,43];

  const pageW=210,margin=17,contentW=176;
  let y=18,page=1;
  function header(first=false){
    if(!first){doc.addPage();page++;y=18;}
    doc.setFillColor(...green);doc.rect(0,0,5,297,'F');
    doc.setTextColor(...green);doc.setFont('helvetica','bold');doc.setFontSize(17);doc.text('NABAT',margin,17);
    doc.setFontSize(8.5);doc.setFont('helvetica','normal');doc.setTextColor(...muted);doc.text('Saudi AgroClimate & Crop Health Intelligence',margin,22);
    doc.setDrawColor(...line);doc.line(margin,27,pageW-margin,27);y=34;
  }
  function footer(){
    const total=doc.getNumberOfPages();
    for(let p=1;p<=total;p++){
      doc.setPage(p);doc.setDrawColor(...line);doc.line(margin,284,pageW-margin,284);
      doc.setTextColor(...muted);doc.setFontSize(7.5);doc.setFont('helvetica','normal');
      doc.text('NABAT Intelligence Report • GDR Network Bio-IT',margin,289);
      doc.text('Page '+p+' of '+total,pageW-margin,289,{align:'right'});
    }
  }
  function ensure(h){if(y+h>277) header(false);}
  function title(txt,sub){
    ensure(22);doc.setTextColor(...dark);doc.setFont('helvetica','bold');doc.setFontSize(18);doc.text(txt,margin,y);y+=7;
    if(sub){doc.setFont('helvetica','normal');doc.setFontSize(9);doc.setTextColor(...muted);const ls=doc.splitTextToSize(sub,contentW);doc.text(ls,margin,y);y+=ls.length*4.2+3;}
  }
  function sec(txt){
    ensure(12);doc.setFillColor(...soft);doc.rect(margin,y-4,contentW,8,'F');doc.setTextColor(...green);doc.setFont('helvetica','bold');doc.setFontSize(9);doc.text(txt.toUpperCase(),margin+2,y+1);y+=10;
  }
  function para(txt,size=9,color=dark){
    const lines=doc.splitTextToSize(txt,contentW);ensure(lines.length*4.5+3);doc.setFont('helvetica','normal');doc.setFontSize(size);doc.setTextColor(...color);doc.text(lines,margin,y);y+=lines.length*4.5+3;
  }
  function keyval(label,value,x,w){
    doc.setFont('helvetica','normal');doc.setFontSize(7.5);doc.setTextColor(...muted);doc.text(label,x,y);
    doc.setFont('helvetica','bold');doc.setFontSize(11);doc.setTextColor(...dark);doc.text(String(value),x,y+5.2);
  }
  function bullet(txt){
    const lines=doc.splitTextToSize(txt,contentW-7);ensure(lines.length*4.3+4);doc.setFillColor(...green);doc.circle(margin+1.5,y-1,1.1,'F');doc.setFont('helvetica','normal');doc.setFontSize(8.8);doc.setTextColor(...dark);doc.text(lines,margin+6,y);y+=lines.length*4.3+3;
  }
  function chart(canvasId,caption,w=176,h=68){
    const cv=$(canvasId);if(!cv)return;
    ensure(h+14);try{
      const img=cv.toDataURL('image/png',1.0);doc.addImage(img,'PNG',margin,y,w,h);
      y+=h+4;doc.setFont('helvetica','italic');doc.setFontSize(7.5);doc.setTextColor(...muted);doc.text(caption,margin,y);y+=7;
    }catch(e){}
  }

  header(true);
  doc.setFillColor(...soft);doc.roundedRect(margin,34,contentW,45,2,2,'F');
  doc.setTextColor(...dark);doc.setFont('helvetica','bold');doc.setFontSize(21);doc.text('Intelligence Report',margin+7,47);
  doc.setFontSize(12);doc.text(crop.name+' • '+(city?city.name+' / ':'')+region.name,margin+7,56);
  doc.setFont('helvetica','normal');doc.setFontSize(8.5);doc.setTextColor(...muted);
  doc.text(mode+' • '+lat.toFixed(5)+', '+lon.toFixed(5)+' • '+horizon+' h',margin+7,64);
  doc.text('Generated '+generated.toLocaleString(),margin+7,71);
  y=88;

  sec('Decision snapshot');
  ensure(26);
  const xs=[margin,margin+45,margin+89,margin+133];
  keyval('Risk',score+'%',xs[0],40);keyval('Confidence',confidence+'%',xs[1],40);
  keyval('Peak temperature',s.maxT.toFixed(1)+' °C',xs[2],40);keyval('Rainfall',s.rain.toFixed(1)+' mm',xs[3],40);y+=14;
  const level=riskLevel(score);
  para('Priority: '+level+'. '+($('decisionHeadline').textContent||'').replace(/^.*?•\s*/,'')+'. Peak risk: '+$('peakTiming').textContent+'.');
  
  sec('Farmer brief');
  actions.forEach(bullet);

  sec('Research summary');
  para($('researchAnalyticsText').textContent||'');
  ensure(24);
  const statItems=[
    ['Mean temp',s.meanT.toFixed(1)+' °C'],['Max RH',s.maxRH.toFixed(0)+'%'],['ET₀',s.eto.toFixed(2)+' mm'],
    ['Min soil moisture',Number.isFinite(s.minSM)?s.minSM.toFixed(3):'NA'],['Max wind',s.maxWind.toFixed(1)+' km/h'],['Risk',score+'%']
  ];
  statItems.forEach((kv,i)=>{const col=i%3,row=Math.floor(i/3);const x=margin+col*59;const yy=y+row*12;doc.setFontSize(7);doc.setTextColor(...muted);doc.text(kv[0],x,yy);doc.setFontSize(10);doc.setFont('helvetica','bold');doc.setTextColor(...dark);doc.text(kv[1],x,yy+4.5);doc.setFont('helvetica','normal');});
  y+=28;
  if(corr.length){doc.setFontSize(8);doc.setTextColor(...muted);doc.text('Exploratory Pearson associations',margin,y);y+=5;corr.forEach(x=>bullet(x));}

  sec('Surveillance');
  lastDiseaseScores.slice(0,6).forEach(d=>bullet(d.name+': '+d.score+'% environmental suitability ('+riskLevel(d.score)+'). '+d.note));

  header(false);
  title('Scientific Analytics','Graphical exploration generated from the same hourly forecast inputs used by the decision engine.');
  chart('climateTrendChart','Figure 1. Hourly temperature and relative-humidity trajectory.');
  chart('dailyRiskChart','Figure 2. Daily mean and peak modeled crop-health risk.');
  chart('driverRadarChart','Figure 3. Standardized environmental driver profile.');
  chart('riskScatterChart','Figure 4. Temperature-humidity-risk exploration; each point represents a forecast hour.');

  sec('Methods');
  para('NABAT v0.5 computes an interpretable environmental decision index from hourly temperature, relative humidity, precipitation, wind speed, FAO reference evapotranspiration (ET₀) and surface soil moisture. Crop-specific thermal, moisture and disease-favourable windows contribute to separate biotic-suitability and abiotic-stress components. The combined index is a decision-priority indicator, not a disease diagnosis or prevalence estimate.');
  para('Operational weather source in the public MVP: Open-Meteo forecast API. Production architecture is designed for server-side Saudi NCM observations, forecasts, leaf-wetness, growing-degree-day and gridded products when authorized credentials are available. Remote-sensing integration is planned through Sentinel-2 field-polygon time series.');

  sec('Secondary research use');
  para('The exported statistics, graphs and forecast-derived associations can be used as descriptive or exploratory secondary data when the report date, coordinates, crop profile, forecast horizon, NABAT version and data source are stated. Pearson correlations shown here describe association within the modelled forecast window and must not be interpreted as causal effects. Disease-suitability scores require field-confirmed labels and independent spatial/temporal validation before they can be reported as predictive probabilities.');
  
  sec('Evidence');
  para('Operational decisions should combine forecast evidence, direct crop observation and locally approved agronomic practice. The system is intended to prioritize observation and decision timing; treatment selection is outside the current model scope.',8.5,[92,76,42]);

  sec('Provenance');
  para('Platform: NABAT — Saudi AgroClimate & Crop Health Intelligence. Development: GDR Network Bio-IT. Individual developer/inventor names will be inserted after final spelling and authorship confirmation. Report generated from the live NABAT client-side decision workspace.');
  footer();
  const safe=(crop.name+'_'+(city?city.name+'_':'')+region.name).replace(/[^A-Za-z0-9]+/g,'_');
  doc.save('NABAT_'+safe+'_'+generated.toISOString().slice(0,10)+'.pdf');
}

document.addEventListener('DOMContentLoaded',init);