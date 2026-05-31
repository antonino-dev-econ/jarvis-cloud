"""
Jarvis Server - Backend API
Questo modulo utilizza FastAPI per creare un server locale.
Funziona da "ponte": riceve i testi e gli screenshot dalla tua interfaccia grafica (GUI), 
li inoltra in modo sicuro alle API di Google Gemini e restituisce le risposte.
"""

# Modulo di sistema per interagire con le variabili d'ambiente del computer
import os
# Modulo per la gestione dei flussi di byte in memoria (indispensabile per leggere le immagini)
import io

# Componenti di FastAPI per creare il server, ricevere file caricati e leggere i campi di testo
from fastapi import FastAPI, UploadFile, File, Form
# SDK ufficiale di Google per comunicare con l'intelligenza artificiale
from google import genai
# Modulo per caricare in memoria le variabili nascoste nel file .env
from dotenv import load_dotenv
# Libreria Pillow (PIL) per aprire, elaborare e gestire le immagini
from PIL import Image
# Modulo per definire tipi di dati opzionali (es. un file che può esserci o non esserci)
from typing import Optional

# 1. CARICAMENTO CHIAVI
# Forza la lettura del file .env situato nella stessa cartella di questo script
load_dotenv(dotenv_path=".env")

# Estrae la chiave API di Google salvata nel file .env e la salva in una variabile
api_key = os.getenv("GEMINI_API_KEY")

# 2. SISTEMA DI DEBUG
# Verifica se la chiave è stata trovata con successo
if api_key:
    # Stampa a terminale i primi 5 caratteri per confermare il caricamento senza esporre tutta la password
    print(f"✅ CHIAVE CARICATA: {api_key[:5]}***********")
else:
    # Mostra un errore evidente se il file .env è assente o vuoto
    print("❌ ERRORE: La chiave non è stata caricata! Controlla il file .env")

# 3. INIZIALIZZAZIONE CLIENT
# Crea l'oggetto 'client' che gestirà tutte le connessioni verso i server di Google usando la nostra chiave
client = genai.Client(api_key=api_key)

# Inizializza l'applicazione FastAPI che gestirà le richieste web
app = FastAPI()

# 4. ENDPOINT DI CONTROLLO
# Definisce l'indirizzo base (http://127.0.0.1:8000/) e ascolta le richieste GET
@app.get("/")
def home():
    # Restituisce un semplice messaggio JSON per confermare che il server è acceso e raggiungibile
    return {"status": "Jarvis Cloud is Online"}

# 5. ENDPOINT PRINCIPALE DELLA CHAT
# Ascolta all'indirizzo /chat usando il metodo POST (necessario per ricevere file pesanti come le immagini)
@app.post("/chat")
async def chat_endpoint(
    # Richiede obbligatoriamente un parametro testuale (il messaggio scritto dall'utente)
    prompt: str = Form(...), 
    # Permette di ricevere un file immagine, ma lo rende opzionale (di default è None)
    file: Optional[UploadFile] = File(None)
):
    try:
        # Se la GUI ha inviato anche un file (significa che è stato premuto il tasto Screenshot)
        if file:
            # Legge il file in formato binario puro (byte) attendendo la fine del caricamento (await)
            image_data = await file.read()
            # Converte i byte in un vero e proprio oggetto Immagine comprensibile da Python
            image = Image.open(io.BytesIO(image_data))
            
            # Invia la richiesta all'IA
            response = client.models.generate_content(
                model='gemini-2.5-flash', # Usa il modello veloce e multimodale
                contents=[image, prompt]  # Fornisce all'IA sia l'immagine che la domanda dell'utente
            )
        # Se la GUI NON ha inviato un file (è stato inviato solo del testo)
        else:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt           # Fornisce all'IA esclusivamente il testo
            )
            
        # Prende il testo generato dall'IA e lo restituisce alla GUI in formato JSON
        return {"response": response.text}
        
    # Se qualcosa va storto (es. connessione assente, token Google esauriti)
    except Exception as e:
        # Cattura l'errore tecnico, lo converte in stringa e lo manda alla chat per fartelo leggere
        return {"response": f"Errore durante l'elaborazione di Gemini: {str(e)}"}