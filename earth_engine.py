import os
import ee
import requests
from datetime import datetime, timedelta

# Ensure authentication works correctly (Set the correct path)
os.environ["EARTHENGINE_CREDENTIALS"] = "/Users/ibm/.config/earthengine/credentials"

# Initialize Earth Engine API
try:
    ee.Initialize()
    print("Google Earth Engine API initialized successfully!")
except Exception as e:
    print(f"Error initializing Earth Engine: {e}")
    exit()

# Miami coordinates (25°46'51"N, 80°13'43"W)
lat = 25.78083
lon = -80.22861

# Slightly larger bounding box (approximately 200 meters)
bbox = [lon - 0.001, lat - 0.001, lon + 0.001, lat + 0.001]

# Function to fetch satellite image from Google Earth Engine
def fetch_satellite_image(date, filename):
    print(f"\nAttempting to fetch image for date: {date}")
    
    # Define the area of interest (bounding box)
    geometry = ee.Geometry.Rectangle(bbox)
    
    # Use Sentinel-2 imagery
    image_collection = ee.ImageCollection("COPERNICUS/S2") \
        .filterBounds(geometry) \
        .filterDate(f"{date}T00:00:00", f"{date}T23:59:59") \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30)) \
        .sort('system:time_start', False)  # Sort by time to get the most recent image

    # Get the first image (most recent within the date range)
    image = image_collection.first()
    
    # Check if a valid image was found
    if image.getInfo() is None:
        print(f"No valid image found for {date}. Skipping...")
        return False

    # Visualize the image in true color (RGB)
    vis_params = {
        'bands': ['B4', 'B3', 'B2'],  # Red, Green, Blue bands
        'min': 0,
        'max': 3000,
    }

    try:
        # Get the URL for the image
        url = image.getThumbURL(vis_params)
        print(f"Image URL: {url}")

        # Download the image
        response = requests.get(url)
        
        if response.status_code == 200:
            with open(filename, "wb") as file:
                file.write(response.content)
            print(f"Successfully saved image as {filename}")
            return True
        else:
            print(f"Failed to retrieve image for {date}. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error fetching image for {date}: {e}")
        return False

# Generate dates for the past week
end_date = datetime.now()
dates_to_try = [(end_date - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(7)]

print("Trying the following dates:", dates_to_try)

for date in dates_to_try:
    success = fetch_satellite_image(date, f"miami_house_{date}.png")
    if success:
        print(f"Successfully retrieved image for {date}")
        break
    else:
        print(f"Failed to retrieve image for {date}\n")
        