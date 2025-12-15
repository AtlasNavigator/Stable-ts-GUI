import customtkinter
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
import os
import json

class App(customtkinter.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        
        self.title("Stable-TS GUI Transcriber")
        self.geometry("800x700")
        
        # Configure grid layout (1x4)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Settings
        self.grid_rowconfigure(1, weight=1) # Drop Zone & Queue
        self.grid_rowconfigure(2, weight=0) # Terminal
        self.grid_rowconfigure(3, weight=0) # Footer

        self.settings = self.load_settings()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_ui()
        self.after(100, self.check_dependencies)

    def check_dependencies(self):
        self.log_to_terminal("Welcome to Stable-TS GUI Transcriber!")
        self.log_to_terminal("Checking dependencies...")
        
        # Check ffmpeg
        import shutil
        if shutil.which("ffmpeg"):
            self.log_to_terminal("ffmpeg found.")
        else:
            self.log_to_terminal("WARNING: ffmpeg not found! Transcription may fail.")
            self.log_to_terminal("Please install ffmpeg and add it to your PATH.")

        self.log_to_terminal("Ready to transcribe.")

    def setup_ui(self):
        # --- Settings Section ---
        self.settings_frame = customtkinter.CTkFrame(self)
        self.settings_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        # Model
        self.model_label = customtkinter.CTkLabel(self.settings_frame, text="Model:")
        self.model_label.grid(row=0, column=0, padx=5, pady=5)
        self.model_var = customtkinter.StringVar(value=self.settings.get("model", "small"))
        self.model_option = customtkinter.CTkOptionMenu(self.settings_frame, variable=self.model_var, 
                                                        values=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"])
        self.model_option.grid(row=0, column=1, padx=5, pady=5)

        # Language
        self.lang_label = customtkinter.CTkLabel(self.settings_frame, text="Language:")
        self.lang_label.grid(row=0, column=2, padx=5, pady=5)
        
        self.languages = ["Auto", "en", "zh", "de", "es", "ru", "ko", "fr", "ja", "pt", "tr", "pl", "ca", "nl", "ar", "sv", "it", "id", "hi", "fi", "vi", "he", "uk", "el", "ms", "cs", "ro", "da", "hu", "ta", "no", "th", "ur", "hr", "bg", "lt", "la", "mi", "ml", "cy", "sk", "te", "fa", "lv", "bn", "sr", "az", "sl", "kn", "et", "mk", "br", "eu", "is", "hy", "ne", "mn", "bs", "kk", "sq", "sw", "gl", "mr", "pa", "si", "km", "sn", "yo", "so", "af", "oc", "ka", "be", "tg", "sd", "gu", "am", "yi", "lo", "uz", "fo", "ht", "ps", "tk", "nn", "mt", "sa", "lb", "my", "bo", "tl", "mg", "as", "tt", "haw", "ln", "ha", "ba", "jw", "su"]
        self.lang_var = customtkinter.StringVar(value=self.settings.get("language", "Auto"))
        self.lang_combo = customtkinter.CTkComboBox(self.settings_frame, variable=self.lang_var, values=self.languages)
        self.lang_combo.grid(row=0, column=3, padx=5, pady=5)
        self.lang_combo._entry.bind("<KeyRelease>", self.filter_languages)

        # Format
        self.format_label = customtkinter.CTkLabel(self.settings_frame, text="Format:")
        self.format_label.grid(row=0, column=4, padx=5, pady=5)
        self.format_var = customtkinter.StringVar(value=self.settings.get("format", "vtt"))
        self.format_option = customtkinter.CTkOptionMenu(self.settings_frame, variable=self.format_var,
                                                         values=["vtt", "srt", "txt", "json"])
        self.format_option.grid(row=0, column=5, padx=5, pady=5)

        # --- Middle Section (Drop Zone & Queue) ---
        self.middle_frame = customtkinter.CTkFrame(self)
        self.middle_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.middle_frame.grid_columnconfigure(0, weight=1)
        self.middle_frame.grid_rowconfigure(2, weight=1)

        # Drop Zone
        self.drop_frame = customtkinter.CTkFrame(self.middle_frame, fg_color=("gray85", "gray25"))
        self.drop_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.drop_label = customtkinter.CTkLabel(self.drop_frame, text="Drag & Drop Video Files Here\nor Click to Select",
                                                 font=("Roboto", 16))
        self.drop_label.pack(pady=20)
        
        # Enable Drag & Drop
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.drop_files)
        self.drop_label.bind("<Button-1>", self.open_file_dialog)
        self.drop_frame.bind("<Button-1>", self.open_file_dialog)

        # Queue List
        self.queue_header_frame = customtkinter.CTkFrame(self.middle_frame, fg_color="transparent")
        self.queue_header_frame.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")
        
        self.queue_label = customtkinter.CTkLabel(self.queue_header_frame, text="Queue:", anchor="w")
        self.queue_label.pack(side="left")
        
        self.clear_btn = customtkinter.CTkButton(self.queue_header_frame, text="Clear Queue", width=80, height=24, fg_color="firebrick", command=self.clear_queue)
        self.clear_btn.pack(side="right")
        
        self.queue_frame = customtkinter.CTkScrollableFrame(self.middle_frame, label_text="Pending Files")
        self.queue_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        self.file_list = [] # List to store file paths

        # --- Terminal Section ---
        self.terminal_frame = customtkinter.CTkFrame(self)
        self.terminal_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.terminal_frame.grid_columnconfigure(0, weight=1)
        
        self.terminal_label = customtkinter.CTkLabel(self.terminal_frame, text="Terminal Output:", anchor="w")
        self.terminal_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        self.terminal_textbox = customtkinter.CTkTextbox(self.terminal_frame, height=150, font=("Consolas", 12))
        self.terminal_textbox.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.terminal_textbox.configure(state="disabled")

        # --- Footer Section ---
        self.footer_frame = customtkinter.CTkFrame(self)
        self.footer_frame.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.footer_frame.grid_columnconfigure(1, weight=1)

        self.start_button = customtkinter.CTkButton(self.footer_frame, text="Start Transcription", command=self.start_transcription)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = customtkinter.CTkButton(self.footer_frame, text="Stop", fg_color="firebrick", state="disabled", command=self.stop_transcription)
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        self.progress_bar = customtkinter.CTkProgressBar(self.footer_frame)
        self.progress_bar.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.progress_bar.set(0)

        self.status_label = customtkinter.CTkLabel(self.footer_frame, text="Pending: 0 | Completed: 0")
        self.status_label.grid(row=0, column=3, padx=10, pady=10)

    def drop_files(self, event):
        files = self.tk.splitlist(event.data)
        for f in files:
            self.add_file_to_queue(f)

    def open_file_dialog(self, event=None):
        files = customtkinter.filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov *.flv *.wmv"), ("All Files", "*.*")])
        for f in files:
            self.add_file_to_queue(f)

    def add_file_to_queue(self, file_path):
        if file_path not in self.file_list:
            self.file_list.append(file_path)
            
            item_frame = customtkinter.CTkFrame(self.queue_frame)
            item_frame.pack(fill="x", padx=5, pady=2)
            
            label = customtkinter.CTkLabel(item_frame, text=os.path.basename(file_path), anchor="w")
            label.pack(side="left", padx=5, fill="x", expand=True)
            
            remove_btn = customtkinter.CTkButton(item_frame, text="✕", width=24, height=24, fg_color="firebrick", 
                                                 command=lambda f=file_path, fr=item_frame: self.remove_file_from_queue(f, fr))
            remove_btn.pack(side="right", padx=5)
            
            self.update_status()

    def clear_queue(self):
        self.file_list = []
        for widget in self.queue_frame.winfo_children():
            widget.destroy()
        self.update_status()

    def filter_languages(self, event):
        value = self.lang_var.get().lower()
        if value == "":
            self.lang_combo.configure(values=self.languages)
        else:
            filtered = [lang for lang in self.languages if value in lang.lower()]
            self.lang_combo.configure(values=filtered)

    def update_status(self):
        self.status_label.configure(text=f"Pending: {len(self.file_list)} | Completed: 0")

    def start_transcription(self):
        if not self.file_list:
            self.log_to_terminal("No files in queue.")
            return

        model = self.model_var.get()
        language = self.lang_var.get()
        output_format = self.format_var.get()

        self.start_button.configure(state="disabled", text="Processing...")
        self.stop_button.configure(state="normal")
        self.log_to_terminal(f"Starting transcription with Model: {model}, Language: {language}, Format: {output_format}")

        # Initialize manager if not already done
        if not hasattr(self, 'manager'):
            from transcriber import TranscriptionManager
            self.manager = TranscriptionManager(self.update_from_thread, self.progress_update)

        self.manager.start(self.file_list, model, language, output_format, app=self)

    def update_from_thread(self, message):
        self.after(0, self.log_to_terminal, message)

    def progress_update(self, completed, total):
        self.after(0, self._update_progress_ui, completed, total)

    def _update_progress_ui(self, completed, total):
        progress = completed / total
        self.progress_bar.set(progress)
        self.status_label.configure(text=f"Pending: {total - completed} | Completed: {completed}")
        if completed == total:
            self.start_button.configure(state="normal", text="Start Transcription")
            self.stop_button.configure(state="disabled")
            # self.file_list = [] # Keep queue for now
            # Actually, clearing the queue visual might be confusing if they want to see what was done.
            # For now, let's just reset the button.

    def log_to_terminal(self, message):
        self.terminal_textbox.configure(state="normal")
        self.terminal_textbox.insert("end", message + "\n")
        self.terminal_textbox.see("end")
        self.terminal_textbox.configure(state="disabled")

    def stop_transcription(self):
        if hasattr(self, 'manager') and self.manager.is_running:
            self.log_to_terminal("Stopping transcription...")
            self.manager.stop()
            self.stop_button.configure(state="disabled")
            self.start_button.configure(state="normal", text="Start Transcription")

    def remove_file_from_queue(self, file_path, frame_widget):
        if file_path in self.file_list:
            self.file_list.remove(file_path)
            frame_widget.destroy()
            self.update_status()

    def load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return {}

    def save_settings(self):
        settings = {
            "model": self.model_var.get(),
            "language": self.lang_var.get(),
            "format": self.format_var.get()
        }
        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f)
        except Exception as e:
            self.log_to_terminal(f"Error saving settings: {e}")

    def on_closing(self):
        self.save_settings()
        if hasattr(self, 'manager') and self.manager.is_running:
            self.manager.stop()
        self.destroy()
