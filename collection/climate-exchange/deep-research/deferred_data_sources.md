# Deferred Data Sources — Research Findings

> Research date: 2026-02-22 | Context: CIE Solomon Islands demo

---

## DL-4: Pacific Fisheries Data Access

### 1. SPC FAME — Oceanic Fisheries Programme

| Field | Value |
|-------|-------|
| **Portal** | https://fame.spc.int/ |
| **Data systems** | https://fame.spc.int/fisheries-data/database-systems-and-access |
| **Key system** | TUFMAN 2 (Tuna Fisheries Data Management) — cloud-hosted web database |
| **Query tool** | Catch and Effort Query System (CES) — operational logsheet summaries, aggregate public-domain catch/effort, annual catch estimates |
| **Auth** | Yes — registered users only; guest users get limited non-confidential resources (generic references, conversion factors) |
| **Granularity** | Operational logsheet level (vessel/set/haul) for members; aggregate 5x5 degree grid for public domain |
| **Temporal** | 1950s–present (varies by dataset) |
| **API** | No public REST API found. Data access via CES web interface or bulk download requests to SPC |
| **SLB query** | Register on TUFMAN 2; request Solomon Islands logsheet data or use CES aggregate extracts |
| **Notes** | Pacific Data Hub (pacificdata.org) is CKAN-based and hosts some SPC fisheries datasets; CKAN API at `pacificdata.org/data/api/3/` may allow programmatic access to catalogue metadata |

### 2. FFA — Forum Fisheries Agency

| Field | Value |
|-------|-------|
| **Portal** | https://www.ffa.int/ |
| **Data system** | TUFMAN 2 (same system as SPC — FFA members use SPC-managed TUFMAN 2) |
| **Reports** | T2 Reports — secured online reporting integrated into TUFMAN 2 |
| **Auth** | Yes — member country access only; no public API |
| **Granularity** | National-level summaries publicly; vessel-level restricted to members |
| **Temporal** | Ongoing |
| **API** | None public. FFA provides data services to member countries through SPC's data management infrastructure |
| **SLB query** | Solomon Islands is an FFA member (HQ is in Honiara) — SLB government can access directly |
| **Public data** | WCPFC-CA Tuna Fisheries reports (annual catch value estimates) available at https://www.ffa.int/download/wcpfc-area-catch-value-estimates/ |

### 3. FAO FishStatJ / FIRMS

| Field | Value |
|-------|-------|
| **Portal** | https://www.fao.org/fishery/en/statistics/software/fishstatj |
| **FIRMS** | https://firms.fao.org/ |
| **Query tool** | https://www.fao.org/fishery/statistics-query/en/global_production/global_production_quantity |
| **Auth** | No — public access, no registration required for aggregate data |
| **Granularity** | National level (country x species x FAO area x year) |
| **Temporal** | 1950–2023 (March 2025 release); next update March 2026 for 1950–2024 |
| **API** | No dedicated REST API with JSON endpoints found. Desktop app (FishStatJ) for bulk access. R package `fishstat` (CRAN) provides programmatic access |
| **SLB query** | Use FishStatJ desktop app or FAO query tool: select country = Solomon Islands, production type = Capture, all species |
| **Data** | Global capture production, aquaculture production, trade flows |
| **Notes** | FAO also has a Solomon Islands country fisheries profile: https://www.fao.org/fishery/docs/DOCUMENT/fcp/en/FI_CP_SB.pdf |

### 4. Global Fishing Watch (GFW)

