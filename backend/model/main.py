from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from predict import predict_image
import requests

app = FastAPI()

BAZA_URL = "http://baza:8000/samples/"


@app.post("/analyze/")
async def analyze_sample(
    image: UploadFile = File(...),
    barcode: int = Form(...),
    algorithm: str = Form(...)
):
    try:
        # Odczytanie zawartości pliku
        image_bytes = await image.read()

        # Przetwarzanie obrazu
        result = predict_image(image_bytes, method=algorithm)

        # Przygotowanie danych do bazy danych
        data_to_forward = {
            "algorithm": algorithm,
            "status": result["prediction"],
            "confidence": result["confidence"],
            "evaluated_image": result["cam_image"]
        }

        # Budowa adresu PUT z numerem próbki
        url = f"{BAZA_URL}{barcode}"

        # Wysłanie danych do bazy
        forward_response = requests.put(url, json=data_to_forward)
        if not forward_response.ok:
            raise HTTPException(status_code=502, detail="Błąd wysyłki do bazy danych")

        # Zwrócenie odpowiedzi do akwizycji
        return JSONResponse(content={"status": "success", "data": data_to_forward})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))