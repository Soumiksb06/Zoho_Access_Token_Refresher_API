from fastapi import FastAPI, HTTPException
import http.client
import urllib.parse
import json
import time
import threading

app = FastAPI()

# Global dictionary to store the latest access token
latest_token = {"access_token": None}

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
        print("✅ Token refreshed successfully:", latest_token["access_token"])
        return {"access_token": token_info["access_token"]}
    else:
        print("❌ Error refreshing token:", token_info)
        raise HTTPException(status_code=400, detail=token_info)

# (Optional) Background auto-refresh could be implemented if you wish
# For example, if you want to auto-refresh using a default set of credentials,
# you can store those in the global latest_token (or elsewhere) and run a background task.
# In this example, auto-refresh is disabled since the credentials are provided per request.

@app.get("/refresh-token")
def refresh_token(client_id: str, client_secret: str, token: str):
    """
    API endpoint to refresh the Zoho access token.
    Provide client_id, client_secret, and refresh token (as 'token') as query parameters.
    """
    return get_new_access_token(client_id, client_secret, token)

@app.get("/latest-token")
def get_latest_token():
    """Returns the most recently refreshed access token."""
    return latest_token
