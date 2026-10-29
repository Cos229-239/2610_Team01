import math
import random
import string
from dataclasses import dataclass, field
from typing import List, Optional
from .node_types import NODE_TYPES


def calculate_password_search_space(password: str) -> int:
    """Calculates exact total combination pool (N^L) based on length and character set diversity."""
    if not password or not password.strip():
        return 50  # Instant threshold for empty/blank keys

    pwd = password.strip()
    length = len(pwd)

    # Detect character set presence
    has_digit = any(c in string.digits for c in pwd)
    has_lower = any(c in string.ascii_lowercase for c in pwd)
    has_upper = any(c in string.ascii_uppercase for c in pwd)
    has_symbol = any(c in string.punctuation for c in pwd)

    # Build exact character set size (N)
    charset_size = 0
    if has_digit:
        charset_size += 10
    if has_lower:
        charset_size += 26
    if has_upper:
        charset_size += 26
    if has_symbol:
        charset_size += 32

    # If password consists of characters outside predefined sets, fallback to minimum
    charset_size = max(charset_size, 10)  # Pure numeric minimum
    
    # Combination space = N^L
    return charset_size ** length


@dataclass
class Node:
    id: str
    status: str = "HEALTHY"
    node_type: str = "PC"
    x: float = 0.0
    y: float = 0.0
    is_patient_zero: bool = False
    infection_step: int = -1
    ip_address: str = ""       # e.g. "192.168.10.5"
    subnet: str = "192.168.1.0/24" # the network this node belongs to


@dataclass
class Edge:
    u: int
    v: int
    status: str = "HEALTHY"
    is_firewall: bool = False
    password: str = ""             # Encryption key
    crack_progress: float = 0.0     # Cracking percentage (0.0 to 1.0)
    crack_attempts: int = 0         # Total brute-force tries attempted
    required_attempts: int = 0      # Total combinations required to breach


