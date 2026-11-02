import os
import json
from typing import Dict, Any


class ThemeManager:
    def __init__(self, themes_dir_name: str = "themes"):
        # Anchor path relative to this file's location (utils/) up to the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(current_dir, "../"))
        self.themes_dir = os.path.join(root_dir, themes_dir_name)
        
        self.available_themes: Dict[str, Dict[str, Any]] = {}
        self.load_all_themes()

    def load_all_themes(self):
        """Scans the absolute themes directory for JSON configuration files."""
        self.available_themes.clear()

        if not os.path.exists(self.themes_dir):
            os.makedirs(self.themes_dir, exist_ok=True)
            print(f"[ThemeManager] Created missing themes directory at: {self.themes_dir}")

        for filename in os.listdir(self.themes_dir):
            if filename.endswith(".json") and filename != "theme_schema.json":
                filepath = os.path.join(self.themes_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        theme_name = data.get("name", filename.replace(".json", "").replace("_", " ").title())
                        self.available_themes[theme_name] = data
                except Exception as e:
                    print(f"[ThemeManager] Error loading theme file '{filename}': {e}")

        # Fallback default if directory is empty or no valid files found
        if not self.available_themes:
            self.available_themes["Classic Beige"] = {
                "name": "Classic Beige",
                "appearance_mode": "Light",
                "canvas_bg": "#d8ccb0",
                "status_colors": {"HEALTHY": "#69F0AE", "WARNING": "#FFB74D", "INFECTED": "#FF5252"},
                "edge_colors": {"HEALTHY": "#8b5a2b", "WARNING": "#FFB74D", "INFECTED": "#FF5252"},
                "pdu_colors": {"ICMP": "#00E676", "ARP": "#FFD54F", "TCP": "#29B6F6", "INFECT": "#FF1744"}
            }

    def get_theme(self, name: str) -> Dict[str, Any]:
        """Returns theme settings dictionary or fallback default."""
        first_theme = list(self.available_themes.values())[0]
        return self.available_themes.get(name, first_theme)