import os
from typing import Dict, Optional, Tuple
import customtkinter as ctk
from PIL import Image, ImageTk

from core.node_types import NODE_TYPES
from core.topology import NetworkGraph

STATUS_COLORS = {
    "INFECTED": "#FF5252",
    "WARNING": "#FFB74D",
    "HEALTHY": "#69F0AE",
}

EDGE_COLORS = {
    "INFECTED": "#FF5252",
    "WARNING": "#FFB74D",
    "HEALTHY": "#8b5a2b",
}


class SpriteSheetManager:
    def __init__(self, atlas_path="assets/zombie_spritesheet_v1.png"):
        if os.path.exists(atlas_path):
            self.atlas = Image.open(atlas_path).convert("RGBA")
        else:
            self.atlas = Image.new("RGBA", (512, 256), (0, 0, 0, 0))

        self.regions = {
            "BIOHAZARD": (0, 0, 128, 128),
            "SKULL": (135, 2, 167, 34),
            "CRAWLER": (16, 130, 48, 162),
            "SHAMBLER": (80, 130, 112, 162),
            "ROUTER": (304, 130, 336, 162),
            "LAPTOP": (368, 130, 400, 162),
        }
        self._cache = {}

    def get_sprite(self, name, size=(32, 32)):
        cache_key = (name, size)
        if name not in self.regions:
            return None
        if cache_key not in self._cache:
            crop_box = self.regions[name]
            sprite = self.atlas.crop(crop_box)
            if size:
                sprite = sprite.resize(size, Image.Resampling.LANCZOS)
            self._cache[cache_key] = ImageTk.PhotoImage(sprite)
        return self._cache[cache_key]


