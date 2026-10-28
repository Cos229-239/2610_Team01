import customtkinter as ctk
from core.topology import TopologyGenerator, NetworkGraph
from core.simulation import SimulationEngine, TelemetryData
from ui.canvas_view import CanvasView
from ui.telemetry_view import TelemetryPanel
from ui.tooltip import ToolTip
from ui.assistant import ClippyAssistant
import tkinter as tk
from tkinter import Menu


class SimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Adaptive AI Outbreak & Threat Simulator")
        self.geometry("1150x700")

        self.sim_engine = SimulationEngine()
        self.graph = NetworkGraph()
        self.is_running = False
        self.loop_job = None
        self.settings = {
            "colorblind_mode": False,
            "dark_mode": False
        }

        self._build_ui()
        self._build_menu()
        
        # Initialize Desktop Interactive Assistant with live simulation context references
        self.assistant = ClippyAssistant(self, sim_engine=self.sim_engine, graph=self.graph)
        
        self._on_level_change("Level 1: Ring Topology")

    # ------------------------------------------------------------------
    # Assistant Toggle
    # ------------------------------------------------------------------

    def toggle_assistant(self):
        """Toggles the floating desktop helper assistant."""
        if self.assistant.winfo_viewable():
            self.assistant.hide()
        else:
            self.assistant.show()

    # ------------------------------------------------------------------
    # Event Callbacks
    # ------------------------------------------------------------------

    def _on_mode_change(self, mode_str: str):
        """Callback for the segmented button (+ Node, + Edge, Move, Infect, Firewall)."""
        mode_map = {
            "Move": "SELECT",
            "+ Node": "ADD_NODE",
            "+ Edge": "CONNECT_EDGE",
            "Infect": "SET_ORIGIN",
            "Firewall": "FIREWALL",
        }
        self.net_canvas.set_mode(mode_map.get(mode_str, "SELECT"))

    def _on_device_type_change(self, selected_type: str):
        """Callback when choosing a device type from the Device dropdown."""
        self.net_canvas.set_active_node_type(selected_type)
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

        self.canvas_wrapper.set_graph(self.graph)

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

        ToolTip(
            self.level_menu,
            "Select a predefined network topology or start with a blank canvas."
        )

        # Segmented Button for Canvas Editing Mode (Includes Firewall)
        self.mode_selector = ctk.CTkSegmentedButton(
            top_ctrl,
            values=["Move", "+ Node", "+ Edge", "Infect", "Firewall"],
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

        ToolTip(
            self.device_menu,
            "Choose what device type will be placed when adding nodes."
        )

        # Spread AI Strategy Selector
        ctk.CTkLabel(top_ctrl, text="AI Mode:", font=("Arial", 11)).grid(
            row=0, column=5, padx=(10, 2), pady=5
        )
        self.ai_mode_menu = ctk.CTkOptionMenu(
            top_ctrl,
            values=["Strategic AI", "Uniform"],
            width=110,
        )
        self.ai_mode_menu.grid(row=0, column=6, padx=5, pady=5)

        ToolTip(
            self.ai_mode_menu,
            "Strategic AI targets the most effective paths. Uniform AI spreads randomly."
        )

        ctk.CTkButton(
            top_ctrl,
            text="Clear",
            width=60,
            fg_color="#C62828",
            command=self._clear_canvas,
        ).grid(row=0, column=7, padx=5, pady=5)

        ctk.CTkButton(
            top_ctrl,
            text="Settings",
            width=70,
            command=self.open_settings
        ).grid(row=0, column=8, padx=5, pady=5)

        # --- Interactive Assistant Toggle Button ---
        self.btn_assistant = ctk.CTkButton(
            top_ctrl,
            text="📎 Help",
            width=65,
            fg_color="#1E88E5",
            hover_color="#1565C0",
            command=self.toggle_assistant
        )
        self.btn_assistant.grid(row=0, column=9, padx=5, pady=5)

        ToolTip(
            self.btn_assistant,
            "Open the interactive desktop assistant for guided instructions."
        )

        # Sliders
        slider_frame = ctk.CTkFrame(left_frame)
        slider_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(slider_frame, text="Infection Rate:").grid(
            row=0, column=0, padx=5, pady=5
        )

        self.inf_value_label = ctk.CTkLabel(slider_frame, text="0.3")
        self.inf_value_label.grid(row=1, column=0, padx=5)

        self.slider_inf = ctk.CTkSlider(
            slider_frame,
            from_=0.1,
            to=1.0,
            number_of_steps=9,
            command=lambda v: self.inf_value_label.configure(text=f"{v:.1f}"),
        )
        self.slider_inf.set(0.3)
        self.slider_inf.grid(row=0, column=1, padx=5, pady=5)

        ToolTip(
            self.slider_inf,
            "Controls how likely an infected node is to spread the outbreak."
        )

        ctk.CTkLabel(slider_frame, text="Defense Power:").grid(
            row=0, column=2, padx=5, pady=5
        )

        self.def_value_label = ctk.CTkLabel(slider_frame, text="0.5")
        self.def_value_label.grid(row=1, column=2, padx=5)

        self.slider_def = ctk.CTkSlider(
            slider_frame,
            from_=0.1,
            to=1.0,
            number_of_steps=9,
            command=lambda v: self.def_value_label.configure(text=f"{v:.1f}"),
        )
        self.slider_def.set(0.5)
        self.slider_def.grid(row=0, column=3, padx=5, pady=5)

        ToolTip(
            self.slider_def,
            "Increase the network's ability to resist infection."
        )

        # Canvas View Wrapper & Direct Canvas Reference
        self.canvas_wrapper = CanvasView(left_frame, self.sim_engine)
        self.net_canvas = self.canvas_wrapper.canvas

        self.canvas_wrapper.set_node_select_callback(
            self.on_node_selected
        )

        self.canvas_wrapper.grid(
            row=2,
            column=0,
            padx=10,
            pady=10,
            sticky="nsew"
        )

        # Simulation & Threat Module Buttons Frame
        btn_frame = ctk.CTkFrame(left_frame)
        btn_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.play_button = ctk.CTkButton(
            btn_frame,
            text="Play",
            fg_color="green",
            command=self.play_sim
        )
        self.play_button.grid(row=0, column=0, padx=3, pady=5, sticky="ew")
        ToolTip(self.play_button, "Start the simulation.")

        ctk.CTkButton(
            btn_frame, text="Pause", fg_color="red", command=self.pause_sim
        ).grid(row=0, column=1, padx=3, pady=5, sticky="ew")
        
        ctk.CTkButton(
            btn_frame, text="Reset", command=self.reset_sim
        ).grid(row=0, column=2, padx=3, pady=5, sticky="ew")

        # --- Manual Threat Module Buttons ---
        self.msf_button = ctk.CTkButton(
            btn_frame,
            text="Run Metasploit",
            fg_color="#D9534F",
            hover_color="#C9302C",
            command=self.on_click_metasploit
        )
        self.msf_button.grid(row=0, column=3, padx=3, pady=5, sticky="ew")
        ToolTip(self.msf_button, "Manually execute Metasploit lateral movement across infected nodes.")

        self.gerald_button = ctk.CTkButton(
            btn_frame,
            text="Run Gerald",
            fg_color="#F0AD4E",
            hover_color="#EC971F",
            command=self.on_click_gerald
        )
        self.gerald_button.grid(row=0, column=4, padx=3, pady=5, sticky="ew")
        ToolTip(self.gerald_button, "Manually execute Gerald password and hash cracking burst.")

        # Telemetry Panel
        self.telemetry_panel = TelemetryPanel(self)
        self.telemetry_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # ------------------------------------------------------------------
    # Manual Threat Module Handlers
    # ------------------------------------------------------------------

    def on_click_metasploit(self):
        """Manually trigger Metasploit action on the targeted node and log to telemetry panel."""
        if hasattr(self, 'sim_engine') and hasattr(self, 'graph'):
            target_idx = getattr(self.net_canvas, "selected_node_idx", 0) or 0
            events = self.sim_engine.trigger_metasploit_manual(self.graph, target_node_idx=target_idx)
            
            infected_cnt = sum(1 for n in self.graph.nodes if n.status == "INFECTED" or n.is_patient_zero)
            telemetry = TelemetryData(
                step=self.sim_engine.step_counter,
                status="MANUAL METASPLOIT TRIGGER",
                infected_nodes=infected_cnt,
                recovered_nodes=self.sim_engine.total_recovered_count,
                total_nodes=self.graph.node_count,
                active_defenses=int(self.slider_def.get() * 10),
                threat_level_pct=(infected_cnt / max(1, self.graph.node_count)) * 100.0,
                escalation_factor=1.0,
                sim_time_seconds=self.sim_engine.step_counter,
                events=events
            )
            self.telemetry_panel.append_log(telemetry, self.sim_engine.history_index)
            
            if hasattr(self.net_canvas, "flash_target_node"):
                self.net_canvas.flash_target_node(target_idx)
            else:
                self.net_canvas.render()

    def on_click_gerald(self):
        """Manually trigger Gerald password cracking and log to telemetry panel."""
        if hasattr(self, 'sim_engine') and hasattr(self, 'graph'):
            events = self.sim_engine.trigger_gerald_manual(self.graph)
            infected_cnt = sum(1 for n in self.graph.nodes if n.status == "INFECTED" or n.is_patient_zero)
            telemetry = TelemetryData(
                step=self.sim_engine.step_counter,
                status="MANUAL GERALD CRACK",
                infected_nodes=infected_cnt,
                recovered_nodes=self.sim_engine.total_recovered_count,
                total_nodes=self.graph.node_count,
                active_defenses=int(self.slider_def.get() * 10),
                threat_level_pct=(infected_cnt / max(1, self.graph.node_count)) * 100.0,
                escalation_factor=1.0,
                sim_time_seconds=self.sim_engine.step_counter,
                events=events
            )
            self.telemetry_panel.append_log(telemetry, self.sim_engine.history_index)
            self.net_canvas.render()

    def _build_menu(self):
        menubar = Menu(self)
        self.config(menu=menubar)

        # File
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Canvas", command=self._clear_canvas)
        file_menu.add_separator()
        file_menu.add_command(label="Export Simulation Report", command=self.canvas_wrapper.trigger_export)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)

        # Edit
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Settings…", command=self.open_settings)

        # View
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)

        self.colorblind_var = tk.BooleanVar(value=self.settings["colorblind_mode"])
        view_menu.add_checkbutton(
            label="Colorblind Mode",
            variable=self.colorblind_var,
            command=lambda: self.toggle_colorblind(self.colorblind_var.get())
        )

        # Simulation
        sim_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        sim_menu.add_command(label="Play", command=self.play_sim)
        sim_menu.add_command(label="Pause", command=self.pause_sim)
        sim_menu.add_command(label="Reset", command=self.reset_sim)

        # Help
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _show_about(self):
        about = ctk.CTkToplevel(self)
        about.title("About")
        about.geometry("360x180")
        about.resizable(False, False)
        about.transient(self)
        about.grab_set()
        about.lift()

        ctk.CTkLabel(
            about,
            text="Adaptive AI Outbreak & Threat Simulator",
            font=("Arial", 14, "bold")
        ).pack(pady=(25, 8))

        ctk.CTkLabel(
            about,
            text="A network infection simulation tool\nwith AI-driven spread models.",
            justify="center"
        ).pack(pady=5)

        ctk.CTkButton(about, text="Close", width=100, command=about.destroy).pack(pady=15)
        
    def on_node_selected(self, node_index: int):
        if 0 <= node_index < len(self.graph.nodes):
            node = self.graph.nodes[node_index]
            self.telemetry_panel.show_node_info(
                node,
                self.graph
            )

    # ------------------------------------------------------------------
    # Simulation Loop Controls
    # ------------------------------------------------------------------
    
    def open_settings(self):
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("320x220")
        settings_window.resizable(False, False)

        settings_window.transient(self)
        settings_window.grab_set()
        settings_window.focus_force()
        settings_window.lift()
        settings_window.after(10, settings_window.lift)

        # ----- Colorblind Mode -----
        colorblind_var = ctk.BooleanVar(value=self.settings["colorblind_mode"])
        ctk.CTkCheckBox(
            settings_window,
            text="Colorblind Mode",
            variable=colorblind_var,
            command=lambda: self.toggle_colorblind(colorblind_var.get())
        ).pack(padx=20, pady=(25, 10), anchor="w")

        # ----- Dark Mode -----
        dark_var = ctk.BooleanVar(value=self.settings["dark_mode"])
        ctk.CTkCheckBox(
            settings_window,
            text="Dark Mode",
            variable=dark_var,
            command=lambda: self.toggle_dark_mode(dark_var.get())
        ).pack(padx=20, pady=10, anchor="w")
        # ----- Cyberpunk Theme -----
        cyber_var = ctk.BooleanVar(value=self.settings.get("cyberpunk_mode", False))
        ctk.CTkCheckBox(
            settings_window,
            text="Cyberpunk Mode (Neon/Dark)",
            variable=cyber_var,
            command=lambda: self.toggle_cyberpunk_theme(cyber_var.get())
        ).pack(padx=20, pady=10, anchor="w")
        
    def toggle_colorblind(self, enabled: bool):
        self.settings["colorblind_mode"] = enabled
        self.canvas_wrapper.set_colorblind_mode(enabled)

    def toggle_dark_mode(self, enabled: bool):
        self.settings["dark_mode"] = enabled
        if enabled:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")
    def toggle_cyberpunk_theme(self, enabled: bool):
        self.settings["cyberpunk_mode"] = enabled
        if enabled:
            ctk.set_appearance_mode("Dark")
            self.settings["dark_mode"] = True
            
            # Cyberpunk Neon Palette
            bg_dark = "#090a0f"      # Deep void black/blue
            panel_dark = "#121420"   # Dark slate purple
            neon_cyan = "#00f0ff"    # Glowing cyan
            neon_magenta = "#ff007f" # Neon pink/magenta
            
            # Apply custom theme colors to active buttons and frames
            self.configure(fg_color=bg_dark)
            if hasattr(self, 'msf_button'):
                self.msf_button.configure(fg_color=neon_magenta, hover_color="#cc0066", text_color="#ffffff")
            if hasattr(self, 'gerald_button'):
                self.gerald_button.configure(fg_color=neon_cyan, hover_color="#00b8c4", text_color="#000000")
        else:
            # Revert to standard colors
            ctk.set_appearance_mode("Dark" if self.settings["dark_mode"] else "Light")
            if hasattr(self, 'msf_button'):
                self.msf_button.configure(fg_color="#D9534F", hover_color="#C9302C")
            if hasattr(self, 'gerald_button'):
                self.gerald_button.configure(fg_color="#F0AD4E", hover_color="#EC971F")

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
        self.graph.reset_states()

        p0_idx = self.graph.get_patient_zero_index() if self.graph.nodes else 0

        for i, node in enumerate(self.graph.nodes):
            node.status = "HEALTHY"
            node.is_patient_zero = (i == p0_idx)

        for edge in self.graph.edges:
            edge.status = "HEALTHY"

        self.net_canvas.render()

    def step_back(self):
        if not self.sim_engine.can_step_back():
            return
        self.pause_sim()
        new_index = self.sim_engine.history_index - 1
        telemetry = self.sim_engine.restore_snapshot(new_index, self.graph)
        if telemetry:
            self.net_canvas.render()
            self.telemetry_panel.show_snapshot(telemetry, new_index)

    def step_forward(self):
        if not self.sim_engine.can_step_forward():
            return
        self.pause_sim()
        new_index = self.sim_engine.history_index + 1
        telemetry = self.sim_engine.restore_snapshot(new_index, self.graph)
        if telemetry:
            self.net_canvas.render()
            self.telemetry_panel.show_snapshot(telemetry, new_index)

    def jump_to_step(self, history_index: int):
        self.pause_sim()
        telemetry = self.sim_engine.restore_snapshot(history_index, self.graph)
        if telemetry:
            self.net_canvas.render()
            self.telemetry_panel.show_snapshot(telemetry, history_index)
        
    def run_loop(self):
        if not self.is_running:
            return

        telemetry = self.sim_engine.step(
            self.graph,
            self.slider_inf.get(),
            self.slider_def.get(),
            ai_mode=self.ai_mode_menu.get(),
        )

        self.net_canvas.render()
        self.telemetry_panel.append_log(telemetry, self.sim_engine.history_index)

        total = telemetry.total_nodes
        infected = telemetry.infected_nodes

        if total > 0:
            if infected == 0:
                self.pause_sim()
                self._show_endgame_dialog(
                    title="THREAT NEUTRALIZED",
                    message="All infected nodes and Patient Zero have been successfully secured!",
                    is_victory=True,
                )
                return

            elif infected == total:
                self.pause_sim()
                self._show_endgame_dialog(
                    title="NETWORK COMPROMISED",
                    message="The threat has completely taken over all network nodes!",
                    is_victory=False,
                )
                return

        self.loop_job = self.after(1000, self.run_loop)

    def _show_endgame_dialog(self, title: str, message: str, is_victory: bool):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("420x220")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        header_color = "#2E7D32" if is_victory else "#C62828"

        ctk.CTkLabel(
            dialog,
            text=title,
            font=("Arial", 18, "bold"),
            text_color=header_color,
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            dialog,
            text=message,
            font=("Arial", 12),
            wraplength=360,
            justify="center",
        ).pack(pady=10)

        ctk.CTkButton(
            dialog,
            text="Acknowledge",
            fg_color=header_color,
            width=120,
            command=dialog.destroy,
        ).pack(pady=(15, 10))


if __name__ == "__main__":
    app = SimulatorApp()
    app.mainloop()