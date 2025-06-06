#!/usr/bin/env python3

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import uvicorn
import hashlib
import os
import cv2
import numpy as np
from PIL import Image
from pyzbar import pyzbar
import re
from datetime import datetime
import io
import httpx
import asyncio

app = FastAPI()


TEAM2_SERVER_URL = "http://0.0.0.0:8001/process" 

class BarcodeImageProcessor:
    def __init__(self, output_folder="processed_images"):
        self.output_folder = output_folder
        self.create_output_folder()
    
    def create_output_folder(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
    
    def sanitize_filename(self, filename):
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = re.sub(r'_+', '_', sanitized)
        sanitized = sanitized.strip('_')
        
        return sanitized if sanitized else "unknown"
    
    def split_image(self, image_array):
        try:
            height, width = image_array.shape[:2]
            
            if width < 227 or height < (227 + 80):
                return None, None

            top_image = image_array[0:227, 0:227]
            
            bottom_start = height - 80
            bottom_image = image_array[bottom_start:height, 0:227]
            
            return top_image, bottom_image
            
        except Exception as e:
            return None, None
    
    def decode_barcode(self, image):
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            barcodes = pyzbar.decode(rgb_image)
            
            if barcodes:
                barcode_data = barcodes[0].data.decode('utf-8')
                return barcode_data
            else:
                gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
                barcodes = pyzbar.decode(gray)
                
                if barcodes:
                    barcode_data = barcodes[0].data.decode('utf-8')
                    return barcode_data
                
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                barcodes = pyzbar.decode(thresh)
                
                if barcodes:
                    barcode_data = barcodes[0].data.decode('utf-8')
                    return barcode_data
                
                return None
                
        except Exception as e:
            return None
    
    def process_image(self, image_content, original_filename, file_hash):
        try:
            nparr = np.frombuffer(image_content, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {
                    "status": "error",
                    "message": "Nie można zdekodować obrazu"
                }
            
            top_image, bottom_image = self.split_image(image)
            
            if top_image is None or bottom_image is None:
                return {
                    "status": "error",
                    "message": "Obraz ma nieprawidłowe wymiary"
                }
            
            barcode_text = self.decode_barcode(bottom_image)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if barcode_text:
                clean_barcode = self.sanitize_filename(barcode_text)
                base_filename = f"{file_hash[:8]}_{clean_barcode}_{timestamp}"
                
                top_filename = f"{base_filename}_top.jpg"
                bottom_filename = f"{base_filename}_barcode.jpg"
                full_filename = f"{base_filename}_full.jpg"
                
                top_path = os.path.join(self.output_folder, top_filename)
                bottom_path = os.path.join(self.output_folder, bottom_filename)
                full_path = os.path.join(self.output_folder, full_filename)
                
                cv2.imwrite(top_path, top_image)
                cv2.imwrite(bottom_path, bottom_image)
                cv2.imwrite(full_path, image)
                
                return {
                    "status": "success",
                    "barcode": barcode_text,
                    "top_image": top_image, 
                    "files": {
                        "top": top_filename,
                        "barcode": bottom_filename,
                        "full": full_filename
                    },
                    "message": f"Pomyślnie przetworzono obraz z kodem: {barcode_text}"
                }
            else:
                base_filename = f"{file_hash[:8]}_no_barcode_{timestamp}"
                
                top_filename = f"{base_filename}_top.jpg"
                bottom_filename = f"{base_filename}_bottom.jpg"
                full_filename = f"{base_filename}_full.jpg"
                
                top_path = os.path.join(self.output_folder, top_filename)
                bottom_path = os.path.join(self.output_folder, bottom_filename)
                full_path = os.path.join(self.output_folder, full_filename)
                
                cv2.imwrite(top_path, top_image)
                cv2.imwrite(bottom_path, bottom_image)
                cv2.imwrite(full_path, image)
                
                return {
                    "status": "warning",
                    "barcode": None,
                    "top_image": top_image, 
                    "files": {
                        "top": top_filename,
                        "bottom": bottom_filename,
                        "full": full_filename
                    },
                    "message": "Nie udało się odczytać kodu kreskowego"
                }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Błąd podczas przetwarzania: {str(e)}"
            }

async def send_to_team2(top_image, barcode, algorithm):

    try:
        _, buffer = cv2.imencode('.jpg', top_image)
        image_bytes = buffer.tobytes()
        
        files = {
            'image': ('processed_image.jpg', image_bytes, 'image/jpeg')
        }
        data = {
            'barcode': str(barcode) if barcode else "None",
            'algorithm': str(algorithm)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TEAM2_SERVER_URL,
                files=files,
                data=data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "team2_response": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Błąd odpowiedzi z serwera zespołu 2: {response.status_code}",
                    "details": response.text
                }
                
    except Exception as e:
        return {
            "status": "error",
            "message": f"Błąd podczas wysyłania do zespołu 2: {str(e)}"
        }

processor = BarcodeImageProcessor()

@app.post('/upload')
async def upload(file: UploadFile = File(...), algorithm: int = Form(...), hash: str = Form(...)):
    content = await file.read()
    
    calculated_hash = hashlib.sha256(content).hexdigest()
    
    if calculated_hash != hash:
        return JSONResponse(
            content={"status": "error", "reason": "Hash mismatch"}, 
            status_code=400
        )
    
    save_dir = "received_photos"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{hash}_{file.filename}")
    
    with open(save_path, "wb") as f:
        f.write(content)
    
    result = processor.process_image(content, file.filename, hash)
    
    if result["status"] in ["success", "warning"] and "top_image" in result:
        team2_result = await send_to_team2(
            result["top_image"],
            result.get("barcode"),
            algorithm
        )
        
        result["team2_forwarding"] = team2_result
    
    return JSONResponse(content={
        "status": "ok",
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)