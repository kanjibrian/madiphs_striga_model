import os
import warnings
import requests
import numpy as np
import requests_cache
import openmeteo_requests
from typing import Optional
from dotenv import load_dotenv
from retry_requests import retry
from datetime import datetime, date, timezone, timedelta

# Load variables from the '.env' file
load_dotenv()

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


def get_weather_data(obsv_date_str: str, latitude: float, longitude: float, variable: str = "rain_sum", planting_date_str: Optional[str] = None, verbose: bool = False) -> float:
    """
    This function fetches daily data for the specified weather variable (by default, rain_sum) over a month given an end date from the Open-Meteo API. 
    Then calculates the monthly Rainfall Intensity Index (RII).

    """

    # Check if date is a string datatype and in the correct format %Y-%m-%d
    if not isinstance(obsv_date_str, str):
        raise TypeError(f"Date {obsv_date_str} must be a string.")
    # try:
    #     datetime.datetime.strptime(date_str, "%Y-%m-%d")
    # except ValueError:
    #     raise ValueError(f"Date {date_str} is not in the format YYYY-MM-DD.")
    
    # Check if latitude and longitude are valid floats
    if not isinstance(latitude, float) or not isinstance(longitude, float):
        raise TypeError(f"Latitude {latitude} and Longitude {longitude} must be floats.")

    # Check if latitude and longitude are valid coordinates
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise ValueError(f"Latitude {latitude} must be between -90 and 90, and Longitude {longitude} must be between -180 and 180.")
    
    # print("All input checks passed. Proceeding to fetch weather data...")


    obsv_date = parse_date_tz_naive(obsv_date_str)  # Convert string to date object
    # end_date = obsv_date - timedelta(days=1)  # Calculate the end date
    end_date = obsv_date  # Use the provided date as the end date
    
    if planting_date_str is not None:
        planting_date = parse_date_tz_naive(planting_date_str)
        if verbose:
            print(f"Planting date provided: {planting_date}")
        if planting_date >= obsv_date:
            if verbose:
                print(f"Planting date {planting_date} should not be after or on observation date {obsv_date}.")
            start_date = end_date - timedelta(days=31)  # Calculate the start date
        elif (end_date - planting_date).days < 31:
            start_date = end_date - timedelta(days=31)  # Calculate the start date
        else:
            start_date = planting_date
    else:
        # print("No planting date provided.")
        start_date = obsv_date - timedelta(days=31)  # Calculate the start date
        
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    if verbose:
        print(f"Fetching {variable} weather data from {start_date_str} to {end_date_str} for coordinates ({latitude}, {longitude})...")
    
    # Initialize & setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    om = openmeteo_requests.Client(session = retry_session) # pyright: ignore[reportArgumentType]
    API_KEY = os.getenv("MY_API_KEY")
    url = f"https://customer-archive-api.open-meteo.com/v1/archive?apikey={API_KEY}"
    params = {
	"latitude": latitude,
	"longitude": longitude,
	"start_date": start_date_str,
	"end_date": end_date_str,
	"daily": variable.strip().lower(),
	"timezone": "auto"
    }
    responses = om.weather_api(url, params=params)
    response = responses[0]
    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_rain = daily.Variables(0).ValuesAsNumpy() # type: ignore
    # daily_rain_sum = daily_rain.sum()  # Sum the daily rain values
    
    # Calculate values at the 10th and 90th percentiles.
    p10 = np.percentile(daily_rain, 10)
    p90 = np.percentile(daily_rain, 90)
    
    # Filter values between the 10th and 90th percentiles (inclusive or exclusive as needed)
    daily_rain_filtered = [x for x in daily_rain if p10 <= x <= p90]

    # Compute daily RII values
    I_min = min(daily_rain_filtered) # type: ignore
    I_max = max(daily_rain_filtered) # type: ignore
    rii_daily = [(I - I_min) / (I_max - I_min) if (I_max - I_min) != 0 else 0 for I in daily_rain_filtered] # type: ignore

    # Monthly RII as average of daily RII
    rii_monthly = sum(rii_daily) / len(rii_daily)
    rii_monthly_final = round(rii_monthly, 3)
    
    return rii_monthly_final