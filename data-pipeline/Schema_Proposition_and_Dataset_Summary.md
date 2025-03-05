
### Schema Structure

---
### **Key Node Types**

1. **District**  
    Represents an administrative region (e.g., a district).  
    **Attributes:**  
    • `district_id` (unique identifier)  
    • `name`  
    • `centroid_latitude`  
    • `centroid_longitude`  
    • `area` (optional)  
    • Other static info (e.g., baseline population, economic indicators)
    
2. **Dataset**  
    Represents the definition/metadata for each dataset source.  
    **Attributes:**  
    • `dataset_id`  
    • `name` (e.g., "MODIS Land Cover", "Sentinel-5P CO", "Sentinel-5P Ozone", "Sentinel-5P Aerosol", "NOAA AOT", "EDF OGIM", "GLDAS", "GHSL")  
    • `description`  
    • `temporal_coverage`  
    • `spatial_resolution`  
    • `projection` (if applicable)  
    • Additional metadata (e.g., valid ranges, units)
    
3. **Measurement**  
    A generic node that represents a single measurement event or observation from a dataset at a specific time for a given district.  
    **Attributes:**  
    • `measurement_id`  
    • `timestamp`  
    • `dataset_type` (or you can rely on the relationship to a Dataset node)  
    • **Dynamic properties:**  
      – _For MODIS Land Cover:_ `LC_Type1`, `LC_Type2`, `LC_Type3`, `LC_Type4`, `LC_Type5`, `LC_Prop1`, `LC_Prop2`, `LC_Prop3`, `LC_Prop1_Assessment`, `LC_Prop2_Assessment`, `LC_Prop3_Assessment`, `QC`, `LW`  
      – _For Sentinel-5P CO:_ `CO_column_number_density`, `H2O_column_number_density`, `cloud_height`, `sensor_altitude`, `sensor_azimuth_angle`, `sensor_zenith_angle`, `solar_azimuth_angle`, `solar_zenith_angle`, `CO_column_number_density_amf`, `CO_column_number_density_uncertainty`, `cloud_fraction`, `measurement_quality`  
      – _For Sentinel-5P Ozone:_ `O3_column_number_density`, `O3_effective_temperature`, `cloud_fraction`, `ozone_total_vertical_column`, `ozone_total_vertical_column_precision`, `air_mass_factor_total`, `qa_value`  
      – _For Sentinel-5P Aerosol:_ `aerosol_index_354_388`, `aerosol_index_340_380`, `aerosol_index_335_367`, plus corresponding sensor and solar angles, `latitude`, `longitude`, `qa_value`  
      – _For NOAA AOT:_ `AOT`, `quality_flag`, `latitude`, `longitude`, `time`  
      – _For GLDAS:_ (all the land surface parameters such as `Swnet_tavg`, `Lwnet_tavg`, `Qle_tavg`, etc.)  
      – _For GHSL:_ `built_volume`  
    _Note:_ You can either create separate node labels (e.g., `:MODISMeasurement`, `:SentinelCO`, etc.) or store all as a unified type with dataset-specific properties.
    
4. **Facility**  
    Represents an oil and gas facility from the EDF OGIM dataset.  
    **Attributes:**  
    • `facility_id`  
    • `facility_name`  
    • `operator_name`  
    • `facility_type`  
    • `latitude`  
    • `longitude`  
    • `status`  
    • `last_inspection_date`  
    • `emission_rate`  
    • `emission_source`
    

---

### **Key Relationships**

1. **(District)-[:HAS_MEASUREMENT]->(Measurement)**  
    Links each district to its time-stamped measurement data. This is the primary connection for spatial analysis.
    
2. **(Measurement)-[:BELONGS_TO]->(Dataset)**  
    Associates each measurement with its dataset source, allowing you to filter and query by dataset metadata.
    
3. **(District)-[:HAS_FACILITY]->(Facility)**  
    Connects facilities (from EDF OGIM) to the district in which they’re located.
    
4. **(District)-[:NEIGHBOR_OF]->(District)**  
    Captures spatial adjacency (or even functional influence) between districts. This can be used to model inter-district influences in your prediction algorithms.
    
5. **Optional: (District)-[:INFLUENCES]->(District)**  
    You can also model directed influence if your analysis shows that changes in one district affect another (e.g., emissions diffusion due to wind or economic activity).
    

