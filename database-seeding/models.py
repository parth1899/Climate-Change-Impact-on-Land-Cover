from dataclasses import dataclass

@dataclass
class Measurement:
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
