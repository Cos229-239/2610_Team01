import os
import sys
import json
from typing import Dict, Optional, Tuple

# Add project root directory to sys.path to resolve 'utils'
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from utils.exporter import export_simulation_summary

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
        self.node_select_callback = None

        # Viewport Transformations (Zoom & Pan)
        self.zoom_factor: float = 1.0
        self.pan_offset_x: float = 0.0
        self.pan_offset_y: float = 0.0
        self._pan_start_x: float = 0.0
        self._pan_start_y: float = 0.0

        self.mouse_x: float = 0.0
        self.mouse_y: float = 0.0

        self.firewall_btn_bounds: Dict[int, Tuple[float, float, float, float]] = {}

        # Primary Interaction Binds
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Motion>", self._on_mouse_move)

        # Pan Binds (Right-Click Drag)
        self.bind("<Button-3>", self._start_pan)
        self.bind("<B3-Motion>", self._on_pan_drag)

        # Zoom Binds (Mouse Wheel Across Platforms)
        self.bind("<MouseWheel>", self._on_zoom)  # Windows / macOS
        self.bind("<Button-4>", self._on_zoom)     # Linux scroll up
        self.bind("<Button-5>", self._on_zoom)     # Linux scroll down

        self.sprite_manager = SpriteSheetManager()

    def set_node_select_callback(self, callback):
        """Registers a callback function invoked when a node is selected in SELECT mode."""
        self.node_select_callback = callback

    # ------------------------------------------------------------------
    # Viewport Coordinate Mapping
    # ------------------------------------------------------------------

    def world_to_screen(self, wx: float, wy: float) -> Tuple[float, float]:
        """Converts graph world coordinates to canvas screen coordinates."""
        sx = (wx * self.zoom_factor) + self.pan_offset_x
        sy = (wy * self.zoom_factor) + self.pan_offset_y
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        """Converts canvas screen coordinates to graph world coordinates."""
        wx = (sx - self.pan_offset_x) / self.zoom_factor
        wy = (sy - self.pan_offset_y) / self.zoom_factor
        return wx, wy

    # ------------------------------------------------------------------
    # Zoom & Pan Event Handlers
    # ------------------------------------------------------------------

    def _on_zoom(self, event):
        """Zoom in / out centered around the cursor position."""
        if event.num == 4 or event.delta > 0:
            zoom_scale = 1.15
        elif event.num == 5 or event.delta < 0:
            zoom_scale = 0.85
        else:
            return

        new_zoom = max(0.4, min(4.0, self.zoom_factor * zoom_scale))
        if new_zoom == self.zoom_factor:
            return

        cursor_x, cursor_y = event.x, event.y
        world_x, world_y = self.screen_to_world(cursor_x, cursor_y)

        self.zoom_factor = new_zoom
        self.pan_offset_x = cursor_x - (world_x * self.zoom_factor)
        self.pan_offset_y = cursor_y - (world_y * self.zoom_factor)

        self.render()

    def _start_pan(self, event):
        """Records initial right-click anchor for panning."""
        self._pan_start_x = event.x - self.pan_offset_x
        self._pan_start_y = event.y - self.pan_offset_y

    def _on_pan_drag(self, event):
        """Updates offset when dragging with right-click."""
        self.pan_offset_x = event.x - self._pan_start_x
        self.pan_offset_y = event.y - self._pan_start_y
        self.render()

    # ------------------------------------------------------------------
    # Canvas Mode Setup
    # ------------------------------------------------------------------

    def set_mode(self, mode: str):
        self.mode = mode
        self.selected_node_idx = None
        self.config(cursor="")
        self.render()

    def set_active_node_type(self, node_type: str):
        self.active_node_type = node_type

    def set_graph(self, graph: NetworkGraph):
        self.graph = graph
        self.zoom_factor = 1.0
        self.pan_offset_x = 0.0
        self.pan_offset_y = 0.0
        self.render()

    def _get_node_at_pos(
        self, wx: float, wy: float, radius: float = 16.0
    ) -> Optional[int]:
        if not self.graph:
            return None
        for i, node in enumerate(self.graph.nodes):
            dist = ((node.x - wx) ** 2 + (node.y - wy) ** 2) ** 0.5
            if dist <= radius:
                return i
        return None

    def _prompt_firewall_password(self, edge_idx: int, is_update: bool = False):
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

        world_x, world_y = self.screen_to_world(event.x, event.y)
        self.mouse_x = world_x
        self.mouse_y = world_y

        if self.mode == "FIREWALL":
            for edge_idx, (bx1, by1, bx2, by2) in self.firewall_btn_bounds.items():
                if bx1 <= event.x <= bx2 and by1 <= event.y <= by2:
                    self._prompt_firewall_password(edge_idx, is_update=True)
                    return

            edge_idx = self.graph.find_edge_near_point(world_x, world_y)
            if edge_idx is not None:
                edge = self.graph.edges[edge_idx]
                if edge.is_firewall:
                    self.graph.toggle_firewall_at_index(edge_idx)
                    self.render()
                else:
                    self._prompt_firewall_password(edge_idx)
            return

        clicked_idx = self._get_node_at_pos(world_x, world_y)

        if self.mode == "ADD_NODE":
            if clicked_idx is None:
                self.graph.add_node(
                    world_x, world_y, node_type=self.active_node_type
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
                if callable(self.node_select_callback):
                    self.node_select_callback(clicked_idx)

    def _on_drag(self, event):
        world_x, world_y = self.screen_to_world(event.x, event.y)
        self.mouse_x = world_x
        self.mouse_y = world_y

        if (
            self.mode == "SELECT"
            and self.selected_node_idx is not None
            and self.graph
        ):
            node = self.graph.nodes[self.selected_node_idx]
            node.x = world_x
            node.y = world_y
            self.render()

    def _on_mouse_move(self, event):
        world_x, world_y = self.screen_to_world(event.x, event.y)
        self.mouse_x = world_x
        self.mouse_y = world_y

        if self.mode == "FIREWALL" and self.graph:
            is_hovering_btn = any(
                bx1 <= event.x <= bx2 and by1 <= event.y <= by2
                for bx1, by1, bx2, by2 in self.firewall_btn_bounds.values()
            )
            hovered_edge = self.graph.find_edge_near_point(world_x, world_y)

            if is_hovering_btn:
                self.config(cursor="hand2")
            else:
                self.config(cursor="X_cursor" if hovered_edge is not None else "crosshair")
        elif self.mode == "CONNECT_EDGE" and self.selected_node_idx is not None:
            self.render()

    # ------------------------------------------------------------------
    # Render Loop
    # ------------------------------------------------------------------

    def render(self):
        self.delete("all")
        self.firewall_btn_bounds.clear()

        if not self.graph:
            return

        zf = self.zoom_factor

        # 1. Render Edges & Firewall Security Barriers
        for index, edge in enumerate(self.graph.edges):
            if edge.u < len(self.graph.nodes) and edge.v < len(self.graph.nodes):
                n1, n2 = self.graph.nodes[edge.u], self.graph.nodes[edge.v]
                s1_x, s1_y = self.world_to_screen(n1.x, n1.y)
                s2_x, s2_y = self.world_to_screen(n2.x, n2.y)

                if getattr(edge, "is_firewall", False):
                    self.create_line(
                        s1_x, s1_y, s2_x, s2_y, fill="#00E5FF", width=max(2, int(6 * zf))
                    )

                    progress = getattr(edge, "crack_progress", 0.0)
                    beam_color = (
                        "#FF1744"
                        if progress > 0.7
                        else ("#FF9100" if progress > 0.3 else "#FFFFFF")
                    )

                    self.create_line(
                        s1_x, s1_y, s2_x, s2_y, fill=beam_color, width=max(1, int(2 * zf))
                    )

                    mid_sx, mid_sy = (s1_x + s2_x) / 2, (s1_y + s2_y) / 2
                    pwd = getattr(edge, "password", "LOCK")

                    badge_w = int(30 * min(1.5, max(0.7, zf)))
                    badge_h = int(14 * min(1.5, max(0.7, zf)))

                    self.create_rectangle(
                        mid_sx - badge_w,
                        mid_sy - badge_h,
                        mid_sx + (badge_w // 3),
                        mid_sy + badge_h,
                        fill="#002b36",
                        outline=beam_color,
                        width=2,
                    )

                    label_text = f"🔑{pwd}\n{int(progress * 100)}%"
                    self.create_text(
                        mid_sx - (badge_w // 3),
                        mid_sy,
                        text=label_text,
                        fill="#00E5FF",
                        font=("Consolas", max(6, int(7 * zf)), "bold"),
                        justify="center",
                    )

                    btn_x1, btn_y1 = mid_sx + (badge_w // 3) + 2, mid_sy - badge_h
                    btn_x2, btn_y2 = mid_sx + badge_w + 4, mid_sy + badge_h

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
                        font=("Arial", max(7, int(9 * zf))),
                    )
                else:
                    edge_color = EDGE_COLORS.get(edge.status, "#444444")
                    edge_width = max(1, int((2 if edge.status != "HEALTHY" else 1) * zf))
                    self.create_line(
                        s1_x, s1_y, s2_x, s2_y, fill=edge_color, width=edge_width
                    )

        # 2. Render Connection Preview Line
        if self.mode == "CONNECT_EDGE" and self.selected_node_idx is not None:
            if self.selected_node_idx < len(self.graph.nodes):
                src = self.graph.nodes[self.selected_node_idx]
                src_sx, src_sy = self.world_to_screen(src.x, src.y)
                cur_sx, cur_sy = self.world_to_screen(self.mouse_x, self.mouse_y)

                self.create_line(
                    src_sx,
                    src_sy,
                    cur_sx,
                    cur_sy,
                    fill="#FFD54F",
                    width=max(1, int(2 * zf)),
                    dash=(4, 4),
                )

        # 3. Render Nodes and Sprites
        for i, node in enumerate(self.graph.nodes):
            sx, sy = self.world_to_screen(node.x, node.y)
            type_cfg = NODE_TYPES.get(
                getattr(node, "node_type", "PC"), NODE_TYPES.get("PC")
            )
            radius = int((type_cfg.radius if type_cfg else 14) * zf)

            if node.is_patient_zero:
                self.create_oval(
                    sx - int(32 * zf),
                    sy - int(32 * zf),
                    sx + int(32 * zf),
                    sy + int(32 * zf),
                    fill="#ff3b3b",
                    outline="",
                    stipple="gray50",
                )
                self.create_oval(
                    sx - int(20 * zf),
                    sy - int(20 * zf),
                    sx + int(20 * zf),
                    sy + int(20 * zf),
                    fill="#ff7b00",
                    outline="#D32F2F",
                    width=max(1, int(2 * zf)),
                )
            elif self.mode == "CONNECT_EDGE" and i == self.selected_node_idx:
                self.create_oval(
                    sx - radius - int(6 * zf),
                    sy - radius - int(6 * zf),
                    sx + radius + int(6 * zf),
                    sy + radius + int(6 * zf),
                    outline="#FFD54F",
                    width=max(1, int(3 * zf)),
                )
            elif self.mode == "SELECT" and i == self.selected_node_idx:
                self.create_oval(
                    sx - radius - int(4 * zf),
                    sy - radius - int(4 * zf),
                    sx + radius + int(4 * zf),
                    sy + radius + int(4 * zf),
                    outline="#333333",
                    width=max(1, int(2 * zf)),
                )

            sprite_size = max(16, int(32 * zf))

            if node.is_patient_zero:
                sprite_img = self.sprite_manager.get_sprite(
                    "BIOHAZARD", size=(sprite_size, sprite_size)
                )
            elif getattr(node, "status", "") == "INFECTED":
                sprite_img = self.sprite_manager.get_sprite(
                    "CRAWLER", size=(sprite_size, sprite_size)
                )
            elif getattr(node, "node_type", "") == "Router":
                sprite_img = self.sprite_manager.get_sprite(
                    "ROUTER", size=(sprite_size, sprite_size)
                )
            else:
                sprite_size_laptop = max(14, int(28 * zf))
                sprite_img = self.sprite_manager.get_sprite(
                    "LAPTOP", size=(sprite_size_laptop, sprite_size_laptop)
                )

            if sprite_img:
                self.create_image(
                    sx, sy, image=sprite_img, anchor="center"
                )

            label = "PATIENT ZERO" if node.is_patient_zero else node.id
            font_color = "#B71C1C" if node.is_patient_zero else "#222222"
            font_sz = max(6, int(8 * zf))

            self.create_text(
                sx,
                sy + int(22 * zf),
                text=label,
                fill=font_color,
                font=("Courier", font_sz, "bold"),
            )


class CanvasView(ctk.CTkFrame):
    def __init__(self, parent, simulation):
        super().__init__(parent)
        self.simulation = simulation

        # Embed the NetworkCanvas inside this view frame
        self.canvas = NetworkCanvas(self)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # Export button placed at the bottom of the view
        self.export_button = ctk.CTkButton(
            self, 
            text="Export Simulation Report", 
            command=self.trigger_export
        )
        self.export_button.pack(pady=10)

    def trigger_export(self):
        """Calls the exporter and displays a popup modal with the report summary."""
        try:
            graph = getattr(self.simulation, "graph", None) or getattr(self.canvas, "graph", None)
            if not graph:
                print("Export failed: Active simulation graph not found.")
                return
            
            filepath = export_simulation_summary(graph)
            
            # Read back the exported JSON to show in the popup preview
            with open(filepath, "r") as f:
                report_data = json.load(f)
            
            # Create a modal popup window (CTkToplevel)
            popup = ctk.CTkToplevel(self)
            popup.title("Simulation Report Exported")
            popup.geometry("480x380")
            popup.transient(self)
            popup.grab_set()

            ctk.CTkLabel(
                popup, 
                text="Report Saved Successfully!", 
                font=("Arial", 14, "bold"), 
                text_color="#2E7D32"
            ).pack(pady=(15, 5))
            
            ctk.CTkLabel(
                popup, 
                text=f"Saved to: {filepath}", 
                font=("Arial", 10), 
                text_color="gray"
            ).pack(pady=5)

            # Text box showing JSON summary preview
            textbox = ctk.CTkTextbox(popup, width=430, height=220)
            textbox.pack(padx=10, pady=10)
            textbox.insert("1.0", json.dumps(report_data, indent=2))
            textbox.configure(state="disabled")

            ctk.CTkButton(
                popup, 
                text="Close", 
                command=popup.destroy
            ).pack(pady=(5, 15))

        except Exception as e:
            print(f"Export failed: {e}")

            # Delegated methods required by app.py:
    def render(self):
        self.canvas.render()

    def set_graph(self, graph):
        self.canvas.set_graph(graph)

    def set_mode(self, mode):
        self.canvas.set_mode(mode)

    def set_active_node_type(self, node_type):
        self.canvas.set_active_node_type(node_type)

    def set_node_select_callback(self, callback):
        self.canvas.set_node_select_callback(callback)