---

### **How It Works Together**

- **Data Ingestion:**  
    Each incoming measurement (e.g., a new Sentinel-5P CO reading) is stored as a `Measurement` node with its timestamp and dataset-specific properties. It is linked to the appropriate `District` node (determined by the measurement’s spatial coordinates) via the `HAS_MEASUREMENT` relationship.  
    Simultaneously, it’s linked to a `Dataset` node that holds the metadata.
    
- **Spatial Queries:**  
    The `NEIGHBOR_OF` (and/or `INFLUENCES`) relationships let you quickly traverse from one district to its adjacent districts. This is crucial when your forecasting method (like Bayesian Spatiotemporal Models) needs to consider spatial dependencies.
    
- **Policy Insights:**  
    When running simulations (e.g., Monte Carlo scenarios), you can query across the graph to extract not only the measurement history for a district but also contextual information from its neighbors. These structured outputs can then be passed to an LLM (via a retrieval-augmented generation approach) to produce interpretable policy documents.
    
- **Flexibility:**  
    The schema is designed to be extensible. If you later decide to incorporate additional datasets or modify relationships, you can do so by adding new node labels or relationship types without overhauling the entire database.
    

---

### **Visual Schema Summary**

```
(:District {district_id, name, centroid_latitude, centroid_longitude, ...})
   ├─[:HAS_MEASUREMENT]->
   (:Measurement {measurement_id, timestamp, ...dataset-specific properties...})
         └─[:BELONGS_TO]->
         (:Dataset {dataset_id, name, description, temporal_coverage, spatial_resolution, ...})
   ├─[:HAS_FACILITY]->
   (:Facility {facility_id, facility_name, operator_name, facility_type, ...})
   └─[:NEIGHBOR_OF]->
   (:District { ... })
```

---

The MODIS Land Cover Type (MCD12Q1) Version 6.1 dataset provides global land cover classifications at a 500-meter spatial resolution, updated annually from 2001 through 2022. This dataset includes multiple classification schemes and associated quality assessments. Below is a summary of the dataset's parameters and characteristics:

|**Parameter Name**|**Description**|**Units**|**Data Type**|**Valid Range**|**Fill Value**|
|---|---|---|---|---|---|
|**LC_Type1**|Annual International Geosphere-Biosphere Programme (IGBP) classification|Class|8-bit unsigned integer|1 to 17|255|
|**LC_Type2**|Annual University of Maryland (UMD) classification|Class|8-bit unsigned integer|0 to 15|255|
|**LC_Type3**|Annual Leaf Area Index (LAI) classification|Class|8-bit unsigned integer|0 to 10|255|
|**LC_Type4**|Annual Biome-Biogeochemical Cycles (BGC) classification|Class|8-bit unsigned integer|0 to 8|255|
|**LC_Type5**|Annual Plant Functional Types (PFT) classification|Class|8-bit unsigned integer|0 to 11|255|
|**LC_Prop1**|Land Cover Classification System (LCCS1) land cover layer|Class|8-bit unsigned integer|1 to 43|255|
|**LC_Prop2**|LCCS2 land use layer|Class|8-bit unsigned integer|1 to 40|255|
|**LC_Prop3**|LCCS3 surface hydrology layer|Class|8-bit unsigned integer|1 to 51|255|
|**LC_Prop1_Assessment**|LCCS1 land cover layer confidence|Percent|8-bit unsigned integer|0 to 100|255|
|**LC_Prop2_Assessment**|LCCS2 land use layer confidence|Percent|8-bit unsigned integer|0 to 100|255|
|**LC_Prop3_Assessment**|LCCS3 surface hydrology layer confidence|Percent|8-bit unsigned integer|0 to 100|255|
|**QC**|Product quality flags|Flags|8-bit unsigned integer|0 to 10|255|
|**LW**|Binary land (class 2) / water (class 1) mask derived from MOD44W|Class|8-bit unsigned integer|1 to 2|255|

**Key Characteristics:**

- **Temporal Coverage:** Annual data from 2001 to 2022.
- **Spatial Resolution:** 500 meters.
- **Spatial Extent:** Global.
- **File Format:** Hierarchical Data Format 4 (HDF4).
- **Coordinate System:** Sinusoidal projection.
- Cadence: 1 Year

