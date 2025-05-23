from dataclasses import dataclass

@dataclass
class CO_Measurement:
    measurement_id: str
    region: str
    timestamp: str
    dataset: str
    CO_column_number_density: float
    H2O_column_number_density: float
    cloud_height: float
    sensor_altitude: float
    sensor_azimuth_angle: float
    sensor_zenith_angle: float
    solar_azimuth_angle: float
    solar_zenith_angle: float

@dataclass
class Ozone_Measurement:
    measurement_id: str
    region: str
    timestamp: str
    dataset: str
    O3_column_number_density: float
    O3_column_number_density_amf: float
    O3_slant_column_number_density: float
    O3_effective_temperature: float
    cloud_fraction: float
    sensor_azimuth_angle: float
    sensor_zenith_angle: float
    solar_azimuth_angle: float
    solar_zenith_angle: float

@dataclass
class Aerosol_AI_Measurement:
    measurement_id: str
    region: str
    timestamp: str
    dataset: str
    absorbing_aerosol_index: float
    sensor_altitude: float
    sensor_azimuth_angle: float
    sensor_zenith_angle: float
    solar_azimuth_angle: float
    solar_zenith_angle: float

@dataclass
class District:
    district_id: str
    name: str
    centroid_latitude: float
    centroid_longitude: float
    area: float

@dataclass
class Dataset:
    dataset_id: str
    name: str
    description: str
    temporal_coverage: str
    spatial_resolution: str


@dataclass
class LandCoverMeasurement:
    measurement_id: str
    region: str
    timestamp: str  # This can store the year (e.g., "2017") or a full ISO date as needed.
    dataset: str
    Water: float
    Trees: float
    Flooded_Vegetation: float
    Crops: float
    Built_Area: float
    Bare_Ground: float
    Snow_Ice: float
    Clouds: float
    Rangeland: float