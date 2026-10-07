import customtkinter as ctk
from typing import Optional
from core.topology import NetworkGraph
from core.node_types import NODE_TYPES

STATUS_COLORS = {
    "INFECTED": "#FF5252",
    "WARNING": "#FFB74D",
    "HEALTHY": "#69F0AE"
}

EDGE_COLORS = {
    "INFECTED": "#FF5252",
    "WARNING": "#FFB74D",
    "HEALTHY": "#444444"
}


class NetworkCanvas(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#1e1e1e", highlightthickness=0, **kwargs)

        self.mode = "SELECT"
        self.active_node_type = "PC"  # Selected type when adding nodes
        self.graph: Optional[NetworkGraph] = None
        self.selected_node_idx: Optional[int] = None

        self.mouse_x: float = 0.0
        self.mouse_y: float = 0.0

        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Motion>", self._on_mouse_move)

    def set_mode(self, mode: str):
        self.mode = mode
        self.selected_node_idx = None
        self.render()

    def set_active_node_type(self, node_type: str):
        self.active_node_type = node_type

    def set_graph(self, graph: NetworkGraph):
        self.graph = graph
        self.render()

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
                self.create_line(
                    n1.x, n1.y, n2.x, n2.y,
                    fill=EDGE_COLORS.get(edge.status, "#444444"),
                    width=2 if edge.status != "HEALTHY" else 1
                )

        if self.mode == "CONNECT_EDGE" and self.selected_node_idx is not None:
            if self.selected_node_idx < len(self.graph.nodes):
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