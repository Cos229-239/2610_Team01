import customtkinter as ctk
from core.simulation import TelemetryData

class TelemetryPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="Live Telemetry & Metrics", font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=10)

        self.log_box = ctk.CTkTextbox(self, font=("Courier", 12))
        self.log_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def append_log(self, data: TelemetryData):
        self.log_box.insert("end", data.format_log())
        self.log_box.see("end")

    def clear(self):
        self.log_box.delete("1.0", "end")
