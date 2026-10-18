-- NABAT reference-data sync for GDR Production Supabase
-- Safe idempotent seed; intended for execution when database connectivity is available.

insert into public.agro_zones (slug,name,region,latitude,longitude,description,primary_stress) values
('riyadh','Riyadh','Riyadh',24.7136,46.6753,'Central hyper-arid plateau and irrigated agriculture.','Extreme heat, evapotranspiration, water deficit'),
('makkah','Makkah','Makkah',21.2854,40.4158,'Western coastal-to-highland agricultural gradient including Taif.','Heat, water availability, highland variability'),
('madinah','Madinah','Madinah',24.5247,39.5692,'Western inland oasis agriculture.','Heat, drought, irrigation demand'),
('qassim','Al-Qassim','Al-Qassim',26.3592,43.9818,'Central-northern irrigated arid agriculture.','Heat, water deficit, protected-crop humidity'),
('eastern','Eastern Province','Eastern Province',25.3830,49.5860,'Gulf-influenced oasis and coastal agriculture including Al-Ahsa.','Heat, humidity, salinity, water quality'),
('asir','Asir','Asir',18.2164,42.5053,'Southwestern highland agriculture.','Rain variability, humidity, erosion'),
('tabuk','Tabuk','Tabuk',28.3838,36.5550,'Northern arid agriculture with cool winters.','Cold-heat variability, drought, wind'),
('hail','Hail','Hail',27.5114,41.7208,'Northern-central continental arid agriculture.','Temperature extremes, drought, wind'),
('northern-borders','Northern Borders','Northern Borders',30.9753,41.0381,'Northern desert agriculture with strong seasonal temperature range.','Frost, drought, wind, heat'),
('jazan','Jazan','Jazan',16.8892,42.5511,'Southwestern Tihamah coastal and mountain agriculture.','Humidity, heat, intense rainfall'),
('najran','Najran','Najran',17.5656,44.2289,'Southern interior valley agriculture.','Heat, water deficit, dust'),
('al-bahah','Al-Bahah','Al-Bahah',20.0129,41.4677,'Southwestern highland agriculture with milder wetter conditions.','Rainfall variability, humidity, slope'),
('al-jouf','Al-Jouf','Al-Jouf',29.9697,40.2064,'Northern interior agriculture with Mediterranean winter influence.','Drought, frost-heat range, irrigation demand')
on conflict (slug) do update set name=excluded.name,region=excluded.region,latitude=excluded.latitude,longitude=excluded.longitude,description=excluded.description,primary_stress=excluded.primary_stress;

insert into public.agro_crops (slug,common_name,scientific_name,notes) values
('date-palm','Date palm','Phoenix dactylifera','Major Saudi perennial fruit crop'),
('wheat','Wheat','Triticum aestivum','Cool-season cereal'),('barley','Barley','Hordeum vulgare','Cool-season cereal and feed crop'),
('alfalfa','Alfalfa','Medicago sativa','Forage crop'),('tomato','Tomato','Solanum lycopersicum','Open-field and protected horticulture'),
('cucumber','Cucumber','Cucumis sativus','Open-field and protected horticulture'),('potato','Potato','Solanum tuberosum','Cool-season vegetable crop'),
('onion','Onion','Allium cepa','Vegetable crop'),('citrus','Citrus','Citrus spp.','Fruit crop group'),('grape','Grape','Vitis vinifera','Fruit crop'),
('olive','Olive','Olea europaea','Fruit and oil crop'),('mango','Mango','Mangifera indica','Tropical/subtropical fruit'),
('banana','Banana','Musa spp.','Tropical fruit'),('coffee','Arabian coffee','Coffea arabica','Highland specialty crop'),
('pomegranate','Pomegranate','Punica granatum','Fruit crop'),('fig','Fig','Ficus carica','Fruit crop'),('apple','Apple','Malus domestica','Temperate fruit crop'),
('watermelon','Watermelon','Citrullus lanatus','Warm-season cucurbit'),('maize','Maize / sorghum','Zea mays / Sorghum bicolor','Warm-season cereal group'),
('sesame','Sesame','Sesamum indicum','Oilseed crop')
on conflict (slug) do update set common_name=excluded.common_name,scientific_name=excluded.scientific_name,notes=excluded.notes;
