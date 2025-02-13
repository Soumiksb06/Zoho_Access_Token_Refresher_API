from fastapi import FastAPI, HTTPException, Depends
import http.client
import urllib.parse
import json
import os
import time
import threading

app = FastAPI()

# Environment variables for security
CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
TOKEN_URL = "accounts.zoho.in"

# Store the latest token
latest_token = {"access_token": None}

def get_new_access_token():
    """Fetches a new access token using the refresh token."""
    global latest_token
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
        latest_token["access_token"] = token_info["access_token"]
        print("✅ Token refreshed successfully:", latest_token["access_token"])
        return {"access_token": token_info["access_token"]}
    else:
        print("❌ Error refreshing token:", token_info)
        return {"error": token_info}

def auto_refresh_token():
    """Runs in the background to refresh the token every 55 minutes."""
    while True:
        get_new_access_token()
        time.sleep(3300)  # 55 minutes

# Start the background refresh task in a separate thread
threading.Thread(target=auto_refresh_token, daemon=True).start()

# Authentication dependency
def verify_refresh_token(token: str):
    """Validates the refresh token before allowing access."""
    if token != REFRESH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid refresh token")
    return token

@app.get("/refresh-token")
def refresh_token(token: str = Depends(verify_refresh_token)):
    """API endpoint to manually refresh the token (requires refresh token authentication)."""
    return get_new_access_token()

@app.get("/latest-token")
def get_latest_token(token: str = Depends(verify_refresh_token)):
    """Returns the latest refreshed token (requires authentication)."""
    return latest_token
