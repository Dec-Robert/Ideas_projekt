from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import hashlib

app = FastAPI()

# Umożliwiamy połączenia z frontendu (np. localhost:8080)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Możesz ograniczyć do [ "http://localhost:8080"] 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_image(
    file: UploadFile = File(...),
    algorithm: str = Form(...)
):
    content = await file.read()
    hash_hex = hashlib.sha256(content).hexdigest()
    return {"hash": hash_hex, "algorithm": algorithm}
