import customtkinter as ctk
from typing import Optional
from core.topology import NetworkGraph

STATUS_COLORS = {
    "INFECTED": "#FF5252",
    "WARNING": "#448AFF",
    "HEALTHY": "#69F0AE"
}


class NetworkCanvas(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#1e1e1e", highlightthickness=0, **kwargs)

        self.mode = "SELECT"  # Modes: "SELECT", "ADD_NODE", "CONNECT_EDGE", "SET_ORIGIN"
        self.graph: Optional[NetworkGraph] = None
        self.selected_node_idx: Optional[int] = None

        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)

    def set_mode(self, mode: str):
        self.mode = mode
        self.selected_node_idx = None
        self.render()

    def set_graph(self, graph: NetworkGraph):
        self.graph = graph
        self.render()

    def _get_node_at_pos(self, x: float, y: float, radius: float = 12.0) -> Optional[int]:
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

        clicked_idx = self._get_node_at_pos(event.x, event.y)

        if self.mode == "ADD_NODE":
            if clicked_idx is None:
                self.graph.add_node(event.x, event.y)
                self.render()

        elif self.mode == "CONNECT_EDGE":
            if clicked_idx is not None:
                if self.selected_node_idx is None:
                    self.selected_node_idx = clicked_idx
                else:
                    self.graph.add_edge(self.selected_node_idx, clicked_idx)
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
        if self.mode == "SELECT" and self.selected_node_idx is not None and self.graph:
            node = self.graph.nodes[self.selected_node_idx]
            node.x = event.x
            node.y = event.y
            self.render()

    def render(self):
        self.delete("all")
        if not self.graph:
            return

        # 1. Draw Edges
        for u, v in self.graph.edges:
            if u < len(self.graph.nodes) and v < len(self.graph.nodes):
                n1, n2 = self.graph.nodes[u], self.graph.nodes[v]
                self.create_line(n1.x, n1.y, n2.x, n2.y, fill="#444444", width=2)

        # 2. Draw Nodes
        dot_radius = 8
        for i, node in enumerate(self.graph.nodes):
            color = STATUS_COLORS.get(node.status, "#69F0AE")

            # Draw glowing ring around Patient Zero
            if node.is_patient_zero:
                self.create_oval(
                    node.x - 14, node.y - 14,
                    node.x + 14, node.y + 14,
                    outline="#FFFFFF", width=3
                )

            # Draw Node Body
            self.create_oval(
                node.x - dot_radius, node.y - dot_radius,
                node.x + dot_radius, node.y + dot_radius,
                fill=color, outline=""
            )

            # Node Label
            label = f"{node.id} (P0)" if node.is_patient_zero else node.id
            self.create_text(node.x, node.y - 16, text=label, fill="#CCCCCC", font=("Arial", 8, "bold"))