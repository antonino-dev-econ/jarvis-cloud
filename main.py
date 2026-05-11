import os
from fastapi import FastAPI
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Caricamento forzato: punta direttamente al file .env nella cartella del progetto
load_dotenv(dotenv_path=".env")

api_key = os.getenv("GEMINI_API_KEY")

# 2. DEBUG: Questo apparirà nel terminale per confermare se la chiave è stata letta
if api_key:
    # Mostra solo i primi 5 caratteri per sicurezza
    print(f"✅ CHIAVE CARICATA: {api_key[:5]}**********")
else:
    print("❌ ERRORE: La chiave non è stata caricata! Controlla il file .env")

# Configura Gemini
genai.configure(api_key=api_key)

# 3. MODELLO: Usiamo 2.0-flash per il primo test, è il più stabile per i nuovi account
model = genai.GenerativeModel('models/gemini-2.0-flash')

app = FastAPI()

@app.api_route("/", methods=["GET","HEAD"])
def home():
    return {"status": "Jarvis Cloud is Online"}

@app.get("/ask")
def ask_jarvis(prompt: str):
    try:
        response = model.generate_content(prompt)
        return {"response": response.text}
    except Exception as e:
        # Questo ci dirà esattamente perché Google rifiuta la richiesta
        return {"error": str(e)}

from fastapi import File, UploadFile
import PIL.Image
import io

@app.post("/vision")
async def vision_analyze(prompt: str, file: UploadFile = File(...)):
    try:
        request_object_content = await file.read()
        img = PIL.Image.open(io.BytesIO(request_object_content))
        
        # Chiamiamo Gemini
        response = model.generate_content([prompt, img])
        
        # CONTROLLO CRITICO: Se Gemini non risponde, cerchiamo di capire perché
        if not response.text:
            return {"response": "Gemini ha visto l'immagine ma non ha generato testo. Prova a cambiare inquadratura."}
            
        return {"response": response.text}
    except Exception as e:
        # Questo ci dirà nei log di Render l'errore esatto (es. Filtri di sicurezza)
        print(f"ERRORE VISION: {str(e)}")
        return {"response": f"Errore interno: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # Avvia il server sulla porta 8080
    uvicorn.run(app, host="0.0.0.0", port=8080)
