import customtkinter as ctk
from core.simulation import TelemetryData


class TelemetryPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            self, text="Live Telemetry & Metrics", font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Live Metrics Strip
        metrics_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        metrics_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Time
        ctk.CTkLabel(metrics_frame, text="Time", font=("Arial", 11)).grid(
            row=0, column=0, padx=5, pady=(8, 0)
        )
        self.time_label = ctk.CTkLabel(
            metrics_frame, text="0s", font=("Arial", 18, "bold")
        )
        self.time_label.grid(row=1, column=0, padx=5, pady=(0, 8))

        # Infected
        ctk.CTkLabel(metrics_frame, text="Infected", font=("Arial", 11)).grid(
            row=0, column=1, padx=5, pady=(8, 0)
        )
        self.infected_label = ctk.CTkLabel(
            metrics_frame, text="0 / 0", font=("Arial", 18, "bold")
        )
        self.infected_label.grid(row=1, column=1, padx=5, pady=(0, 8))

        # Threat
        ctk.CTkLabel(metrics_frame, text="Threat", font=("Arial", 11)).grid(
            row=0, column=2, padx=5, pady=(8, 0)
        )
        self.threat_label = ctk.CTkLabel(
            metrics_frame, text="0.0%", font=("Arial", 18, "bold")
        )
        self.threat_label.grid(row=1, column=2, padx=5, pady=(0, 8))

        # Status
        ctk.CTkLabel(metrics_frame, text="Status", font=("Arial", 11)).grid(
            row=0, column=3, padx=5, pady=(8, 0)
        )
        self.status_label = ctk.CTkLabel(
            metrics_frame, text="IDLE", font=("Arial", 14, "bold")
        )
        self.status_label.grid(row=1, column=3, padx=5, pady=(0, 8))

        # --- BOTNET THREAT MULTIPLIER GAUGE (1.0x - 100.0x) ---
        botnet_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        botnet_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        botnet_frame.grid_columnconfigure(0, weight=1)

        header_box = ctk.CTkFrame(botnet_frame, fg_color="transparent")
        header_box.grid(row=0, column=0, padx=8, pady=(6, 2), sticky="ew")

        ctk.CTkLabel(
            header_box, text="Botnet Power Gauge:", font=("Arial", 11, "bold")
        ).pack(side="left")

        self.botnet_val_label = ctk.CTkLabel(
            header_box, text="1.00x", font=("Consolas", 12, "bold"), text_color="#69F0AE"
        )
        self.botnet_val_label.pack(side="right")

        self.botnet_gauge = ctk.CTkProgressBar(botnet_frame, height=10)
        self.botnet_gauge.set(0.01)
        self.botnet_gauge.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="ew")

        # Selected Node Information
        self.node_info_frame = ctk.CTkFrame(self)
        self.node_info_frame.grid(
            row=3,
            column=0,
            padx=10,
            pady=5,
            sticky="ew"
        )

        ctk.CTkLabel(
            self.node_info_frame,
            text="Selected Node",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=5, pady=(5, 2))

        self.node_info_label = ctk.CTkLabel(
            self.node_info_frame,
            text="No node selected",
            justify="left"
        )
        self.node_info_label.pack(
            anchor="w",
            padx=5,
            pady=(0, 5)
        )

        # Scrolling Log
        self.log_box = ctk.CTkTextbox(self, font=("Courier", 12))
        self.log_box.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

        # Navigation bar
        nav_frame = ctk.CTkFrame(self)
        nav_frame.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="ew")
        nav_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_back = ctk.CTkButton(
            nav_frame, text="◀ Step Back", command=master.step_back, width=100
        )
        self.btn_back.grid(row=0, column=0, padx=5, pady=5)

        self.step_indicator = ctk.CTkLabel(nav_frame, text="Step 0 / 0")
        self.step_indicator.grid(row=0, column=1, padx=5, pady=5)

        self.btn_fwd = ctk.CTkButton(
            nav_frame, text="Step Forward ▶", command=master.step_forward, width=100
        )
        self.btn_fwd.grid(row=0, column=2, padx=5, pady=5)

        self.log_box.bind("<Button-1>", self._on_log_click)
        self._log_step_map = {}

    def _update_metrics_and_gauge(self, data: TelemetryData):
        """Helper to update all live metric labels and the botnet gauge."""
        self.time_label.configure(text=f"{data.sim_time_seconds}s")
        self.infected_label.configure(
            text=f"{data.infected_nodes} / {data.total_nodes}"
        )
        self.threat_label.configure(text=f"{data.threat_level_pct:.1f}%")
        self.status_label.configure(text=data.status)

        # Color the threat / status labels based on threat percentage
        if data.threat_level_pct > 75:
            self.threat_label.configure(text_color="#FF5252")
            self.status_label.configure(text_color="#FF5252")
        elif data.threat_level_pct > 40:
            self.threat_label.configure(text_color="#FFB74D")
            self.status_label.configure(text_color="#FFB74D")
        else:
            self.threat_label.configure(text_color=("#2E7D32", "#69F0AE"))
            self.status_label.configure(text_color=("#2E7D32", "#69F0AE"))

        # --- UPDATE BOTNET POWER GAUGE ---
        power_x = getattr(data, "escalation_factor", 1.0)
        
        # Map 1.0x -> 100.0x onto 0.0 -> 1.0 progress range
        gauge_val = min(1.0, max(0.01, (power_x - 1.0) / 99.0))
        self.botnet_gauge.set(gauge_val)

        # Dynamic color transitions for the power gauge
        if power_x > 50.0:
            gauge_color = "#FF1744"  # Critical Red
        elif power_x > 15.0:
            gauge_color = "#FF9100"  # High Orange
        elif power_x > 3.0:
            gauge_color = "#FFB74D"  # Warning Amber
        else:
            gauge_color = "#69F0AE"  # Low Green

        self.botnet_gauge.configure(progress_color=gauge_color)
        self.botnet_val_label.configure(
            text=f"{power_x:.2f}x", text_color=gauge_color
        )

    def append_log(self, data: TelemetryData, history_index: int = None):
        self._update_metrics_and_gauge(data)

        # Append to history log
        start_line = int(self.log_box.index("end-1c").split(".")[0])
        self.log_box.insert("end", data.format_log())
        end_line = int(self.log_box.index("end-1c").split(".")[0])

        if history_index is not None:
            for line in range(start_line, end_line):
                self._log_step_map[line] = history_index

        self.log_box.see("end")
        self._update_indicator()

    def show_snapshot(self, data: TelemetryData, history_index: int):
        """Called when user jumps to a past step – updates metrics and gauge only."""
        self._update_metrics_and_gauge(data)
        self._update_indicator(history_index)

    def _update_indicator(self, current: int = None):
        engine = self.master.sim_engine
        total = len(engine.history)
        idx = current if current is not None else engine.history_index
        self.step_indicator.configure(text=f"Step {idx + 1} / {total}")
        self.btn_back.configure(
            state="normal" if engine.can_step_back() else "disabled"
        )
        self.btn_fwd.configure(
            state="normal" if engine.can_step_forward() else "disabled"
        )

    def _on_log_click(self, event):
        index = self.log_box.index(f"@{event.x},{event.y}")
        line = int(index.split(".")[0])
        if line in self._log_step_map:
            self.master.jump_to_step(self._log_step_map[line])

    def show_node_info(self, node, graph):
        node_index = graph.nodes.index(node)
        connection = sum(
            1
            for edge in graph.edges
            if edge.u == node_index or edge.v == node_index
        )

        self.node_info_label.configure(
            text=(
                f"ID: {node.id}\n"
                f"Type: {node.node_type}\n"
                f"Status: {node.status}\n"
                f"Patient Zero: {'Yes' if node.is_patient_zero else 'No'}\n"
                f"Connections: {connection}"
            )
        )

    def clear(self):
        self.log_box.delete("1.0", "end")
        self.time_label.configure(text="0s")
        self.infected_label.configure(text="0 / 0")
        self.threat_label.configure(text="0.0%", text_color=("gray10", "gray90"))
        self.status_label.configure(text="IDLE", text_color=("gray10", "gray90"))
        self.botnet_val_label.configure(text="1.00x", text_color="#69F0AE")
        self.botnet_gauge.set(0.01)
        self.botnet_gauge.configure(progress_color="#69F0AE")
        self._log_step_map.clear()
        self._update_indicator()