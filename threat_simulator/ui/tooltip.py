import customtkinter as ctk

class ToolTip:
    def __init__(self, widget, text, delay=350):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.delay = delay
        self._after_id = None

        widget.bind("<Enter>", self._schedule_show)
        widget.bind("<Leave>", self._schedule_hide)
        widget.bind("<ButtonPress>", self.hide_tooltip)   # also hide when clicking

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
        if self.tooltip is not None:
            return  # already visible

        # Position just below the widget
        x = self.widget.winfo_rootx() + 15
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.attributes("-topmost", True)
        self.tooltip.geometry(f"+{x}+{y}")

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

        # Hide if the mouse enters the tooltip and then leaves it
        self.tooltip.bind("<Leave>", self.hide_tooltip)

    def hide_tooltip(self, event=None):
        self._cancel_schedule()
        if self.tooltip is not None:
            try:
                self.tooltip.destroy()
            except Exception:
                pass
            self.tooltip = None