import os
import ee
import requests
from PIL import Image
from io import BytesIO
import logging

# Set up logging for better error tracking
logging.basicConfig(level=logging.DEBUG)

# Set your OpenCage API key
api_key = 'f4909b358d6c496b8e6387ab83474d39'

if not api_key:
    logging.error("OpenCage API key is missing. Please set it.")
    exit(1)

# Define the address you want to geocode
address = '15620 Kinross Cir, Fort Myers, FL 33912'

# Create the URL with your OpenCage API key and address
url = f'https://api.opencagedata.com/geocode/v1/json?q={address}&key={api_key}'

# Send the request to the API
try:
    response = requests.get(url)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    data = response.json()

    if data['results']:
        # Extract latitude and longitude
        latitude = data['results'][0]['geometry']['lat']
        longitude = data['results'][0]['geometry']['lng']
        logging.debug(f"Latitude: {latitude}, Longitude: {longitude}")
    else:
        logging.error("Address not found.")
        latitude = None
        longitude = None
except requests.exceptions.RequestException as e:
    logging.error(f"Error during geocoding request: {e}")
    latitude = None
    longitude = None

# If the coordinates are valid, proceed with the Earth Engine code
if latitude and longitude:
    try:
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

        logging.debug(f"Number of NAIP images found: {image_collection.size().getInfo()}")

        # Get the first image
        image = image_collection.first()

        if image.getInfo() is None:
            logging.error("No valid NAIP image found for the specified date range.")
        else:
            # Clip the image to the geometry
            image = image.clip(geometry)

            # Set visualization parameters using native resolution only
            vis_params = {
                'bands': ['R', 'G', 'B'],
                'min': 0,
                'max': 255,
                'scale': 0.1,  # NAIP is ~1 m per pixel
            }

            # Get the thumbnail URL without specifying 'dimensions'
            url = image.getThumbURL(vis_params)
            logging.debug(f"NAIP Image URL: {url}")

            # Download the image
            img_response = requests.get(url)
            img_response.raise_for_status()  # Check for HTTP errors

            # Save the image to a file
            filename = f"naip_house_image_{start_date}_{end_date}.png"
            with open(filename, "wb") as file:
                file.write(img_response.content)
            logging.info(f"Successfully saved image as {filename}")

            # Open and display the image
            img = Image.open(BytesIO(img_response.content))
            img.show()

    except ee.EEException as e:
        logging.error(f"Error during Earth Engine processing: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during image download: {e}")
else:
    logging.error("Skipping Earth Engine processing due to invalid coordinates.")
