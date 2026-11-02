import customtkinter as ctk


class PDUControlPanel(ctk.CTkFrame):
    def __init__(self, parent, engine, on_tick_callback):
        super().__init__(parent, fg_color="#1e1e1e", corner_radius=6)
        self.engine = engine
        self.on_tick_callback = on_tick_callback
        self.timer_id = None

        # Play / Pause Toggle (Drives tick progression without forcing attacks)
        self.btn_play = ctk.CTkButton(
            self, text="▶ Play", width=70, fg_color="#2E7D32", command=self.toggle_play
        )
        self.btn_play.pack(side="left", padx=5, pady=5)

        # Step Forward Button
        self.btn_step = ctk.CTkButton(
            self, text="⏭ Step", width=70, fg_color="#0277BD", command=self.step_once
        )
        self.btn_step.pack(side="left", padx=5, pady=5)

        # Explicit Attack Trigger Button
        self.btn_attack = ctk.CTkButton(
            self,
            text="☣️ Launch Attack",
            width=115,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            command=self.launch_attack,
        )
        self.btn_attack.pack(side="left", padx=5, pady=5)

        # Auto-Spread Toggle Switch
        self.switch_auto = ctk.CTkSwitch(
            self,
            text="Auto-Spread",
            font=("Arial", 11),
            progress_color="#D32F2F",
            command=self._toggle_auto_infect,
        )
        self.switch_auto.pack(side="left", padx=(10, 5), pady=5)

        # Reset Simulation Button
        self.btn_reset = ctk.CTkButton(
            self, text="🔄 Reset", width=70, fg_color="#C62828", command=self.reset_simulation
        )
        self.btn_reset.pack(side="left", padx=5, pady=5)

        # Speed Slider
        ctk.CTkLabel(self, text="Speed:", font=("Arial", 11)).pack(side="left", padx=(15, 5))
        self.speed_slider = ctk.CTkSlider(
            self, from_=10, to=150, width=120, command=self._update_speed
        )
        self.speed_slider.set(40)
        self.speed_slider.pack(side="left", padx=5)

    def launch_attack(self):
        """Triggers Patient Zero malware outbreak on demand without auto-playing."""
        if hasattr(self.engine, "trigger_patient_zero_outbreak"):
            self.engine.trigger_patient_zero_outbreak()
        self.on_tick_callback()

    def _toggle_auto_infect(self):
        """Updates the engine's auto-infection flag based on the switch state."""
        if hasattr(self.engine, "auto_infect"):
            self.engine.auto_infect = bool(self.switch_auto.get())

    def toggle_play(self):
        self.engine.is_running = not self.engine.is_running
        if self.engine.is_running:
            self.btn_play.configure(text="⏸ Pause", fg_color="#F57C00")
            self._run_loop()
        else:
            self.btn_play.configure(text="▶ Play", fg_color="#2E7D32")
            if self.timer_id:
                self.after_cancel(self.timer_id)
                self.timer_id = None

    def step_once(self):
        if self.engine.is_running:
            self.toggle_play()
        has_more = self.engine.step_simulation()
        self.on_tick_callback()
        return has_more

    def reset_simulation(self):
        if self.engine.is_running:
            self.toggle_play()
        self.engine.active_pdus.clear()
        if self.engine.graph:
            self.engine.graph.reset_states()
        self.on_tick_callback()

    def _run_loop(self):
        if not self.engine.is_running:
            return

        has_more = self.engine.step_simulation()
        self.on_tick_callback()

        if has_more:
            self.timer_id = self.after(self.engine.tick_delay_ms, self._run_loop)
        else:
            self.toggle_play()

    def _update_speed(self, value):
        # Invert scale: lower delay = faster playback
        self.engine.tick_delay_ms = int(160 - value)