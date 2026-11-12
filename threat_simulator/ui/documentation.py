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

        # ---------- Header ----------
        header = ctk.CTkFrame(self, fg_color=("gray90", "gray17"), corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="📖  Documentation",
            font=("Segoe UI", 18, "bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=20, pady=(14, 2), sticky="w")

        ctk.CTkLabel(
            header,
            text="Learn how networks work and how to use the simulator",
            font=("Segoe UI", 12),
            text_color=("gray40", "gray65"),
            anchor="w",
        ).grid(row=1, column=0, padx=20, pady=(0, 14), sticky="w")

        # ---------- Sidebar ----------
        sidebar = ctk.CTkFrame(
            self, width=230, corner_radius=0, fg_color=("gray95", "gray14")
        )
        sidebar.grid(row=1, column=0, sticky="nsw")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            sidebar,
            text="TOPICS",
            font=("Segoe UI", 11, "bold"),
            text_color=("gray45", "gray60"),
            anchor="w",
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        self.topic_list = ctk.CTkScrollableFrame(
            sidebar, fg_color="transparent", corner_radius=0
        )
        self.topic_list.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))

        # ---------- Content area ----------
        content_frame = ctk.CTkFrame(
            self, corner_radius=0, fg_color=("gray98", "gray10")
        )
        content_frame.grid(row=1, column=1, sticky="nsew")
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Search bar (Glossary only)
        self.search_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.search_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 0))
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Search glossary…",
            height=32,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._on_search)
        self.search_frame.grid_remove()

        self.content_box = ctk.CTkTextbox(
            content_frame,
            font=("Segoe UI", 13),
            wrap="word",
            fg_color="transparent",
            border_width=0,
            corner_radius=0,
        )
        self.content_box.grid(row=1, column=0, sticky="nsew", padx=24, pady=18)

        # Text tags
        self.content_box._textbox.tag_configure(
            "h1", font=("Segoe UI", 18, "bold"), foreground="#3B82F6", spacing3=8
        )
        self.content_box._textbox.tag_configure(
            "h2",
            font=("Segoe UI", 14, "bold"),
            foreground="#F59E0B",
            spacing1=12,
            spacing3=4,
        )
        self.content_box._textbox.tag_configure(
            "bold", font=("Segoe UI", 13, "bold")
        )
        self.content_box._textbox.tag_configure(
            "highlight", foreground="#EF4444", font=("Segoe UI", 13, "bold")
        )
        self.content_box._textbox.tag_configure(
            "tip", foreground="#10B981", font=("Segoe UI", 12, "italic")
        )
        self.content_box._textbox.tag_configure(
            "body", font=("Segoe UI", 13), spacing3=2
        )

        self.content_box.configure(state="disabled")

        # Static topics (Glossary is built dynamically)
        self.topics = {
            "Overview": self._overview(),
            "What is a Network?": self._what_is_a_network(),
            "Network Topologies": self._topologies(),
            "Devices & Roles": self._devices(),
            "How Infection Spreads": self._infection_spread(),
            "Canvas Controls": self._canvas_controls(),
            "AI Modes": self._ai_modes(),
            "Threat Modules": self._threat_modules(),
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
                self.topic_list,
                text=f"  {topic}",
                anchor="w",
                height=34,
                fg_color="transparent",
                text_color=("gray20", "gray85"),
                hover_color=("gray85", "gray25"),
                font=("Segoe UI", 13),
                corner_radius=6,
                command=lambda t=topic: self.show_topic(t),
            )
            btn.pack(fill="x", pady=2, padx=4)
            self.topic_buttons[topic] = btn

        self.show_topic("Overview")

    def show_topic(self, topic: str):
        self._current_topic = topic

        for name, btn in self.topic_buttons.items():
            if name == topic:
                btn.configure(
                    fg_color=("#3B82F6", "#2563EB"),
                    text_color="#FFFFFF",
                    hover_color=("#2563EB", "#1D4ED8"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("gray20", "gray85"),
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
        query = self.search_entry.get()
        content = self._glossary(filter_text=query)
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

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------
    def _overview(self) -> str:
        return """OVERVIEW

Adaptive AI Outbreak & Threat Simulator is an interactive tool for learning how computer networks work and how threats can spread through them.

## What you can do
• Build or load different network layouts (topologies)
• Place common devices (PC, Router, Server, Switch, Firewall)
• Watch an infection spread using different AI strategies
• Manually launch threat modules (**Metasploit**, **Gerald**, **DDoS**, **Nuke**)
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
• **Topology** — The shape or arrangement of the connections. Topology strongly affects how fast information (or a threat) can spread.
• **Patient Zero** — The first infected node. In real incidents this is similar to the first compromised machine in an outbreak.

When one node becomes infected, the threat can try to move to its neighbors through the links. The more connected a network is, the faster a threat can usually spread.
"""

    def _topologies(self) -> str:
        return """NETWORK TOPOLOGIES

Topology = how devices are arranged and connected.

## Ring Topology
Each node connects to two neighbors, forming a circle.
• Traffic (or infection) often travels around the ring
• Simple and organized, but a few broken links can disrupt the path
• Good for watching sequential spread

## Mesh Network
Many nodes connect to many others.
• Highly redundant and resilient
• Infection can spread very quickly because there are many paths
• Common in modern dense networks

## Star Cluster
One central node connects to many outer nodes.
• Easy to manage
• The center is a **high-value target** — if it falls, many devices are at risk
• Very common in offices and homes (router in the middle)

## Custom Canvas
Build any shape you want. Useful for testing ideas or recreating a real layout.

Tip: Try the same threat settings on different topologies and compare how fast the network falls.
"""

    def _devices(self) -> str:
        return """DEVICES & THEIR ROLES

## PC / Laptop
End-user device. Often the starting point of an infection (email, download, etc.).

## Router
Directs traffic between networks or parts of a network. **High strategic value** — compromising a router can open many paths.

## Switch
Connects devices inside the same local network. Important for local spread.

## Server
Provides services (files, websites, authentication). Attractive target because many users depend on it.

## Modem
Connects a network to the outside world (ISP). Less common as a lateral-movement target in this sim.

## Firewall
Security device that can block or filter traffic. In this simulator, firewalls appear on edges and can slow or stop spread until they are cracked.

Different device types can have different defense strengths. The **Strategic AI** prefers high-value targets such as routers and well-connected nodes.
"""

    def _infection_spread(self) -> str:
        return """HOW INFECTION SPREADS

The simulator models a simplified cyber outbreak:

1. A node becomes **Patient Zero** (manually or by scenario).
2. On each time step, infected nodes may try to infect their neighbors.
3. Success depends on:
   • Infection Rate slider
   • Defense Power slider
   • Device type defenses
   • Whether a **firewall** is present on the link
   • AI mode (Strategic vs Uniform)

## Statuses you will see
• **HEALTHY** – not infected
• **WARNING** – next to an infected node (at risk)
• **INFECTED** – compromised
• Firewall / cracking progress – the link is protected but under attack

This is similar to real malware that moves laterally across a network after the first machine is compromised.
"""

    def _canvas_controls(self) -> str:
        return """CANVAS CONTROLS

## Mode selector (top toolbar)
• **Move** – Select and drag nodes
• **+ Node** – Place a new device (choose type in the Device dropdown)
• **+ Edge** – Connect two nodes
• **Infect** – Set Patient Zero (the starting point of the outbreak)
• **Firewall** – Place or remove a firewall on a link

## Extra tips
• Right-click a node for more options (set Patient Zero, force infect/clean, edit IP, delete)
• Double-click a node to open a simple CLI-style terminal
• Scroll to zoom, right-drag to pan
"""

    def _ai_modes(self) -> str:
        return """AI MODES

## Strategic AI
Tries to choose the most useful targets first (routers, highly connected nodes, etc.).
Behaves more like a skilled attacker moving through a network.

## Uniform
Spreads more randomly.
Useful as a baseline to compare against Strategic AI.

## Sliders
• **Infection Rate** – how aggressive the spread is
• **Defense Power** – how hard it is for the threat to succeed and how quickly nodes can recover
"""

    def _threat_modules(self) -> str:
        return """THREAT MODULES

Manual actions you can trigger at any time:

## Run Metasploit
Simulates lateral movement / exploitation against the selected node.
In real life, Metasploit is a framework used for developing and running exploits.

## Run Gerald
Password / hash cracking burst.
Can break **firewalls** that protect links.

## Run DDoS
Simulates a volumetric flood against the selected node (overwhelming it with traffic).

## ☢ NUKE
Fires all modules at once after a short countdown, plus an extra “logic bomb” effect that infects many remaining healthy nodes.

Use these to experiment with sudden escalations or to recover a stuck scenario.
"""

    def _firewalls(self) -> str:
        return """FIREWALLS & PASSWORDS

In this simulator, firewalls sit on the connections (edges) between nodes.

• A firewall can block or slow the spread of infection across that link
• Each firewall has a **password / encryption key**
• The **Gerald** module (and the normal simulation over time) can attempt to crack the password
• Progress is shown on the link. When cracking finishes, the firewall falls and the link becomes usable by the threat

You can place firewalls with the Firewall tool and optionally set a custom password. Stronger / longer passwords take longer to crack.
"""

    def _simulation_controls(self) -> str:
        return """SIMULATION CONTROLS

• **Play** – Start the simulation clock
• **Pause** – Freeze the simulation
• **Reset** – Return nodes and edges to a clean state (Patient Zero stays)

You can also step backward and forward through history using the Telemetry panel controls.

The simulation ends when:
• Every node is clean again (**victory**), or
• Every node is infected (**network compromised**)
"""

    def _telemetry(self) -> str:
        return """TELEMETRY PANEL

The right-hand panel shows live information:

• Simulation time
• Infected vs total nodes
• Threat percentage
• **Botnet Power Gauge** (how strong the outbreak has become)
• Details of the currently selected node
• Scrollable event log
• **What just happened?** plain-language summary of the latest step

Clicking items in the log lets you jump back to that moment in the simulation history.
"""

    def _settings(self) -> str:
        return """SETTINGS & THEMES

Open Settings from the toolbar or the Edit menu.

• **UI Theme Palette** – Change the visual style of the app
• **Dark Mode Override**
• **Background Music** – Turn music on/off and adjust volume
• **What just happened?** – Show or hide the plain-language step summary
• **Colorblind Mode** (View menu) – Switches to a colorblind-friendly palette for node/edge status colors

Themes are loaded from JSON files in the themes folder. You can add your own and press Reload.
"""

    def _tips(self) -> str:
        return """TIPS & EASTER EGGS

• Click **Reset** three times quickly to trigger a special Clippy event
• Firewalls slow the outbreak but can be cracked over time or by Gerald / Nuke
• **Strategic AI** is usually more dangerous than Uniform mode on the same topology
• Try the same infection settings on Ring vs Mesh vs Star and compare the results
• Use the **Analytics** button for live graphs of the outbreak
• The floating Help assistant (📎) can give contextual guidance while you work
• Open **Help → Glossary** and use the search box to look up terms
"""