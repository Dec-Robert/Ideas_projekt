from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from predict import predict_image
from fastapi.responses import JSONResponse
import base64
import requests

app = FastAPI()

BAZA_URL = "http://baza:8000/store/"


class AnalyzeRequest(BaseModel):
    sample_id: int
    algorithm: str
    original_image_base64: str


@app.post("/analyze/")
async def analyze_sample(request: AnalyzeRequest):
    try:
        # Przetwarzanie obrazu
        result = predict_image(request.original_image_base64, method=request.algorithm)

        # Przygotowanie danych do przekazania dalej
        data_to_forward = {
            "sample_id": request.sample_id,
            "original_image": request.original_image_base64,
            "algorithm": request.algorithm,
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "cam_image": result["cam_image"]
        }

        # Wysłanie do Bazy danych
        forward_response = requests.post(BAZA_URL, json=data_to_forward)
        if not forward_response.ok:
            raise HTTPException(status_code=502, detail="Błąd wysyłki do bazy danych")

        # Odpowiedź do Akwizycji Obrazu - opcjonalnie
        return JSONResponse(content={"status": "success", "forwarded": True, "data": data_to_forward})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