@dataclass
class NetworkGraph:
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)

    # Base network for this graph (third octet changes per topology)
    base_network: str = "192.168.1.0/24"
    _next_subnet: int = 1           # next host number to hand out

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    def _generate_unique_subnet_and_ip(self) -> tuple[str, str]:
        """
        Returns (ip_address, subnet) where every node gets a distinct / 24.
        Example sequence:
            192.168.1.10  ->  192.168.1.0/24
            192.168.2.10  ->  192.168.2.0/24
            192.168.3.10  ->  192.168.3.0/24
            ...
        """

        # Allow the base_network to set the starting third octet if desired
        try:
            start_octet = int(self.base_network.split(".") [2])
        except (IndexError, ValueError):
            start_octet = 1

        third = start_octet + self._next_subnet - 1
        self._next_subnet += 1

        # Keep third octet in valid range (1-254)
        if third > 254:
            third = ((third - 1) % 254) + 1

        subnet = f"192.168.{third}.0/24"
        ip     = f"192.168.{third}.10"   # .10 is a safe host address

        return ip, subnet

    def add_node(self, x: float, y: float, node_type: str = "PC", ip_address: Optional[str] = None, subnet: Optional[str] = None,) -> Node:
        """Adds a new node with a specific device type at canvas coordinates."""
        node_id = f"{node_type[:2].upper()}-{len(self.nodes) + 1:02d}"
        is_first = len(self.nodes) == 0

        if ip_address is None or subnet is None:
            # Automatic unique subnet mode
            auto_ip, auto_subnet = self._generate_unique_subnet_and_ip()
            ip_address = ip_address or auto_ip
            subnet = subnet or auto_subnet
        else:
            # Manual mode - still advance the counter so future auto nodes stay unique
            self._netd_subnet += 1

        # ip, subnet = self._generate_unique_subnet_and_ip()

        new_node = Node(
            id=node_id,
            status="HEALTHY",
            node_type=node_type,
            x=x,
            y=y,
            is_patient_zero=is_first,
            ip_address=ip_address,
            subnet=subnet,
        )
        self.nodes.append(new_node)
        return new_node

    def set_node_ip(
        self,
        node_index: int,
        ip_address: str,
        subnet: str,
        ) -> bool:
        """
        Manually set (or change) the IP address and subnet of an existing node.

        Returns True on success, False if the index is invalid.
        """
        if not (0 <= node_index < len(self.nodes)):
            return False

        node = self.nodes[node_index]
        node.ip_address = ip_address.strip()
        node.subnet = subnet.strip()
        return True

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

    def find_edge_near_point(
        self, px: float, py: float, tolerance: float = 10.0
    ) -> Optional[int]:
        """Calculates distance from point (px, py) to all edges and returns
        the index of the edge closest to the point within a tolerance radius.
        """
        for index, edge in enumerate(self.edges):
            if edge.u < len(self.nodes) and edge.v < len(self.nodes):
                n1, n2 = self.nodes[edge.u], self.nodes[edge.v]

                dx = n2.x - n1.x
                dy = n2.y - n1.y
                if dx == 0 and dy == 0:
                    continue

                t = max(
                    0.0,
                    min(
                        1.0,
                        ((px - n1.x) * dx + (py - n1.y) * dy) / (dx * dx + dy * dy),
                    ),
                )

                proj_x = n1.x + t * dx
                proj_y = n1.y + t * dy

                dist = math.hypot(px - proj_x, py - proj_y)
                if dist <= tolerance:
                    return index
        return None

    def toggle_firewall_at_index(self, index: int, custom_pwd: str = "") -> bool:
        """Toggles an active firewall barrier, sets a custom or random password key,
        and computes the total search space complexity.
        """
        if 0 <= index < len(self.edges):
            edge = self.edges[index]
            edge.is_firewall = not edge.is_firewall
            edge.crack_progress = 0.0
            edge.crack_attempts = 0

            if edge.is_firewall:
                if custom_pwd and custom_pwd.strip():
                    edge.password = custom_pwd.strip()[:6]
                else:
                    edge.password = "".join(random.choices("0123456789", k=3))  # Default short numeric key

                edge.required_attempts = calculate_password_search_space(edge.password)
            else:
                edge.password = ""
                edge.required_attempts = 0
            return True
        return False

    def reset_states(self):
        """Resets all node and edge statuses, restores Patient Zero, and disarms firewalls."""
        p0_idx = self.get_patient_zero_index() if self.nodes else 0

        for i, node in enumerate(self.nodes):
            node.status = "HEALTHY"
            node.is_patient_zero = (i == p0_idx)

        for edge in self.edges:
            edge.status = "HEALTHY"
            edge.is_firewall = False
            edge.password = ""
            edge.crack_progress = 0.0
            edge.crack_attempts = 0
            edge.required_attempts = 0

    def clear(self):
        """Clears all nodes and edges from the graph instance."""
        self.nodes.clear()
        self.edges.clear()
        self._next_subnet = 1


class TopologyGenerator:
    """Strategy class for generating preset network topologies."""

    @staticmethod
    def generate_ring(num_nodes: int = 20) -> NetworkGraph:
        graph = NetworkGraph(base_network="192.168.10.0/24")
        types = ["Router", "Modem", "PC", "PC"]

        for i in range(num_nodes):
            node = graph.add_node(0, 0, node_type=types[i % len(types)])
            node.id = f"PC-{i+1:02d}"

        if graph.nodes:
            graph.nodes[0].is_patient_zero = True

        for i in range(num_nodes):
            graph.add_edge(i, (i + 1) % num_nodes)
            if i % 3 == 0:
                graph.add_edge(i, (i + 5) % num_nodes)

        return graph

    @staticmethod
    def generate_mesh(num_nodes: int = 24) -> NetworkGraph:
        graph = NetworkGraph(base_network="192.168.20.0/24")
        types = ["Router", "PC", "Modem", "PC"]
        
        for i in range(num_nodes):
            node = graph.add_node(0, 0, node_type=types[i % len(types)])
            node.id = f"MS-{i+1:02d}"

        if graph.nodes:
            graph.nodes[0].is_patient_zero = True

        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                graph.add_edge(i, j)

        return graph

    @staticmethod
    def generate_star(num_nodes: int = 18) -> NetworkGraph:
        graph = NetworkGraph(base_network="192.168.30.0/24")

        for i in range(num_nodes):
            ntype = "Router" if i == 0 else ("PC" if i % 2 == 0 else "Modem")
            node = graph.add_node(0, 0, node_type=ntype)
            node.id = f"ST-{i+1:02d}"

        if graph.nodes:
            graph.nodes[0].is_patient_zero = True

        for i in range(1, num_nodes):
            graph.add_edge(0, i)

        return graph

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