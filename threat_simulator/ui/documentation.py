import customtkinter as ctk


class DocumentationWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Documentation - Adaptive AI Outbreak & Threat Simulator")
        self.geometry("820x560")
        self.minsize(700, 450)
        self.transient(master)
        self.focus_force()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left side - topic list
        sidebar = ctk.CTkFrame(self, width=220)
        sidebar.grid(row=0, column=0, sticky="nsw", padx=(10, 5), pady=10)
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="Topics", font=("Arial", 14, "bold")
        ).pack(pady=(10, 8), padx=10, anchor="w")

        self.topic_list = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        self.topic_list.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        # Right side - content
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        self.content_box = ctk.CTkTextbox(
            content_frame, font=("Segoe UI", 13), wrap="word"
        )
        self.content_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.content_box.configure(state="disabled")

        # Topics and their content
        self.topics = {
            "Overview": self._overview(),
            "Network Topologies": self._topologies(),
            "Canvas Controls": self._canvas_controls(),
            "AI Modes": self._ai_modes(),
            "Threat Modules": self._threat_modules(),
            "Simulation Controls": self._simulation_controls(),
            "Telemetry Panel": self._telemetry(),
            "Settings & Themes": self._settings(),
            "Tips & Easter Eggs": self._tips(),
        }

        self.topic_buttons = {}
        for topic in self.topics:
            btn = ctk.CTkButton(
                self.topic_list,
                text=topic,
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray30"),
                command=lambda t=topic: self.show_topic(t),
            )
            btn.pack(fill="x", pady=2, padx=4)
            self.topic_buttons[topic] = btn

        # Show first topic by default
        self.show_topic("Overview")

    def show_topic(self, topic: str):
        # Highlight selected button
        for name, btn in self.topic_buttons.items():
            if name == topic:
                btn.configure(fg_color=("gray75", "gray35"))
            else:
                btn.configure(fg_color="transparent")

        content = self.topics.get(topic, "Topic not found.")
        self.content_box.configure(state="normal")
        self.content_box.delete("1.0", "end")
        self.content_box.insert("1.0", content)
        self.content_box.configure(state="disabled")

    # ------------------------------------------------------------------
    # Documentation content
    # ------------------------------------------------------------------
    def _overview(self) -> str:
        return """OVERVIEW

Adaptive AI Outbreak & Threat Simulator is an interactive network infection simulation tool.

You can:
• Build or load network topologies
• Place devices (PC, Router, Modem, Server, Switch, Firewall)
• Watch infection spread using different AI strategies
• Manually trigger threat modules (Metasploit, Gerald, DDoS, Nuke)
• Monitor live telemetry and analytics
• Customize themes and audio

The goal is to explore how threats propagate through different network structures and how defenses can slow or stop them.
"""

    def _topologies(self) -> str:
        return """NETWORK TOPOLOGIES

The Scenario dropdown lets you choose a starting layout:

• Level 1: Ring Topology
  Nodes arranged in a ring with some extra connections. Good for observing sequential spread.

• Level 2: Mesh Network
  Highly connected network. Infection can spread very quickly.

• Level 3: Star Cluster
  One central hub connected to many leaf nodes. The center is a high-value target.

• Custom Canvas
  Start with an empty canvas and build your own network using the tools.
"""

    def _canvas_controls(self) -> str:
        return """CANVAS CONTROLS

Mode selector (top toolbar):

• Move – Select and drag nodes
• + Node – Place a new device (choose type in the Device dropdown)
• + Edge – Connect two nodes
• Infect – Set Patient Zero (starting infection point)
• Firewall – Toggle a firewall on an edge (requires a password that can be cracked)

Device types:
PC, Router, Modem, Server, Switch, Firewall

Routers and servers generally have higher strategic value for the AI.
"""

    def _ai_modes(self) -> str:
        return """AI MODES

• Strategic AI
  Prioritizes high-value targets (routers, nodes with many uninfected neighbors, etc.). More realistic and aggressive.

• Uniform
  Spreads more randomly. Useful for comparison and simpler experiments.

Infection Rate and Defense Power sliders control how quickly the outbreak grows and how effective recovery is.
"""

    def _threat_modules(self) -> str:
        return """THREAT MODULES

Manual buttons at the bottom:

• Run Metasploit
  Performs lateral movement / exploit against the currently selected node.

• Run Gerald
  Password / hash cracking burst. Can break firewalls on edges.

• Run DDoS
  Volumetric flood against the selected node.

• ☢ NUKE
  Triggers a dramatic countdown and then fires all threat modules at once (including a Logic Bomb effect).

These can be used at any time, even while the simulation is running or paused.
"""

    def _simulation_controls(self) -> str:
        return """SIMULATION CONTROLS

• Play – Start the simulation loop
• Pause – Stop the simulation
• Reset – Return the network to a clean state (Patient Zero remains)

You can also step backward and forward through history using the controls in the Telemetry panel.

The simulation ends automatically when:
• All nodes are clean (victory), or
• Every node is infected (network compromised)
"""

    def _telemetry(self) -> str:
        return """TELEMETRY PANEL

The right-hand panel shows:

• Current simulation time
• Number of infected vs total nodes
• Threat percentage
• Botnet Power Gauge (escalation factor)
• Selected node details
• Scrollable event log

Clicking entries in the log lets you jump to that point in history.
"""

    def _settings(self) -> str:
        return """SETTINGS & THEMES

Open Settings from the toolbar or the Edit menu.

• UI Theme Palette – Switch between available JSON themes
• Dark Mode Override
• Background Music – Enable/disable and volume slider

Themes are loaded from the themes folder. You can add or edit JSON theme files and use the Reload button.
"""

    def _tips(self) -> str:
        return """TIPS & EASTER EGGS

• Click Reset three times quickly to trigger a special Clippy event.
• Firewalls on edges can be cracked over time by Gerald or by the Nuke protocol.
• Strategic AI is generally more dangerous than Uniform mode on the same topology.
• Use the Analytics button for live graphs of the outbreak.
• The floating Help assistant (📎) can give contextual guidance.
"""