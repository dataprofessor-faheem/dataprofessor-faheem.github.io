# NABAT True Intelligence Layer

## Objective

Move NABAT from a transparent crop-weather baseline DSS to a validated Saudi agricultural intelligence platform that integrates official meteorology, Earth observation, crop phenology and field-confirmed outcomes.

## 1. Location layer

Two operating modes are supported:

- **Farm GPS**: device latitude/longitude is used for the weather query when the user is physically within the Saudi operating extent.
- **Regional reference**: one of the 13 administrative-region reference coordinates is used when GPS is not supplied.

The crop catalogue remains linked to the nearest Saudi regional agricultural profile.

## 2. Saudi NCM production connector

NCM is the intended primary operational meteorological source. Credentials must be stored only in a secure server/Edge Function.

Recommended parameters:

- `t_2m:C`
- `relative_humidity_2m:p`
- precipitation / rainfall accumulations
- `wind_speed_10m:ms`
- `evapotranspiration_1h:mm`
- `growing_degree_days_accumulated:gdd`
- `leaf_wetness:idx`
- `soil_moisture_index_-5cm:idx`
- `soil_moisture_index_-15cm:idx`
- `volumetric_soil_water_-5cm:m3m3`
- soil temperatures where crop models require them

NCM supports time-series, station and gridded data. The production connector should request a token server-side or use secure basic authentication according to the account configuration.

## 3. Sentinel-2 / Copernicus layer

Use field polygons rather than a single point wherever farm boundaries are available.

Recommended features:

- NDVI – vegetation greenness / vigor
- NDRE or red-edge vegetation condition
- NDWI / moisture-sensitive indicators
- canopy anomaly relative to the field's own recent history
- temporal change rate
- cloud-screened field median / quantiles
- optional LAI / chlorophyll products where suitable

Copernicus Data Space Sentinel Hub / openEO / Statistical APIs should be called from the server layer where authentication is required.

## 4. Crop phenology layer

Add to every field observation:

- crop and cultivar
- planting / transplanting date
- current growth stage
- flowering / fruiting status where relevant
- irrigation method
- previous crop
- key management events

Phenology should modify disease and abiotic-risk thresholds rather than being displayed as a passive label.

## 5. Field-confirmed biological outcomes

The model-training dataset must distinguish:

- no disease observed
- suspected disease
- expert-confirmed disease
- laboratory-confirmed disease where applicable
- pest trap counts / field counts
- symptom severity
- spatial extent
- observation date/time

Environmental suitability must not be treated as the disease label.

## 6. Calibration and validation

Recommended evaluation design:

1. Train only on past seasons / farms.
2. Keep complete farms or regions out of model development for spatial external validation.
3. Keep a later season/year out for temporal validation.
4. Report AUROC and AUPRC for discrimination where appropriate.
5. Report calibration curve, calibration slope/intercept and Brier score for probability models.
6. Evaluate decision thresholds in terms of false alerts, missed events and scouting workload.
7. Compare the calibrated model against the transparent rule-based NABAT baseline.

## 7. National GIS risk mapping

Only validated crop-specific models should be promoted to national mapping.

Pipeline:

NCM gridded forecast + crop distribution + Sentinel crop condition + soil / terrain + calibrated crop-health model -> gridded probability / stress surface -> regional summaries -> national dashboard.

Every map layer should retain:

- forecast timestamp
- model version
- input-data versions
- spatial resolution
- confidence / uncertainty
- crop
- growth stage assumptions

## 8. Farmer decision brief

The live application converts the same hourly variables used by the model into six direct actions:

1. field-inspection priority and timing
2. irrigation / water-status review
3. disease or pest scouting priority
4. heat-stress response
5. humidity / wetness follow-up
6. next forecast review and field-recording action

The brief is therefore traceable to the analytical plots and not generated independently from them.

## 9. Research analytics

Current analytics include:

- hourly temperature and humidity trajectories
- daily mean and peak risk
- standardized environmental-driver radar
- temperature × humidity scatter with risk encoded by point size/color
- summary statistics
- exploratory Pearson correlations between modeled hourly risk and climate variables

These correlations describe association inside the modeled forecast window; they are not causal estimates.

## 10. Governance

Production deployment should maintain:

- server-side secrets
- role-based access
- row-level security for farm observations
- provenance for all official and satellite data
- versioned models
- audit trail for predictions used in studies
- bilingual Arabic/English user communication
- Saudi-approved agronomic guidance for treatment recommendations

© 2026 GDR Network & Saudi DSS — NABAT