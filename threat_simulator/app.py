import customtkinter as ctk
from core.topology import TopologyGenerator, NetworkGraph
from core.simulation import SimulationEngine
from ui.canvas_view import NetworkCanvas
from ui.telemetry_view import TelemetryPanel


class SimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Adaptive AI Outbreak & Threat Simulator")
        self.geometry("1100x700")

        self.sim_engine = SimulationEngine()
        self.graph = NetworkGraph()
        self.is_running = False
        self.loop_job = None

        self._build_ui()
        self._on_level_change("Level 1: Ring Topology")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Left Frame
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Controls Header
        top_ctrl = ctk.CTkFrame(left_frame)
        top_ctrl.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(top_ctrl, text="Select Scenario:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5)
        self.level_menu = ctk.CTkOptionMenu(
            top_ctrl,
            values=["Level 1: Ring Topology", "Level 2: Mesh Network", "Level 3: Star Cluster"],
            command=self._on_level_change,
        )
        self.level_menu.grid(row=0, column=1, padx=5, pady=5)

        # Sliders
        slider_frame = ctk.CTkFrame(left_frame)
        slider_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(slider_frame, text="Infection Rate:").grid(row=0, column=0, padx=5, pady=5)
        self.slider_inf = ctk.CTkSlider(slider_frame, from_=0.1, to=1.0, number_of_steps=9)
        self.slider_inf.set(0.3)
        self.slider_inf.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(slider_frame, text="Defense Power:").grid(row=0, column=2, padx=5, pady=5)
        self.slider_def = ctk.CTkSlider(slider_frame, from_=0.1, to=1.0, number_of_steps=9)
        self.slider_def.set(0.5)
        self.slider_def.grid(row=0, column=3, padx=5, pady=5)

        # Canvas
        self.net_canvas = NetworkCanvas(left_frame)
        self.net_canvas.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Buttons
        btn_frame = ctk.CTkFrame(left_frame)
        btn_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(btn_frame, text="Play", fg_color="green", command=self.play_sim).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="Pause", fg_color="red", command=self.pause_sim).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="Reset", command=self.reset_sim).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Right Frame (Telemetry)
        self.telemetry_panel = TelemetryPanel(self)
        self.telemetry_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def _on_level_change(self, selected_level: str):
        self.reset_sim()
        if "Ring" in selected_level:
            self.graph = TopologyGenerator.generate_ring(num_nodes=20)
        elif "Mesh" in selected_level:
            self.graph = TopologyGenerator.generate_mesh(num_nodes=24)
        else:
            self.graph = TopologyGenerator.generate_star(num_nodes=18)
        self.net_canvas.render(self.graph)

    def play_sim(self):
        if not self.is_running:
            self.is_running = True
            self.run_loop()

    def pause_sim(self):
        self.is_running = False
        if self.loop_job is not None:
            self.after_cancel(self.loop_job)
            self.loop_job = None

    def reset_sim(self):
        self.pause_sim()
        self.sim_engine.reset()
        self.telemetry_panel.clear()
        for node in self.graph.nodes:
            node.status = "HEALTHY"
        self.net_canvas.render(self.graph)

    def run_loop(self):
        if not self.is_running:
            return

        telemetry = self.sim_engine.step(
            self.graph,
            self.slider_inf.get(),
            self.slider_def.get()
        )

        self.net_canvas.render(self.graph)
        self.telemetry_panel.append_log(telemetry)

        self.loop_job = self.after(1000, self.run_loop)


if __name__ == "__main__":
    app = SimulatorApp()
    app.mainloop()