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

        # Tracking variables for custom drag positioning
        self._drag_start_x = 0
        self._drag_start_y = 0
        self.is_custom_positioned = False

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
            cursor="fleur",
        )
        self.container.pack(fill="both", expand=True, padx=2, pady=2)

        # Bind mouse drag handlers to move the window
        self.container.bind("<Button-1>", self._start_drag)
        self.container.bind("<B1-Motion>", self._on_drag)

        # Speech Bubble
        self.bubble_frame = ctk.CTkFrame(
            self.container, fg_color=("gray85", "gray25"), corner_radius=10
        )
        self.bubble_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        self.bubble_frame.bind("<Button-1>", self._start_drag)
        self.bubble_frame.bind("<B1-Motion>", self._on_drag)

        self.title_label = ctk.CTkLabel(
            self.bubble_frame,
            text="",
            font=("Arial", 12, "bold"),
            text_color="#3B82F6",
            anchor="w",
        )
        self.title_label.pack(fill="x", padx=10, pady=(8, 2))
        self.title_label.bind("<Button-1>", self._start_drag)
        self.title_label.bind("<B1-Motion>", self._on_drag)

        self.body_label = ctk.CTkLabel(
            self.bubble_frame,
            text="",
            font=("Arial", 11),
            wraplength=220,
            justify="left",
        )
        self.body_label.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        self.body_label.bind("<Button-1>", self._start_drag)
        self.body_label.bind("<B1-Motion>", self._on_drag)

        # Avatar & Controls Row
        self.bottom_row = ctk.CTkFrame(self.container, fg_color="transparent")
        self.bottom_row.pack(fill="x", padx=10, pady=(0, 8))

        # Emoji Avatar Badge
        self.avatar_label = ctk.CTkLabel(
            self.bottom_row, text="📎", font=("Arial", 28)
        )
        self.avatar_label.pack(side="left", padx=(5, 10))
        self.avatar_label.bind("<Button-1>", self._start_drag)
        self.avatar_label.bind("<B1-Motion>", self._on_drag)

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

        # Display initial tip and position
        self.show_tip(0)
        self.reposition()
        self.parent.bind("<Configure>", lambda e: self.reposition())

        # Start idle floating bounce animation
        self._animate_idle()

    def _start_drag(self, event):
        """Records initial click offsets for window dragging."""
        self._drag_start_x = event.x_root - self.winfo_x()
        self._drag_start_y = event.y_root - self.winfo_y()
        self.is_custom_positioned = True

    def _on_drag(self, event):
        """Updates window coordinates as mouse drags."""
        new_x = event.x_root - self._drag_start_x
        new_y = event.y_root - self._drag_start_y
        self.geometry(f"+{new_x}+{new_y}")

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
        """Snaps window near bottom-right corner unless manually dragged by user."""
        if not self.winfo_exists() or self.is_custom_positioned:
            return
        try:
            px = self.parent.winfo_x()
            py = self.parent.winfo_y()
            pw = self.parent.winfo_width()
            ph = self.parent.winfo_height()

            width = 260
            height = 160

            target_x = px + pw - width - 20
            target_y = py + ph - height - 20

            x = max(px + 10, min(target_x, px + pw - width - 10))
            y = max(py + 10, min(target_y, py + ph - height - 10))

            self.geometry(f"{width}x{height}+{max(0, int(x))}+{max(0, int(y))}")
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