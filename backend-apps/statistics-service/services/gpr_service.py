from neo4j_utilities.query_gpr import (
    get_measurements,
    get_neighbor_measurements,
    get_landcover_timeseries,
    get_neighbor_landcover_timeseries
)

def fetch_data_service(data):
    """
    Fetches atmospheric and landcover data for a given district based on input parameters.
    
    Expected keys in data:
      - district (str): Name of the district.
      - start_date (str): Start date (ISO format).
      - end_date (str): End date (ISO format).
      - prediction_target (str): Primary atmospheric measurement type ("CO", "Ozone", or "Aerosol").
      - neighbor_influence (bool, optional): Whether to fetch neighboring measurements.
      - landcover_influence (bool, optional): Whether to fetch landcover timeseries data.
      - atmospheric_influence (bool, optional): If true, fetch additional atmospheric measurements
          (those not equal to prediction_target).
    
    Final JSON output will be structured as:
      {
        "district": <district>,
        "landcover": <landcover timeseries (list)>,
        "atmosphere": <dictionary keyed by atmospheric measurement type>,
        "neighbour_landcover": <dictionary keyed by neighbor district>,
        "neighbour_atmosphere": <dictionary keyed by neighbor district, each with atmospheric types>
      }
    """
    district = data["district"]
    start_date = data["start_date"]
    end_date = data["end_date"]
    prediction_target = data["prediction_target"]
    neighbor_influence = data.get("neighbor_influence", False)
    landcover_influence = data.get("landcover_influence", False)
    atmospheric_influence = data.get("atmospheric_influence", False)
    
    # Fetch primary atmospheric measurements.
    primary_measurements = get_measurements(district, start_date, end_date, prediction_target)
    primary_neighbor = (get_neighbor_measurements(district, start_date, end_date, prediction_target)
                        if neighbor_influence else {})

    # Build atmosphere output as a dictionary keyed by measurement type.
    atmosphere = {prediction_target: primary_measurements}
    
    # Build neighbour atmosphere: a dictionary keyed by neighbor district.
    neighbour_atmosphere = {}
    if neighbor_influence:
        for neighbor, meas_list in primary_neighbor.items():
            neighbour_atmosphere.setdefault(neighbor, {})[prediction_target] = meas_list

    # If atmospheric_influence is true, fetch additional atmospheric measurements.
    if atmospheric_influence:
        all_types = ["CO", "Ozone", "Aerosol"]
        additional_types = [t for t in all_types if t != prediction_target]
        for atm_type in additional_types:
            atm_measurements = get_measurements(district, start_date, end_date, atm_type)
            atmosphere[atm_type] = atm_measurements
            if neighbor_influence:
                add_neigh = get_neighbor_measurements(district, start_date, end_date, atm_type)
                for neighbor, meas_list in add_neigh.items():
                    neighbour_atmosphere.setdefault(neighbor, {})[atm_type] = meas_list

    # Fetch landcover data if enabled.
    landcover = get_landcover_timeseries(district) if landcover_influence else None
    neighbour_landcover = (get_neighbor_landcover_timeseries(district)
                           if (landcover_influence and neighbor_influence) else None)

    return {
        "district": district,
        "landcover": landcover,
        "atmosphere": atmosphere,
        "neighbour_landcover": neighbour_landcover,
        "neighbour_atmosphere": neighbour_atmosphere
    }
