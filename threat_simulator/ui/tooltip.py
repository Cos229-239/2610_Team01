import customtkinter as ctk


class ToolTip:
    def __init__(self, widget, text, delay: int = 400):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.delay = delay
        self._after_id = None

        widget.bind("<Enter>", self._schedule_show)
        widget.bind("<Leave>", self._schedule_hide)
        widget.bind("<ButtonPress>", self._schedule_hide)

    def _schedule_show(self, event=None):
        self._cancel_schedule()
        self._after_id = self.widget.after(self.delay, self.show_tooltip)

    def _schedule_hide(self, event=None):
        self._cancel_schedule()
        self.hide_tooltip()

    def _cancel_schedule(self):
        if self._after_id is not None:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def show_tooltip(self, event=None):
        if self.tooltip is not None or not self.text:
            return

        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        try:
            self.tooltip.attributes("-topmost", True)
        except Exception:
            pass

        label = ctk.CTkLabel(
            self.tooltip,
            text=self.text,
            fg_color="#222222",
            text_color="white",
            corner_radius=6,
            padx=10,
            pady=5,
        )
        label.pack()

        # Force Tkinter to calculate window dimensions before positioning
        self.tooltip.update_idletasks()

        # Initial target coordinates
        x = self.widget.winfo_rootx() + 15
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

        # Screen and tooltip dimensions
        screen_width = self.tooltip.winfo_screenwidth()
        screen_height = self.tooltip.winfo_screenheight()
        tw_width = self.tooltip.winfo_width()
        tw_height = self.tooltip.winfo_height()

        # Right edge boundary check (shift left if clipping)
        if x + tw_width > screen_width:
            x = screen_width - tw_width - 10

        # Bottom edge boundary check (flip above the widget if clipping)
        if y + tw_height > screen_height:
            y = self.widget.winfo_rooty() - tw_height - 6

        # Left / Top safety clamps
        if x < 0:
            x = 10
        if y < 0:
            y = 10

        self.tooltip.geometry(f"+{x}+{y}")

    def hide_tooltip(self, event=None):
        self._cancel_schedule()
        if self.tooltip is not None:
            try:
                self.tooltip.destroy()
            except Exception:
                pass
            self.tooltip = None