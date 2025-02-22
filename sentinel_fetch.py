import requests
import json
from sentinel_auth import get_sentinel_token
from datetime import datetime, timedelta

# Miami coordinates (25°46'51"N, 80°13'43"W)
lat = 25.78083
lon = -80.22861

# Slightly larger bounding box (approximately 200 meters)
bbox = [lon - 0.001, lat - 0.001, lon + 0.001, lat + 0.001]

def fetch_satellite_image(date, filename):
    access_token = get_sentinel_token()
    print(f"\nAttempting to fetch image for date: {date}")
    print(f"Using bounding box: {bbox}")
    
    url = "https://services.sentinel-hub.com/api/v1/process"

    evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: ["B04", "B03", "B02"],
            output: { 
                bands: 3,
                sampleType: "UINT8"
            }
        };
    }

    function evaluatePixel(sample) {
        // Enhanced RGB composite
        var gain = 3.5;
        
        // Check if we have valid data
        if (sample.B04 === 0 && sample.B03 === 0 && sample.B02 === 0) {
            return [0, 0, 0];
        }
        
        return [
            sample.B04 * gain * 255,
            sample.B03 * gain * 255,
            sample.B02 * gain * 255
        ].map(v => Math.min(255, Math.max(0, v)));
    }
    """

    payload = {
        "input": {
            "bounds": {
                "bbox": bbox,
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
            },
            "data": [
                {
                    "type": "S2L2A",
                    "dataFilter": {
                        "timeRange": {
                            "from": f"{date}T00:00:00Z",
                            "to": f"{date}T23:59:59Z"
                        },
                        "maxCloudCoverage": 30
                    }
                }
            ]
        },
        "evalscript": evalscript,
        "output": {
            "width": 256,
            "height": 256,
            "format": "image/png"
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        print("\nMaking request with payload:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(url, headers=headers, json=payload)
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"Error Response Text: {response.text}")
            return False
        
        content_length = len(response.content)
        print(f"Response size: {content_length} bytes")
        
        if content_length < 1000:
            print("Warning: Response content seems too small for an image")
            return False

        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Successfully saved image as {filename}")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
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
        
        