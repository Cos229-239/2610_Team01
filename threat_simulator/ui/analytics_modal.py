import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AnalyticsModal(ctk.CTkToplevel):
    def __init__(self, master, sim_engine):
        super().__init__(master)
        self.title("📊 Live Simulation Analytics & Telemetry")
        self.geometry("720x500")
        self.resizable(False, False)
        self.transient(master)

        self.sim_engine = sim_engine

        # Dark theme background
        self.configure(fg_color="#1e1e1e")

        ctk.CTkLabel(
            self, 
            text="Real-Time Outbreak Spread & Threat Escalation", 
            font=("Consolas", 14, "bold"),
            text_color="#69F0AE"
        ).pack(pady=(15, 5))

        # Setup Matplotlib figure & axes
        self.fig = Figure(figsize=(7.0, 3.8), facecolor="#141414")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#1e1e1e")
        self.ax2 = self.ax.twinx()

        self.canvas_agg = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_agg.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=10)

        # Draw initial data
        self.refresh()

        # Close button
        ctk.CTkButton(
            self, 
            text="Close Analytics", 
            fg_color="#333333", 
            hover_color="#444444", 
            command=self.destroy
        ).pack(pady=(0, 15))

    def refresh(self):
        """Redraws the Matplotlib chart with Infected Count, Threat %, and Escalation Factor (x)."""
        if not self.winfo_exists():
            return

        steps = []
        infected = []
        threat_levels = []
        escalation_factors = []

        if hasattr(self.sim_engine, "history") and self.sim_engine.history:
            for snap in self.sim_engine.history:
                steps.append(snap.step)
                infected.append(snap.telemetry.infected_nodes)
                threat_levels.append(snap.telemetry.threat_level_pct)
                escalation_factors.append(getattr(snap.telemetry, "escalation_factor", 1.0))
        else:
            steps = [0]
            infected = [0]
            threat_levels = [0.0]
            escalation_factors = [1.0]

        # Clear previous lines
        self.ax.clear()
        self.ax2.clear()

        # Re-apply dark styling
        self.ax.set_facecolor("#1e1e1e")
        
        # 1. Primary Axis: Infected Nodes (Red)
        line1 = self.ax.plot(steps, infected, color="#FF1744", marker="o", markersize=3, label="Infected Nodes", linewidth=2)
        self.ax.set_ylabel("Infected Count", color="#FF1744", fontsize=10)
        self.ax.set_xlabel("Simulation Steps", color="white", fontsize=10)

        # 2. Secondary Axis: Threat Level % (Cyan Dashed) & Escalation Factor (Amber Dotted)
        line2 = self.ax2.plot(steps, threat_levels, color="#00E5FF", linestyle="--", label="Threat Level %", linewidth=1.5)
        line3 = self.ax2.plot(steps, escalation_factors, color="#FFB74D", linestyle=":", label="Escalation Factor (x)", linewidth=2)
        
        self.ax2.set_ylabel("Threat % & Escalation Multiplier (x)", color="#00E5FF", fontsize=10)
        self.ax2.set_ylim(0, max(105, max(escalation_factors) * 1.1 if escalation_factors else 100))

        # Styling axis labels, grid, and combined legend
        self.ax.tick_params(colors="white", labelcolor="white")
        self.ax2.tick_params(colors="white", labelcolor="white")
        self.ax.grid(True, color="#333333", linestyle=":", alpha=0.7)
        self.ax.set_title("Live Infection Progression, Threat Level & 100x Escalation", fontsize=11, color="white", pad=10)

        # Combine legends from both axes
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        self.ax.legend(lines, labels, loc="upper left", facecolor="#1e1e1e", edgecolor="#333333", labelcolor="white", fontsize=8)

        self.canvas_agg.draw()