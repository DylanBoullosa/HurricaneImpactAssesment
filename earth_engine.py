import ee
import requests
from PIL import Image
from io import BytesIO

# Authenticate and initialize Earth Engine
ee.Initialize()

# Define Miami coordinates (for a point of interest)
lat = 25.7610
lon = 80.1345
geometry = ee.Geometry.Point([lon, lat]).buffer(5000)  # Reduce the area to a 5km buffer

# Define the date range
start_date = '2022-02-16'
end_date = '2025-02-22'

# Load the Sentinel-2 imagery
image_collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterBounds(geometry) \
    .filterDate(start_date, end_date) \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50)) \
    .sort('system:time_start', False)  # Sort by time (most recent first)

# Get the first image (most recent one)
image = image_collection.first()

# Check if a valid image was found
if image.getInfo() is None:
    print("No valid image found for the specified date range.")
else:
    # Clip the image to the geometry (smaller region)
    image = image.clip(geometry)
    
    # Visualize the image in true color (RGB)
    vis_params = {
        'bands': ['B4', 'B3', 'B2'],  # Red, Green, Blue bands
        'min': 0,
        'max': 3000,
        'dimensions': 512,  # Set smaller dimensions for the thumbnail
    }
    
    # Get the thumbnail URL for the image
    url = image.getThumbURL(vis_params)
    print(f"Image URL: {url}")

    # Download the image
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Downloaded image of size: {len(response.content)} bytes")
        
        # Save the image
        filename = f"miami_image_{start_date}_{end_date}.png"
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Successfully saved image as {filename}")

        # Optionally, display the image (if using Jupyter or an IDE that supports it)
        img = Image.open(BytesIO(response.content))
        img.show()  # This will display the image
    else:
        print(f"Failed to retrieve image. Status code: {response.status_code}")

        
