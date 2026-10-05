import math
import customtkinter as ctk

# Attempt C++ module import with fallback for standalone UI testing
try:
    import network_engine as sim_engine
except ImportError:
    sim_engine = None


class SimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Adaptive AI Outbreak & Threat Simulator")
        self.geometry("1100x700")

        self.is_running = False
        self.step_counter = 0
        self.loop_job = None

        self.canvas_nodes = []
        self.nodes_data = []
        self.edges = []

        self._build_ui()
        self._on_level_change("Level 1: Ring Topology")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Left Column: Canvas + Controls
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Top Control Panel (Level Select + Sliders)
        top_control_frame = ctk.CTkFrame(left_frame)
        top_control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(top_control_frame, text="Select Scenario:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5)
        self.level_menu = ctk.CTkOptionMenu(
            top_control_frame,
            values=["Level 1: Ring Topology", "Level 2: Mesh Network", "Level 3: Star Cluster"],
            command=self._on_level_change
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

        # Network Canvas
        self.net_canvas = ctk.CTkCanvas(left_frame, bg="#1e1e1e", highlightthickness=0)
        self.net_canvas.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Play/Pause/Reset Buttons
        btn_frame = ctk.CTkFrame(left_frame)
        btn_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_play = ctk.CTkButton(btn_frame, text="Play", fg_color="green", command=self.play_sim)
        self.btn_play.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_pause = ctk.CTkButton(btn_frame, text="Pause", fg_color="red", command=self.pause_sim)
        self.btn_pause.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.btn_reset = ctk.CTkButton(btn_frame, text="Reset", command=self.reset_sim)
        self.btn_reset.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Right Column: Telemetry Log
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right_frame, text="Live Telemetry & Metrics", font=("Arial", 16, "bold")).grid(row=0, column=0, padx=10, pady=10)

        self.log_box = ctk.CTkTextbox(right_frame, font=("Courier", 12))
        self.log_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def _on_level_change(self, selected_level):
        self.reset_sim()
        if "Ring" in selected_level:
            self._generate_circular_topology(num_nodes=20)
        elif "Mesh" in selected_level:
            self._generate_mesh_topology(num_nodes=24)
        else:
            self._generate_star_topology(num_nodes=18)
        self._render_network_topology()

    def _generate_circular_topology(self, num_nodes=20):
        self.nodes_data = [{"id": f"NODE-{i+1:02d}", "status": "HEALTHY"} for i in range(num_nodes)]
        self.edges = []
        for i in range(num_nodes):
            self.edges.append((i, (i + 1) % num_nodes))
            if i % 3 == 0:
                self.edges.append((i, (i + 5) % num_nodes))

    def _generate_mesh_topology(self, num_nodes=24):
        self.nodes_data = [{"id": f"NODE-{i+1:02d}", "status": "HEALTHY"} for i in range(num_nodes)]
        self.edges = []
        for i in range(num_nodes):
            self.edges.append((i, (i + 1) % num_nodes))
            self.edges.append((i, (i + 2) % num_nodes))
            if i % 2 == 0:
                self.edges.append((i, (i + 6) % num_nodes))

    def _generate_star_topology(self, num_nodes=18):
        self.nodes_data = [{"id": f"NODE-{i+1:02d}", "status": "HEALTHY"} for i in range(num_nodes)]
        self.edges = []
        for i in range(1, num_nodes):
            self.edges.append((0, i))
            if i % 2 == 0:
                self.edges.append((i, (i % (num_nodes - 1)) + 1))

    def _render_network_topology(self):
        self.net_canvas.delete("all")
        width = self.net_canvas.winfo_width() or 500
        height = self.net_canvas.winfo_height() or 400

        center_x, center_y = width / 2, height / 2
        radius = min(width, height) * 0.35

        num_nodes = len(self.nodes_data)
        if num_nodes == 0:
            return

        node_coords = []
        for i in range(num_nodes):
            angle = (2 * math.pi / num_nodes) * i
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            node_coords.append((x, y))

        for u, v in self.edges:
            if u < len(node_coords) and v < len(node_coords):
                x1, y1 = node_coords[u]
                x2, y2 = node_coords[v]
                self.net_canvas.create_line(x1, y1, x2, y2, fill="#444444", width=1)

        dot_radius = 8
        for i, (x, y) in enumerate(node_coords):
            status = self.nodes_data[i]["status"] if i < len(self.nodes_data) else "HEALTHY"
            if status == "INFECTED":
                color = "#FF5252"
            elif status == "WARNING":
                color = "#448AFF"
            else:
                color = "#69F0AE"

            self.net_canvas.create_oval(
                x - dot_radius, y - dot_radius,
                x + dot_radius, y + dot_radius,
                fill=color, outline=""
            )

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
        self.step_counter = 0
        self.log_box.delete("1.0", "end")
        for i in range(len(self.nodes_data)):
            self.nodes_data[i]["status"] = "HEALTHY"
        self._render_network_topology()

    def run_loop(self):
        if not self.is_running:
            return

        self.step_counter += 1

        inf_rate = self.slider_inf.get()
        def_power = self.slider_def.get()

        if sim_engine is not None:
            telemetry = sim_engine.run_step_telemetry(self.step_counter, inf_rate, def_power)
            total_nodes = telemetry.get('total_nodes', len(self.nodes_data))
        else:
            total_nodes = len(self.nodes_data)

        # Calculate infection progress dynamically across total active topology nodes
        effective_rate = max(0.05, inf_rate - (def_power * 0.8))
        infected_cnt = max(1, int(self.step_counter * effective_rate * 2))
        infected_cnt = min(total_nodes, infected_cnt)

        if sim_engine is not None:
            telemetry['infected_nodes'] = infected_cnt
            telemetry['threat_level_pct'] = (infected_cnt / max(1, total_nodes)) * 100.0
        else:
            telemetry = {
                'step': self.step_counter,
                'status': 'CONTAINMENT ACTIVE',
                'infected_nodes': infected_cnt,
                'total_nodes': total_nodes,
                'active_defenses': int(def_power * 5),
                'threat_level_pct': (infected_cnt / float(total_nodes)) * 100.0
            }

        for i in range(len(self.nodes_data)):
            if i < infected_cnt:
                self.nodes_data[i]['status'] = 'INFECTED'
            elif i < infected_cnt + 2 and i < len(self.nodes_data):
                self.nodes_data[i]['status'] = 'WARNING'
            else:
                self.nodes_data[i]['status'] = 'HEALTHY'

        self._render_network_topology()

        s = telemetry['step']
        st = telemetry['status']
        inf = telemetry['infected_nodes']
        tot = telemetry['total_nodes']
        df = telemetry['active_defenses']
        th = telemetry['threat_level_pct']

        log_entry = (
            "[STEP " + str(s) + "] Status: " + str(st) + "\n"
            " ├── Infected Nodes: " + str(inf) + "/" + str(tot) + "\n"
            " ├── Active Defenses: " + str(df) + "\n"
            " └── Threat Level: " + str(round(th, 1)) + "%\n\n"
        )

        self.log_box.insert('end', log_entry)
        self.log_box.see('end')

        self.loop_job = self.after(1000, self.run_loop)


if __name__ == '__main__':
    app = SimulatorApp()
    app.mainloop()
