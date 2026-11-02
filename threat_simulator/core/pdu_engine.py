import uuid
from typing import List, Optional


class PDU:
    def __init__(
        self,
        src_node_idx: int,
        dst_node_idx: int,
        edge_idx: int,
        protocol: str = "ICMP",
        speed: float = 0.05,
    ):
        self.id = str(uuid.uuid4())[:6]
        self.src_node_idx = src_node_idx
        self.dst_node_idx = dst_node_idx
        self.edge_idx = edge_idx
        self.protocol = protocol  # "ICMP", "ARP", "TCP", "INFECT"
        self.progress = 0.0       # Movement progress from 0.0 to 1.0
        self.speed = speed        # Progress increment per simulation tick
        self.delivered = False

    def step(self) -> bool:
        """Advances PDU position by one tick. Returns True when destination is reached."""
        if self.delivered:
            return True
        self.progress += self.speed
        if self.progress >= 1.0:
            self.progress = 1.0
            self.delivered = True
            return True
        return False


class PDUSimulationEngine:
    def __init__(self, graph=None):
        self.graph = graph
        self.active_pdus: List[PDU] = []
        self.is_running: bool = False
        self.tick_delay_ms: int = 40  # Speed control (~25 FPS)
        self.auto_infect: bool = False  # Toggle switch for automated propagation

    def spawn_pdu(
        self,
        src_idx: int,
        dst_idx: int,
        edge_idx: int,
        protocol: str = "ICMP",
        speed: float = 0.05,
    ):
        """Enqueues a new PDU onto an active edge path."""
        pdu = PDU(
            src_node_idx=src_idx,
            dst_node_idx=dst_idx,
            edge_idx=edge_idx,
            protocol=protocol,
            speed=speed,
        )
        self.active_pdus.append(pdu)

    def trigger_patient_zero_outbreak(self):
        """Explicitly enqueues initial attack PDUs from Patient Zero to adjacent nodes."""
        if not self.graph or not self.graph.nodes:
            return

        p0_idx = self.graph.get_patient_zero_index()
        p0_node = self.graph.nodes[p0_idx]
        p0_node.status = "INFECTED"

        # Find all edges attached to Patient Zero and enqueue INFECT PDUs
        for edge_idx, edge in enumerate(self.graph.edges):
            target_idx = None
            if edge.u == p0_idx:
                target_idx = edge.v
            elif edge.v == p0_idx:
                target_idx = edge.u

            if target_idx is not None:
                self.spawn_pdu(
                    src_idx=p0_idx,
                    dst_idx=target_idx,
                    edge_idx=edge_idx,
                    protocol="INFECT",
                    speed=0.03,
                )

    def step_simulation(self) -> bool:
        """Executes a single simulation tick forward."""
        if not self.active_pdus:
            return False

        remaining_pdus = []
        for pdu in self.active_pdus:
            reached = pdu.step()
            if not reached:
                remaining_pdus.append(pdu)
            else:
                self._on_pdu_arrival(pdu)

        self.active_pdus = remaining_pdus
        return len(self.active_pdus) > 0

    def _on_pdu_arrival(self, pdu: PDU):
        """Callback executed when a PDU reaches its target node."""
        if not self.graph or not (0 <= pdu.dst_node_idx < len(self.graph.nodes)):
            return

        dst_node = self.graph.nodes[pdu.dst_node_idx]

        # 1. Malware propagation protocol
        if pdu.protocol == "INFECT":
            dst_node.status = "INFECTED"

            # Propagate further to neighboring healthy nodes only if auto_infect is enabled
            if self.auto_infect:
                for edge_idx, edge in enumerate(self.graph.edges):
                    next_target = None
                    if edge.u == pdu.dst_node_idx:
                        next_target = edge.v
                    elif edge.v == pdu.dst_node_idx:
                        next_target = edge.u

                    if next_target is not None and next_target != pdu.src_node_idx:
                        target_node = self.graph.nodes[next_target]
                        if target_node.status == "HEALTHY":
                            self.spawn_pdu(
                                src_idx=pdu.dst_node_idx,
                                dst_idx=next_target,
                                edge_idx=edge_idx,
                                protocol="INFECT",
                                speed=0.03,
                            )

        # 2. ICMP Ping Request -> Automatically enqueue return ARP Reply
        elif pdu.protocol == "ICMP":
            return_edge_idx = self._find_edge_between(pdu.dst_node_idx, pdu.src_node_idx)
            if return_edge_idx is not None:
                self.spawn_pdu(
                    src_idx=pdu.dst_node_idx,
                    dst_idx=pdu.src_node_idx,
                    edge_idx=return_edge_idx,
                    protocol="ARP",
                    speed=pdu.speed * 1.2,
                )

    def _find_edge_between(self, u: int, v: int) -> Optional[int]:
        """Helper method to locate an edge index connecting two node indices."""
        if not self.graph:
            return None
        for idx, edge in enumerate(self.graph.edges):
            if (edge.u == u and edge.v == v) or (edge.u == v and edge.v == u):
                return idx
        return None