This dataset is particularly useful for researchers and policymakers involved in land cover and land use change studies, environmental monitoring, and climate modeling. The multiple classification schemes and quality assessment layers provide a comprehensive view of global land cover dynamics.


----
The Copernicus Sentinel-5 Precursor (S5P) Near Real-Time (NRTI) Level 3 Carbon Monoxide (CO) dataset provides global measurements of atmospheric carbon monoxide concentrations. This dataset is essential for monitoring air quality and understanding the distribution and transport of CO in the Earth's atmosphere. Below is a summary of the dataset's parameters and characteristics:

|**Parameter Name**|**Description**|**Units**|**Data Type**|**Valid Range**|**Fill Value**|
|---|---|---|---|---|---|
|**CO_column_number_density**|Total column of carbon monoxide in the atmosphere|mol/m²|Float32|≥ 0|NaN|
|**H2O_column_number_density**|Total column of water vapor in the atmosphere|mol/m²|Float32|≥ 0|NaN|
|**cloud_height**|Height of the cloud layer|meters|Float32|≥ 0|NaN|
|**sensor_altitude**|Altitude of the satellite sensor|meters|Float32|≥ 0|NaN|
|**sensor_azimuth_angle**|Azimuth angle of the satellite sensor|degrees|Float32|-180 to 180|NaN|
|**sensor_zenith_angle**|Zenith angle of the satellite sensor|degrees|Float32|0 to 180|NaN|
|**solar_azimuth_angle**|Azimuth angle of the sun|degrees|Float32|-180 to 180|NaN|
|**solar_zenith_angle**|Zenith angle of the sun|degrees|Float32|0 to 180|NaN|
|**CO_column_number_density_amf**|Air mass factor for the CO column number density|Unitless|Float32|≥ 0|NaN|
|**CO_column_number_density_uncertainty**|Uncertainty associated with the CO column number density|mol/m²|Float32|≥ 0|NaN|
|**cloud_fraction**|Fraction of the ground pixel covered by clouds|Unitless|Float32|0 to 1|NaN|
|**measurement_quality**|Quality indicator for the measurement|Unitless|Float32|0 to 1|NaN|

**Key Characteristics:**

- **Temporal Coverage:** Near real-time data, typically available within 3 hours of observation.
- **Spatial Resolution:** 7 km × 7 km at nadir.
- **Spatial Extent:** Global coverage.
- **File Format:** NetCDF-4.
- **Projection:** Geographical latitude-longitude grid.
- Revisit Interval: 2 Days

This dataset is invaluable for researchers and policymakers focusing on air quality assessment, pollution tracking, and atmospheric chemistry studies. The near real-time availability of data allows for timely analysis and response to pollution events.

---
The Copernicus Sentinel-5 Precursor (S5P) Near Real-Time (NRTI) Level 3 Ozone (O₃) dataset provides global measurements of total atmospheric ozone concentrations. This dataset is crucial for monitoring ozone distribution, assessing air quality, and studying atmospheric chemistry. Below is a summary of the dataset's parameters and characteristics:

|**Parameter Name**|**Description**|**Units**|**Data Type**|**Valid Range**|**Fill Value**|
|---|---|---|---|---|---|
|**O3_column_number_density**|Total column of ozone in the atmosphere|mol/m²|Float32|≥ 0|NaN|
|**O3_effective_temperature**|Effective temperature of the ozone column|Kelvin|Float32|≥ 0|NaN|
|**cloud_fraction**|Fraction of the ground pixel covered by clouds|Unitless|Float32|0 to 1|NaN|
|**sensor_altitude**|Altitude of the satellite sensor|meters|Float32|≥ 0|NaN|
|**sensor_azimuth_angle**|Azimuth angle of the satellite sensor|degrees|Float32|-180 to 180|NaN|
|**sensor_zenith_angle**|Zenith angle of the satellite sensor|degrees|Float32|0 to 180|NaN|
|**solar_azimuth_angle**|Azimuth angle of the sun|degrees|Float32|-180 to 180|NaN|
|**solar_zenith_angle**|Zenith angle of the sun|degrees|Float32|0 to 180|NaN|
|**ozone_total_vertical_column**|Total vertical column of ozone|mol/m²|Float32|≥ 0|NaN|
|**ozone_total_vertical_column_precision**|Uncertainty associated with the total vertical column of ozone|mol/m²|Float32|≥ 0|NaN|
|**air_mass_factor_total**|Air mass factor for the total ozone column|Unitless|Float32|≥ 0|NaN|
|**qa_value**|Quality assurance value indicating the reliability of the data|Unitless|Float32|0 to 1|NaN|

