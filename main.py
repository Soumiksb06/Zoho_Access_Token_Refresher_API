from fastapi import FastAPI
import http.client
import urllib.parse
import json
import os

app = FastAPI()

# Environment variables for security
CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
TOKEN_URL = "accounts.zoho.in"

def get_new_access_token():
    """Fetches a new access token using the refresh token."""
    conn = http.client.HTTPSConnection(TOKEN_URL)
    
    params = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    })
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    conn.request("POST", "/oauth/v2/token", params, headers)
    
    response = conn.getresponse()
    data = response.read().decode("utf-8")
    conn.close()
    
    token_info = json.loads(data)
    
    if "access_token" in token_info:
        return {"access_token": token_info["access_token"]}
    else:
        return {"error": token_info}

@app.get("/refresh-token")
def refresh_token():
    """API endpoint to refresh Zoho access token."""
    return get_new_access_token()