| Field | Value |
|-------|-------|
| **Portal** | https://globalfishingwatch.org/our-apis/ |
| **API docs** | https://globalfishingwatch.org/our-apis/documentation |
| **Python client** | https://github.com/GlobalFishingWatch/gfw-api-python-client |
| **R client** | https://globalfishingwatch.github.io/gfwr/ |
| **Auth** | Yes — API token required (free registration) |
| **Granularity** | 0.01 degree grid cells (AIS-derived) |
| **Temporal** | 2012–present (~5 days lag) |
| **API endpoints** | Vessels API (search/identity), Events API (encounters, loitering, port visits, fishing events), 4Wings API (fishing effort, vessel presence, SAR detections), Insights API (risk indicators) |
| **Catch/CPUE data** | **NO** — GFW provides *apparent fishing effort* (hours) derived from AIS vessel tracking and behavior classification, NOT catch or CPUE data |
| **SLB query** | Filter by Solomon Islands EEZ geometry; returns fishing effort hours by gear type |
| **CIE status** | Already have GFW connectors (`gfw_fishing_effort`, `gfw_vessel_events`) — these cover vessel activity, not catch |

### 5. OpenFisheries.org

| Field | Value |
|-------|-------|
| **Portal** | https://www.openfisheries.org/ |
| **API** | `http://openfisheries.org/api/landings.json` (global), `http://openfisheries.org/api/landings/{ISO3}.json` (per country) |
| **GitHub** | https://github.com/andrewjdyck/api.openfisheries.org |
| **Auth** | No — fully open, no registration |
| **Granularity** | National level (country x year total landings) |
| **Temporal** | 1950–~2018 (sourced from FAO; may lag several years) |
| **API format** | JSON |
| **SLB query** | `GET http://openfisheries.org/api/landings/SLB.json` |
| **Notes** | Very simple API; data is a subset of FAO FishStatJ. Good for quick national totals but no species breakdown, no sub-national, no gear type. Project appears semi-maintained |

### 6. Pacific Data Hub (CKAN)

| Field | Value |
|-------|-------|
| **Portal** | https://pacificdata.org/data/dataset/?member_countries=sb&topic=Fisheries |
| **Platform** | CKAN + Drupal (AWS-hosted) |
| **API** | Standard CKAN API v3: `https://pacificdata.org/data/api/3/action/package_search?q=fisheries&fq=member_countries:sb` |
| **Auth** | No — public CKAN API for metadata; individual datasets may have access restrictions |
| **Granularity** | Varies by dataset — mostly reports and publications, some tabular data |
| **SLB query** | Filter by member_countries=sb and topic=Fisheries |
| **Notes** | Primarily a metadata catalogue; actual fisheries catch data lives in TUFMAN 2 (restricted) |

### Fisheries Data Summary

| Source | Has API? | Auth? | Catch Data? | Granularity | Best For |
|--------|----------|-------|-------------|-------------|----------|
| SPC TUFMAN 2 | No (web UI) | Yes (members) | Yes | Logsheet/5x5 grid | Detailed Pacific tuna catch (restricted) |
| FFA | No | Yes (members) | Via TUFMAN 2 | National/vessel | Same as SPC |
| FAO FishStatJ | No REST; R pkg | No | Yes | National x species | Historical national catch time series |
| GFW | Yes (REST) | Yes (token) | **No** (effort only) | 0.01 deg grid | Fishing effort, vessel tracking |
| OpenFisheries | Yes (REST) | No | Yes (FAO subset) | National total | Quick national landings check |
| Pacific Data Hub | Yes (CKAN) | No | Metadata only | Varies | Dataset discovery |

**Recommendation for CIE**: OpenFisheries API is the quickest to integrate (simple JSON, no auth) for national-level catch trends. FAO query tool / R package for species-level breakdown. GFW already integrated for effort data. For detailed Pacific tuna data, would need SPC/FFA member access (government partnership).

---

## DL-6: Sub-National Health Data for Solomon Islands

### 1. DHS Program — Demographic and Health Surveys

