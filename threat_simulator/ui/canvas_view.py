
import customtkinter as ctk
from core.topology import NetworkGraph, TopologyGenerator

STATUS_COLORS = {
    "INFECTED": "#FF5252",
    "WARNING": "#448AFF",
    "HEALTHY": "#69F0AE"
}

class NetworkCanvas(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#1e1e1e", highlightthickness=0, **kwargs)

    def render(self, graph: NetworkGraph):
        self.delete("all")
        width = self.winfo_width() or 500
        height = self.winfo_height() or 400

        coords = TopologyGenerator.calculate_positions(graph.node_count, width, height)

        # Draw Edges
        for u, v in graph.edges:
            if u < len(coords) and v < len(coords):
                x1, y1 = coords[u]
                x2, y2 = coords[v]
                self.create_line(x1, y1, x2, y2, fill="#444444", width=1)

        # Draw Nodes
        dot_radius = 8
        for i, (x, y) in enumerate(coords):
            status = graph.nodes[i].status if i < len(graph.nodes) else "HEALTHY"
            color = STATUS_COLORS.get(status, "#69F0AE")
            self.create_oval(
                x - dot_radius, y - dot_radius,
                x + dot_radius, y + dot_radius,
                fill=color, outline=""
            )