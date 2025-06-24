from openmeteoweather import weather_request

date_str = "2023-10-08"  # Example date in YYYY-MM-DD format
latitude = -13.8440779 # Example latitude
longitude = 34.541665 # Example longitude

rainfall_intensity_index = weather_request.get_weather_data(date_str, latitude, longitude)
print(f'Rainfall Intensity Index: {rainfall_intensity_index}')