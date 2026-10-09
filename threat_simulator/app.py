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

    # ------------------------------------------------------------------
    # Event Callbacks
    # ------------------------------------------------------------------

    def _on_mode_change(self, mode_str: str):
        """Callback for the segmented button (+ Node, + Edge, Move, Infect)."""
        mode_map = {
            "Move": "SELECT",
            "+ Node": "ADD_NODE",
            "+ Edge": "CONNECT_EDGE",
            "Infect": "SET_ORIGIN",
        }
        self.net_canvas.set_mode(mode_map.get(mode_str, "SELECT"))

    def _on_device_type_change(self, selected_type: str):
        """Callback when choosing a device type from the Device dropdown."""
        self.net_canvas.set_active_node_type(selected_type)
        # Automatically set canvas mode to add node when changing device type
        self.mode_selector.set("+ Node")
        self.net_canvas.set_mode("ADD_NODE")

    def _clear_canvas(self):
        """Clears all nodes and edges from the canvas."""
        self.reset_sim()
        self.graph.clear()
        self.level_menu.set("Custom Canvas")
        self.net_canvas.render()

    def _on_level_change(self, selected_level: str):
        """Handles scenario dropdown switching."""
        self.reset_sim()
        w = self.net_canvas.winfo_width() or 500
        h = self.net_canvas.winfo_height() or 400

        if "Ring" in selected_level:
            self.graph = TopologyGenerator.generate_ring(20)
            TopologyGenerator.apply_ring_layout(self.graph, w, h)
        elif "Mesh" in selected_level:
            self.graph = TopologyGenerator.generate_mesh(24)
            TopologyGenerator.apply_ring_layout(self.graph, w, h)
        elif "Star" in selected_level:
            self.graph = TopologyGenerator.generate_star(18)
            TopologyGenerator.apply_ring_layout(self.graph, w, h)
        else:
            self.graph.clear()

        self.net_canvas.set_graph(self.graph)

    # ------------------------------------------------------------------
    # UI Layout Builder
    # ------------------------------------------------------------------

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Left Column Frame
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Controls Header
        top_ctrl = ctk.CTkFrame(left_frame)
        top_ctrl.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(top_ctrl, text="Scenario:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, padx=5, pady=5
        )
        self.level_menu = ctk.CTkOptionMenu(
            top_ctrl,
            values=[
                "Level 1: Ring Topology",
                "Level 2: Mesh Network",
                "Level 3: Star Cluster",
                "Custom Canvas",
            ],
            command=self._on_level_change,
        )
        self.level_menu.grid(row=0, column=1, padx=5, pady=5)

        # Segmented Button for Canvas Editing Mode
        self.mode_selector = ctk.CTkSegmentedButton(
            top_ctrl,
            values=["Move", "+ Node", "+ Edge", "Infect"],
            command=self._on_mode_change,
        )
        self.mode_selector.set("Move")
        self.mode_selector.grid(row=0, column=2, padx=10, pady=5)

        # Device Selection Menu for Node Placement
        ctk.CTkLabel(top_ctrl, text="Device:", font=("Arial", 11)).grid(
            row=0, column=3, padx=(10, 2), pady=5
        )
        self.device_menu = ctk.CTkOptionMenu(
            top_ctrl,
            values=["PC", "Router", "Modem"],
            width=90,
            command=self._on_device_type_change,
        )
        self.device_menu.grid(row=0, column=4, padx=5, pady=5)

        ctk.CTkButton(
            top_ctrl,
            text="Clear",
            width=60,
            fg_color="#C62828",
            command=self._clear_canvas,
        ).grid(row=0, column=5, padx=5, pady=5)

        # Sliders
        slider_frame = ctk.CTkFrame(left_frame)
        slider_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(slider_frame, text="Infection Rate:").grid(
            row=0, column=0, padx=5, pady=5
        )

        self.inf_value_label = ctk.CTkLabel(slider_frame, text = "0.3")
        self.inf_value_label.grid(row=1, column=0, padx=5)

        self.slider_inf = ctk.CTkSlider(
            slider_frame, from_=0.1, to=1.0, number_of_steps=9, 
            command=lambda v: self.inf_value_label.configure(text=f"{v:.1f}")
        )
        self.slider_inf.set(0.3)
        self.slider_inf.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(slider_frame, text="Defense Power:").grid(
            row=0, column=2, padx=5, pady=5
        )

        self.def_value_label = ctk.CTkLabel(slider_frame, text = "0.5")
        self.def_value_label.grid(row=1, column=2, padx=5)

        self.slider_def = ctk.CTkSlider(
            slider_frame, from_=0.1, to=1.0, number_of_steps=9,
            command=lambda v: self.def_value_label.configure(text=f"{v:.1f}")
        )
        self.slider_def.set(0.5)
        self.slider_def.grid(row=0, column=3, padx=5, pady=5)

        # Canvas
        self.net_canvas = NetworkCanvas(left_frame)
        self.net_canvas.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Buttons (Play/Pause/Reset)
        btn_frame = ctk.CTkFrame(left_frame)
        btn_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            btn_frame, text="Play", fg_color="green", command=self.play_sim
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(
            btn_frame, text="Pause", fg_color="red", command=self.pause_sim
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(
            btn_frame, text="Reset", command=self.reset_sim
        ).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Telemetry Panel
        self.telemetry_panel = TelemetryPanel(self)
        self.telemetry_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # ------------------------------------------------------------------
    # Simulation Loop Controls
    # ------------------------------------------------------------------

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
        for i, node in enumerate(self.graph.nodes):
            node.status = "HEALTHY"
            # Restore initial Patient Zero (default to Node 0 if none set)
            node.is_patient_zero = (i == 0)

        for edge in self.graph.edges:
            edge.status = "HEALTHY"

        self.net_canvas.render()


    def run_loop(self):
        if not self.is_running:
            return

        telemetry = self.sim_engine.step(
            self.graph, self.slider_inf.get(), self.slider_def.get()
        )

        self.net_canvas.render()
        self.telemetry_panel.append_log(telemetry)

        # -------------------------------------------------------------
        # ENDGAME TERMINATION CHECK
        # -------------------------------------------------------------
        total = telemetry.total_nodes
        infected = telemetry.infected_nodes

        if total > 0:
            # Condition 1: Threat Neutralized (Victory)
            if infected == 0:
                self.pause_sim()
                self._show_endgame_dialog(
                    title="THREAT NEUTRALIZED",
                    message="All infected nodes and Patient Zero have been successfully secured!",
                    is_victory=True
                )
                return

            # Condition 2: Entire Network Infected (Defeat)
            elif infected == total:
                self.pause_sim()
                self._show_endgame_dialog(
                    title="NETWORK COMPROMISED",
                    message="The threat has completely taken over all network nodes!",
                    is_victory=False
                )
                return

        # Schedule next loop step if game is ongoing
        self.loop_job = self.after(1000, self.run_loop)

        self.loop_job = self.after(1000, self.run_loop)


    def _show_endgame_dialog(self, title: str, message: str, is_victory: bool):
        """Displays a clean modal popup when simulation reaches an endgame state."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("420x220")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set() 

        # Header Color
        header_color = "#2E7D32" if is_victory else "#C62828"  # Green for Victory, Red for Defeat

        # Title Label
        ctk.CTkLabel(
            dialog,
            text=title,
            font=("Arial", 18, "bold"),
            text_color=header_color
        ).pack(pady=(20, 10))

        # Message Body
        ctk.CTkLabel(
            dialog,
            text=message,
            font=("Arial", 12),
            wraplength=360,
            justify="center"
        ).pack(pady=10)

        # OK / Close Button
        ctk.CTkButton(
            dialog,
            text="Acknowledge",
            fg_color=header_color,
            width=120,
            command=dialog.destroy
        ).pack(pady=(15, 10))



if __name__ == "__main__":
    app = SimulatorApp()
    app.mainloop()