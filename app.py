import customtkinter as ctk
import tkinter as tk
import sim_engine
import math
import random

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Adaptive AI Outbreak & Threat Simulator")
        
        # Start maximized or fallback to a standard aspect ratio
        self.geometry("1100x750")

        self.step_counter = 0
        self.is_running = False
        self.loop_job = None

        self.nodes = []
        self.edges = []

        self.steps_history = []
        self.threat_history = []
        self.infected_history = []

        # Grid Layout Configuration - Balanced Row Weights
        self.grid_rowconfigure(0, weight=3) # Canvas & Log
        self.grid_rowconfigure(1, weight=2) # Matplotlib Plot
        self.grid_rowconfigure(2, weight=1) # Controls & Sliders
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Top Left: Interactive Network Canvas
        self.canvas_frame = ctk.CTkFrame(self, corner_radius=10)
        self.canvas_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        self.canvas_label = ctk.CTkLabel(self.canvas_frame, text="Interactive Network Canvas", font=("Arial", 14, "bold"))
        self.canvas_label.pack(pady=2)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(padx=5, pady=5, fill="both", expand=True)

        # 2. Top Right: Live Log Feed
        self.telemetry_frame = ctk.CTkFrame(self, corner_radius=10)
        self.telemetry_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        self.telemetry_label = ctk.CTkLabel(self.telemetry_frame, text="Live Telemetry & Metrics", font=("Arial", 14, "bold"))
        self.telemetry_label.pack(pady=2)

        self.log_box = ctk.CTkTextbox(self.telemetry_frame, width=380, height=180)
        self.log_box.pack(padx=5, pady=5, fill="both", expand=True)

        # 3. Middle Section: Real-Time Matplotlib Telemetry Plot
        self.plot_frame = ctk.CTkFrame(self, corner_radius=10)
        self.plot_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        self.init_matplotlib_figure()

        # 4. Bottom Panel: Playback Controls & Dynamic Parameters
        self.control_frame = ctk.CTkFrame(self, corner_radius=10)
        self.control_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        # Buttons
        self.btn_play = ctk.CTkButton(self.control_frame, text="Play", command=self.play_sim, fg_color="#2FA572", hover_color="#1E6B49", width=80)
        self.btn_play.pack(side="left", padx=10, pady=10)

        self.btn_pause = ctk.CTkButton(self.control_frame, text="Pause", command=self.pause_sim, fg_color="#D35B58", hover_color="#8E3C3A", width=80)
        self.btn_pause.pack(side="left", padx=5, pady=10)

        self.btn_reset = ctk.CTkButton(self.control_frame, text="Reset", command=self.reset_sim, fg_color="#555555", hover_color="#333333", width=80)
        self.btn_reset.pack(side="left", padx=5, pady=10)

        # Sliders
        self.lbl_inf = ctk.CTkLabel(self.control_frame, text="Infection Rate:", font=("Arial", 11, "bold"))
        self.lbl_inf.pack(side="left", padx=(15, 2), pady=10)
        self.slider_infection = ctk.CTkSlider(self.control_frame, from_=0.1, to=3.0, number_of_steps=29, width=130)
        self.slider_infection.set(1.2)
        self.slider_infection.pack(side="left", padx=5, pady=10)

        self.lbl_def = ctk.CTkLabel(self.control_frame, text="Defense Power:", font=("Arial", 11, "bold"))
        self.lbl_def.pack(side="left", padx=(15, 2), pady=10)
        self.slider_defense = ctk.CTkSlider(self.control_frame, from_=0.1, to=3.0, number_of_steps=29, width=130)
        self.slider_defense.set(1.0)
        self.slider_defense.pack(side="left", padx=5, pady=10)

        self.after(200, self.init_network_graph)

    def init_matplotlib_figure(self):
        # Compact figure size (figsize height set to 1.8)
        self.fig = Figure(figsize=(8, 1.8), dpi=100, facecolor="#2b2b2b")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#1a1a1a")

        self.ax.tick_params(colors="white", labelsize=7)
        self.ax.spines['bottom'].set_color('#555555')
        self.ax.spines['top'].set_color('#555555')
        self.ax.spines['left'].set_color('#555555')
        self.ax.spines['right'].set_color('#555555')

        self.ax.set_title("Real-Time Threat & Infection Progression", color="white", fontsize=9, fontweight="bold")
        self.ax.set_xlabel("Simulation Step", color="white", fontsize=7)
        self.ax.set_ylabel("Threat Level (%)", color="white", fontsize=7)

        self.line_threat, = self.ax.plot([], [], color="#FF4B4B", linewidth=2, label="Threat Level %")
        self.line_infected, = self.ax.plot([], [], color="#3399FF", linewidth=2, linestyle="--", label="Infected Count")

        self.ax.legend(loc="upper left", facecolor="#2b2b2b", edgecolor="none", labelcolor="white", fontsize=7)

        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(padx=5, pady=2, fill="both", expand=True)

    def init_network_graph(self):
        self.canvas.delete("all")
        self.nodes.clear()
        self.edges.clear()

        width = self.canvas.winfo_width() or 400
        height = self.canvas.winfo_height() or 250
        center_x, center_y = width / 2, height / 2
        radius = min(width, height) * 0.35

        num_nodes = 25
        for i in range(num_nodes):
            angle = (2 * math.pi / num_nodes) * i
            x = center_x + radius * math.cos(angle) + random.randint(-10, 10)
            y = center_y + radius * math.sin(angle) + random.randint(-10, 10)
            self.nodes.append({"x": x, "y": y, "status": "healthy"})

        for i in range(num_nodes):
            next_node = (i + 1) % num_nodes
            cross_node = (i + 7) % num_nodes
            line1 = self.canvas.create_line(self.nodes[i]["x"], self.nodes[i]["y"], self.nodes[next_node]["x"], self.nodes[next_node]["y"], fill="#333333", width=2)
            line2 = self.canvas.create_line(self.nodes[i]["x"], self.nodes[i]["y"], self.nodes[cross_node]["x"], self.nodes[cross_node]["y"], fill="#222222", width=1)
            self.edges.extend([line1, line2])

        for i, node in enumerate(self.nodes):
            r = 7
            oval = self.canvas.create_oval(node["x"]-r, node["y"]-r, node["x"]+r, node["y"]+r, fill="#17B890", outline="#0E6B53", width=2)
            node["oval_id"] = oval

    def play_sim(self):
        if not self.is_running:
            self.is_running = True
            if self.loop_job:
                self.after_cancel(self.loop_job)
                self.loop_job = None
            self.run_loop()

    def pause_sim(self):
        self.is_running = False
        if self.loop_job is not None:
            self.after_cancel(self.loop_job)
            self.loop_job = None

    def reset_sim(self):
        self.pause_sim()
        self.step_counter = 0
        
        self.steps_history.clear()
        self.threat_history.clear()
        self.infected_history.clear()
        
        self.line_threat.set_data([], [])
        self.line_infected.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.chart_canvas.draw()

        self.log_box.delete("1.0", "end")
        self.log_box.insert("end", "[SYSTEM] Simulation state reset.\n" + "-"*40 + "\n")
        self.init_network_graph()

    def update_canvas_visuals(self, infected_count, defense_count):
        for i, node in enumerate(self.nodes):
            if i < infected_count // 4:
                color, outline = "#FF4B4B", "#990000"
            elif i < (infected_count // 4) + (defense_count // 4):
                color, outline = "#1F78B4", "#0D324D"
            else:
                color, outline = "#17B890", "#0E6B53"

            self.canvas.itemconfig(node["oval_id"], fill=color, outline=outline)

    def update_plot(self, step, threat_pct, infected_count):
        self.steps_history.append(step)
        self.threat_history.append(threat_pct)
        self.infected_history.append(infected_count)

        self.line_threat.set_data(self.steps_history, self.threat_history)
        self.line_infected.set_data(self.steps_history, self.infected_history)

        self.ax.relim()
        self.ax.autoscale_view()
        self.chart_canvas.draw_idle()

    def run_loop(self):
        if not self.is_running:
            return

        self.step_counter += 1

        inf_rate = float(self.slider_infection.get())
        def_power = float(self.slider_defense.get())
        
        telemetry = sim_engine.run_step_telemetry(self.step_counter, inf_rate, def_power)

        log_entry = (
            f"[STEP {telemetry['step']}] Status: {telemetry['status']}\n"
            f" ├─ Infection Rate: {inf_rate:.1f}x | Defense Power: {def_power:.1f}x\n"
            f" ├─ Infected Nodes: {telemetry['infected_nodes']}/{telemetry['total_nodes']}\n"
            f" ├─ Active Defenses: {telemetry['active_defenses']}\n"
            f" └─ Threat Level: {telemetry['threat_level_pct']:.1f}%\n"
            f"{'-'*40}\n"
        )
        self.log_box.insert("end", log_entry)
        self.log_box.see("end")

        self.update_canvas_visuals(telemetry['infected_nodes'], telemetry['active_defenses'])
        self.update_plot(telemetry['step'], telemetry['threat_level_pct'], telemetry['infected_nodes'])

        self.loop_job = self.after(500, self.run_loop)

if __name__ == "__main__":
    app = SimulatorApp()
    app.mainloop()
