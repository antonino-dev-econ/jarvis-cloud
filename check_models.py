import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carica la chiave
load_dotenv(dotenv_path=".env")
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("--- RICERCA MODELLI DISPONIBILI ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Modello: {m.name}")
except Exception as e:
    print(f"Errore durante la lettura dei modelli: {e}")