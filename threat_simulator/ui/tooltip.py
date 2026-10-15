import customtkinter as ctk

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None

        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20

        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
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

    def hide_tooltip(self, event=None):

        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
