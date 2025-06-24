import rasterdata
from rasterdata import extract_data
from importlib.resources import files

# File paths for raster data
soil_fertility_index_filepath = str(files(rasterdata).joinpath("data/soil_fertility_index.tif"))
habitat_suitability_filepath = str(files(rasterdata).joinpath("data/habitat_suitability.tif"))

latitude = -13.8440779 # Example latitude
longitude = 34.541665 # Example longitude

soil_fertility_index = extract_data.extraction(soil_fertility_index_filepath, longitude, latitude)
habitat_suitability = extract_data.extraction(habitat_suitability_filepath, longitude, latitude)
print(f"Soil Fertility Index: {soil_fertility_index}")
print(f"Striga Habitat Suitability: {habitat_suitability}")