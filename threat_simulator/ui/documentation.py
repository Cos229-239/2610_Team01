import customtkinter as ctk
import re


class DocumentationWindow(ctk.CTkToplevel):
    GLOSSARY_ENTRIES = [
        ("Node", "Any device on the network (PC, router, server, switch, etc.)."),
        ("Edge / Link", "A connection between two nodes. Infection and data travel along edges."),
        ("Topology", "The arrangement of nodes and links (Ring, Mesh, Star, or custom)."),
        ("Patient Zero", "The first infected node. The outbreak starts here."),
        ("Lateral movement", "When a threat moves from an already infected machine to other machines on the same network."),
        ("Firewall (in this sim)", "A barrier on a link that can block or slow infection until its password is cracked."),
        ("Infection Rate", "How aggressively infected nodes try to spread to neighbors each step."),
        ("Defense Power", "How strongly the network resists infection and how easily nodes recover."),
        ("Strategic AI", "Spread logic that prefers high-value targets (routers, well-connected nodes)."),
        ("Uniform AI", "Spread logic that chooses targets more randomly."),
        ("Metasploit (module)", "Simulated exploit / lateral-movement attack against a selected node."),
        ("Gerald (module)", "Simulated password/hash cracking. Can break firewalls on links."),
        ("DDoS (module)", "Simulated flood of traffic meant to overwhelm a target node."),
        ("Nuke", "Fires all threat modules at once, plus a large forced-infection effect."),
        ("Telemetry", "Live stats and event log: time, infected count, threat level, and step history."),
        ("Botnet Power", "How strong the outbreak has become (escalation factor). Higher means faster, harder-to-stop spread."),
        ("Quarantine", "Isolating a link or node so the infection cannot use that path."),
        ("Subnet", "A logical group of addresses. Crossing subnets can be harder for a threat than staying inside one."),
        ("Federal Intervention", "Countermeasure that attempts a large-scale defensive response across the network."),
        ("Zero-Trust Reset", "Countermeasure that forces credential rotation / stricter trust assumptions."),
        ("Sinkhole Routing", "Countermeasure that redirects malicious traffic to a controlled sinkhole."),
        ("Dynamic Quarantine", "Countermeasure that isolates outbreak zones via segmentation."),
    ]

    def __init__(self, master):
        super().__init__(master)
        self.title("Documentation – Adaptive AI Outbreak & Threat Simulator")
        self.geometry("900x600")
        self.minsize(760, 500)
        self.transient(master)
        self.focus_force()

        self._current_topic = "Overview"

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=("gray90", "gray17"), corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="📖  Documentation", font=("Segoe UI", 18, "bold"), anchor="w"
        ).grid(row=0, column=0, padx=20, pady=(14, 2), sticky="w")
        ctk.CTkLabel(
            header,
            text="Learn how networks work and how to use the simulator",
            font=("Segoe UI", 12),
            text_color=("gray40", "gray65"),
            anchor="w",
        ).grid(row=1, column=0, padx=20, pady=(0, 14), sticky="w")

        sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=("gray95", "gray14"))
        sidebar.grid(row=1, column=0, sticky="nsw")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            sidebar, text="TOPICS", font=("Segoe UI", 11, "bold"),
            text_color=("gray45", "gray60"), anchor="w"
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        self.topic_list = ctk.CTkScrollableFrame(sidebar, fg_color="transparent", corner_radius=0)
        self.topic_list.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))

        content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray98", "gray10"))
        content_frame.grid(row=1, column=1, sticky="nsew")
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        self.search_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.search_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 0))
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            self.search_frame, placeholder_text="Search glossary…", height=32
        )
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._on_search)
        self.search_frame.grid_remove()

        self.content_box = ctk.CTkTextbox(
            content_frame, font=("Segoe UI", 13), wrap="word",
            fg_color="transparent", border_width=0, corner_radius=0
        )
        self.content_box.grid(row=1, column=0, sticky="nsew", padx=24, pady=18)

        self.content_box._textbox.tag_configure(
            "h1", font=("Segoe UI", 18, "bold"), foreground="#3B82F6", spacing3=8
        )
        self.content_box._textbox.tag_configure(
            "h2", font=("Segoe UI", 14, "bold"), foreground="#F59E0B", spacing1=12, spacing3=4
        )
        self.content_box._textbox.tag_configure("bold", font=("Segoe UI", 13, "bold"))
        self.content_box._textbox.tag_configure(
            "highlight", foreground="#EF4444", font=("Segoe UI", 13, "bold")
        )
        self.content_box._textbox.tag_configure(
            "tip", foreground="#10B981", font=("Segoe UI", 12, "italic")
        )
        self.content_box._textbox.tag_configure("body", font=("Segoe UI", 13), spacing3=2)
        self.content_box.configure(state="disabled")

        self.topics = {
            "Overview": self._overview(),
            "What is a Network?": self._what_is_a_network(),
            "Network Topologies": self._topologies(),
            "Devices & Roles": self._devices(),
            "How Infection Spreads": self._infection_spread(),
            "Canvas Controls": self._canvas_controls(),
            "AI Modes": self._ai_modes(),
            "Threat Modules": self._threat_modules(),
            "Countermeasures": self._countermeasures(),
            "Firewalls & Passwords": self._firewalls(),
            "Simulation Controls": self._simulation_controls(),
            "Telemetry Panel": self._telemetry(),
            "Settings & Themes": self._settings(),
            "Tips & Easter Eggs": self._tips(),
            "Glossary": "",
        }

        self.topic_buttons = {}
        for topic in self.topics:
            btn = ctk.CTkButton(
                self.topic_list, text=f"  {topic}", anchor="w", height=34,
                fg_color="transparent", text_color=("gray20", "gray85"),
                hover_color=("gray85", "gray25"), font=("Segoe UI", 13),
                corner_radius=6, command=lambda t=topic: self.show_topic(t),
            )
            btn.pack(fill="x", pady=2, padx=4)
            self.topic_buttons[topic] = btn

        self.show_topic("Overview")

    def show_topic(self, topic: str):
        self._current_topic = topic
        for name, btn in self.topic_buttons.items():
            if name == topic:
                btn.configure(
                    fg_color=("#3B82F6", "#2563EB"), text_color="#FFFFFF",
                    hover_color=("#2563EB", "#1D4ED8"),
                )
            else:
                btn.configure(
                    fg_color="transparent", text_color=("gray20", "gray85"),
                    hover_color=("gray85", "gray25"),
                )

        if topic == "Glossary":
            self.search_frame.grid()
            self.search_entry.delete(0, "end")
            content = self._glossary("")
        else:
            self.search_frame.grid_remove()
            content = self.topics.get(topic, "Topic not found.")

        self._insert_formatted(content)

    def _on_search(self, event=None):
        if getattr(self, "_current_topic", None) != "Glossary":
            return
        content = self._glossary(filter_text=self.search_entry.get())
        self._insert_formatted(content)

    def _insert_formatted(self, text: str):
        self.content_box.configure(state="normal")
        self.content_box.delete("1.0", "end")
        tb = self.content_box._textbox

        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                tb.insert("end", "\n")
                continue
            if stripped.isupper() and len(stripped) > 3 and not stripped.startswith("•"):
                tb.insert("end", stripped + "\n", ("h1",))
                continue
            if stripped.startswith("## "):
                tb.insert("end", stripped[3:] + "\n", ("h2",))
                continue
            if stripped.lower().startswith("tip:"):
                tb.insert("end", stripped + "\n", ("tip",))
                continue
            parts = re.split(r"(\*\*[^*]+\*\*)", line)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    tb.insert("end", part[2:-2], ("highlight",))
                else:
                    tb.insert("end", part, ("body",))
            tb.insert("end", "\n")

        self.content_box.configure(state="disabled")

    def _glossary(self, filter_text: str = "") -> str:
        q = (filter_text or "").strip().lower()
        lines = ["GLOSSARY", ""]
        matches = 0
        for term, definition in self.GLOSSARY_ENTRIES:
            if q and q not in term.lower() and q not in definition.lower():
                continue
            lines.append(f"## {term}")
            lines.append(definition)
            lines.append("")
            matches += 1
        if q and matches == 0:
            lines.append(f'No glossary entries match “{filter_text}".')
        elif not q:
            lines.append("Tip: Type in the search box above to filter terms.")
        return "\n".join(lines)

    def _overview(self) -> str:
        return """OVERVIEW

Adaptive AI Outbreak & Threat Simulator is an interactive tool for learning how computer networks work and how threats can spread through them.

## What you can do
• Build or load different network layouts (topologies)
• Place common devices (PC, Router, Server, Switch, Firewall)
• Watch an infection spread using different AI strategies
• Manually launch threat modules (**Metasploit**, **Gerald**, **DDoS**, **Nuke**)
• Deploy **countermeasures** (Federal Intervention, Zero-Trust, Sinkhole, Quarantine)
• Monitor live telemetry and analytics
• Experiment with defenses such as **firewalls**

The goal is to help you understand both network structure and how attacks move through a system.
"""

    def _what_is_a_network(self) -> str:
        return """WHAT IS A COMPUTER NETWORK?

A computer network is a group of devices connected so they can share data.

## Key concepts
• **Node** — Any device on the network (PC, router, server, etc.).
• **Edge / Link** — A connection between two nodes. Data travels along these links.
• **Topology** — The shape or arrangement of the connections.
• **Patient Zero** — The first infected node.

When one node becomes infected, the threat can try to move to its neighbors through the links. The more connected a network is, the faster a threat can usually spread.
"""

    def _topologies(self) -> str:
        return """NETWORK TOPOLOGIES

## Ring Topology
Each node connects to two neighbors, forming a circle. Good for sequential spread.

## Mesh Network
Many nodes connect to many others. Infection can spread very quickly.

## Star Cluster
One central node connects to many outer nodes. The center is a high-value target.

## Custom Canvas
Build any shape you want.

Tip: Try the same threat settings on different topologies and compare results.
"""

    def _devices(self) -> str:
        return """DEVICES & THEIR ROLES

## PC / Laptop
End-user device. Often the starting point of an infection.

## Router
Directs traffic. **High strategic value**.

## Switch
Connects devices inside the same local network.

## Server
Provides services. Attractive target.

## Modem
Connects a network to the outside world.

## Firewall
Can block or filter traffic. In this sim, firewalls sit on edges until cracked.
"""

    def _infection_spread(self) -> str:
        return """HOW INFECTION SPREADS

1. A node becomes **Patient Zero**.
2. Each step, infected nodes may infect neighbors.
3. Success depends on Infection Rate, Defense Power, device defenses, firewalls, and AI mode.

## Statuses
• **HEALTHY** – not infected
• **WARNING** – at risk
• **INFECTED** – compromised
"""

    def _canvas_controls(self) -> str:
        return """CANVAS CONTROLS

• **Move** – Select and drag nodes
• **+ Node** – Place a device
• **+ Edge** – Connect two nodes
• **Infect** – Set Patient Zero
• **Firewall** – Place/remove firewall on a link

Tips: right-click node for options; double-click for CLI; scroll to zoom; right-drag to pan.
"""

    def _ai_modes(self) -> str:
        return """AI MODES

## Strategic AI
Prefers high-value targets (routers, well-connected nodes).

## Uniform
Spreads more randomly.

## Sliders
• **Infection Rate** – aggressiveness
• **Defense Power** – resistance and recovery
"""

    def _threat_modules(self) -> str:
        return """THREAT MODULES

## Run Metasploit
Lateral movement / exploit against the selected node.

## Run Gerald
Password/hash cracking. Can break firewalls.

## Run DDoS
Volumetric flood against the selected node.

## ☢ NUKE
Fires all modules after a countdown, plus a large infection effect.
"""

    def _countermeasures(self) -> str:
        return """COUNTERMEASURES

Use the countermeasure dropdown and **Execute** button in the toolbar.

## Federal Intervention
Large-scale defensive response using current defense power and active node count.

## Zero-Trust Reset
Forces credential rotation / stricter trust assumptions.

## Sinkhole Routing
Redirects malicious traffic toward a controlled sinkhole.

## Dynamic Quarantine
Isolates outbreak zones through segmentation-style isolation.

Tip: Watch the telemetry log after executing a countermeasure.
"""

    def _firewalls(self) -> str:
        return """FIREWALLS & PASSWORDS

Firewalls sit on edges between nodes.
• They slow or block spread
• Each has a password/key
• **Gerald** and normal simulation progress can crack them
• Stronger passwords take longer to crack
"""

    def _simulation_controls(self) -> str:
        return """SIMULATION CONTROLS

• **Play** – start
• **Pause** – freeze
• **Reset** – clean state (Patient Zero stays)

History controls are in the Telemetry panel.
"""

    def _telemetry(self) -> str:
        return """TELEMETRY PANEL

Shows:
• Time, infected count, threat %
• Botnet Power Gauge
• Selected node info
• Event log
• **What just happened?** plain-language summary

Click log lines to jump in history.
"""

    def _settings(self) -> str:
        return """SETTINGS & THEMES

• UI Theme Palette
• Dark Mode Override
• Background Music + volume
• Show/hide **What just happened?**
• Colorblind Mode (View menu)
"""

    def _tips(self) -> str:
        return """TIPS & EASTER EGGS

• Click **Reset** three times for a Clippy event
• Compare Ring vs Mesh vs Star under the same settings
• Use **Analytics** for live graphs
• Open **Help → Glossary** and search terms
• Countermeasures appear in the telemetry log
"""