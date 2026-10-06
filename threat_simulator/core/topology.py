import math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict

@dataclass
class Node:
    id: str
    status: str = "HEALTHY"

@dataclass
class NetworkGraph:
    nodes: List[Node] = field(default_factory=list)
    edges: List[Tuple[int, int]] = field(default_factory=list)

    @property
    def node_count(self) -> int:
        return len(self.nodes)


class TopologyGenerator:
    """Strategy class for building network topologies and computing canvas coordinates."""

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
    def calculate_positions(num_nodes: int, width: float, height: float) -> List[Tuple[float, float]]:
        if num_nodes == 0:
            return []
        center_x, center_y = width / 2, height / 2
        radius = min(width, height) * 0.35
        coords = []
        for i in range(num_nodes):
            angle = (2 * math.pi / num_nodes) * i
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            coords.append((x, y))
        return coords
