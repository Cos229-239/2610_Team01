import customtkinter as ctk
from typing import Optional
from core.topology import NetworkGraph
from PIL import Image, ImageTk
import os
from core.node_types import NODE_TYPES

STATUS_COLORS = {
    "INFECTED": "#FF5252",
    "WARNING": "#FFB74D",
    "HEALTHY": "#69F0AE"
}

EDGE_COLORS = {
    "INFECTED": "#FF5252",
    "WARNING": "#FFB74D",
    "HEALTHY": "#8b5a2b"
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
            "LAPTOP": (368, 130, 400, 162)
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
        self.active_node_type = "PC"  # Selected type when adding nodes
        self.graph: Optional[NetworkGraph] = None
        self.selected_node_idx: Optional[int] = None

        self.mouse_x: float = 0.0
        self.mouse_y: float = 0.0

        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Motion>", self._on_mouse_move)
        
        self.sprite_manager = SpriteSheetManager()
        
    def set_mode(self, mode: str):
        self.mode = mode
        self.selected_node_idx = None
        self.render()

    def set_active_node_type(self, node_type: str):
        self.active_node_type = node_type

    def set_graph(self, graph: NetworkGraph):
        self.graph = graph
        self.render()

    def _get_node_at_pos(self, x: float, y: float, radius: float = 16.0) -> Optional[int]:
    def _get_node_at_pos(self, x: float, y: float, radius: float = 14.0) -> Optional[int]:
        if not self.graph:
            return None
        for i, node in enumerate(self.graph.nodes):
            dist = ((node.x - x) ** 2 + (node.y - y) ** 2) ** 0.5
            if dist <= radius:
                return i
        return None

    def _on_click(self, event):
        if not self.graph:
            return

        self.mouse_x = float(event.x)
        self.mouse_y = float(event.y)
        clicked_idx = self._get_node_at_pos(event.x, event.y)

        if self.mode == "ADD_NODE":
            if clicked_idx is None:
                # Add node with active node type
                self.graph.add_node(event.x, event.y, node_type=self.active_node_type)
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
        if self.mode == "SELECT" and self.selected_node_idx is not None and self.graph:
            node = self.graph.nodes[self.selected_node_idx]
            node.x = event.x
            node.y = event.y
            self.render()

    def _on_mouse_move(self, event):
        self.mouse_x = float(event.x)
        self.mouse_y = float(event.y)
        if self.mode == "CONNECT_EDGE" and self.selected_node_idx is not None:
            self.render()

    def render(self):
        self.delete("all")
        if not self.graph:
            return

        for edge in self.graph.edges:
            if edge.u < len(self.graph.nodes) and edge.v < len(self.graph.nodes):
                n1, n2 = self.graph.nodes[edge.u], self.graph.nodes[edge.v]
                edge_color = EDGE_COLORS.get(edge.status, "#555555")
                edge_width = EDGE_WIDTHS.get(edge.status, 1)

                self.create_line(
                    n1.x, n1.y, n2.x, n2.y,
                    fill=EDGE_COLORS.get(edge.status, "#444444"),
                    width=2 if edge.status != "HEALTHY" else 1
                )

        if self.mode == "CONNECT_EDGE" and self.selected_node_idx is not None:
            if self.selected_node_idx < len(self.graph.nodes):
                source_node = self.graph.nodes[self.selected_node_idx]
                self.create_line(
                    source_node.x, source_node.y,
                    self.mouse_x, self.mouse_y,
                    fill="#C62828", width=2, dash=(4, 4)
                )

        for i, node in enumerate(self.graph.nodes):
            if node.is_patient_zero:
                self.create_oval(
                    node.x - 32, node.y - 32,
                    node.x + 32, node.y + 32,
                    fill="#ff3b3b", outline="", stipple="gray50"
                )
                self.create_oval(
                    node.x - 20, node.y - 20,
                    node.x + 20, node.y + 20,
                    fill="#ff7b00", outline="#D32F2F", width=2
                )

            if self.mode == "CONNECT_EDGE" and i == self.selected_node_idx:
                self.create_oval(node.x - 22, node.y - 22, node.x + 22, node.y + 22, outline="#FFD54F", width=3)
            elif self.mode == "SELECT" and i == self.selected_node_idx:
                self.create_oval(node.x - 20, node.y - 20, node.x + 20, node.y + 20, outline="#333333", width=2)

            if node.is_patient_zero:
                sprite_img = self.sprite_manager.get_sprite("BIOHAZARD", size=(32, 32))
            elif getattr(node, "status", "") == "INFECTED":
                sprite_img = self.sprite_manager.get_sprite("CRAWLER", size=(32, 32))
            elif getattr(node, "is_router", False):
                sprite_img = self.sprite_manager.get_sprite("ROUTER", size=(32, 32))
            else:
                sprite_img = self.sprite_manager.get_sprite("SKULL", size=(28, 28))

            if sprite_img:
                self.create_image(node.x, node.y, image=sprite_img, anchor="center")

            label = "PATIENT ZERO" if node.is_patient_zero else node.id
            font_color = "#B71C1C" if node.is_patient_zero else "#222222"
            self.create_text(node.x, node.y + 22, text=label, fill=font_color, font=("Courier", 8, "bold"))
                src = self.graph.nodes[self.selected_node_idx]
                self.create_line(src.x, src.y, self.mouse_x, self.mouse_y, fill="#FFD54F", width=2, dash=(4, 4))

        for i, node in enumerate(self.graph.nodes):
            type_cfg = NODE_TYPES.get(node.node_type, NODE_TYPES["PC"])
            radius = type_cfg.radius

            if node.status in ("INFECTED", "WARNING"):
                fill_color = STATUS_COLORS[node.status]
            else:
                fill_color = type_cfg.color

            if node.is_patient_zero:
                self.create_oval(node.x - radius - 5, node.y - radius - 5, node.x + radius + 5, node.y + radius + 5, outline="#FF5252", width=2)
            elif self.mode == "CONNECT_EDGE" and i == self.selected_node_idx:
                self.create_oval(node.x - radius - 6, node.y - radius - 6, node.x + radius + 6, node.y + radius + 6, outline="#FFD54F", width=3)

            self.create_oval(node.x - radius, node.y - radius, node.x + radius, node.y + radius, fill=fill_color, outline="")

            label_text = f"{type_cfg.symbol} {node.id}"
            if node.is_patient_zero:
                label_text += " (P0)"
            self.create_text(node.x, node.y - radius - 10, text=label_text, fill="#FFFFFF", font=("Arial", 9, "bold"))
