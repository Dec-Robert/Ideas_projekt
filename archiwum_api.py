from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import os
import uuid

# --- KONFIGURACJA BAZY ---
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017/samplesdb")
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
db = client["samplesdb"]
collection = db["samples"]

# --- FASTAPI ---
app = FastAPI(title="API Archiwum Próbek")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lub ["http://localhost:5173"] dla większego bezpieczeństwa
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELE ---

class SampleCreate(BaseModel):
    sample_number: str
    cropped_image: str = Field(..., description="Base64-encoded cropped image")

class SampleUpdate(BaseModel):
    algorithm: str
    status: str  # 'positive', 'negative'
    evaluated_image: str = Field(..., description="Base64-encoded prediction image")
    confidence: float

class SampleOut(BaseModel):
    sample_number: str
    date_added: str
    cropped_image: str
    status: str
    algorithm: Optional[str]
    evaluated_image: Optional[str]
    confidence: Optional[float]
    date_predicted: Optional[str]

# --- ENDPOINTY ---

@app.post("/samples", status_code=201)
def create_sample(sample: SampleCreate):
    if collection.find_one({"sample_number": sample.sample_number}):
        raise HTTPException(status_code=400, detail="Sample with this number already exists")

    doc = {
        "sample_number": sample.sample_number,
        "date_added": datetime.utcnow().isoformat(),
        "cropped_image": sample.cropped_image,
        "status": "in_progress",
        "algorithm": None,
        "evaluated_image": None,
        "confidence": None,
        "date_predicted": None
    }
    collection.insert_one(doc)
    return {"message": "Sample created", "sample_number": sample.sample_number}

@app.put("/samples/{sample_number}")
def update_sample(sample_number: str, update: SampleUpdate):
    result = collection.update_one(
        {"sample_number": sample_number},
        {"$set": {
            "algorithm": update.algorithm,
            "status": update.status,
            "evaluated_image": update.evaluated_image,
            "confidence": update.confidence,
            "date_predicted": datetime.utcnow().isoformat()
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sample not found")
    return {"message": "Sample updated"}

@app.get("/samples", response_model=List[SampleOut])
def get_all_samples():
    samples = list(collection.find({}, {"_id": 0}))
    return samples

@app.get("/samples/{sample_number}", response_model=SampleOut)
def get_sample(sample_number: str):
    sample = collection.find_one({"sample_number": sample_number}, {"_id": 0})
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample
