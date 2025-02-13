from fastapi import FastAPI, HTTPException
import http.client
import urllib.parse
import json
import time
import threading

app = FastAPI()

# Store the latest access token and client credentials
latest_token = {"access_token": None, "refresh_token": None, "client_id": None, "client_secret": None}

def get_new_access_token(client_id: str, client_secret: str, refresh_token: str):
    """Fetch a new access token from Zoho using the provided credentials."""
    conn = http.client.HTTPSConnection("accounts.zoho.in")
    
    params = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
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
        latest_token["refresh_token"] = refresh_token  # Save for auto-refresh
        latest_token["client_id"] = client_id
        latest_token["client_secret"] = client_secret
        print("✅ Token refreshed successfully:", latest_token["access_token"])
        return {"access_token": token_info["access_token"]}
    else:
        print("❌ Error refreshing token:", token_info)
        raise HTTPException(status_code=400, detail=token_info)

def auto_refresh_token():
    """Background task to refresh the token every 55 minutes using the last provided credentials."""
    while True:
        if latest_token["refresh_token"] and latest_token["client_id"] and latest_token["client_secret"]:
            get_new_access_token(latest_token["client_id"], latest_token["client_secret"], latest_token["refresh_token"])
        time.sleep(3300)  # Refresh every 55 minutes

# Start the background refresh task
threading.Thread(target=auto_refresh_token, daemon=True).start()

@app.get("/refresh-token")
def refresh_token(client_id: str, client_secret: str, token: str):
    """
    API endpoint to refresh the Zoho access token manually.
    Provide client_id, client_secret, and refresh token as query parameters.
    """
    return get_new_access_token(client_id, client_secret, token)

@app.get("/latest-token")
def get_latest_token():
    """Returns the most recently refreshed access token."""
    if latest_token["access_token"]:
        return latest_token
    else:
        raise HTTPException(status_code=404, detail="No token available yet.")
