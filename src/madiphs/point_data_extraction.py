import os
import warnings
import rasterio as rio
from rasterio.warp import transform

# Ignore any warnings
warnings.filterwarnings("ignore")


def extraction(path, longitude, latitude, band_number=1):
    # Ensure the file path exists
    if not os.path.exists(path):
        raise FileNotFoundError(f"No file exists at {path}")
    
    # Ensure raster file is valid
    if not path.lower().endswith(('.tif', '.tiff')):
        raise ValueError(f"File at {path} is not a valid raster file. Supported formats are .tif and .tiff.")   
    
    # Ensure longitude and latitude are valid floats
    if not isinstance(longitude, float) or not isinstance(latitude, float):
        raise TypeError(f"Longitude {longitude} and Latitude {latitude} must be floats.")

    with rio.open(path) as src:
        
        # Ensure the raster CRS is defined
        if src.crs is None:
            raise ValueError("The raster does not have a defined Coordinate Reference System (CRS).")
        
        # Transform coordinates if CRS is not WGS84
        # if src.crs.to_string() != "EPSG:4326":
        #     lon, lat = transform("EPSG:4326", src.crs.to_string(), [lon], [lat]) # type: ignore
        # else:
        #     lon, lat = lon, lat
            
        # Ensure the band number is valid
        if band_number < 1 or band_number > src.count:
            raise ValueError(f"Band number {band_number} is out of range. This raster has {src.count} band(s).")
        
        # Ensure point is inside bounds
        if not (src.bounds.left <= longitude <= src.bounds.right and src.bounds.bottom <= latitude <= src.bounds.top):
            raise ValueError("Point is outside raster or Malawi bounds.")

        # Convert geographic coordinates to raster row/col
        row, col = src.index(longitude, latitude)

        # Read only the desired band
        band_array = src.read(band_number)  

        value = band_array[row, col]

        # Handle nodata if set
        if src.nodata is not None and value == src.nodata:
            return None

        return value.round(3)