**Key Characteristics:**

- **Temporal Coverage:** Near real-time data, typically available within 3 hours of observation.
- **Spatial Resolution:** 5.5 km × 3.5 km at nadir.
- **Spatial Extent:** Global coverage.
- **File Format:** NetCDF-4.
- **Projection:** Geographical latitude-longitude grid.
- **Revisit Interval**: 2 Days

This dataset is invaluable for researchers and policymakers focusing on ozone layer monitoring, air quality assessment, and atmospheric studies. The near real-time availability of data allows for timely analysis and response to environmental events.


---

The Copernicus Sentinel-5 Precursor (S5P) Near Real-Time (NRTI) Level 3 Aerosol Index (AER_AI) dataset provides global measurements of the ultraviolet (UV) Aerosol Index, also known as the Absorbing Aerosol Index (AAI). This index is instrumental in detecting and monitoring UV-absorbing aerosols such as dust, smoke, and volcanic ash, which are crucial for air quality assessments and climate studies. Below is a summary of the dataset's parameters and characteristics:

|**Parameter Name**|**Description**|**Units**|**Data Type**|**Valid Range**|**Fill Value**|
|---|---|---|---|---|---|
|**aerosol_index_354_388**|Aerosol index calculated using 354 nm and 388 nm wavelength pair|Unitless|Float32|-|NaN|
|**aerosol_index_340_380**|Aerosol index calculated using 340 nm and 380 nm wavelength pair|Unitless|Float32|-|NaN|
|**aerosol_index_335_367**|Aerosol index calculated using 335 nm and 367 nm wavelength pair|Unitless|Float32|-|NaN|
|**sensor_altitude**|Altitude of the satellite sensor|meters|Float32|≥ 0|NaN|
|**sensor_azimuth_angle**|Azimuth angle of the satellite sensor|degrees|Float32|-180 to 180|NaN|
|**sensor_zenith_angle**|Zenith angle of the satellite sensor|degrees|Float32|0 to 180|NaN|
|**solar_azimuth_angle**|Azimuth angle of the sun|degrees|Float32|-180 to 180|NaN|
|**solar_zenith_angle**|Zenith angle of the sun|degrees|Float32|0 to 180|NaN|
|**latitude**|Latitude of the measurement|degrees|Float32|-90 to 90|NaN|
|**longitude**|Longitude of the measurement|degrees|Float32|-180 to 180|NaN|
|**qa_value**|Quality assurance value indicating the reliability of the data|Unitless|Float32|0 to 1|NaN|

**Key Characteristics:**

- **Temporal Coverage:** Near real-time data, typically available within 3 hours of observation.
- **Spatial Resolution:** 5.5 km × 3.5 km at nadir.
- **Spatial Extent:** Global coverage.
- **File Format:** NetCDF-4.
- **Projection:** Geographical latitude-longitude grid.
- **Revisit Interval**: 2 days

This dataset is invaluable for researchers and policymakers focusing on air quality monitoring, aerosol research, and climate studies. The near real-time availability of data allows for timely analysis and response to environmental events such as dust storms, wildfires, and volcanic eruptions.

---
The NOAA Climate Data Record (CDR) of Advanced Very High Resolution Radiometer (AVHRR) Aerosol Optical Thickness (AOT) Version 4.0 dataset provides global daily measurements of aerosol optical thickness over oceans. This dataset is essential for monitoring aerosol distributions, assessing air quality, and studying climate change impacts. Below is a summary of the dataset's parameters and characteristics:

