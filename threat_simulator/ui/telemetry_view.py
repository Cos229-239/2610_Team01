import customtkinter as ctk
from core.simulation import TelemetryData

class TelemetryPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            self, text="Live Telemetry & Metrics", font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Live Metrics Strip
        metrics_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        metrics_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Time
        ctk.CTkLabel(metrics_frame, text="Time", font=("Arial", 11)).grid(
            row=0, column=0, padx=5, pady=(8, 0)
        )
        self.time_label = ctk.CTkLabel(
            metrics_frame, text="0s", font=("Arial", 18, "bold")
        )
        self.time_label.grid(row=1, column=0, padx=5, pady=(0, 8))

        # Infected
        ctk.CTkLabel(metrics_frame, text="Infected", font=("Arial", 11)).grid(
            row=0, column=1, padx=5, pady=(8, 0)
        )
        self.infected_label = ctk.CTkLabel(
            metrics_frame, text="0 / 0", font=("Arial", 18, "bold")
        )
        self.infected_label.grid(row=1, column=1, padx=5, pady=(0, 8))

        # Threat
        ctk.CTkLabel(metrics_frame, text="Threat", font=("Arial", 11)).grid(
            row=0, column=2, padx=5, pady=(8, 0)
        )
        self.threat_label = ctk.CTkLabel(
            metrics_frame, text="0.0%", font=("Arial", 18, "bold")
        )
        self.threat_label.grid(row=1, column=2, padx=5, pady=(0, 8))

        # Status
        ctk.CTkLabel(metrics_frame, text="Status", font=("Arial", 11)).grid(
            row=0, column=3, padx=5, pady=(8, 0)
        )
        self.status_label = ctk.CTkLabel(
            metrics_frame, text="IDLE", font=("Arial", 14, "bold")
        )
        self.status_label.grid(row=1, column=3, padx=5, pady=(0, 8))

        # Scrolling Log
        self.log_box = ctk.CTkTextbox(self, font=("Courier", 12))
        self.log_box.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    def append_log(self, data: TelemetryData):
        # Update live metrics
        self.time_label.configure(text=f"{data.sim_time_seconds}s")
        self.infected_label.configure(
            text=f"{data.infected_nodes} / {data.total_nodes}"
        )
        self.threat_label.configure(text=f"{data.threat_level_pct:.1f}%")
        self.status_label.configure(text=data.status)

        # Colour the threat / status labels for quick visual feedback
        if data.threat_level_pct > 75:
            self.threat_label.configure(text_color="#FF5252")
            self.status_label.configure(text_color="#FF5252")
        elif data.threat_level_pct > 40:
            self.threat_label.configure(text_color="#FFB74D")
            self.status_label.configure(text_color="#FFB74D")
        else:
            self.threat_label.configure(text_color=("#2E7D32", "#69F0AE"))
            self.status_label.configure(text_color=("#2E7D32", "#69F0AE"))

        # Append to history log
        self.log_box.insert("end", data.format_log())
        self.log_box.see("end")

    def clear(self):
        self.log_box.delete("1.0", "end")
        self.time_label.configure(text="0s")
        self.infected_label.configure(text="0 / 0")
        self.threat_label.configure(text="0.0%", text_color=("gray10", "gray90"))
        self.status_label.configure(text="IDLE", text_color=("gray10", "gray90"))
    
    
    
    """
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
"""