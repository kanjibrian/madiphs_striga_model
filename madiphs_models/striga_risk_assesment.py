from datetime import datetime, date, timezone
import pandas as pd
import numpy as np
import warnings
np.random.seed(42) # Set a random seed for reproducibility

# Ignore any warnings
warnings.filterwarnings("ignore")

def parse_date_tz_naive(date_str: str) -> date:
    """
    Parses a date string into a tz-naive datetime.date object.
    Handles plain dates, datetimes, and ISO strings with timezones.
    """
    try:
        # First try: strict YYYY-MM-DD
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        # Fallback: use fromisoformat() which can handle time and tz
        try:
            dt = datetime.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"Unsupported date format: {date_str}")

    # If datetime is tz-aware, make it naive
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    return dt.date()

class striga_risk_assessment():
    """
    A class to assess the risk of Striga infestation in crops.
    This class provides methods to calculate striga risk based on the following parameters: 
        - Crop type (maize, sorghum).
        - Crop planting day.
        - Crop growth stage (0-1).
        - Weed removal day.
        - Soil fertility index (0-1).
        - Rainfall intensity index (0-1).
        - Habitat suitability index (0-1).
        - Historical presence of Striga.

    """

    # def __init__(self, planting_day: str, crop_type: str, weed_removal_day: str, soil_fertility_index: float, rainfall_intensity: float, habitat_suitability: float, historical_striga: str):
    #     self.planting_day = planting_day
    #     self.crop_type = crop_type
    #     self.weed_removal_day = weed_removal_day
    #     self.soil_fertility_index = soil_fertility_index
    #     self.rainfall_intensity = rainfall_intensity
    #     self.habitat_suitability = habitat_suitability
    #     self.historical_striga = historical_striga

    @classmethod # This allows to call this class method without creating an instance.
    def host_plant_interaction(cls, crop_type: str, growth_stage: float) -> float:
        """ 
        Calculate the interaction risk based on crop type and growth stage.

        Args:
            crop_type: maize, sorghum
            growth_stage: Normalized growth stage (0-1)

        Returns:
            float: Interaction risk score (0-1)
        """
        # Example logic for interaction risk
        crop_factor = 0.8 if crop_type.lower() == "maize" else 0.5
        growth_factor = (1 - growth_stage) * 0.5 + 0.5
        return crop_factor * growth_factor
    @classmethod # This allows to call this class method without creating an instance.
    def risk_assessment(cls, planting_day: str, crop_type: str, weed_removal_day: str, soil_fertility_index: float, rainfall_intensity: float, habitat_suitability: float, historical_striga: str) -> float:
        """
        Function for Striga risk assessment.

        Args:
            planting_day: Day of year for planting
            crop_type: maize, sorghum
            weed_removal_day: Day of weed removal
            soil_fertility_index: Soil fertility index (0-1)
            rainfall_intensity: Rainfall intensity (0-1)
            habitat_suitability: Habitat suitability index (0-1)
            historical_striga: Boolean indicating historical presence

        Returns:
            float: Normalized risk score (0-1)
        """
        # Calculate growth stage based on crop type and days since planting
        growth_duration = 120 if crop_type.strip().lower() == "maize" else 100
        planting_day_date = parse_date_tz_naive(planting_day)
        weed_removal_day_date = parse_date_tz_naive(weed_removal_day)
        days_since_planting = (weed_removal_day_date - planting_day_date).days
        if days_since_planting < 0:
            growth_stage = 0.0
        else:
            growth_stage = days_since_planting / growth_duration
        growth_stage = np.clip(growth_stage, 0.0, 1.0)


        # Calculate weeding effectiveness
        days_between_weeding_and_planting = (planting_day_date - weed_removal_day_date).days
        weeding_effect = 0.8 if abs(days_between_weeding_and_planting) < 30 else 1 # Adjusting based on weeding timing

        # Environmental factors
        environmental_risk = habitat_suitability
        interaction_risk = cls.host_plant_interaction(crop_type, growth_stage)
        soil_risk = (1 - soil_fertility_index) * 0.5 + 0.5 # Adjusting soil fertility to contribute positively

        # Risk modifiers (using presence of historical striga & rainfall intensity)
        historical_modifier = 1.2 if historical_striga.strip().lower() == "yes" else 1.0 # Increasing risk if Striga was historically present
        rainfall_effect = 1.2 if rainfall_intensity > 0.7 else 1.0 # Increasing risk for high rainfall intensity

        # Composite risk calculation
        overall_risk = ((environmental_risk + interaction_risk + soil_risk) * weeding_effect * historical_modifier * rainfall_effect) / 3

        return np.clip(overall_risk, 0, 1) # Ensuring risk level is within 0 to 1

    @classmethod # This allows to call this class method without creating an instance.
    def management_recommendations(cls, risk_level_score: float) -> list:
        """Generate management advice based on risk score level."""
        if pd.isna(risk_level_score):
            return [np.nan, np.nan, np.nan]
        elif risk_level_score > 0.75:
            return [4, "High risk", "Delay planting, use resistant varieties, apply soil amendments."]
        elif risk_level_score > 0.5:
            return [3, "Moderate risk", "Monitor closely, consider inter-cropping with legumes."]
        else:
            return [2, "Low risk", "Standard practices should suffice."]