import math
from dataclasses import dataclass, field
from typing import List, Optional
from core.node_types import NODE_TYPES


@dataclass
class Node:
    id: str
    status: str = "HEALTHY"
    node_type: str = "PC"
    x: float = 0.0
    y: float = 0.0
    is_patient_zero: bool = False


@dataclass
class Edge:
    u: int
    v: int
    status: str = "HEALTHY"


@dataclass
class NetworkGraph:
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    def add_node(self, x: float, y: float, node_type: str = "PC") -> Node:
        """Adds a new node with a specific device type at canvas coordinates."""
        node_id = f"{node_type[:2].upper()}-{len(self.nodes) + 1:02d}"
        is_first = len(self.nodes) == 0
        new_node = Node(
            id=node_id,
            status="HEALTHY",
            node_type=node_type,
            x=x,
            y=y,
            is_patient_zero=is_first,
        )
        self.nodes.append(new_node)
        return new_node

    def add_edge(self, u_index: int, v_index: int):
        """Adds an undirected edge between two node indices if valid."""
        if u_index == v_index or not (
            0 <= u_index < len(self.nodes) and 0 <= v_index < len(self.nodes)
        ):
            return

        for e in self.edges:
            if (e.u == u_index and e.v == v_index) or (
                e.u == v_index and e.v == u_index
            ):
                return

        self.edges.append(Edge(u=u_index, v=v_index))

    def set_patient_zero(self, node_index: int):
        """Sets a single node as Patient Zero and clears other nodes."""
        for i, node in enumerate(self.nodes):
            node.is_patient_zero = i == node_index

    def get_patient_zero_index(self) -> int:
        """Returns index of Patient Zero, default to 0."""
        for i, node in enumerate(self.nodes):
            if node.is_patient_zero:
                return i
        return 0

    def clear(self):
        """Clears all nodes and edges from the graph instance."""
        self.nodes.clear()
        self.edges.clear()


class TopologyGenerator:
    """Strategy class for generating preset network topologies."""

    @staticmethod
    def generate_ring(num_nodes: int = 20) -> NetworkGraph:
        types = ["Router", "Modem", "PC", "PC"]
        nodes = [
            Node(id=f"PC-{i+1:02d}", node_type=types[i % len(types)])
            for i in range(num_nodes)
        ]
        if nodes:
            nodes[0].is_patient_zero = True

        edges = []
        for i in range(num_nodes):
            edges.append(Edge(u=i, v=(i + 1) % num_nodes))
            if i % 3 == 0:
                edges.append(Edge(u=i, v=(i + 5) % num_nodes))

        return NetworkGraph(nodes=nodes, edges=edges)

    @staticmethod
    def generate_mesh(num_nodes: int = 24) -> NetworkGraph:
        types = ["Router", "PC", "Modem", "PC"]
        nodes = [
            Node(id=f"MS-{i+1:02d}", node_type=types[i % len(types)])
            for i in range(num_nodes)
        ]
        if nodes:
            nodes[0].is_patient_zero = True

        edges = []
        for i in range(num_nodes):
            for j in range(i+1, num_nodes):
                edges.append(Edge(u=i, v=j))

        return NetworkGraph(nodes=nodes, edges=edges)

    @staticmethod
    def generate_star(num_nodes: int = 18) -> NetworkGraph:
        nodes = [
            Node(
                id=f"ST-{i+1:02d}",
                node_type="Router" if i == 0 else ("PC" if i % 2 == 0 else "Modem"),
            )
            for i in range(num_nodes)
        ]
        if nodes:
            nodes[0].is_patient_zero = True

        edges = []
        for i in range(1, num_nodes):
            edges.append(Edge(u=0, v=i))
            if i % 2 == 0:
                edges.append(Edge(u=i, v=(i % (num_nodes - 1)) + 1))

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