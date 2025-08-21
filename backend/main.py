from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

import auth
import health

app = FastAPI()
# Enable CORS for frontend hosted on AWS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust later to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)  # Mount the endpoints in auth.py
app.include_router(health.router)  # Mount the endpoints in health.py

@app.get("/media/all", response_model=list[str])
def media_all():
    directory = Path('/media')
    try:
        return [str(f) for f in directory.iterdir() if f.is_file()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
