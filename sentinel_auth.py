import requests

import requests

# Sentinel Hub OAuth credentials
CLIENT_ID = "51579aaf-1ff9-4e31-82de-271905203311" 
CLIENT_SECRET = "MeHQxczmc9rkmtl3GOEn3U1Zi4VnuX73"  
TOKEN_URL = "https://services.sentinel-hub.com/oauth/token"

def get_sentinel_token():
    """
    Authenticate with Sentinel Hub and retrieve an access token.
    """
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    response = requests.post(TOKEN_URL, data=data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Access token retrieved successfully!")
        return token
    else:
        print(f"❌ Error retrieving access token: {response.text}")
        return None

# Test the function
if __name__ == "__main__":
    token = get_sentinel_token()
    print("Access Token:", token)