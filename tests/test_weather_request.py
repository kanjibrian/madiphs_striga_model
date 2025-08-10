from madiphs_models import weather_request

def test_weather_request(date_str="2023-10-08", latitude=-13.8440779, longitude=34.541665, user_defined="no"):
    """
    This function tests the weather request module.
    Date string is in YYYY-MM-DD format.
    Latitude and longitude should be in decimal degrees numerical format.yes
    """
    if user_defined == "yes":
        # Allow user to define their own latitude and longitude
        latitude = float(input("Enter latitude: "))
        longitude = float(input("Enter longitude: "))
        date_str = input("Enter end date (YYYY-MM-DD): ")
        
    rainfall_intensity_index = weather_request.get_weather_data(date_str, latitude, longitude)
    
    return print(f"For Latitude: {latitude}, Longitude: {longitude}, & End Date: {date_str}, Rainfall Intensity Index: {rainfall_intensity_index}")

if __name__ == "__main__":
    test_weather_request(user_defined=input("Do you want to define your own latitude and longitude? (yes/no): ").strip().lower())