|**Parameter Name**|**Description**|**Units**|**Data Type**|**Valid Range**|**Fill Value**|
|---|---|---|---|---|---|
|**AOT**|Aerosol Optical Thickness at 0.63 microns|Unitless|Float32|0 to 5|-999.0|
|**Latitude**|Latitude of the pixel center|Degrees|Float32|-90 to 90|-999.0|
|**Longitude**|Longitude of the pixel center|Degrees|Float32|-180 to 180|-999.0|
|**Time**|Time of observation|Seconds since 1970-01-01|Int32|-|-999.0|
|**Quality_Flag**|Quality flag indicating the reliability of the AOT measurement (0: Good, 1: Degraded, 2: Bad)|Unitless|Int8|0 to 2|-999.0|

**Key Characteristics:**

- **Temporal Coverage:** From January 1, 1982, to the present, with daily updates.
- **Spatial Resolution:** 0.1° latitude × 0.1° longitude grid (~10 km × 10 km at the equator).
- **Spatial Extent:** Global oceans.
- **File Format:** NetCDF-4.
- **Projection:** Geographical latitude-longitude grid.
- Cadence - 1 day

This dataset is invaluable for researchers and policymakers focusing on aerosol monitoring, climate modeling, and environmental studies. The long-term, consistent data record supports analyses of aerosol trends and their effects on climate and air quality.

---
The Environmental Defense Fund's Oil and Gas Infrastructure Monitoring (EDF OGIM) dataset provides near real-time information on oil and gas infrastructure, including locations, operational status, and emissions data. This dataset is essential for environmental monitoring, regulatory compliance, and research into the impacts of oil and gas operations. Below is a summary of the dataset's parameters and characteristics:

|**Parameter Name**|**Description**|**Units**|**Data Type**|**Valid Range**|**Fill Value**|
|---|---|---|---|---|---|
|**facility_id**|Unique identifier for each facility|-|String|-|-|
|**facility_name**|Name of the facility|-|String|-|-|
|**operator_name**|Name of the company operating the facility|-|String|-|-|
|**facility_type**|Type of facility (e.g., well, processing plant)|-|String|-|-|
|**latitude**|Latitude coordinate of the facility location|Degrees|Float|-90 to 90|-|
|**longitude**|Longitude coordinate of the facility location|Degrees|Float|-180 to 180|-|
|**status**|Operational status of the facility (e.g., active, inactive)|-|String|-|-|
|**last_inspection_date**|Date of the most recent inspection|Date|Date|-|-|
|**emission_rate**|Measured emission rate of pollutants (e.g., methane)|kg/hr|Float|≥ 0|-|
|**emission_source**|Source of the emission data (e.g., sensor type, estimation method)|-|String|-|-|

**Key Characteristics:**

- **Temporal Coverage:** Near real-time data with updates as frequently as new information becomes available.
- **Spatial Resolution:** Point locations corresponding to individual facilities.
- **Spatial Extent:** Regions with oil and gas infrastructure, primarily focusing on areas within the United States.
- **File Format:** GeoJSON, CSV, and other geospatial data formats.
- **Projection:** Geographical latitude-longitude coordinate system (WGS 84).
- Cadence - Only 1 Image, infra doesnt change

This dataset is invaluable for environmental agencies, researchers, and policymakers aiming to monitor and mitigate the environmental impacts of oil and gas operations. The detailed facility-level data supports efforts in emissions reduction, regulatory compliance, and public transparency.


---

The NASA Global Land Data Assimilation System (GLDAS) Version 2.2 Catchment Land Surface Model (CLSM) dataset provides global daily simulations of land surface states and fluxes. This dataset is essential for hydrological studies, climate research, and water resource management. Below is a summary of the dataset's parameters and characteristics:

