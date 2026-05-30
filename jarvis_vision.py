import os
import sys
import tkinter as tk
import customtkinter as ctk
import pyautogui
import requests
import threading
from PIL import Image

# Configurazione iniziale della grafica
ctk.set_appearance_mode("System")  # Segue il tema di Windows (Dark o Light)
ctk.set_default_color_theme("blue") # Colore dei bottoni e dettagli

SERVER_URL = "http://127.0.0.1:8000/chat"

class JarvisGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurazione Finestra
        self.title("JARVIS VISION GUI")
        self.geometry("600x700")
        self.minsize(500, 600)

        # Layout a griglia principale
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- AREA CHAT (SCROLLABLE) ---
        self.chat_frame = ctk.CTkScrollableFrame(self, label_text="Conversazione con Jarvis")
        self.chat_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        
        # --- AREA DI COMANDO (INPUT + BOTTONI) ---
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Campo di testo per l'utente
        self.entry_message = ctk.CTkEntry(self.input_frame, placeholder_text="Chiedi qualcosa a Jarvis o descrivi cosa fare...")
        self.entry_message.grid(row=0, column=0, padx=(10, 10), pady=10, sticky="ew")
        self.entry_message.bind("<Return>", lambda event: self.invia_messaggio())

        # Bottone Invia
        self.btn_send = ctk.CTkButton(self.input_frame, text="Invia Testo", command=self.invia_messaggio)
        self.btn_send.grid(row=0, column=1, padx=(0, 10), pady=10)

        # Bottone Cattura Schermo e Invia
        self.btn_screenshot = ctk.CTkButton(self.input_frame, text="📸 Cattura e Chiedi", fg_color="#2cba00", hover_color="#229200", command=self.avvia_cattura_thread)
        self.btn_screenshot.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        # Messaggio di benvenuto iniziale
        self.aggiungi_messaggio("Jarvis", "Pronto ai tuoi comandi. Posso leggere lo schermo se usi 'Cattura e Chiedi'.")

    def aggiungi_messaggio(self, mittente, testo):
        """Aggiunge un fumetto di testo nella chat in modo ordinato"""
        corpo_testo = f"[{mittente}]: {testo}\n"
        
        # Scegliamo un colore diverso a seconda di chi parla
        colore_testo = "#1f6aa5" if mittente == "Tu" else "#dce4ee"
        if mittente == "Jarvis":
            colore_testo = "#2cc990"

        lbl_msg = ctk.CTkLabel(self.chat_frame, text=corpo_testo, wraplength=500, justify="left", text_color=colore_testo, font=("Consolas", 14))
        lbl_msg.pack(anchor="w", padx=10, pady=5)
        
        # Forza lo scroll verso il basso per vedere l'ultimo messaggio
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def invia_messaggio(self):
        text = self.entry_message.get().strip()
        if not text:
            return
        
        self.aggiungi_messaggio("Tu", text)
        self.entry_message.delete(0, tk.END)
        
        # Eseguiamo la richiesta HTTP in un thread separato per non bloccare la grafica
        threading.Thread(target=self._interagisci_con_server, args=(text, None), daemon=True).start()

    def avvia_cattura_thread(self):
        text = self.entry_message.get().strip()
        if not text:
            text = "Analizza questo schermo e dimmi cosa vedi."
            
        self.aggiungi_messaggio("Tu", f"{text} (Inviando Screenshot...)")
        self.entry_message.delete(0, tk.END)
        
        # Avvia il processo in background
        threading.Thread(target=self._cattura_e_invia, args=(text,), daemon=True).start()

    def _cattura_e_invia(self, prompt):
        # Nasconde temporaneamente la finestra grafica per non includerla nello screenshot
        self.withdraw()
        self.after(300) # Piccolo delay per far sparire la finestra
        
        screenshot_path = "screenshot_temp.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        
        # Mostra di nuovo la finestra grafica
        self.deiconify()

        self._interagisci_con_server(prompt, screenshot_path)

    def _interagisci_con_server(self, prompt, image_path=None):
        try:
            payload = {"prompt": prompt}
            
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    files = {"file": (os.path.basename(image_path), f, "image/png")}
                    response = requests.post(SERVER_URL, data=payload, files=files)
                # Pulisce lo screenshot temporaneo
                os.remove(image_path)
            else:
                response = requests.post(SERVER_URL, data=payload)

            if response.status_code == 200:
                risposta_jarvis = response.json().get("response", "Nessuna risposta ricevuta.")
                self.aggiungi_messaggio("Jarvis", risposta_jarvis)
            else:
                self.aggiungi_messaggio("Errore", f"Il server ha risposto con codice {response.status_code}")
        except Exception as e:
            self.aggiungi_messaggio("Errore", f"Impossibile connettersi al server locale: {e}")

if __name__ == "__main__":
    app = JarvisGUI()
    app.mainloop()