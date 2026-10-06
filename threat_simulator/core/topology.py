import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class Node:
    id: str
    status: str = "HEALTHY"
    x: float = 0.0
    y: float = 0.0


@dataclass
class NetworkGraph:
    nodes: List[Node] = field(default_factory=list)
    edges: List[Tuple[int, int]] = field(default_factory=list)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    def add_node(self, x: float, y: float) -> Node:
        """Adds a new node at specific canvas coordinates."""
        node_id = f"NODE-{len(self.nodes) + 1:02d}"
        new_node = Node(id=node_id, x=x, y=y)
        self.nodes.append(new_node)
        return new_node

    def add_edge(self, u_index: int, v_index: int):
        """Adds an undirected edge between two node indices if valid."""
        if (u_index, v_index) not in self.edges and (v_index, u_index) not in self.edges:
            if u_index != v_index and 0 <= u_index < len(self.nodes) and 0 <= v_index < len(self.nodes):
                self.edges.append((u_index, v_index))

    def clear(self):
        """Clears all nodes and edges from the graph instance."""
        self.nodes.clear()
        self.edges.clear()


class TopologyGenerator:
    """Strategy class for building network topologies and computing layouts."""

    @staticmethod
    def generate_ring(num_nodes: int = 20) -> NetworkGraph:
        nodes = [Node(id=f"NODE-{i+1:02d}") for i in range(num_nodes)]
        edges = []
        for i in range(num_nodes):
            edges.append((i, (i + 1) % num_nodes))
            if i % 3 == 0:
                edges.append((i, (i + 5) % num_nodes))
        return NetworkGraph(nodes=nodes, edges=edges)

    @staticmethod
    def generate_mesh(num_nodes: int = 24) -> NetworkGraph:
        nodes = [Node(id=f"NODE-{i+1:02d}") for i in range(num_nodes)]
        edges = []
        for i in range(num_nodes):
            edges.append((i, (i + 1) % num_nodes))
            edges.append((i, (i + 2) % num_nodes))
            if i % 2 == 0:
                edges.append((i, (i + 6) % num_nodes))
        return NetworkGraph(nodes=nodes, edges=edges)

    @staticmethod
    def generate_star(num_nodes: int = 18) -> NetworkGraph:
        nodes = [Node(id=f"NODE-{i+1:02d}") for i in range(num_nodes)]
        edges = []
        for i in range(1, num_nodes):
            edges.append((0, i))
            if i % 2 == 0:
                edges.append((i, (i % (num_nodes - 1)) + 1))
        return NetworkGraph(nodes=nodes, edges=edges)

    @staticmethod
    def apply_ring_layout(graph: NetworkGraph, width: float, height: float):
        """Calculates circular canvas positions for all nodes in the graph."""
        num_nodes = len(graph.nodes)
        if num_nodes == 0:
            return

        center_x, center_y = width / 2, height / 2
        radius = min(width, height) * 0.35

        for i, node in enumerate(graph.nodes):
            angle = (2 * math.pi / num_nodes) * i
            node.x = center_x + radius * math.cos(angle)
            node.y = center_y + radius * math.sin(angle)