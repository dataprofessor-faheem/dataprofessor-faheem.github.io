# Saudi AgroClimate Intelligence & Crop Health DSS

Founding MVP for a Saudi Arabia agricultural climate and crop-health decision-support system under the GDR Network.

## Live MVP

The public dashboard is served from GitHub Pages at `/saudi-agroclimate/`.

## Current MVP capabilities

- Live weather and 7-day forecast retrieval for selected Saudi agricultural locations.
- Current temperature, relative humidity, precipitation, wind, reference ET0 and upper-layer soil moisture.
- Date palm, wheat, potato and tomato/protected-crop profiles.
- Transparent biotic-risk and abiotic-stress scoring.
- Hourly early-warning visualization for 24 h, 72 h or 7 days.
- Initial Saudi agro-climatic location profiles for Al-Qassim, Riyadh, Al-Ahsa, Madinah, Jazan, Asir, Tabuk and Al-Jouf.
- Mobile-responsive farmer/research dashboard.

## Data architecture

### Production primary source
Saudi National Center for Meteorology (NCM) Weather API. NCM provides historical, current, forecast, station and gridded meteorological data. Agriculture-relevant variables include evapotranspiration, growing-degree days and leaf wetness. NCM credentials must never be committed to this public repository; production integration should use a server-side proxy/Edge Function.

### Public MVP weather source
The browser MVP uses Open-Meteo forecast data so that a public demonstration can operate without exposing credentials. This is a bootstrap source, not a substitute for NCM in the validated Saudi production system.

### Planned sources
- Saudi NCM observations and forecasts
- MEWA / GASTAT crop and production datasets where licensed/available
- Sentinel-2 / Landsat vegetation indices
- ERA5 / ERA5-Land historical climate
- CMIP6 climate projections
- Soil layers and farm IoT sensors
- Field disease/pest confirmations

## Production modules

1. Weather ingestion
2. Saudi agro-climatic zoning
3. Crop registry
4. Disease/pest knowledge base
5. Farm/field registry
6. Field observation and diagnostic labels
7. Biotic prediction engine
8. Abiotic stress engine
9. Remote-sensing pipeline
10. Alert and recommendation service
11. Research/admin national dashboard
12. Farmer/mobile interface
13. Climate-change suitability module (2030–2050)

## Security

Do not store NCM usernames/passwords, service keys or Supabase service-role secrets in frontend JavaScript. Use server-side environment secrets and Row Level Security for farm/user records.

## Scientific status

The current risk score is a transparent demonstration model for software validation. It represents environmental suitability/stress and must not be interpreted as a confirmed diagnosis. Disease-specific models require pathogen-specific thresholds, crop phenology, historical disease labels and independent spatial/temporal validation before operational agricultural use.