|**Parameter Name**|**Description**|**Units**|**Data Type**|**Valid Range**|**Fill Value**|
|---|---|---|---|---|---|
|**Swnet_tavg**|Net shortwave radiation flux|W/m²|Float32|-|-|
|**Lwnet_tavg**|Net longwave radiation flux|W/m²|Float32|-|-|
|**Qle_tavg**|Latent heat flux|W/m²|Float32|-|-|
|**Qh_tavg**|Sensible heat flux|W/m²|Float32|-|-|
|**Qg_tavg**|Ground heat flux|W/m²|Float32|-|-|
|**Snowf_tavg**|Snowfall rate|kg/m²/s|Float32|-|-|
|**Rainf_tavg**|Rainfall rate|kg/m²/s|Float32|-|-|
|**Evap_tavg**|Evapotranspiration|kg/m²/s|Float32|-|-|
|**Qs_tavg**|Surface runoff (non-infiltrating)|kg/m²/s|Float32|-|-|
|**Qsb_tavg**|Subsurface runoff (baseflow)|kg/m²/s|Float32|-|-|
|**Qsm_tavg**|Snowmelt|kg/m²/s|Float32|-|-|
|**SnowT_tavg**|Snowpack temperature|K|Float32|-|-|
|**AvgSurfT_tavg**|Average surface skin temperature|K|Float32|-|-|
|**SWE_tavg**|Snow water equivalent|kg/m²|Float32|-|-|
|**SnowDepth_tavg**|Snow depth|m|Float32|-|-|
|**SoilMoist_S_tavg**|Surface soil moisture (0-2 cm)|kg/m²|Float32|-|-|
|**SoilMoist_RZ_tavg**|Root zone soil moisture|kg/m²|Float32|-|-|
|**SoilMoist_P_tavg**|Profile soil moisture|kg/m²|Float32|-|-|
|**ECanop_tavg**|Canopy water evaporation|kg/m²/s|Float32|-|-|
|**Tveg_tavg**|Transpiration|kg/m²/s|Float32|-|-|
|**ESoil_tavg**|Direct evaporation from bare soil|kg/m²/s|Float32|-|-|
|**CanopInt_tavg**|Canopy water storage|kg/m²|Float32|-|-|
|**EvapSnow_tavg**|Sublimation (evaporation from snow)|kg/m²/s|Float32|-|-|
|**Acond_tavg**|Aerodynamic conductance|m/s|Float32|-|-|
|**TWS_tavg**|Terrestrial water storage|mm|Float32|-|-|
|**GWS_tavg**|Groundwater storage|mm|Float32|-|-|
|**Wind_f_tavg**|Near-surface wind speed|m/s|Float32|-|-|
|**Rainf_f_tavg**|Near-surface rainfall rate|kg/m²/s|Float32|-|-|
|**Tair_f_tavg**|Near-surface air temperature|K|Float32|-|-|
|**Qair_f_tavg**|Near-surface specific humidity|kg/kg|Float32|-|-|
|**Psurf_f_tavg**|Surface pressure|Pa|Float32|-|-|
|**SWdown_f_tavg**|Surface downward shortwave radiation|W/m²|Float32|-|-|
|**LWdown_f_tavg**|Surface downward longwave radiation|W/m²|Float32|-|-|

**Key Characteristics:**

- **Temporal Coverage:** From January 1, 2000, to the present, with a latency of approximately 1.5 months.
- **Spatial Resolution:** 0.25° × 0.25° (approximately 25 km × 25 km at the equator).
- **Spatial Extent:** Global coverage, excluding Greenland and Antarctica.
- **File Format:** NetCDF-4.
- **Projection:** Geographical latitude-longitude grid.
- Cadence: 1 day

This dataset is invaluable for researchers and policymakers focusing on hydrology, climate change, and water resource management. The comprehensive set of land surface parameters enables detailed analysis of terrestrial water and energy cycles.

---

The Global Human Settlement Layer (GHSL) produced by the Joint Research Centre (JRC) offers the **GHS-BUILT-V** dataset, which provides a global depiction of building volumes. This dataset is instrumental for urban planning, infrastructure development, and assessing human settlement patterns. Below is a summary of the dataset's parameters and characteristics:

|**Parameter Name**|**Description**|**Units**|**Data Type**|**Valid Range**|**Fill Value**|
|---|---|---|---|---|---|
|**built_volume**|Total volume of buildings within a 100m x 100m grid cell|m³|Float32|≥ 0|0|

**Key Characteristics:**

- **Temporal Coverage:** Data available for multiple epochs, including 1975, 1990, 2000, 2015, and 2030 projections.
- **Spatial Resolution:** 100 meters.
- **Spatial Extent:** Global coverage.
- **File Format:** GeoTIFF.
- **Projection:** EPSG:4326 (WGS 84).
- Cadence: yearly

This dataset is invaluable for researchers and policymakers focusing on urbanization trends, infrastructure planning, and sustainable development. The detailed building volume information supports analyses of urban density, growth patterns, and resource allocation.