class NetworkCanvas(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#d8ccb0", highlightthickness=0, **kwargs)

        self.mode = "SELECT"
        self.active_node_type = "PC"
        self.graph: Optional[NetworkGraph] = None
        self.selected_node_idx: Optional[int] = None

        self.mouse_x: float = 0.0
        self.mouse_y: float = 0.0

        # Stores button hitboxes for firewall password edit buttons: index -> (x1, y1, x2, y2)
        self.firewall_btn_bounds: Dict[int, Tuple[float, float, float, float]] = {}

        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Motion>", self._on_mouse_move)

        self.sprite_manager = SpriteSheetManager()

    def set_mode(self, mode: str):
        self.mode = mode
        self.selected_node_idx = None
        self.config(cursor="")
        self.render()

    def set_active_node_type(self, node_type: str):
        self.active_node_type = node_type

    def set_graph(self, graph: NetworkGraph):
        self.graph = graph
        self.render()

    def _get_node_at_pos(
        self, x: float, y: float, radius: float = 16.0
    ) -> Optional[int]:
        if not self.graph:
            return None
        for i, node in enumerate(self.graph.nodes):
            dist = ((node.x - x) ** 2 + (node.y - y) ** 2) ** 0.5
            if dist <= radius:
                return i
        return None

    def _prompt_firewall_password(self, edge_idx: int, is_update: bool = False):
        """Displays a modal dialog allowing the user to assign or update a custom password key."""
        title_text = "Update Firewall Password" if is_update else "Assign Firewall Password"
        prompt_text = (
            "Enter New Encryption Key (resets crack progress):"
            if is_update
            else "Enter Firewall Password (or leave blank for random):"
        )

        dialog = ctk.CTkInputDialog(text=prompt_text, title=title_text)
        user_pwd = dialog.get_input()

        if user_pwd is not None:
            if is_update:
                # Update password directly and reset cracking progress without disarming barrier
                edge = self.graph.edges[edge_idx]
                if user_pwd.strip():
                    edge.password = user_pwd.strip().upper()[:6]
                edge.crack_progress = 0.0
            else:
                self.graph.toggle_firewall_at_index(edge_idx, custom_pwd=user_pwd)
            self.render()

    def _on_click(self, event):
        if not self.graph:
            return

        self.mouse_x = float(event.x)
        self.mouse_y = float(event.y)

        # -------------------------------------------------------------
        # FIREWALL BARRIER & PASSWORD BUTTON CLICK HANDLING
        # -------------------------------------------------------------
        if self.mode == "FIREWALL":
            # 1. Check if user clicked a Firewall Password Edit Button (⚙️)
            for edge_idx, (bx1, by1, bx2, by2) in self.firewall_btn_bounds.items():
                if bx1 <= event.x <= bx2 and by1 <= event.y <= by2:
                    self._prompt_firewall_password(edge_idx, is_update=True)
                    return

            # 2. Toggle or create firewall on nearest edge segment
            edge_idx = self.graph.find_edge_near_point(event.x, event.y)
            if edge_idx is not None:
                edge = self.graph.edges[edge_idx]
                if edge.is_firewall:
                    self.graph.toggle_firewall_at_index(edge_idx)
                    self.render()
                else:
                    self._prompt_firewall_password(edge_idx)
            return

        clicked_idx = self._get_node_at_pos(event.x, event.y)

        if self.mode == "ADD_NODE":
            if clicked_idx is None:
                self.graph.add_node(
                    event.x, event.y, node_type=self.active_node_type
                )
                self.render()

        elif self.mode == "CONNECT_EDGE":
            if clicked_idx is not None:
                if self.selected_node_idx is None:
                    self.selected_node_idx = clicked_idx
                else:
                    self.graph.add_edge(self.selected_node_idx, clicked_idx)
                    self.selected_node_idx = None
                self.render()
            else:
                self.selected_node_idx = None
                self.render()

        elif self.mode == "SET_ORIGIN":
            if clicked_idx is not None:
                self.graph.set_patient_zero(clicked_idx)
                self.render()

        elif self.mode == "SELECT":
            if clicked_idx is not None:
                self.selected_node_idx = clicked_idx

    def _on_drag(self, event):
        self.mouse_x = float(event.x)
        self.mouse_y = float(event.y)
        if (
            self.mode == "SELECT"
            and self.selected_node_idx is not None
            and self.graph
        ):
            node = self.graph.nodes[self.selected_node_idx]
            node.x = event.x
            node.y = event.y
            self.render()

    def _on_mouse_move(self, event):
        self.mouse_x = float(event.x)
        self.mouse_y = float(event.y)

        if self.mode == "FIREWALL" and self.graph:
            # Check hover over gear button
            is_hovering_btn = any(
                bx1 <= event.x <= bx2 and by1 <= event.y <= by2
                for bx1, by1, bx2, by2 in self.firewall_btn_bounds.values()
            )
            hovered_edge = self.graph.find_edge_near_point(event.x, event.y)

            if is_hovering_btn:
                self.config(cursor="hand2")
            else:
                self.config(cursor="X_cursor" if hovered_edge is not None else "crosshair")
        elif self.mode == "CONNECT_EDGE" and self.selected_node_idx is not None:
            self.render()

    def render(self):
        self.delete("all")
        self.firewall_btn_bounds.clear()

        if not self.graph:
            return

        # 1. Render Edges & Firewall Security Barriers
        for index, edge in enumerate(self.graph.edges):
            if edge.u < len(self.graph.nodes) and edge.v < len(self.graph.nodes):
                n1, n2 = self.graph.nodes[edge.u], self.graph.nodes[edge.v]

                if getattr(edge, "is_firewall", False):
                    # Outer cyan security wall glow
                    self.create_line(
                        n1.x, n1.y, n2.x, n2.y, fill="#00E5FF", width=6
                    )

                    progress = getattr(edge, "crack_progress", 0.0)
                    beam_color = (
                        "#FF1744"
                        if progress > 0.7
                        else ("#FF9100" if progress > 0.3 else "#FFFFFF")
                    )

                    # Core beam
                    self.create_line(
                        n1.x, n1.y, n2.x, n2.y, fill=beam_color, width=2
                    )

                    # Midpoint Firewall Badge & Password Display
                    mid_x, mid_y = (n1.x + n2.x) / 2, (n1.y + n2.y) / 2
                    pwd = getattr(edge, "password", "LOCK")

                    # Badge background
                    self.create_rectangle(
                        mid_x - 30,
                        mid_y - 14,
                        mid_x + 10,
                        mid_y + 14,
                        fill="#002b36",
                        outline=beam_color,
                        width=2,
                    )

                    label_text = f"🔑{pwd}\n{int(progress * 100)}%"
                    self.create_text(
                        mid_x - 10,
                        mid_y,
                        text=label_text,
                        fill="#00E5FF",
                        font=("Consolas", 7, "bold"),
                        justify="center",
                    )

                    # Password Edit Button (⚙️)
                    btn_x1, btn_y1 = mid_x + 12, mid_y - 14
                    btn_x2, btn_y2 = mid_x + 32, mid_y + 14

                    self.firewall_btn_bounds[index] = (btn_x1, btn_y1, btn_x2, btn_y2)

                    self.create_rectangle(
                        btn_x1,
                        btn_y1,
                        btn_x2,
                        btn_y2,
                        fill="#00B0FF",
                        outline="#FFFFFF",
                        width=1,
                    )
                    self.create_text(
                        (btn_x1 + btn_x2) / 2,
                        (btn_y1 + btn_y2) / 2,
                        text="⚙️",
                        fill="#FFFFFF",
                        font=("Arial", 9),
                    )
                else:
                    edge_color = EDGE_COLORS.get(edge.status, "#444444")
                    edge_width = 2 if edge.status != "HEALTHY" else 1
                    self.create_line(
                        n1.x, n1.y, n2.x, n2.y, fill=edge_color, width=edge_width
                    )

        # 2. Render Connection Preview Line
        if self.mode == "CONNECT_EDGE" and self.selected_node_idx is not None:
            if self.selected_node_idx < len(self.graph.nodes):
                src = self.graph.nodes[self.selected_node_idx]
                self.create_line(
                    src.x,
                    src.y,
                    self.mouse_x,
                    self.mouse_y,
                    fill="#FFD54F",
                    width=2,
                    dash=(4, 4),
                )

        # 3. Render Nodes and Sprites
        for i, node in enumerate(self.graph.nodes):
            type_cfg = NODE_TYPES.get(
                getattr(node, "node_type", "PC"), NODE_TYPES.get("PC")
            )
            radius = type_cfg.radius if type_cfg else 14

            if node.is_patient_zero:
                self.create_oval(
                    node.x - 32,
                    node.y - 32,
                    node.x + 32,
                    node.y + 32,
                    fill="#ff3b3b",
                    outline="",
                    stipple="gray50",
                )
                self.create_oval(
                    node.x - 20,
                    node.y - 20,
                    node.x + 20,
                    node.y + 20,
                    fill="#ff7b00",
                    outline="#D32F2F",
                    width=2,
                )
            elif self.mode == "CONNECT_EDGE" and i == self.selected_node_idx:
                self.create_oval(
                    node.x - radius - 6,
                    node.y - radius - 6,
                    node.x + radius + 6,
                    node.y + radius + 6,
                    outline="#FFD54F",
                    width=3,
                )
            elif self.mode == "SELECT" and i == self.selected_node_idx:
                self.create_oval(
                    node.x - radius - 4,
                    node.y - radius - 4,
                    node.x + radius + 4,
                    node.y + radius + 4,
                    outline="#333333",
                    width=2,
                )

            if node.is_patient_zero:
                sprite_img = self.sprite_manager.get_sprite(
                    "BIOHAZARD", size=(32, 32)
                )
            elif getattr(node, "status", "") == "INFECTED":
                sprite_img = self.sprite_manager.get_sprite(
                    "CRAWLER", size=(32, 32)
                )
            elif getattr(node, "node_type", "") == "Router":
                sprite_img = self.sprite_manager.get_sprite(
                    "ROUTER", size=(32, 32)
                )
            else:
                sprite_img = self.sprite_manager.get_sprite(
                    "LAPTOP", size=(28, 28)
                )

            if sprite_img:
                self.create_image(
                    node.x, node.y, image=sprite_img, anchor="center"
                )

            label = "PATIENT ZERO" if node.is_patient_zero else node.id
            font_color = "#B71C1C" if node.is_patient_zero else "#222222"
            self.create_text(
                node.x,
                node.y + 22,
                text=label,
                fill=font_color,
                font=("Courier", 8, "bold"),
            )