| Field | Value |
|-------|-------|
| **Portal** | https://dhsprogram.com/ |
| **API** | https://api.dhsprogram.com/ — REST API for indicator-level data |
| **Surveys conducted** | 2006–2007 (pilot, ADB/SPC funded), 2015 (full, DFAT/UNICEF funded) |
| **Auth** | Registration required for microdata; API for aggregate indicators is open |
| **Geographic granularity** | **Provincial level** in published reports; GPS cluster data available in microdata (requires registration + approval) |
| **Key indicators** | Fertility, family planning, child mortality, adult/maternal mortality, nutritional status (stunting, wasting, underweight), maternal/child health services, HIV/AIDS knowledge |
| **DHS 2015 sample** | 6,266 women (15–49), 3,591 men (15–54) — nationally representative |
| **Access** | Register at https://dhsprogram.com/data/new-user-registration.cfm; approval typically 24–48 hours; access granted per country (all SLB surveys) |
| **Data format** | Microdata: Stata/SPSS/CSV; API: JSON |
| **SLB API query** | `https://api.dhsprogram.com/rest/dhs/data?countryIds=SB&indicatorIds=CN_NUTS_C_HA2` (stunting) |

### 2. UNICEF MICS — Multiple Indicator Cluster Survey

| Field | Value |
|-------|-------|
| **Portal** | https://mics.unicef.org/ |
| **Survey list** | https://mics.unicef.org/surveys |
| **SLB status** | **No MICS completed yet** — first-ever MICS planned for 2026 (in progress) |
| **Partners** | SINSO + UNICEF Pacific |
| **Expected coverage** | ~40 SDG indicators; data on children, women, education, WASH, nutrition, child protection |
| **Geographic granularity** | Expected to be provincial level (TBD — survey in design phase) |
| **Notes** | Solomon Islands is one of 14 Pacific countries in the regional MICS initiative. Results not yet available |
| **URL** | https://statistics.gov.sb/donors-and-partners-roundtabe-for-first-ever-multi-indicator-cluster-survey-mics-in-solomon-islands/ |

### 3. WHO STEPS Survey — NCD Risk Factors

| Field | Value |
|-------|-------|
| **Portal** | https://www.who.int/teams/noncommunicable-diseases/surveillance/data/solomon-islands |
| **Surveys conducted** | 2005–2006 (first), 2014–2015 (second, nationally representative) |
| **Reports** | 2006: https://cdn.who.int/media/docs/default-source/ncds/ncd-surveillance/data-reporting/solomon-islands/steps/2006-solomon-islands-steps-report.pdf |
| | 2015: https://cdn.who.int/media/docs/default-source/ncds/ncd-surveillance/data-reporting/solomon-islands/solomon_islands_steps_survey_final_2015.pdf |
| **Auth** | Reports freely accessible; microdata requires WHO application |
| **Geographic granularity** | **National level only** (STEPS surveys are designed for national estimates) |
| **Key indicators** | Tobacco use, alcohol, diet (fruit/veg, salt, sugar), physical activity, BMI, blood pressure, blood glucose, cholesterol |
| **Key findings (2015)** | 46.6% add salt before eating; 18.6% insufficient physical activity; 87.4% <5 servings fruit/veg daily; hypercholesterolaemia increasing |
| **Data format** | PDF reports; microdata via WHO NCD portal |

### 4. SPC Statistics for Development Division (SDD)

| Field | Value |
|-------|-------|
| **Portal** | https://sdd.spc.int/sb |
| **Data explorer** | https://stats.pacificdata.org/ (Pacific Data Hub .Stat) |
| **Auth** | No — public access |
| **Geographic granularity** | Mostly **national level**; some indicators at provincial level from census data |
| **Key health indicators** | Stunting (29.8% under-5, 2022), overweight (5.5% under-5, 2022), COVID-19 case counts, civil registration completeness |
| **DHS 2015 hosted** | https://sdd.spc.int/digital_library/solomon-islands-demographic-and-health-survey-dhs-2015 |
| **API** | Pacific Data Hub .Stat uses SDMX REST API: `https://stats.pacificdata.org/rest/data/{dataflow}/{key}` |
| **SLB query** | `https://stats.pacificdata.org/rest/data/SPC,DF_SDG,3.0/..SB..?format=csv` |
| **Notes** | Best source for standardized Pacific health indicators with API access |

