import customtkinter as ctk

# Custom Theme Color Palette
DARK_BG = "#0B1015"
CONTAINER_BG = "#0F171E"
ACCENT_CYAN = "#1FA2BD"
CYAN_BORDER = "#144955"
TEXT_COLOR = "#E1F5FE"
HOVER_CYAN = "#26C6DA"

class LevelSelectionFrame(ctk.CTkFrame):
    def __init__(self, master, on_start_mission):
        super().__init__(
            master,
            fg_color=CONTAINER_BG,
            corner_radius=10,
            border_width=2,
            border_color=CYAN_BORDER
        )
        self.on_start_mission = on_start_mission

        # Header Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Select Mission & Targeted Area",
            font=ctk.CTkFont(family="Courier", size=22, weight="bold"),
            text_color=ACCENT_CYAN
        )
        self.title_label.pack(anchor="w", padx=25, pady=(25, 15))

        # Radio Group Frame for Levels
        self.level_var = ctk.StringVar(value="Level 1")
        self.levels_container = ctk.CTkFrame(
            self,
            fg_color="#090E13",
            corner_radius=8,
            border_width=1,
            border_color=CYAN_BORDER
        )
        self.levels_container.pack(fill="x", padx=25, pady=10)

        levels = [
            ("Level 1: Small Office (10 Nodes | Low Threat)", "Level 1"),
            ("Level 2: Enterprise Grid (50 Nodes | Adaptive Threat)", "Level 2"),
            ("Level 3: Critical Infrastructure (100+ Nodes | High Severity)", "Level 3")
        ]

        for text, val in levels:
            rb = ctk.CTkRadioButton(
                self.levels_container,
                text=text,
                value=val,
                variable=self.level_var,
                fg_color=ACCENT_CYAN,
                hover_color=HOVER_CYAN,
                border_color=CYAN_BORDER,
                text_color=TEXT_COLOR,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            rb.pack(anchor="w", padx=15, pady=12)

        # Target Subnet Dropdown
        self.subnet_label = ctk.CTkLabel(
            self,
            text="Target User Subnet Zone:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_COLOR
        )
        self.subnet_label.pack(anchor="w", padx=25, pady=(15, 5))

        self.subnet_var = ctk.StringVar(value="Internal LAN")
        self.subnet_dropdown = ctk.CTkOptionMenu(
            self,
            variable=self.subnet_var,
            values=["Internal LAN", "DMZ Network", "SCADA Segment", "Global WAN"],
            fg_color="#122530",
            button_color=CYAN_BORDER,
            button_hover_color=ACCENT_CYAN,
            text_color=TEXT_COLOR,
            dropdown_fg_color=CONTAINER_BG,
            dropdown_text_color=TEXT_COLOR
        )
        self.subnet_dropdown.pack(anchor="w", padx=25, pady=(0, 15))

        # AI Threat Intensity Segmented Control
        self.intensity_label = ctk.CTkLabel(
            self,
            text="AI Threat Intensity:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_COLOR
        )
        self.intensity_label.pack(anchor="w", padx=25, pady=(5, 5))

        self.intensity_var = ctk.StringVar(value="Adaptive AI")
        self.intensity_selector = ctk.CTkSegmentedButton(
            self,
            values=["Standard", "Adaptive AI", "Stress Test"],
            variable=self.intensity_var,
            selected_color=ACCENT_CYAN,
            selected_hover_color=HOVER_CYAN,
            unselected_color="#122530",
            unselected_hover_color=CYAN_BORDER,
            text_color=TEXT_COLOR
        )
        self.intensity_selector.pack(anchor="w", padx=25, pady=(0, 20))

        # Launch Button
        self.launch_btn = ctk.CTkButton(
            self,
            text="Launch Simulation Engine",
            command=self._launch_mission,
            fg_color=ACCENT_CYAN,
            hover_color=HOVER_CYAN,
            text_color="#000000",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=6
        )
        self.launch_btn.pack(anchor="e", padx=25, pady=(10, 25))

    def _launch_mission(self):
        mission_config = {
            "level": self.level_var.get(),
            "target_zone": self.subnet_var.get(),
            "difficulty": self.intensity_var.get()
        }
        self.on_start_mission(mission_config)
