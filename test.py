from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.post('/upload')
async def upload(file: UploadFile = File(...), algorithm: int = Form(...), hash: str = Form(...)):
    # Odbiór pliku i informacji o algorytmie
    content = await file.read()
    print(f"Odebrano plik: {file.filename}, hash: {hash}")
    print(f"Wybrany algorytm: {algorithm}")
    return JSONResponse(content={"status": "ok", "algorithm": algorithm, "hash": hash})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
