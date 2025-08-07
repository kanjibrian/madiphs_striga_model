import os
import datetime
import warnings
import requests
import numpy as np
import requests_cache
import openmeteo_requests
from dotenv import load_dotenv
from retry_requests import retry

# Load variables from the '.env' file
load_dotenv()

# Ignore any warnings
warnings.filterwarnings("ignore")

def get_weather_data(date_str, latitude, longitude, variable="rain_sum") -> float:
    """
    This function fetches daily rain fall weather data for a month given an end date from the Open-Meteo API. 
    Then calculates the monthly Rainfall Intensity Index (RII).

    """

    # Check if date is a string datatype and in the correct format %Y-%m-%d
    if not isinstance(date_str, str):
        raise TypeError(f"Date {date_str} must be a string.")
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Date {date_str} is not in the format YYYY-MM-DD.")
    
    # Check if latitude and longitude are valid floats
    if not isinstance(latitude, float) or not isinstance(longitude, float):
        raise TypeError(f"Latitude {latitude} and Longitude {longitude} must be floats.")

    # Check if latitude and longitude are valid coordinates
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise ValueError(f"Latitude {latitude} must be between -90 and 90, and Longitude {longitude} must be between -180 and 180.")
    
    # print("All input checks passed. Proceeding to fetch weather data...")
    
    
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date() # Convert string to date object
    # end_date = date - datetime.timedelta(days=1)  # Calculate the end date
    end_date = date  # Use the provided date as the end date
    start_date = date - datetime.timedelta(days=31)  # Calculate the start date
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
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
	"daily": variable,
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