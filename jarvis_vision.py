import pyautogui
import requests
import os
from PIL import Image

# Ora punta al server locale del tuo PC sulla porta 8080
URL = "http://127.0.0.1:8080/vision"

def avvia_jarvis():
    print("\n--- JARVIS VISION OTTIMIZZATO (LOCALE) ---")
    while True:
        domanda = input("\nTu: ")
        if domanda.lower() in ["esci", "quit"]: 
            break
            
        try:
            print("Cattura e compressione in corso...")
            # 1. Scatta lo screenshot
            screenshot = pyautogui.screenshot()
            
            # 2. Ridimensiona l'immagine al 50% per renderla leggerissima
            w, h = screenshot.size
            screenshot = screenshot.resize((w//2, h//2), Image.LANCZOS)
            
            # Salva temporaneamente con compressione JPG
            screenshot.convert('RGB').save("temp_screen.jpg", "JPEG", quality=70)
            
            # 3. Invia i dati al tuo server locale
            with open("temp_screen.jpg", "rb") as f:
                files = {"file": f}
                params = {"prompt": domanda}
                response = requests.post(URL, data=params, files=files)
            
            if response.status_code == 200:
                print(f"\nJARVIS: {response.json().get('response')}")
            else:
                print(f"\nErrore del server: {response.text}")
                
        except Exception as e:
            print(f"Errore: {e}")
        finally:
            # Cancella subito il file temporaneo per non lasciare traccia sul PC
            if os.path.exists("temp_screen.jpg"): 
                os.remove("temp_screen.jpg")

if __name__ == "__main__":
    avvia_jarvis()