### 5. Solomon Islands National Statistics Office (SINSO)

| Field | Value |
|-------|-------|
| **Portal** | https://statistics.gov.sb/ |
| **Auth** | No — public access to publications |
| **Geographic granularity** | **Provincial level** available in census and DHS reports; community-level data not publicly released |
| **Key publications** | DHS 2015, Census 2019, HIES (Household Income/Expenditure Survey) |
| **API** | None — publication downloads only (PDF/Excel) |
| **Data** | Demographics, health, education, WASH, economic indicators |
| **Notes** | Primary statistical authority; publications available but no programmatic data access. MICS 2026 in planning |

### 6. HDX — Humanitarian Data Exchange

| Field | Value |
|-------|-------|
| **Portal** | https://data.humdata.org/group/slb |
| **Health dataset** | https://data.humdata.org/dataset/who-data-for-solomon-islands |
| **Auth** | No — fully open |
| **Geographic granularity** | **National level** (WHO-sourced indicators) |
| **Key indicators** | Nutrition (hemoglobin, low birth weight, underweight/overweight prevalence), maternal/newborn health, child mortality, immunization, malaria, NCDs, TB, health workforce |
| **API** | CKAN API: `https://data.humdata.org/api/3/action/package_show?id=who-data-for-solomon-islands` |
| **Data format** | CSV downloads; CKAN API returns JSON metadata |
| **Other SLB datasets** | World Bank combined indicators, food prices (FAOSTAT), population estimates |
| **Notes** | Good aggregation point; data is WHO/World Bank sourced (same as going to source directly) |

### Health Data Summary

| Source | API? | Auth? | Sub-national? | Most Recent | Best For |
|--------|------|-------|---------------|-------------|----------|
| DHS 2015 | Yes (REST) | Registration | Provincial + GPS clusters | 2015 | Nutrition, mortality, MCH — richest sub-national |
| UNICEF MICS | N/A | N/A | Expected provincial | **2026 (in progress)** | Future — not available yet |
| WHO STEPS | No (PDF) | WHO for microdata | National only | 2015 | NCD risk factors |
| SPC SDD / .Stat | Yes (SDMX) | No | Mostly national | 2022 | Standardized Pacific indicators |
| SINSO | No | No | Provincial (in reports) | 2019 (census) | Census-derived health stats |
| HDX | Yes (CKAN) | No | National | Varies | Quick access to WHO indicators |

**Recommendation for CIE**: DHS API (`api.dhsprogram.com`) is the best programmatic source for health indicators with some sub-national breakdown. SPC .Stat SDMX API for standardized Pacific indicators. HDX CKAN API for quick WHO health data. Sub-national health data is limited — the richest source is the DHS 2015 microdata (requires registration).

---

## Integration Priority for CIE

### Quick Wins (can integrate now)
1. **OpenFisheries API** — national catch trends, no auth, simple JSON
2. **DHS API** — health indicators by country, open aggregate API
3. **HDX CKAN API** — WHO health indicators, open
4. **SPC .Stat SDMX API** — Pacific health/development indicators

### Medium Effort (needs registration)
5. **DHS microdata** — sub-national health data (24–48h registration)
6. **GFW** — already integrated; no catch data available

### Requires Partnership (government access)
7. **SPC TUFMAN 2** — detailed Pacific tuna catch (member access only)
8. **FFA** — same as TUFMAN 2

### Future
9. **UNICEF MICS** — first SLB survey in 2026, results TBD

## Audience
- Engineers and reviewers working on this artifact.

## Prerequisites
- Repository checkout on \ and relevant packet context.

## How to Use
1. Read this document in full.
2. Apply the described checks/updates in your lane.
3. Record verification evidence before closure.

## Troubleshooting
- If verification fails, capture failing command output and update the tracker before retrying.

## Change Log
- 2026-02-22: Added required documentation section headers for doc-lint compliance.
