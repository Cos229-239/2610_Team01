import math
import customtkinter as ctk

# Outbreak Simulation Guided Tips
HELP_TOPICS = [
    (
        "👋 Welcome!",
        "I'm your AI assistant! Ask me any question about managing network outbreaks and firewalls.",
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
    def __init__(self, parent, sim_engine=None, graph=None):
        super().__init__(parent)

        self.parent = parent
        self.sim_engine = sim_engine
        self.graph = graph

        self.topic_index = 0
        self.anim_phase = 0.0
        self.typing_frame = None

        # Tracking variables for custom drag positioning
        self._drag_start_x = 0
        self._drag_start_y = 0
        self.is_custom_positioned = False

        # Borderless, always-on-top overlay setup
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Set valid background color matching CustomTkinter dark/light themes
        self.configure(fg_color=("gray90", "gray13"))

        # Main Container Frame using grid layout
        self.container = ctk.CTkFrame(
            self,
            fg_color=("gray95", "gray15"),
            corner_radius=12,
            border_width=2,
            border_color="#3B82F6",
        )
        self.container.pack(fill="both", expand=True, padx=2, pady=2)
        self.container.grid_rowconfigure(1, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Header Control Bar (Row 0)
        self.header_frame = ctk.CTkFrame(
            self.container, fg_color="transparent", height=28, cursor="fleur"
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 2))
        self.header_frame.bind("<Button-1>", self._start_drag)
        self.header_frame.bind("<B1-Motion>", self._on_drag)

        self.avatar_label = ctk.CTkLabel(
            self.header_frame,
            text="📎 Clippy Assistant",
            font=("Arial", 12, "bold"),
            text_color="#3B82F6",
            cursor="fleur",
        )
        self.avatar_label.pack(side="left", padx=4)
        self.avatar_label.bind("<Button-1>", self._start_drag)
        self.avatar_label.bind("<B1-Motion>", self._on_drag)

        self.btn_close = ctk.CTkButton(
            self.header_frame,
            text="✕",
            width=22,
            height=22,
            fg_color="#FF5252",
            hover_color="#D32F2F",
            command=self.hide,
        )
        self.btn_close.pack(side="right", padx=2)

        self.btn_next = ctk.CTkButton(
            self.header_frame,
            text="Tip ▶",
            width=45,
            height=22,
            font=("Arial", 10, "bold"),
            command=self.next_tip,
        )
        self.btn_next.pack(side="right", padx=2)

        # Scrollable Conversation View (Row 1)
        self.chat_scroll = ctk.CTkScrollableFrame(
            self.container, fg_color=("gray85", "gray20"), corner_radius=8
        )
        self.chat_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)

        # Input Row (Row 2 - Fixed Bottom)
        self.input_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(2, 6))

        self.entry_box = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type a message...",
            height=28,
            font=("Arial", 11),
        )
        self.entry_box.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.entry_box.bind("<Button-1>", self._focus_entry)
        self.entry_box.bind("<Return>", lambda event: self.send_message())

        self.btn_send = ctk.CTkButton(
            self.input_frame,
            text="Send",
            width=50,
            height=28,
            font=("Arial", 10, "bold"),
            command=self.send_message,
        )
        self.btn_send.pack(side="right")

        # Initial Welcome Message
        self._append_message("Clippy", HELP_TOPICS[0][1], is_user=False)

        # Initial positioning
        self.reposition()
        self.parent.bind("<Configure>", lambda e: self.reposition())

        # Start idle floating bounce animation
        self._animate_idle()

    # ------------------------------------------------------------------
    # Focus & Input Handlers
    # ------------------------------------------------------------------

    def _focus_entry(self, event=None):
        """Forces window and entry widget focus when user clicks inside text box."""
        self.lift()
        self.focus_force()
        self.entry_box.focus_set()

    # ------------------------------------------------------------------
    # Instant Messaging Engine
    # ------------------------------------------------------------------

    def send_message(self):
        """Processes user chat input, renders an instant message, and displays a typing animation."""
        user_text = self.entry_box.get().strip()
        if not user_text:
            return

        self.entry_box.delete(0, "end")
        self._focus_entry()

        self._append_message("You", user_text, is_user=True)
        self._show_typing_indicator()

        self.after(450, lambda: self._handle_reply(user_text))

    def _show_typing_indicator(self):
        """Renders a temporary typing bubble."""
        self._remove_typing_indicator()
        self.typing_frame = ctk.CTkFrame(
            self.chat_scroll, fg_color=("gray75", "gray30"), corner_radius=8
        )
        self.typing_frame.pack(fill="x", pady=3, padx=2, anchor="w")

        label = ctk.CTkLabel(
            self.typing_frame,
            text="Clippy is typing...",
            font=("Arial", 9, "italic"),
            text_color="gray60",
        )
        label.pack(padx=8, pady=4, anchor="w")
        self._scroll_to_bottom()

    def _remove_typing_indicator(self):
        """Removes typing bubble from view."""
        if self.typing_frame and self.typing_frame.winfo_exists():
            self.typing_frame.destroy()
            self.typing_frame = None

    def _handle_reply(self, user_text: str):
        """Generates and displays the assistant's reply."""
        self._remove_typing_indicator()
        reply = self._generate_response(user_text)
        self._append_message("Clippy", reply, is_user=False)

    def _append_message(self, sender: str, text: str, is_user: bool):
        """Renders speech bubbles inside the scrollable chat frame."""
        msg_frame = ctk.CTkFrame(
            self.chat_scroll,
            fg_color=("#1E88E5", "#1565C0") if is_user else ("gray75", "gray30"),
            corner_radius=8,
        )
        msg_frame.pack(fill="x", pady=3, padx=2, anchor="e" if is_user else "w")

        label = ctk.CTkLabel(
            msg_frame,
            text=f"{sender}: {text}",
            font=("Arial", 10),
            wraplength=220,
            justify="left",
            text_color="white" if is_user else ("black", "white"),
        )
        label.pack(padx=6, pady=4, anchor="w")
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        """Forces chat scrollview to lock to the bottom."""
        self.update_idletasks()
        try:
            self.chat_scroll._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    def _generate_response(self, query: str) -> str:
        """Parses query keywords and inspects live simulation telemetry for context-aware responses."""
        q = query.lower()

        telemetry = None
        if self.sim_engine and getattr(self.sim_engine, "history", None):
            if 0 <= self.sim_engine.history_index < len(self.sim_engine.history):
                telemetry = self.sim_engine.history[self.sim_engine.history_index].telemetry

        # -------------------------------------------------------------
        # LIVE TELEMETRY QUERIES
        # -------------------------------------------------------------
        if "infected" in q or "status" in q or "how many" in q or "state" in q or "outbreak" in q:
            if not telemetry or telemetry.total_nodes == 0:
                return "The simulation hasn't started yet! Add nodes to the canvas and press Play."

            pct = telemetry.threat_level_pct
            inf = telemetry.infected_nodes
            total = telemetry.total_nodes
            power = getattr(telemetry, "escalation_factor", 1.0)

            return (
                f"📊 Live Outbreak Status:\n"
                f"• Infected: {inf} / {total} nodes ({pct:.1f}%)\n"
                f"• Botnet Power: {power:.2f}x\n"
                f"• Status: {telemetry.status}"
            )

        elif "firewall" in q or "password" in q or "crack" in q:
            if not self.graph:
                return "Click an edge line on the canvas to deploy a firewall!"

            firewalls = [e for e in self.graph.edges if getattr(e, "is_firewall", False)]
            if not firewalls:
                return "There are no active firewalls on the network canvas. Click an edge line to deploy one!"

            active_cracks = [f for f in firewalls if getattr(f, "crack_progress", 0.0) > 0.0]
            if active_cracks:
                edge = active_cracks[0]
                return (
                    f"🛡️ Firewall Under Attack!\n"
                    f"• Password: '{edge.password}'\n"
                    f"• Crack Progress: {edge.crack_progress * 100.0:.1f}%\n"
                    f"• Attempts: {edge.crack_attempts:,} / {edge.required_attempts:,}"
                )
            return f"There are {len(firewalls)} active firewall(s) guarding the network topology."

        elif "botnet" in q or "power" in q or "scale" in q:
            power = getattr(telemetry, "escalation_factor", 1.0) if telemetry else 1.0
            return f"⚡ Current Botnet Threat Power is running at {power:.2f}x strength!"

        elif "reset" in q or "clear" in q:
            return "Click 'Clear' to erase the canvas, or 'Reset' to return all nodes to healthy states."
        elif "node" in q or "device" in q or "router" in q:
            return "Use '+ Node' mode to place PCs, Routers, or Modems on the canvas."
        elif "hi" in q or "hello" in q or "hey" in q:
            return "Greetings Commander! Type any question about active infections, firewall status, or botnet power."
        else:
            return "I can inspect live telemetry! Try asking: 'How many nodes are infected?' or 'What is the firewall progress?'"

    def next_tip(self):
        """Displays the next guided tip topic directly in the chat window."""
        self.topic_index = (self.topic_index + 1) % len(HELP_TOPICS)
        title, tip = HELP_TOPICS[self.topic_index]
        self._append_message("Clippy Tip", f"[{title}] {tip}", is_user=False)

    # ------------------------------------------------------------------
    # Drag & Position Handlers
    # ------------------------------------------------------------------

    def _start_drag(self, event):
        """Records initial drag offsets."""
        self._drag_start_x = event.x_root - self.winfo_x()
        self._drag_start_y = event.y_root - self.winfo_y()
        self.is_custom_positioned = True

    def _on_drag(self, event):
        """Updates window coordinates on mouse drag."""
        new_x = event.x_root - self._drag_start_x
        new_y = event.y_root - self._drag_start_y
        self.geometry(f"+{new_x}+{new_y}")

    def reposition(self):
        """Snaps window near bottom-right corner unless manually dragged by user."""
        if not self.winfo_exists() or self.is_custom_positioned:
            return
        try:
            px = self.parent.winfo_x()
            py = self.parent.winfo_y()
            pw = self.parent.winfo_width()
            ph = self.parent.winfo_height()

            width = 300
            height = 320

            target_x = px + pw - width - 20
            target_y = py + ph - height - 20

            x = max(px + 10, min(target_x, px + pw - width - 10))
            y = max(py + 10, min(target_y, py + ph - height - 10))

            self.geometry(f"{width}x{height}+{max(0, int(x))}+{max(0, int(y))}")
        except Exception:
            pass

    def _animate_idle(self):
        """Creates a continuous floating bounce effect for the assistant header."""
        if self.winfo_exists() and self.winfo_viewable():
            self.anim_phase += 0.2
            offset = int(math.sin(self.anim_phase) * 2)
            top_pad = max(0, 6 + offset)
            bottom_pad = max(0, 2 - offset)
            self.header_frame.grid_configure(pady=(top_pad, bottom_pad))
            self.after(90, self._animate_idle)

    def show(self):
        """Shows and updates position."""
        self.deiconify()
        self._focus_entry()
        self.reposition()
        self._animate_idle()

    def hide(self):
        """Hides the assistant window."""
        self.withdraw()