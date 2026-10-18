# NABAT — Saudi AgroClimate & Crop Health Intelligence

NABAT is a GDR Network research-technology platform for climate-aware crop-health decision support in the Kingdom of Saudi Arabia.

## Live application

GitHub Pages: `/saudi-agroclimate/`

## Product identity

**NABAT**  
*Saudi AgroClimate & Crop Health Intelligence*

The platform is designed for two complementary users:

- **Farmers:** interpretable risk level, peak-risk timing, dominant drivers and practical monitoring actions.
- **Researchers:** transparent variables, crop thresholds, biotic/abiotic components, confidence and methodological limitations.

## National coverage

The interface covers all 13 Saudi administrative regions:

1. Riyadh
2. Makkah
3. Madinah
4. Al-Qassim
5. Eastern Province
6. Asir
7. Tabuk
8. Hail
9. Northern Borders
10. Jazan
11. Najran
12. Al-Bahah
13. Al-Jouf

Representative regional crop profiles include date palm, wheat, barley, alfalfa, tomato, cucumber, potato, onion, citrus, grape, olive, mango, banana, Arabian coffee, pomegranate, fig, apple, watermelon, maize/sorghum and sesame. Crop lists are intended as an extensible research reference rather than an exhaustive legal crop census.

## Forecast system

NABAT currently generates decision-support outputs for:

- current meteorological conditions
- next 24 hours
- next 72 hours
- next 7 days

Variables currently consumed by the public MVP:

- 2 m air temperature
- relative humidity
- precipitation
- 10 m wind speed
- FAO reference evapotranspiration (ET0)
- surface soil moisture

The system computes:

- crop-specific biotic environmental suitability
- crop-specific abiotic stress
- combined crop-health index
- forecast confidence
- peak-risk timing
- risk trend
- dominant environmental drivers
- farmer-facing action summary
- researcher-facing interpretation

## Risk interpretation

- **0–24:** Low — routine monitoring.
- **25–49:** Moderate — increase observation.
- **50–74:** High — prioritise field scouting and management review.
- **75–100:** Critical — rapid field assessment and expert agronomic review advised.

These values are not disease prevalence, infection probability, yield loss estimates or treatment recommendations.

## Scientific safeguards

The current engine is an interpretable rule-based prototype. It deliberately avoids presenting itself as a clinically or agriculturally validated machine-learning diagnostic system.

Before operational deployment, disease- and pest-specific models require:

- field-confirmed labels
- crop growth stage
- cultivar information
- local management history
- leaf-wetness or microclimate data
- independent temporal validation
- independent spatial/farm validation
- calibration and uncertainty analysis

## Data architecture

### Intended Saudi primary source

Saudi National Center for Meteorology (NCM) observations, forecasts, station data and agricultural meteorological parameters. NCM credentials must remain server-side.

### Public MVP source

The browser demonstration currently uses Open-Meteo for operational weather retrieval without exposing private credentials.

### Planned supporting layers

- Saudi NCM
- MEWA / GASTAT crop and production data
- Sentinel-2 / Landsat
- ERA5 / ERA5-Land
- CMIP6 future-climate ensembles
- soil datasets
- IoT farm sensors
- field disease and pest observations

## Backend

The project uses the existing GDR Production Supabase backend for:

- authenticated user accounts
- farms / monitoring sites
- field observations
- risk-run records
- reference zones and crops

Row Level Security protects owner-specific farm data. Public frontend code uses only the Supabase publishable key. Service-role credentials must never be committed.

## UI design principles

The current interface uses an institutional scholarly style: light surfaces, editorial hierarchy, restrained typography, formal navigation, persistent research context and accessibility-conscious contrast. It takes general inspiration from professional academic publishing conventions without copying Oxford University Press branding, templates or protected design assets.

## Development credits

GDR Network Bio-IT  
Dr. Muhammad Fahim Khan  
Dr. Saeed

© 2026 GDR Network & Saudi DSS. All rights reserved.

## Current limitation

NABAT is a research and decision-support prototype. Environmental suitability does not equal confirmed crop disease, pest infestation or regulatory treatment need. Farmers should use field scouting and locally approved Saudi agronomic recommendations before intervention.
