from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# --- AUTH SETUP ---
security = HTTPBasic()

APP_USER = "user"
APP_PASS = "changeit"

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != APP_USER and credentials.password != APP_PASS:
        raise HTTPException(
            status_code=400,
            detail="Unauthorized",
            headers = {"WW-Authenticate": "Basic"}
        )
    return credentials.username