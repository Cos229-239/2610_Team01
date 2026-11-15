import customtkinter as ctk


class HighlightBox(ctk.CTkToplevel):
    """Draws a semi-transparent colored border around a target widget."""

    def __init__(self, master, target, pad=6, color="#3B82F6"):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # More transparent overall window (0.0 = invisible, 1.0 = solid)
        try:
            self.attributes("-alpha", 0.55)
        except Exception:
            pass

        self.target = target
        self.pad = pad
        self.border_color = color

        # Transparent-ish background; border is the visible part
        self.configure(fg_color=color)

        # Hollow center: match a dark neutral so it doesn't flash white
        self.inner = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        self.inner.pack(fill="both", expand=True, padx=3, pady=3)

        self._reposition()
        self.after(80, self._tick)

    def _reposition(self):
        try:
            if not self.target.winfo_exists():
                self.destroy()
                return
            self.update_idletasks()
            x = self.target.winfo_rootx() - self.pad
            y = self.target.winfo_rooty() - self.pad
            w = max(40, self.target.winfo_width() + self.pad * 2)
            h = max(28, self.target.winfo_height() + self.pad * 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _tick(self):
        if not self.winfo_exists():
            return
        self._reposition()
        self.after(80, self._tick)


class TutorialWindow(ctk.CTkToplevel):
    """Step-by-step tutorial with optional widget highlight."""

    def __init__(self, master, steps, on_finish=None):
        super().__init__(master)
        self.title("Interactive Tutorial")
        self.geometry("500x300")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.focus_force()

        self.app = master
        self.steps = steps
        self.index = 0
        self.on_finish = on_finish
        self.highlight = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            self, text="", font=("Segoe UI", 16, "bold"), anchor="w"
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(18, 6), sticky="ew")

        self.body_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 13),
            anchor="nw",
            justify="left",
            wraplength=450,
        )
        self.body_label.grid(row=1, column=0, padx=20, pady=8, sticky="nsew")

        self.progress_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 11),
            text_color=("gray40", "gray65"),
        )
        self.progress_label.grid(row=2, column=0, padx=20, pady=(0, 4), sticky="w")

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=3, column=0, padx=20, pady=(8, 16), sticky="ew")

        self.btn_skip = ctk.CTkButton(
            btn_row, text="Skip", width=80, fg_color="gray", command=self._finish
        )
        self.btn_skip.pack(side="left")

        self.btn_next = ctk.CTkButton(
            btn_row, text="Next", width=90, command=self._next
        )
        self.btn_next.pack(side="right")

        self.btn_back = ctk.CTkButton(
            btn_row, text="Back", width=80, command=self._back
        )
        self.btn_back.pack(side="right", padx=(0, 8))

        self.protocol("WM_DELETE_WINDOW", self._finish)
        self._render_step()

    def _clear_highlight(self):
        if self.highlight is not None:
            try:
                self.highlight.destroy()
            except Exception:
                pass
            self.highlight = None

    def _apply_highlight(self, step):
        self._clear_highlight()

        target = step.get("widget")
        if target is None:
            # optional name lookup on app, e.g. "play_button"
            name = step.get("widget_name")
            if name:
                target = getattr(self.app, name, None)

        if target is not None:
            try:
                if target.winfo_exists():
                    self.highlight = HighlightBox(self.app, target)
            except Exception:
                self.highlight = None

        # optional extra callback
        highlight_cb = step.get("highlight")
        if callable(highlight_cb):
            try:
                highlight_cb()
            except Exception:
                pass

    def _render_step(self):
        step = self.steps[self.index]
        self.title_label.configure(text=step.get("title", f"Step {self.index + 1}"))
        self.body_label.configure(text=step.get("body", ""))
        self.progress_label.configure(
            text=f"Step {self.index + 1} of {len(self.steps)}"
        )

        self.btn_back.configure(state="normal" if self.index > 0 else "disabled")
        self.btn_next.configure(
            text="Finish" if self.index == len(self.steps) - 1 else "Next"
        )

        self._apply_highlight(step)

    def _next(self):
        if self.index >= len(self.steps) - 1:
            self._finish()
            return
        self.index += 1
        self._render_step()

    def _back(self):
        if self.index > 0:
            self.index -= 1
            self._render_step()

    def _finish(self):
        self._clear_highlight()
        if callable(self.on_finish):
            try:
                self.on_finish()
            except Exception:
                pass
        self.destroy()