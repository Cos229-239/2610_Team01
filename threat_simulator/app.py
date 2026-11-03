import os
import sys
import json
import tkinter as tk
from tkinter import Menu
from typing import Dict, List, Optional, Tuple

# Add project root directory to sys.path to resolve internal modules
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import customtkinter as ctk

from core.topology import TopologyGenerator, NetworkGraph
from core.simulation import SimulationEngine, TelemetryData
from ui.canvas_view import CanvasView
from ui.telemetry_view import TelemetryPanel
from ui.tooltip import ToolTip
from ui.assistant import ClippyAssistant
from ui.pdu_controls import PDUControlPanel
from utils.theme_loader import ThemeManager


class SimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Adaptive AI Outbreak & Threat Simulator")
        self.geometry("1150x820")

        self.sim_engine = SimulationEngine()
        self.graph = NetworkGraph()
        self.is_running = False
        self.loop_job = None

        # Dynamic Theme Engine Manager
        self.theme_manager = ThemeManager()
        
        # Dynamically grab the first loaded theme name
        theme_names = list(self.theme_manager.available_themes.keys())
        self.current_theme_name = theme_names[0] if theme_names else "Classic Beige"

        self.settings = {
            "colorblind_mode": False,
            "dark_mode": False,
            "cyberpunk_mode": False,
            "active_theme": self.current_theme_name,
        }

        self._build_ui()
        self._build_menu()

        # Initialize Desktop Interactive Assistant with live simulation context references
        self.assistant = ClippyAssistant(
            self, sim_engine=self.sim_engine, graph=self.graph
        )

        self._on_level_change("Level 1: Ring Topology")
        
        # Apply initial theme to canvas and assistant
        self.select_json_theme(self.current_theme_name)

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

        # Update bindings to the active graph instance
        self.canvas_wrapper.set_graph(self.graph)
        if hasattr(self, "pdu_controls") and hasattr(self.graph, "pdu_engine"):
            self.pdu_controls.engine = self.graph.pdu_engine

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
            "Select a predefined network topology or start with a blank canvas.",
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
            values=["PC", "Router", "Modem", "Server", "Switch", "Firewall"],
            width=90,
            command=self._on_device_type_change,
        )
        self.device_menu.grid(row=0, column=4, padx=5, pady=5)

        ToolTip(
            self.device_menu,
            "Choose what device type will be placed when adding nodes.",
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
            "Strategic AI targets the most effective paths. Uniform AI spreads randomly.",
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
            command=self.open_settings,
        ).grid(row=0, column=8, padx=5, pady=5)

        # Interactive Assistant Toggle Button
        self.btn_assistant = ctk.CTkButton(
            top_ctrl,
            text="📎 Help",
            width=65,
            fg_color="#1E88E5",
            hover_color="#1565C0",
            command=self.toggle_assistant,
        )
        self.btn_assistant.grid(row=0, column=9, padx=5, pady=5)

        ToolTip(
            self.btn_assistant,
            "Open the interactive desktop assistant for guided instructions.",
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
            "Controls how likely an infected node is to spread the outbreak.",
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
            "Increase the network's ability to resist infection.",
        )

        # Canvas View Wrapper & Direct Canvas Reference
        self.canvas_wrapper = CanvasView(left_frame, self.sim_engine)
        self.net_canvas = self.canvas_wrapper.canvas

        self.canvas_wrapper.set_node_select_callback(self.on_node_selected)

        self.canvas_wrapper.grid(
            row=2,
            column=0,
            padx=10,
            pady=(10, 5),
            sticky="nsew",
        )

        # Cisco Packet Tracer PDU Animation Control Panel
        self.pdu_controls = PDUControlPanel(
            parent=left_frame,
            engine=getattr(self.graph, "pdu_engine", None),
            on_tick_callback=self.net_canvas.render,
        )
        self.pdu_controls.grid(row=3, column=0, padx=10, pady=(0, 5), sticky="ew")

        # Simulation & Threat Module Buttons Frame (Expanded for 6 Buttons)
        btn_frame = ctk.CTkFrame(left_frame)
        btn_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        self.play_button = ctk.CTkButton(
            btn_frame,
            text="Play",
            fg_color="green",
            command=self.play_sim,
        )
        self.play_button.grid(row=0, column=0, padx=2, pady=5, sticky="ew")
        ToolTip(self.play_button, "Start the simulation.")

        ctk.CTkButton(
            btn_frame, text="Pause", fg_color="red", command=self.pause_sim
        ).grid(row=0, column=1, padx=2, pady=5, sticky="ew")

        ctk.CTkButton(
            btn_frame, text="Reset", command=self.reset_sim
        ).grid(row=0, column=2, padx=2, pady=5, sticky="ew")

        # Manual Threat Module Buttons
        self.msf_button = ctk.CTkButton(
            btn_frame,
            text="Run Metasploit",
            fg_color="#D9534F",
            hover_color="#C9302C",
            command=self.on_click_metasploit,
        )
        self.msf_button.grid(row=0, column=3, padx=2, pady=5, sticky="ew")
        ToolTip(
            self.msf_button,
            "Manually execute Metasploit lateral movement across infected nodes.",
        )

        self.gerald_button = ctk.CTkButton(
            btn_frame,
            text="Run Gerald",
            fg_color="#F0AD4E",
            hover_color="#EC971F",
            command=self.on_click_gerald,
        )
        self.gerald_button.grid(row=0, column=4, padx=2, pady=5, sticky="ew")
        ToolTip(
            self.gerald_button,
            "Manually execute Gerald password and hash cracking burst.",
        )

        self.ddos_button = ctk.CTkButton(
            btn_frame,
            text="Run DDoS",
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            command=self.on_click_ddos,
        )
        self.ddos_button.grid(row=0, column=5, padx=2, pady=5, sticky="ew")
        ToolTip(
            self.ddos_button,
            "Execute a volumetric DDoS flood against the selected node.",
        )

        # --- Nuke Protocol Button ---
        self.nuke_button = ctk.CTkButton(
            btn_frame,
            text="☢ NUKE",
            fg_color="#B71C1C",
            hover_color="#880E4F",
            font=("Arial", 12, "bold"),
            command=self.on_click_nuke
        )
        self.nuke_button.grid(row=0, column=6, padx=2, pady=5, sticky="ew")
        ToolTip(self.nuke_button, "Execute all threat modules simultaneously with a countdown.")

        # Telemetry Panel
        self.telemetry_panel = TelemetryPanel(self)
        self.telemetry_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # ------------------------------------------------------------------
    # Dynamic Theme Integration
    # ------------------------------------------------------------------

    def select_json_theme(self, theme_name: str):
        """Applies chosen JSON theme data to the canvas view and assistant UI."""
        self.current_theme_name = theme_name
        self.settings["active_theme"] = theme_name
        theme_data = self.theme_manager.get_theme(theme_name)

        if "appearance_mode" in theme_data:
            ctk.set_appearance_mode(theme_data["appearance_mode"])
            self.settings["dark_mode"] = (theme_data["appearance_mode"] == "Dark")

        # Apply theme to canvas view
        self.net_canvas.apply_custom_theme(theme_data)

        # Apply theme and custom avatar config to Clippy assistant
        if hasattr(self, "assistant") and self.assistant:
            self.assistant.apply_theme(theme_data)

    def reload_themes(self, dropdown_menu=None):
        """Rescans themes directory and refreshes dropdown options."""
        self.theme_manager.load_all_themes()
        theme_list = list(self.theme_manager.available_themes.keys())
        if dropdown_menu and dropdown_menu.winfo_exists():
            dropdown_menu.configure(values=theme_list)
            if self.current_theme_name in theme_list:
                dropdown_menu.set(self.current_theme_name)
            else:
                self.current_theme_name = theme_list[0]
                dropdown_menu.set(self.current_theme_name)
                self.select_json_theme(self.current_theme_name)

    # ------------------------------------------------------------------
    # Manual Threat Module Handlers
    # ------------------------------------------------------------------

    def on_click_metasploit(self):
        """Manually trigger Metasploit action on the targeted node and log to telemetry panel."""
        if hasattr(self, "sim_engine") and hasattr(self, "graph"):
            target_idx = getattr(self.net_canvas, "selected_node_idx", 0) or 0
            events = self.sim_engine.trigger_metasploit_manual(
                self.graph, target_node_idx=target_idx
            )

            infected_cnt = sum(
                1 for n in self.graph.nodes if n.status == "INFECTED" or n.is_patient_zero
            )
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
                events=events,
            )
            self.telemetry_panel.append_log(telemetry, self.sim_engine.history_index)

            if hasattr(self.net_canvas, "flash_target_node"):
                self.net_canvas.flash_target_node(target_idx)
            else:
                self.net_canvas.render()

    def on_click_gerald(self):
        """Manually trigger Gerald password cracking and log to telemetry panel."""
        if hasattr(self, "sim_engine") and hasattr(self, "graph"):
            events = self.sim_engine.trigger_gerald_manual(self.graph)
            infected_cnt = sum(
                1 for n in self.graph.nodes if n.status == "INFECTED" or n.is_patient_zero
            )
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
                events=events,
            )
            self.telemetry_panel.append_log(telemetry, self.sim_engine.history_index)
            self.net_canvas.render()

    def on_click_ddos(self):
        """Manually trigger a DDoS flood on the targeted node and log to telemetry panel."""
        if hasattr(self, "sim_engine") and hasattr(self, "graph"):
            target_idx = getattr(self.net_canvas, "selected_node_idx", 0) or 0
            events = self.sim_engine.trigger_ddos_manual(
                self.graph, target_node_idx=target_idx
            )

            infected_cnt = sum(
                1 for n in self.graph.nodes if n.status == "INFECTED" or n.is_patient_zero
            )
            telemetry = TelemetryData(
                step=self.sim_engine.step_counter,
                status="VOLUMETRIC DDOS ATTACK",
                infected_nodes=infected_cnt,
                recovered_nodes=self.sim_engine.total_recovered_count,
                total_nodes=self.graph.node_count,
                active_defenses=int(self.slider_def.get() * 10),
                threat_level_pct=(infected_cnt / max(1, self.graph.node_count)) * 100.0,
                escalation_factor=1.0,
                sim_time_seconds=self.sim_engine.step_counter,
                events=events,
            )
            self.telemetry_panel.append_log(telemetry, self.sim_engine.history_index)

            if hasattr(self.net_canvas, "flash_target_node"):
                self.net_canvas.flash_target_node(target_idx)
            else:
                self.net_canvas.render()

    def on_click_nuke(self):
        """Displays a dramatic countdown modal before launching the Nuke Protocol."""
        nuke_dialog = ctk.CTkToplevel(self)
        nuke_dialog.title("⚠️ NUKE PROTOCOL INITIATED")
        nuke_dialog.geometry("380x240")
        nuke_dialog.resizable(False, False)
        nuke_dialog.transient(self)
        nuke_dialog.grab_set()
        nuke_dialog.focus_force()

        ctk.CTkLabel(
            nuke_dialog,
            text="☢ FULL NUKE SALVO ☢",
            font=("Arial", 18, "bold"),
            text_color="#FF1744",
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            nuke_dialog,
            text="Initiating simultaneous attack sequence across all threat modules:\nMetasploit • Gerald • DDoS • Logic Bomb",
            font=("Arial", 11),
            justify="center",
            wraplength=340,
        ).pack(pady=5)

        self.countdown_seconds = 3
        countdown_label = ctk.CTkLabel(
            nuke_dialog,
            text=f"DETONATION IN: {self.countdown_seconds}",
            font=("Consolas", 20, "bold"),
            text_color="#FF1744",
        )
        countdown_label.pack(pady=10)

        modal_btn_frame = ctk.CTkFrame(nuke_dialog, fg_color="transparent")
        modal_btn_frame.pack(pady=10)

        self.nuke_timer_job = None

        def abort_nuke():
            if self.nuke_timer_job:
                self.after_cancel(self.nuke_timer_job)
                self.nuke_timer_job = None
            nuke_dialog.destroy()
            if hasattr(self, 'telemetry_panel'):
                self.telemetry_panel.append_raw_event("SYSTEM", "[ABORT] Nuke Protocol canceled by operator.")

        def execute_salvo():
            if self.nuke_timer_job:
                self.after_cancel(self.nuke_timer_job)
                self.nuke_timer_job = None
            nuke_dialog.destroy()
            
            if hasattr(self, 'sim_engine') and hasattr(self, 'graph'):
                events = getattr(self.sim_engine, "trigger_nuke_all", lambda g: ["Nuke salvo triggered."])(self.graph)
                infected_cnt = sum(
                    1 for n in self.graph.nodes 
                    if getattr(n, 'status', '') == "INFECTED" or getattr(n, 'is_patient_zero', False)
                )
                
                telemetry = TelemetryData(
                    step=self.sim_engine.step_counter,
                    status="CRITICAL: FULL NUKE SALVO EXECUTED",
                    infected_nodes=infected_cnt,
                    recovered_nodes=self.sim_engine.total_recovered_count,
                    total_nodes=self.graph.node_count,
                    active_defenses=int(self.slider_def.get() * 10),
                    threat_level_pct=(infected_cnt / max(1, self.graph.node_count)) * 100.0,
                    escalation_factor=100.0,
                    sim_time_seconds=self.sim_engine.step_counter,
                    events=events
                )
                self.telemetry_panel.append_log(telemetry, self.sim_engine.history_index)
                self.net_canvas.render()

        def update_timer():
            if self.countdown_seconds > 1:
                self.countdown_seconds -= 1
                countdown_label.configure(text=f"DETONATION IN: {self.countdown_seconds}")
                self.nuke_timer_job = self.after(1000, update_timer)
            else:
                execute_salvo()

        ctk.CTkButton(
            modal_btn_frame, text="ABORT", fg_color="#D32F2F", hover_color="#9A0007", width=110, command=abort_nuke
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            modal_btn_frame, text="BYPASS (FIRE NOW)", fg_color="#FF6F00", hover_color="#C43E00", width=130, command=execute_salvo
        ).pack(side="left", padx=10)

        self.nuke_timer_job = self.after(1000, update_timer)

    # ------------------------------------------------------------------
    # Menu & Dialogs
    # ------------------------------------------------------------------

    def _build_menu(self):
        menubar = Menu(self)
        self.config(menu=menubar)

        # File
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Canvas", command=self._clear_canvas)
        file_menu.add_separator()
        file_menu.add_command(
            label="Export Simulation Report", command=self.canvas_wrapper.trigger_export
        )
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
            command=lambda: self.toggle_colorblind(self.colorblind_var.get()),
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
            font=("Arial", 14, "bold"),
        ).pack(pady=(25, 8))

        ctk.CTkLabel(
            about,
            text="A network infection simulation tool\nwith AI-driven spread models.",
            justify="center",
        ).pack(pady=5)

        ctk.CTkButton(about, text="Close", width=100, command=about.destroy).pack(
            pady=15
        )

    def on_node_selected(self, node_index: int):
        if 0 <= node_index < len(self.graph.nodes):
            node = self.graph.nodes[node_index]
            self.telemetry_panel.show_node_info(node, self.graph)

    # ------------------------------------------------------------------
    # Settings Window with Dynamic JSON Theme Selector
    # ------------------------------------------------------------------

    def open_settings(self):
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("360x260")
        settings_window.resizable(False, False)

        settings_window.transient(self)
        settings_window.grab_set()
        settings_window.focus_force()
        settings_window.lift()
        settings_window.after(10, settings_window.lift)

        # Dynamic JSON Theme Dropdown Selection & Reload Button Frame
        ctk.CTkLabel(
            settings_window, text="UI Theme Palette:", font=("Arial", 11, "bold")
        ).pack(padx=20, pady=(15, 2), anchor="w")

        theme_row = ctk.CTkFrame(settings_window, fg_color="transparent")
        theme_row.pack(padx=20, pady=(0, 10), anchor="w", fill="x")

        theme_list = list(self.theme_manager.available_themes.keys())
        theme_dropdown = ctk.CTkOptionMenu(
            theme_row,
            values=theme_list,
            command=self.select_json_theme,
        )
        if self.current_theme_name in theme_list:
            theme_dropdown.set(self.current_theme_name)
        theme_dropdown.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Hot-Reload Themes Button
        btn_reload = ctk.CTkButton(
            theme_row,
            text="🔄 Reload",
            width=85,
            command=lambda: self.reload_themes(theme_dropdown),
        )
        btn_reload.pack(side="right")
        ToolTip(btn_reload, "Scan themes/ folder for newly added or edited JSON theme files.")

        # Dark Mode Override Toggle
        dark_var = ctk.BooleanVar(value=self.settings["dark_mode"])
        ctk.CTkCheckBox(
            settings_window,
            text="Dark Mode Override",
            variable=dark_var,
            command=lambda: self.toggle_dark_mode(dark_var.get()),
        ).pack(padx=20, pady=10, anchor="w")

    def toggle_dark_mode(self, enabled: bool):
        self.settings["dark_mode"] = enabled
        if enabled:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    # ------------------------------------------------------------------
    # Simulation Loop Controls
    # ------------------------------------------------------------------

    def show_clippy_ransomware(self):
        """Displays a bright red themed Clippy Ransomware pop-up Easter egg."""
        ransom = ctk.CTkToplevel(self)
        ransom.title("📎 CLIPPY SECURITY ALERT")
        ransom.geometry("420x260")
        ransom.resizable(False, False)
        ransom.transient(self)
        ransom.grab_set()
        ransom.focus_force()
        
        # Hazard dark red background theme
        ransom.configure(fg_color="#1a0000")

        ctk.CTkLabel(
            ransom,
            text="📎 IT LOOKS LIKE YOU'RE BEING RANSOMED!",
            font=("Arial", 14, "bold"),
            text_color="#FF1744"  # Bright alarm red header
        ).pack(pady=(20, 10))

        msg = (
            "Your network topology pointers and node memory addresses "
            "have been encrypted by The Bay Harbor Butcher.\n\n"
            "To recover your simulation session, please transfer 5000 Dogecoin "
            "to Garret's wallet or click 'Pay Ransom' below."
        )

        ctk.CTkLabel(
            ransom, 
            text=msg, 
            font=("Arial", 11), 
            text_color="#FFFFFF",  # High-contrast white text for readability
            justify="center", 
            wraplength=360
        ).pack(pady=10)

        btn_frame = ctk.CTkFrame(ransom, fg_color="transparent")
        btn_frame.pack(pady=15)

        def pay_ransom():
            ransom.destroy()
            if hasattr(self, 'telemetry_panel'):
                self.telemetry_panel.append_raw_event(
                    "CLIPPY RANSOMWARE",
                    "Payment processing failed: Invalid Dogecoin address. Session host forced to cry about it."
                )

        ctk.CTkButton(
            btn_frame, text="Pay Ransom (500 DOGE)", fg_color="#00C853", hover_color="#009624", width=160, command=pay_ransom
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="Refuse", fg_color="#D32F2F", hover_color="#9A0007", width=100, command=ransom.destroy
        ).pack(side="left", padx=5)

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
        # Easter egg: 3 rapid reset clicks triggers Clippy's ransomware prank
        self.reset_click_count = getattr(self, 'reset_click_count', 0) + 1
        if self.reset_click_count == 3:
            self.reset_click_count = 0
            self.show_clippy_ransomware()
            return

        self.pause_sim()
        self.sim_engine.reset()
        self.telemetry_panel.clear()
        self.graph.reset_states()

        if hasattr(self.graph, "pdu_engine") and self.graph.pdu_engine:
            self.graph.pdu_engine.active_pdus.clear()

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

        # ── CRITICAL: Advance PDU packet animation frames on every step tick ──
        if hasattr(self.graph, "pdu_engine") and self.graph.pdu_engine:
            self.graph.pdu_engine.update_packets()

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