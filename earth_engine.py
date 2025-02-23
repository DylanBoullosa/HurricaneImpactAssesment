import ee
import requests
from PIL import Image
from io import BytesIO

# Your PositionStack API key
api_key = '29e5b2182f173975fa9e719c401a3769'

# Define the address you want to geocode
address = '17 Chapel Hill Ct, Sparta Twp., NJ 07871'

# Create the URL with your API key and address
url = f'https://api.positionstack.com/v1/forward?access_key={api_key}&query={address}'

# Send the request to the API
response = requests.get(url)

# Check if the response is successful
if response.status_code == 200:
    data = response.json()
    if data['data']:
        # Extract latitude and longitude
        latitude = data['data'][0]['latitude']
        longitude = data['data'][0]['longitude']
        print(f"Latitude: {latitude}, Longitude: {longitude}")
    else:
        print("Address not found.")
else:
    print(f"Error: {response.status_code}")
    latitude = None
    longitude = None

# If the coordinates are valid, proceed with the Earth Engine code
if latitude and longitude:
    # Authenticate and initialize Earth Engine
    ee.Initialize()

    # Define the coordinates for the house using the API response
    geometry = ee.Geometry.Point([longitude, latitude]).buffer(50)  # 50m buffer around the house

    # Define the date range
    start_date = '2022-01-01'
    end_date = '2023-12-31'

    # Load the NAIP imagery
    image_collection = ee.ImageCollection("USDA/NAIP/DOQQ") \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date)

    print("Number of NAIP images found:", image_collection.size().getInfo())

    # Get the first image
    image = image_collection.first()

    if image.getInfo() is None:
        print("No valid NAIP image found for the specified date range.")
    else:
        # Clip the image to the geometry
        image = image.clip(geometry)

        # Set visualization parameters using native resolution only
        vis_params = {
            'bands': ['R', 'G', 'B'],
            'min': 0,
            'max': 255,
            'scale': 1,  # NAIP is ~1 m per pixel
        }

        # Get the thumbnail URL without specifying 'dimensions'
        url = image.getThumbURL(vis_params)
        print(f"NAIP Image URL: {url}")

        # Download the image
        response = requests.get(url)
        if response.status_code == 200:
            filename = f"naip_house_image_{start_date}_{end_date}.png"
            with open(filename, "wb") as file:
                file.write(response.content)
            print(f"Successfully saved image as {filename}")
            img = Image.open(BytesIO(response.content))
            img.show()
        else:
            print(f"Failed to retrieve image. Status code: {response.status_code}")
else:
    print("Skipping Earth Engine processing due to invalid coordinates.")

        
