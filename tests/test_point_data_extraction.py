from madiphs_models import data
from madiphs_models import point_data_extraction
from importlib.resources import files

def test_point_data_extraction(latitude=-13.8440779, longitude=34.541665, user_defined="no"):
    
    # File paths for raster data
    soil_fertility_index_filepath = str(files(data).joinpath("raster/soil_fertility_index.tif"))
    habitat_suitability_filepath = str(files(data).joinpath("raster/striga_habitat_suitability.tif"))

    if user_defined == "yes":
        latitude = float(input("Enter latitude: "))
        longitude = float(input("Enter longitude: "))

    soil_fertility_index = point_data_extraction.extraction(soil_fertility_index_filepath, longitude, latitude)
    habitat_suitability = point_data_extraction.extraction(habitat_suitability_filepath, longitude, latitude)
    
    return print(f"For Latitude: {latitude}, Longitude: {longitude}, Soil Fertility Index: {soil_fertility_index} & Striga Habitat Suitability: {habitat_suitability}")

if __name__ == "__main__":
    test_point_data_extraction(user_defined=input("Do you want to define your own latitude and longitude? (yes/no): ").strip().lower())