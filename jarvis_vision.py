"""
Jarvis Vision - Interfaccia ispirata alla GUI di Gemini.
Layout a flusso continuo con testo ad andamento naturale e barra di input a pillola.
Il codice separa la gestione grafica dai thread di rete per garantire la massima fluidità.
"""

import os
import io
import tkinter as tk
import customtkinter as ctk
import pyautogui
import requests
import threading

# Palette colori nativa di Gemini (Dark Mode)
# Grigio quasi nero per lo sfondo principale e grigio scuro per gli elementi in rilievo
COR_SFONDO_PRINCIPALE = "#131314"
COR_SFONDO_PANNELLI = "#1e1f20"
COR_TESTO_UTENTE = "#e3e3e3"
COR_ACCENTO_JARVIS = "#9bbaff"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

SERVER_URL = "http://127.0.0.1:8000/chat"


class JarvisProGUI(ctk.CTk):
    """Finestra principale dell'applicazione con design minimalista a singola colonna di lettura."""

    def __init__(self):
        super().__init__()

        # Configurazione geometrica della finestra principale
        self.title("Jarvis Vision")
        self.geometry("900x750")
        self.minsize(750, 550)
        self.configure(fg_color=COR_SFONDO_PRINCIPALE)

        # Griglia principale: la barra laterale (colonna 0) ha dimensione fissa,
        # l'area di lavoro (colonna 1) si espande per occupare tutto lo spazio.
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Inizializzazione dei tre macro-componenti dell'interfaccia
        self._costruisci_sidebar()
        self._costruisci_area_chat()
        self._costruisci_barra_input()

        # Messaggio iniziale di sistema stampato al caricamento
        self.aggiungi_messaggio("Jarvis", "Sistemi online. Interfaccia operativa. Come posso assisterti?")

    def _costruisci_sidebar(self):
        """Crea la barra laterale sinistra per la gestione dello stato dell'applicazione."""
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=COR_SFONDO_PANNELLI, border_width=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Gestione dello spazio verticale: la riga 3 spinge i dettagli tecnici verso il basso
        self.sidebar.grid_rowconfigure(3, weight=1)

        # Titolo dell'applicazione nella barra laterale
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Jarvis Vision", font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"), text_color="#ffffff")
        self.logo_label.grid(row=0, column=0, padx=25, pady=(35, 10), sticky="w")

        # Indicatore di stato della connessione locale
        self.status_label = ctk.CTkLabel(self.sidebar, text="🟢 Connesso", text_color="#2cc990", font=ctk.CTkFont(family="Segoe UI", size=13))
        self.status_label.grid(row=1, column=0, padx=25, pady=5, sticky="w")

        # Etichetta informativa posizionata sul fondo della sidebar
        self.info_label = ctk.CTkLabel(self.sidebar, text="Modello: Gemini 2.5 Flash\nInterfaccia: Desktop Pro", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#808082", justify="left")
        self.info_label.grid(row=4, column=0, padx=25, pady=25, sticky="sw")

    def _costruisci_area_chat(self):
        """Crea lo spazio centrale flessibile in cui scorrono i messaggi della conversazione."""
        self.main_frame = ctk.CTkFrame(self, fg_color=COR_SFONDO_PRINCIPALE)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=(20, 10))
        
        # Espansione verticale totale assegnata alla griglia dei messaggi
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Contenitore dei messaggi con scorrimento verticale integrato
        self.chat_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color=COR_SFONDO_PRINCIPALE, corner_radius=0)
        self.chat_frame.grid(row=0, column=0, sticky="nsew")

        # Barra di caricamento lineare posizionata subito sotto il flusso della chat
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, mode="indeterminate", height=3, fg_color=COR_SFONDO_PRINCIPALE, progress_color=COR_ACCENTO_JARVIS)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()

    def _costruisci_barra_input(self):
        """Disegna la barra di input a forma di pillola ispirata direttamente al design di Gemini."""
        # Frame esterno che funge da riga di posizionamento inferiore
        self.bottom_frame = ctk.CTkFrame(self, fg_color=COR_SFONDO_PRINCIPALE)
        self.bottom_frame.grid(row=1, column=1, sticky="ew", padx=30, pady=(0, 25))
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        # La "Pillola": Contenitore arrotondato compatto che racchiude testo e pulsanti d'azione
        self.pill_container = ctk.CTkFrame(self.bottom_frame, fg_color=COR_SFONDO_PANNELLI, corner_radius=28, height=56)
        self.pill_container.grid(row=0, column=0, sticky="ew")
        self.pill_container.grid_columnconfigure(0, weight=1)
        self.pill_container.grid_propagate(False) # Blocca l'altezza minima per non far deformare la pillola

        # Campo di testo interno senza bordi evidenti per un effetto di fusione con il pannello
        self.entry_message = ctk.CTkEntry(
            self.pill_container, 
            placeholder_text="Chiedi a Jarvis o analizza lo schermo...", 
            fg_color="transparent", 
            border_width=0,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COR_TESTO_UTENTE
        )
        self.entry_message.grid(row=0, column=0, padx=(20, 10), sticky="ew")
        self.entry_message.bind("<Return>", lambda event: self.invia_messaggio())
        
        # Allineamento verticale del campo testo all'interno della pillola
        self.pill_container.grid_rowconfigure(0, weight=1)

        # Pulsante per lo screenshot integrato sul lato destro della pillola
        self.btn_screenshot = ctk.CTkButton(
            self.pill_container, 
            text="📸", 
            width=40, 
            height=36, 
            corner_radius=18, 
            fg_color="transparent", 
            hover_color="#2d2f31", 
            font=ctk.CTkFont(size=16),
            command=self.avvia_cattura
        )
        self.btn_screenshot.grid(row=0, column=1, padx=2)

        # Pulsante di invio testo posizionato all'estremità destra all'interno della pillola
        self.btn_send = ctk.CTkButton(
            self.pill_container, 
            text="➔", 
            width=40, 
            height=36, 
            corner_radius=18, 
            fg_color="transparent", 
            hover_color="#2d2f31", 
            font=ctk.CTkFont(size=16),
            text_color=COR_ACCENTO_JARVIS,
            command=self.invia_messaggio
        )
        self.btn_send.grid(row=0, column=2, padx=(2, 15))

    def aggiungi_messaggio(self, mittente, testo):
        """Inserisce un blocco di testo nel flusso continuo della conversazione con a capo automatico."""
        is_user = mittente == "Tu"
        colore_nome = "#ffffff" if is_user else COR_ACCENTO_JARVIS

        # Creazione di un blocco invisibile di riga per distanziare i paragrafi della conversazione
        row_box = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        row_box.pack(fill="x", padx=40, pady=12, anchor="w")

        # Intestazione del mittente (Nome)
        lbl_name = ctk.CTkLabel(
            row_box, 
            text=mittente, 
            font=ctk.CTkFont(family="Segoe UI", weight="bold", size=13), 
            text_color=colore_nome
        )
        lbl_name.pack(anchor="w", pady=(0, 4))

        # Testo del messaggio a scorrimento e andamento naturale.
        # wraplength=580 costringe le frasi ad andare a capo automaticamente a fine riga,
        # eliminando la necessità di barre di scorrimento orizzontali e mantenendo la lettura pulita.
        lbl_text = ctk.CTkLabel(
            row_box, 
            text=testo, 
            wraplength=580, 
            justify="left", 
            font=ctk.CTkFont(family="Segoe UI", size=14), 
            text_color=COR_TESTO_UTENTE
        )
        lbl_text.pack(anchor="w")
        
        # Forza la finestra di scorrimento a spostarsi verso l'elemento più recente inserito in fondo
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def _stato_caricamento(self, attivo):
        """Controlla lo stato dei componenti durante l'invio dei dati per simulare l'attesa di sistema."""
        if attivo:
            self.btn_send.configure(state="disabled")
            self.btn_screenshot.configure(state="disabled")
            self.entry_message.configure(state="disabled")
            self.progress_bar.grid()
            self.progress_bar.start()
        else:
            self.btn_send.configure(state="normal")
            self.btn_screenshot.configure(state="normal")
            self.entry_message.configure(state="normal")
            self.progress_bar.stop()
            self.progress_bar.grid_remove()

    def invia_messaggio(self):
        """Estrae l'input testuale dell'utente e lo invia al processo in background."""
        text = self.entry_message.get().strip()
        if not text: 
            return
        
        self.aggiungi_messaggio("Tu", text)
        self.entry_message.delete(0, tk.END)
        self._stato_caricamento(True)
        
        # Il thread secondario previene il congelamento dell'interfaccia durante i tempi di risposta delle API
        threading.Thread(target=self._chiama_server, args=(text, None), daemon=True).start()

    def avvia_cattura(self):
        """Prepara l'interfaccia per l'acquisizione dell'immagine dello schermo."""
        text = self.entry_message.get().strip() or "Analizza questo schermo nel dettaglio."
        
        self.aggiungi_messaggio("Tu", f"📸 [Analisi Schermo Richiesta] {text}")
        self.entry_message.delete(0, tk.END)
        self._stato_caricamento(True)
        
        threading.Thread(target=self._cattura_e_invia, args=(text,), daemon=True).start()

    def _cattura_e_invia(self, prompt):
        """Nasconde temporaneamente la finestra per effettuare lo screenshot del desktop sottostante."""
        self.withdraw()
        self.after(300) # Pausa tecnica per dare il tempo al sistema operativo di elaborare la scomparsa della GUI
        
        screenshot_path = "temp_screen.png"
        pyautogui.screenshot().save(screenshot_path)
        
        self.deiconify() # Ripristina la visibilità della GUI subito dopo lo scatto
        self._chiama_server(prompt, screenshot_path)

    def _chiama_server(self, prompt, image_path):
        """Esegue materialmente la richiesta POST verso il backend locale FastAPI."""
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
                risposta = response.json().get("response", "Errore: Risposta vuota dal server.")
            else:
                risposta = f"Errore di comunicazione: Codice HTTP {response.status_code}"
                
        except Exception as e:
            risposta = f"Connessione fallita. Assicurati che il server FastAPI sia attivo. Dettaglio: {e}"

        # Ritorno sicuro sul thread principale di Tkinter per mostrare il testo ricevuto
        self.after(0, self._concludi_chiamata, risposta)

    def _concludi_chiamata(self, risposta):
        """Ripristina i controlli di input e mostra la risposta dell'intelligenza artificiale."""
        self._stato_caricamento(False)
        self.aggiungi_messaggio("Jarvis", risposta)


if __name__ == "__main__":
    app = JarvisProGUI()
    app.mainloop()