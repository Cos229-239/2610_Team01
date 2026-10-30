import os
import sys
import json
import tkinter as tk
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
from core.topology import NetworkGraph, calculate_password_search_space

# Standard Palette (Red / Amber / Green)
STATUS_COLORS_STD = {
    "INFECTED": "#FF5252",
    "WARNING": "#FFB74D",
    "HEALTHY": "#69F0AE",
}

EDGE_COLORS_STD = {
    "INFECTED": "#FF5252",
    "WARNING": "#FFB74D",
    "HEALTHY": "#8b5a2b",
}

# Colorblind-Friendly Palette (High Contrast Orange-Red / Amber / Blue)
STATUS_COLORS_CB = {
    "INFECTED": "#D55E00",  # Okabe-Ito Vermillion
    "WARNING": "#E69F00",   # Okabe-Ito Amber
    "HEALTHY": "#0072B2",   # Okabe-Ito Blue
}

EDGE_COLORS_CB = {
    "INFECTED": "#D55E00",
    "WARNING": "#E69F00",
    "HEALTHY": "#0072B2",
}


class AssetManager:
    def __init__(self, assets_dir="assets"):
        self.assets_dir = assets_dir
        self._cache = {}

        self.image_files = {
            "BIOHAZARD": "noun_ComputerVirus_8334320_@700.png",
            "CRAWLER": "noun_trojanvirus_8281247_@700.png",
            "ROUTER": "noun_Router_7285821_@700.png",
            "LAPTOP": "noun_Laptop_8479843_@700.png",
            "PC": "noun_Computer_6856966_@700.png",
            "SERVER": "noun_Server_1211215_@700.png",
            "PHONE": "noun_mobilephone_8150848_@700.png",
        }

    def get_sprite(self, name, size=(32, 32)):
        cache_key = (name, size)
        if cache_key in self._cache:
            return self._cache[cache_key]

        filename = self.image_files.get(name)
        if not filename:
            return None

        path = os.path.join(self.assets_dir, filename)
        if not os.path.exists(path):
            path = os.path.join("..", self.assets_dir, filename)

        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            photo_img = ImageTk.PhotoImage(img)
            self._cache[cache_key] = photo_img
            return photo_img

        return None


