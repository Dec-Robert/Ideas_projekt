from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from predict import predict_image
import requests
import uvicorn
import os

app = FastAPI()

BAZA_URL = os.getenv("BAZA_URL", "http://localhost:8000/samples/")


@app.post("/process")
async def analyze_sample(
        image: UploadFile = File(...),
        barcode: str = Form(...),
        algorithm: int = Form(...)
):
    try:
        # Odczytanie zawartosci pliku
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

        url = f"{BAZA_URL}{barcode}"

        # Wyslanie danych do bazy
        forward_response = requests.put(url, json=data_to_forward)
        if not forward_response.ok:
            raise HTTPException(status_code=502, detail="Blad wysylki do bazy danych")

        # Zwrocenie odpowiedzi do akwizycji
        return JSONResponse(content={"status": "success", "data": data_to_forward})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
