import os
import io
import tkinter as tk
import customtkinter as ctk
import pyautogui
import requests
import threading

# Configurazione Grafica Professionale
ctk.set_appearance_mode("Dark")  # Forza il tema scuro elegante
ctk.set_default_color_theme("blue")

SERVER_URL = "http://127.0.0.1:8000/chat"

class JarvisProGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Finestra Principale ---
        self.title("Jarvis Vision - Pro Edition")
        self.geometry("850x700")
        self.minsize(700, 500)

        # Layout a griglia 1 riga, 2 colonne (Sidebar + Main)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1) # La colonna chat si espande

        # ==========================================
        # 1. BARRA LATERALE (SIDEBAR)
        # ==========================================
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1) # Spinge gli elementi in alto e in basso

        self.logo_label = ctk.CTkLabel(self.sidebar, text="JARVIS\nVISION", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        self.status_label = ctk.CTkLabel(self.sidebar, text="🟢 Server Online", text_color="#2cc990", font=ctk.CTkFont(size=14))
        self.status_label.grid(row=1, column=0, padx=20, pady=10)

        # Spazio vuoto centrale gestito dal rowconfigure
        
        self.info_label = ctk.CTkLabel(self.sidebar, text="Modello: Gemini 2.5 Flash\nStatus: Pronto", font=ctk.CTkFont(size=12), text_color="gray")
        self.info_label.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="s")

        # ==========================================
        # 2. AREA CHAT PRINCIPALE
        # ==========================================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Chatbox Scorrevole
        self.chat_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="#1e1e1e", corner_radius=15)
        self.chat_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))

        # Barra di caricamento animata (nascosta di default)
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, mode="indeterminate", height=4)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.progress_bar.set(0)
        self.progress_bar.grid_remove() # Nascosta all'avvio

        # ==========================================
        # 3. AREA INPUT E COMANDI
        # ==========================================
        self.input_area = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_area.grid(row=2, column=0, sticky="ew")
        self.input_area.grid_columnconfigure(0, weight=1)

        self.entry_message = ctk.CTkEntry(self.input_area, placeholder_text="Scrivi a Jarvis...", height=45, corner_radius=20)
        self.entry_message.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry_message.bind("<Return>", lambda event: self.invia_messaggio())

        self.btn_send = ctk.CTkButton(self.input_area, text="Invia", height=45, corner_radius=20, width=80, command=self.invia_messaggio)
        self.btn_send.grid(row=0, column=1, padx=(0, 10))

        self.btn_screenshot = ctk.CTkButton(self.input_area, text="📸 Analizza Schermo", height=45, corner_radius=20, fg_color="#2cba00", hover_color="#229200", command=self.avvia_cattura)
        self.btn_screenshot.grid(row=0, column=2)

        # Messaggio di benvenuto
        self.aggiungi_messaggio("Jarvis", "Sistemi online. Interfaccia operativa. Come posso assisterti?")

    # ==========================================
    # LOGICA DELL'INTERFACCIA
    # ==========================================
    def aggiungi_messaggio(self, mittente, testo):
        """Formatta e aggiunge i messaggi alla chat"""
        is_user = mittente == "Tu"
        
        # Frame contenitore per il singolo messaggio
        msg_box = ctk.CTkFrame(self.chat_frame, fg_color="#2b2b2b" if is_user else "transparent", corner_radius=10)
        msg_box.pack(anchor="e" if is_user else "w", padx=10, pady=5, fill="x")

        # Scelta del colore del testo (Corretto qui!)
        colore_nome = "#3a7ebf" if is_user else "#2cc990"

        # Intestazione (Nome)
        lbl_name = ctk.CTkLabel(msg_box, text=mittente, font=ctk.CTkFont(weight="bold", size=12), text_color=colore_nome)
        lbl_name.pack(anchor="w", padx=10, pady=(5, 0))

        # Corpo del testo
        lbl_text = ctk.CTkLabel(msg_box, text=testo, wraplength=550, justify="left", font=ctk.CTkFont(size=14))
        lbl_text.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Scroll automatico verso il basso
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def _stato_caricamento(self, attivo):
        """Attiva o disattiva le animazioni e i pulsanti"""
        if attivo:
            self.btn_send.configure(state="disabled")
            self.btn_screenshot.configure(state="disabled")
            self.entry_message.configure(state="disabled")
            self.progress_bar.grid()
            self.progress_bar.start() # Avvia l'animazione della barra progressiva
        else:
            self.btn_send.configure(state="normal")
            self.btn_screenshot.configure(state="normal")
            self.entry_message.configure(state="normal")
            self.progress_bar.stop()
            self.progress_bar.grid_remove()

    def invia_messaggio(self):
        text = self.entry_message.get().strip()
        if not text: return
        
        self.aggiungi_messaggio("Tu", text)
        self.entry_message.delete(0, tk.END)
        self._stato_caricamento(True)
        
        threading.Thread(target=self._chiama_server, args=(text, None), daemon=True).start()

    def avvia_cattura(self):
        text = self.entry_message.get().strip() or "Analizza questo schermo nel dettaglio."
        
        self.aggiungi_messaggio("Tu", f"📸 [Screenshot Inviato] {text}")
        self.entry_message.delete(0, tk.END)
        self._stato_caricamento(True)
        
        threading.Thread(target=self._cattura_e_invia, args=(text,), daemon=True).start()

    def _cattura_e_invia(self, prompt):
        self.withdraw() # Nasconde la GUI temporaneamente
        self.after(300) 
        
        screenshot_path = "temp_screen.png"
        pyautogui.screenshot().save(screenshot_path)
        
        self.deiconify() # Mostra di nuovo la GUI
        self._chiama_server(prompt, screenshot_path)

    def _chiama_server(self, prompt, image_path):
        try:
            payload = {"prompt": prompt}
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    files = {"file": (os.path.basename(image_path), f, "image/png")}
                    response = requests.post(SERVER_URL, data=payload, files=files)
                os.remove(image_path)
            else:
                response = requests.post(SERVER_URL, data=payload)

            if response.status_code == 200:
                risposta = response.json().get("response", "Errore: Nessuna risposta.")
            else:
                risposta = f"Errore server: {response.status_code}"
                
        except Exception as e:
            risposta = f"Impossibile connettersi al server: {e}"

        # Aggiorna la GUI in modo sicuro sul thread principale
        self.after(0, self._concludi_chiamata, risposta)

    def _concludi_chiamata(self, risposta):
        self._stato_caricamento(False)
        self.aggiungi_messaggio("Jarvis", risposta)

if __name__ == "__main__":
    app = JarvisProGUI()
    app.mainloop()