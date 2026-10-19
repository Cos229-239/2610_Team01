"""
ui/assistant.py
----------------
Animated Desktop Helper Overlay (Clippy-style) for CustomTkinter.
Provides interactive guided tours, contextual tips, and system help.
"""

import math
import customtkinter as ctk

# Outbreak Simulation Guided Tips
HELP_TOPICS = [
    (
        "👋 Welcome!",
        "I'm your AI assistant! Let me guide you through managing network outbreaks and firewalls.",
    ),
    (
        "🎯 Infect",
        "Click any node to toggle 'Patient Zero'. This is where infections originate during simulation!",
    ),
    (
        "+Node",
        "Click the drop down to select the node type, and click on canvas to place the node.",
    ),
    (
        "+Edge",
        "Click on one node, then another to connect them via an edge line.",
    ),
    (
        "🛡️ Active Firewalls",
        "Click on any network edge to deploy a firewall! Enter encryption keys to slow down brute-force attacks.",
    ),
    (
        "⚡ Botnet Scaling",
        "As the AI infects more nodes, its Botnet Power scales up to 100x, cracking simple keys almost instantly!",
    ),
    (
        "🔍 Camera Controls",
        "Use the mouse wheel to zoom in/out, or click and drag the canvas background to pan around the topology.",
    ),
    (
        "⏮️ Time Travel",
        "Click any step entry in the Live Telemetry log box to jump backward or forward to past snapshot states!",
    ),
]


class ClippyAssistant(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.topic_index = 0
        self.anim_phase = 0.0

        # Borderless, always-on-top overlay setup
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Set valid background color matching CustomTkinter dark/light themes
        self.configure(fg_color=("gray90", "gray13"))

        # Container Frame
        self.container = ctk.CTkFrame(
            self,
            fg_color=("gray95", "gray15"),
            corner_radius=12,
            border_width=2,
            border_color="#3B82F6",
        )
        self.container.pack(fill="both", expand=True, padx=2, pady=2)

        # Speech Bubble
        self.bubble_frame = ctk.CTkFrame(
            self.container, fg_color=("gray85", "gray25"), corner_radius=10
        )
        self.bubble_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        self.title_label = ctk.CTkLabel(
            self.bubble_frame,
            text="",
            font=("Arial", 12, "bold"),
            text_color="#3B82F6",
            anchor="w",
        )
        self.title_label.pack(fill="x", padx=10, pady=(8, 2))

        self.body_label = ctk.CTkLabel(
            self.bubble_frame,
            text="",
            font=("Arial", 11),
            wraplength=220,
            justify="left",
        )
        self.body_label.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        # Avatar & Controls Row
        self.bottom_row = ctk.CTkFrame(self.container, fg_color="transparent")
        self.bottom_row.pack(fill="x", padx=10, pady=(0, 8))

        # Emoji Avatar Badge
        self.avatar_label = ctk.CTkLabel(
            self.bottom_row, text="📎", font=("Arial", 28)
        )
        self.avatar_label.pack(side="left", padx=(5, 10))

        # Action Buttons
        self.btn_next = ctk.CTkButton(
            self.bottom_row,
            text="Next Tip ▶",
            width=75,
            height=24,
            font=("Arial", 10, "bold"),
            command=self.next_tip,
        )
        self.btn_next.pack(side="right", padx=2)

        self.btn_close = ctk.CTkButton(
            self.bottom_row,
            text="✕",
            width=24,
            height=24,
            fg_color="#FF5252",
            hover_color="#D32F2F",
            command=self.hide,
        )
        self.btn_close.pack(side="right", padx=2)

        # Display initial tip and stick to parent position
        self.show_tip(0)
        self.reposition()
        self.parent.bind("<Configure>", lambda e: self.reposition())

        # Start idle floating bounce animation
        self._animate_idle()

    def show_tip(self, index: int):
        """Displays a specific help topic from the topics list."""
        self.topic_index = index % len(HELP_TOPICS)
        title, body = HELP_TOPICS[self.topic_index]
        self.title_label.configure(text=title)
        self.body_label.configure(text=body)

    def next_tip(self):
        """Cycles to the next tip topic."""
        self.show_tip(self.topic_index + 1)

    def reposition(self):
        """Snaps the overlay assistant near the bottom-right corner of the parent app."""
        if not self.winfo_exists():
            return
        try:
            px = self.parent.winfo_x()
            py = self.parent.winfo_y()
            pw = self.parent.winfo_width()
            ph = self.parent.winfo_height()

            # Place 260x160 window inside bottom-right corner with padding
            width = 260
            height = 160
            x = px + pw - width - 25
            y = py + ph - height - 25

            self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

    def _animate_idle(self):
        """Creates a continuous floating bounce effect for the assistant emoji."""
        if self.winfo_exists() and self.winfo_viewable():
            self.anim_phase += 0.2
            offset = int(math.sin(self.anim_phase) * 3)
            top_pad = max(0, 4 + offset)
            bottom_pad = max(0, 4 - offset)
            self.avatar_label.pack_configure(pady=(top_pad, bottom_pad))
            self.after(80, self._animate_idle)

    def show(self):
        """Shows and updates position."""
        self.deiconify()
        self.reposition()
        self._animate_idle()

    def hide(self):
        """Hides the assistant window."""
        self.withdraw()