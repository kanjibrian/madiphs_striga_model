import numpy as np
import sys
import json

np.random.seed(42) # Set a random seed for reproducibility

from openmeteoweather import weather_request
import data
from data import extract_data
from importlib.resources import files


def host_plant_interaction(crop_type: int, growth_stage: float) -> float:
    """Calculate crop-specific risk modifier based on growth stage."""
    crop_factor = 0.8 if crop_type == 0 else 0.5
    growth_factor = (1 - growth_stage) * 0.5 + 0.5
    return crop_factor * growth_factor

def striga_risk_assessment(planting_day: int, crop_type: int, weed_removal_day: int, soil_fertility_index: float, rainfall_intensity: float, habitat_suitability: float, historical_striga: bool  # NEW PARAMETER
                           ) -> float:
    """
    API endpoint for Striga risk assessment.

    Args:
        planting_day: Day of year for planting (1-365)
        crop_type: 0 = maize, 1 = sorghum
        weed_removal_day: Day of weed removal (1-365)
        location_index: Geographic location index (0-364)
        historical_striga: Boolean indicating historical presence

    Returns:
        float: Normalized risk score (0-1)
    """
    # Calculate growth stage based on crop type and days since planting
    growth_duration = 120 if crop_type == 0 else 100
    days_since_planting = weed_removal_day - planting_day
    if days_since_planting < 0:
        growth_stage = 0.0
    else:
        growth_stage = days_since_planting / growth_duration
    growth_stage = np.clip(growth_stage, 0.0, 1.0)


    # Calculate weeding effectiveness
    days_between = planting_day - weed_removal_day
    weeding_effect = 0.8 if days_between < 30 else 1

    # Environmental factors
    environmental_risk = habitat_suitability
    interaction_risk = host_plant_interaction(crop_type, growth_stage)
    soil_risk = (1 - soil_fertility_index) * 0.5 + 0.5

    # Risk modifiers (using passed historical_striga)
    historical_modifier = 1.2 if historical_striga else 1.0
    rainfall_effect = 1.2 if rainfall_intensity > 0.7 else 1.0

    # Composite risk calculation
    overall_risk = (
        (environmental_risk + interaction_risk + soil_risk)
        * weeding_effect
        * historical_modifier
        * rainfall_effect
    ) / 3

    return np.clip(overall_risk, 0, 1)

def management_recommendations(risk_level: float) -> str:
    """Generate management advice based on risk score."""
    if risk_level > 0.75:
        return "High risk: Delay planting, use resistant varieties, apply soil amendments."
    elif risk_level > 0.5:
        return "Moderate risk: Monitor closely, consider inter-cropping with legumes."
    else:
        return "Low risk: Standard practices should suffice."


if __name__ == "__main__":

    # File paths for raster data
    soil_fertility_index_filepath = str(files(data).joinpath("raster/soil_fertility_index.tif"))
    habitat_suitability_filepath = str(files(data).joinpath("raster/habitat_suitability.tif"))

    date_str = str(sys.argv[4])  # date in YYYY-MM-DD format
    latitude = float(sys.argv[7]) # latitude
    longitude = float(sys.argv[6]) # longitude


    HABITAT_SUITABILITY = extract_data.extraction(habitat_suitability_filepath, longitude, latitude)
    RAINFALL_INTENSITY = weather_request.get_weather_data(date_str, latitude, longitude)
    SOIL_FERTILITY = extract_data.extraction(soil_fertility_index_filepath, longitude, latitude)


    # Variables passed from external system mobile application API call with all parameters
    risk_score = striga_risk_assessment(
        planting_day=int(sys.argv[1]),
        crop_type=int(sys.argv[2]),
        weed_removal_day=int(sys.argv[3]),
        soil_fertility_index=SOIL_FERTILITY,
        rainfall_intensity=RAINFALL_INTENSITY,
        habitat_suitability=HABITAT_SUITABILITY,
        historical_striga=sys.argv[5]  # Direct parameter input
    )


    model_output = {
        "computed_risk": round(risk_score, 2),
        "recommendation": management_recommendations(risk_score)
    }

    # release output as JSON to the external mobile application
    json_str = json.dumps(model_output)
    print(json_str)