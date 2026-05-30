import os
import io
from fastapi import FastAPI, UploadFile, File, Form
from google import genai
from dotenv import load_dotenv
from PIL import Image
from typing import Optional

# 1. Caricamento forzato: punta direttamente al file .env nella cartella del progetto
load_dotenv(dotenv_path=".env")

api_key = os.getenv("GEMINI_API_KEY")

# 2. DEBUG: Questo apparirà nel terminale per confermare se la chiave è stata letta
if api_key:
    # Mostra solo i primi 5 caratteri per sicurezza
    print(f"✅ CHIAVE CARICATA: {api_key[:5]}***********")
else:
    print("❌ ERRORE: La chiave non è stata caricata! Controlla il file .env")

# 3. CONFIGURAZIONE: Inizializza il client di Google GenAI
client = genai.Client(api_key=api_key)

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Jarvis Cloud is Online"}

@app.post("/chat")
async def chat_endpoint(prompt: str = Form(...), file: Optional[UploadFile] = File(None)):
    try:
        # Se la GUI ha inviato uno screenshot insieme al testo
        if file:
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Inviamo sia l'immagine che il testo a Gemini 2.5 Flash
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[image, prompt]
            )
        else:
            # Se l'utente ha inviato solo un messaggio di testo
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
        return {"response": response.text}
        
    except Exception as e:
        return {"response": f"Errore durante l'elaborazione di Gemini: {str(e)}"}