class NetworkCanvas(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#d8ccb0", highlightthickness=0, **kwargs)

        self.mode = "SELECT"
        self.active_node_type = "PC"
        self.graph: Optional[NetworkGraph] = None
        self.selected_node_idx: Optional[int] = None
        self.flashing_node_idx: Optional[int] = None
        self.flash_state: bool = False
        self.flash_timer_id = None

        self.node_select_callback = None
        self.colorblind_mode: bool = False

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
        self.bind("<Double-Button-1>", self._on_double_click)

        # Pan Binds (Right-Click Drag)
        self.bind("<Button-3>", self._start_pan)
        self.bind("<B3-Motion>", self._on_pan_drag)

        # Zoom Binds
        self.bind("<MouseWheel>", self._on_zoom)
        self.bind("<Button-4>", self._on_zoom)
        self.bind("<Button-5>", self._on_zoom)

        self.sprite_manager = AssetManager()

    def set_colorblind_mode(self, enabled: bool):
        """Toggles colorblind-friendly rendering palette on canvas."""
        self.colorblind_mode = bool(enabled)
        self.render()

    def set_node_select_callback(self, callback):
        """Registers a callback function invoked when a node is selected in SELECT mode."""
        self.node_select_callback = callback

    def flash_target_node(self, node_idx: int, pulses: int = 6):
        """Flashes a target ring animation around the specified node upon attack/exploit."""
        if not self.graph or node_idx < 0 or node_idx >= len(self.graph.nodes):
            return

        if self.flash_timer_id is not None:
            self.after_cancel(self.flash_timer_id)
            self.flash_timer_id = None

        self.flashing_node_idx = node_idx
        self.flash_state = True
        
        def _pulse_step(count):
            if count <= 0 or self.flashing_node_idx is None:
                self.flashing_node_idx = None
                self.flash_state = False
                self.render()
                return

            self.flash_state = not self.flash_state
            self.render()
            self.flash_timer_id = self.after(120, lambda: _pulse_step(count - 1))

        _pulse_step(pulses)

    # ------------------------------------------------------------------
    # Viewport Coordinate Mapping
    # ------------------------------------------------------------------

    def world_to_screen(self, wx: float, wy: float) -> Tuple[float, float]:
        sx = (wx * self.zoom_factor) + self.pan_offset_x
        sy = (wy * self.zoom_factor) + self.pan_offset_y
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        wx = (sx - self.pan_offset_x) / self.zoom_factor
        wy = (sy - self.pan_offset_y) / self.zoom_factor
        return wx, wy

    # ------------------------------------------------------------------
    # Zoom & Pan Event Handlers
    # ------------------------------------------------------------------

    def _on_zoom(self, event):
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
        """Right-click: show context menu if on a node, otherwise start panning."""
        if not self.graph:
            return

        world_x, world_y = self.screen_to_world(event.x, event.y)
        clicked_idx = self._get_node_at_pos(world_x, world_y)

        if clicked_idx is not None:
            # Right-clicked a node -> show context menu
            self._show_node_context_menu(event, clicked_idx)
        else:
            # Right-clicked empty space -> start panning
            self._pan_start_x = event.x - self.pan_offset_x
            self._pan_start_y = event.y - self.pan_offset_y

    def _on_pan_drag(self, event):
        self.pan_offset_x = event.x - self._pan_start_x
        self.pan_offset_y = event.y - self._pan_start_y
        self.render()

    def _on_double_click(self, event):
        """Double-click a node to edit its IP address and subnet."""
        if not self.graph:
            return

        world_x, world_y = self.screen_to_world(event.x, event.y)
        clicked_idx = self._get_node_at_pos(world_x, world_y)

        if clicked_idx is not None:
            self.selected_node_idx = clicked_idx
            self._edit_node_ip_dialog(clicked_idx)

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
        self.selected_node_idx = None
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
                    edge.password = user_pwd.strip()[:6]
                edge.crack_progress = 0.0
                edge.crack_attempts = 0
                edge.required_attempts = calculate_password_search_space(edge.password)
            else:
                self.graph.toggle_firewall_at_index(edge_idx, custom_pwd=user_pwd)
            self.render()

    def _show_node_context_menu(self, event, node_idx: int):
        """Shows a right-click context for the selected node."""
        if not self.graph or not (0 <= node_idx < len(self.graph.nodes)):
            return

        node = self.graph.nodes[node_idx]
        self.selected_node_idx = node_idx
        self.render()

        menu = tk.Menu(self, tearoff=0)

        menu.add_command(
            label=f"EditIP / Subnet... ({node.id})",
            command=lambda: self._edit_node_ip_dialog(node_idx)
        )
        menu.add_separator()

        menu.add_command(
            label="Set as Patient Zero",
            command=lambda: self._context_set_patient_zero(node_idx)
        )
        menu.add_command(
            label="Force Infect",
            command=lambda: self._context_force_status(node_idx, "INFECTED")
        )
        menu.add_command(
            label="Force Clean (Healthy)",
            command=lambda: self._context_force_status(node_idx, "HEALTHY")
        )
        menu.add_separator()

        menu.add_command(
            label="Delete Node",
            command=lambda: self._context_delete_node(node_idx)
        )

        # Show menu at mouse position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _context_set_patient_zero(self, node_idx: int):
        if self.graph:
            self.graph.set_patient_zero(node_idx)
            self.render()

    def _context_force_status(self, node_idx: int, status: str):
        if self.graph and 0 <= node_idx < len(self.graph.nodes):
            node = self.graph.nodes[node_idx]
            node.status = status
            if status == "HEALTHY":
                node.is_patient_zero = False
            self.render()

    def _context_delete_node(self, node_idx: int):
        if not self.graph or not (0 <= node_idx < len(self.graph.nodes)):
            return

        # Remove all edges connected to this node
        self.graph.edges = [
            e for e in self.graph.edges
            if e.u != node_idx and e.v != node_idx
        ]

        # Re-index the remaining edges
        for e in self.graph.edges:
            if e.u > node_idx:
                e.u -= 1
            if e.v > node_idx:
                e.v -= 1

        # Remove the node
        del self.graph.nodes[node_idx]

        self.selected_node_idx = None
        self.render()
            
    def _edit_node_ip_dialog(self, node_idx: int):
        """Opens a dialog to manually edit the IP address and subnet of a node."""
        if not self.graph or not (0 <= node_idx < len(self.graph.nodes)):
            return

        node = self.graph.nodes[node_idx]

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit IP - {node.id}")
        dialog.geometry("340x220")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        # Center the dialog roughly
        dialog.update_idletasks()
        x = self.winfo_rootx() + 80
        y = self.winfo_rooty() + 80
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialog, text=f"Node: {node.id}", font=("Arial", 13, "bold")).pack(pady=(15, 8))

        # IP Address
        ctk.CTkLabel(dialog, text="IP Address:").pack(anchor="w", padx=25)
        ip_entry = ctk.CTkEntry(dialog, width=260, placeholder_text="e.g. 192.168.10.5")
        ip_entry.pack(padx=25, pady=(0, 10))
        ip_entry.insert(0, node.ip_address or "")

        # Subnet
        ctk.CTkLabel(dialog, text="Subnet:").pack(anchor="w", padx=25)
        subnet_entry = ctk.CTkEntry(dialog, width=260, placeholder_text="e.g. 192.168.10.0/24")
        subnet_entry.pack(padx=25, pady=(0, 15))
        subnet_entry.insert(0, node.subnet or "")

        def save():
            new_ip = ip_entry.get().strip()
            new_subnet = subnet_entry.get().strip()

            if not new_ip or not new_subnet:
                return  # simple validation – both required

            # Use the helper we added earlier
            self.graph.set_node_ip(node_idx, new_ip, new_subnet)
            self.render()
            dialog.destroy()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=5)

        ctk.CTkButton(btn_frame, text="Save", width=100, command=save).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color="gray", command=dialog.destroy).pack(side="left", padx=8)

        # Focus the IP field
        ip_entry.focus_set()

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

        # Record active selection index for Clippy or tools
        if clicked_idx is not None:
            self.selected_node_idx = clicked_idx

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
            self.render()

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
        edge_palette = EDGE_COLORS_CB if self.colorblind_mode else EDGE_COLORS_STD

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
                    attempts = getattr(edge, "crack_attempts", 0)
                    req_attempts = getattr(edge, "required_attempts", 10000)

                    remaining = max(0, req_attempts - attempts)
                    eta_ticks = int(remaining / 250) if remaining > 0 else 0
                    eta_text = f"ETA {eta_ticks}s" if eta_ticks > 0 else "BREACH"

                    badge_w = int(40 * min(1.5, max(0.7, zf)))
                    badge_h = int(18 * min(1.5, max(0.7, zf)))

                    self.create_rectangle(
                        mid_sx - badge_w,
                        mid_sy - badge_h,
                        mid_sx + (badge_w // 3),
                        mid_sy + badge_h,
                        fill="#002b36",
                        outline=beam_color,
                        width=2,
                    )

                    label_text = f"🔑{pwd}\n{int(progress * 100)}%\n[{attempts:,} Tries]\n{eta_text}"
                    self.create_text(
                        mid_sx - (badge_w // 3),
                        mid_sy,
                        text=label_text,
                        fill="#00E5FF",
                        font=("Consolas", max(5, int(6 * zf)), "bold"),
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
                    edge_color = edge_palette.get(edge.status, "#444444")
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

            # High contrast attack flash animation overlay
            if i == self.flashing_node_idx and self.flash_state:
                self.create_oval(
                    sx - radius - int(12 * zf),
                    sy - radius - int(12 * zf),
                    sx + radius + int(12 * zf),
                    sy + radius + int(12 * zf),
                    outline="#FF1744",
                    width=max(2, int(4 * zf)),
                )

            if node.is_patient_zero:
                p0_color = "#D55E00" if self.colorblind_mode else "#ff3b3b"
                self.create_oval(
                    sx - int(32 * zf),
                    sy - int(32 * zf),
                    sx + int(32 * zf),
                    sy + int(32 * zf),
                    fill=p0_color,
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
            elif i == self.selected_node_idx:
                self.create_oval(
                    sx - radius - int(4 * zf),
                    sy - radius - int(4 * zf),
                    sx + radius + int(4 * zf),
                    sy + radius + int(4 * zf),
                    outline="#3B82F6",
                    width=max(1, int(3 * zf)),
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
                sy + int(20 * zf),
                text=label,
                fill=font_color,
                font=("Courier", font_sz, "bold"),
            )

            # IP address under the node name
            if getattr(node, "ip_address", ""):
                ip_font_sz = max(5, int(7 * zf))
                self.create_text(
                    sx,
                    sy + int(32 * zf),
                    text=node.ip_address,
                    fill="#444444",
                    font=("Consolas", ip_font_sz),
                )


class CanvasView(ctk.CTkFrame):
    def __init__(self, parent, simulation):
        super().__init__(parent)
        self.simulation = simulation

        self.canvas = NetworkCanvas(self)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        self.export_button = ctk.CTkButton(
            self, 
            text="Export Simulation Report", 
            command=self.trigger_export
        )
        self.export_button.pack(pady=10)

    @property
    def selected_node_idx(self) -> Optional[int]:
        """Provides direct access to selected node index on inner canvas."""
        return self.canvas.selected_node_idx

    def flash_target_node(self, node_idx: int):
        """Delegates node flash animation trigger to inner canvas."""
        self.canvas.flash_target_node(node_idx)

    def trigger_export(self):
        try:
            graph = getattr(self.simulation, "graph", None) or getattr(self.canvas, "graph", None)
            if not graph:
                print("Export failed: Active simulation graph not found.")
                return
            
            filepath = export_simulation_summary(graph)
            
            with open(filepath, "r") as f:
                report_data = json.load(f)
            
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

    def set_colorblind_mode(self, enabled: bool):
        """Delegates colorblind mode setting to inner canvas."""
        self.canvas.set_colorblind_mode(enabled)