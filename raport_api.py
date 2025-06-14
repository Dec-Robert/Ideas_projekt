from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import base64
from docx import Document
from datetime import datetime
import os
from fastapi.responses import FileResponse

ARCHIWUM_API_URL = os.getenv("ARCHIWUM_API_URL", "http://archiwum-api:8000")

app = FastAPI()

class BatchRequest(BaseModel):
    sample_ids: List[str]

@app.post("/generate-report", response_class=FileResponse)
def generate_report(request: BatchRequest):
    # Pobierz dane z archiwum_api
    try:
        response = requests.post(f"{ARCHIWUM_API_URL}/samples/batch", json={"ids": request.sample_ids})
        response.raise_for_status()
        samples = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd pobierania danych z archiwum: {e}")

    # Załaduj szablon raportu
    doc = Document("szablon.docx")
    doc.add_heading("Raport z analizy próbek", level=1)

    for sample in samples:
        doc.add_heading(f"Próbka {sample['sample_number']}", level=2)
        doc.add_paragraph(f"Numer próbki: {sample['sample_number']}")
        doc.add_paragraph(f"Data dodania: {sample['date_added']}")
        doc.add_paragraph(f"Data predykcji: {sample.get('date_predicted', 'Brak')}")
        doc.add_paragraph(f"Algorytm: {sample['algorithm']}")
        doc.add_paragraph(f"Status: {sample['status']}")
        doc.add_paragraph(f"Pewność (confidence): {sample.get('confidence', 'Brak')}")

        # Dodaj zdjęcie
        image_data = sample.get("evaluated_image")
        if image_data:
            image_bytes = base64.b64decode(image_data)
            image_path = f"/tmp/{sample['sample_number']}.jpg"
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            try:
                doc.add_picture(image_path, width=None)
            except Exception:
                pass  # zabezpieczenie, jeśli obraz nieczytelny

    # Zapisz raport
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"/tmp/raport_{timestamp}.docx"
    doc.save(report_filename)

    # Zwróć raport jako plik do pobrania
    return FileResponse(report_filename, filename=f"raport_{timestamp}.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
