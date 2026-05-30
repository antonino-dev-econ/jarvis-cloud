import os
import io
from fastapi import FastAPI, UploadFile, File, Form
from google import genai
from dotenv import load_dotenv
from PIL import Image

# 1. Caricamento forzato: punta direttamente al file .env nella cartella del progetto
load_dotenv(dotenv_path=".env")

api_key = os.getenv("GEMINI_API_KEY")

# 2. DEBUG: Questo apparirà nel terminale per confermare se la chiave è stata letta
if api_key:
    # Mostra solo i primi 5 caratteri per sicurezza
    print(f"✅ CHIAVE CARICATA: {api_key[:5]}**********")
else:
    print("❌ ERRORE: La chiave non è stata caricata! Controlla il file .env")

# 3. CONFIGURAZIONE: Inizializza il nuovo client di Google GenAI
client = genai.Client(api_key=api_key)

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Jarvis Cloud is Online"}

@app.get("/ask")
def ask_jarvis(prompt: str):
    try:
        # Usiamo gemini-2.5-flash, il nuovo standard ultra-veloce
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}

# --- NUOVO ENDPOINT PER GLI SCREENSHOT DI JARVIS VISION ---
@app.post("/vision")
async def ask_jarvis_vision(prompt: str = Form(...), file: UploadFile = File(...)):
    try:
        # 1. Legge il file inviato dallo script e lo trasforma in un'immagine PIL
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # 2. Invia sia l'immagine che la domanda a Gemini 2.5 Flash
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt]
        )
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Avvia il server sulla porta 8080
    uvicorn.run(app, host="0.0.0.0", port=8080)