from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from predict import predict_image
from fastapi.responses import JSONResponse
import base64
import requests

app = FastAPI()

BAZA_URL = "http://baza:8000/samples/"


class AnalyzeRequest(BaseModel):
    sample_number: int
    algorithm: str
    original_image_base64: str


@app.post("/analyze/")
async def analyze_sample(request: AnalyzeRequest):
    try:
        # Przetwarzanie obrazu
        result = predict_image(request.original_image_base64, method=request.algorithm)

        # Przygotowanie danych do przekazania dalej (bez sample_number, bo jest w URL)
        data_to_forward = {
            "algorithm": request.algorithm,
            "status": result["prediction"],
            "confidence": result["confidence"],
            "evaluated_image": result["cam_image"]
        }

        # Budowa URL z sample_number w ścieżce
        url = f"{BAZA_URL}{request.sample_number}"

        # Wysłanie PUT do bazy danych
        forward_response = requests.put(url, json=data_to_forward)
        if not forward_response.ok:
            raise HTTPException(status_code=502, detail="Błąd wysyłki do bazy danych")

        # Odpowiedź do Akwizycji Obrazu - opcjonalnie
        # return JSONResponse(content={"status": "success", "forwarded": True, "data": data_to_forward})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
