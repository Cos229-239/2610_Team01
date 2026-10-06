from collections import deque
from dataclasses import dataclass
from typing import List, Optional, Dict
from core.topology import NetworkGraph, Node

try:
    import network_engine
    HAS_CPP_ENGINE = True
except ImportError:
    network_engine = None
    HAS_CPP_ENGINE = False


@dataclass
class TelemetryData:
    step: int
    status: str
    infected_nodes: int
    total_nodes: int
    active_defenses: int
    threat_level_pct: float

    def format_log(self) -> str:
        engine_tag = "[C++ Engine]" if HAS_CPP_ENGINE else "[Python Fallback]"
        return (
            f" ├── Infected Nodes: {self.infected_nodes}/{self.total_nodes}\n"
            f" ├── Active Defenses: {self.active_defenses}\n"
            f" └── Threat Level: {self.threat_level_pct:.1f}%\n\n"
        )


class SimulationEngine:
    def __init__(self):
        self.step_counter: int = 0

    def reset(self) -> None:
        self.step_counter = 0

    def _bfs_infection_spread(self, graph: NetworkGraph, depth_limit: int) -> List[int]:
        """Calculates infected node indices using BFS starting from Patient Zero."""
        if not graph.nodes:
            return []

        start_idx = graph.get_patient_zero_index()
        
        # Build adjacency list
        adj = {i: [] for i in range(len(graph.nodes))}
        for u, v in graph.edges:
            adj[u].append(v)
            adj[v].append(u)

        visited = {start_idx}
        queue = deque([(start_idx, 0)])
        infected_indices = []

        while queue:
            curr, dist = queue.popleft()
            if dist > depth_limit:
                continue
            infected_indices.append(curr)

            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))

        return infected_indices

    def step(self, graph: NetworkGraph, inf_rate: float, def_power: float) -> TelemetryData:
        self.step_counter += 1
        total_nodes = graph.node_count

        if total_nodes == 0:
            return TelemetryData(self.step_counter, "NO NODES", 0, 0, 0, 0.0)

        # Rate controls how many BFS distance hops are breached per step
        effective_rate = max(0.1, inf_rate - (def_power * 0.7))
        bfs_depth = int(self.step_counter * effective_rate * 2)

        # Get infected nodes starting from Patient Zero
        infected_set = set(self._bfs_infection_spread(graph, depth_limit=bfs_depth))
        
        # Get warning nodes (1 hop further)
        warning_set = set(self._bfs_infection_spread(graph, depth_limit=bfs_depth + 1)) - infected_set

        # Update node visual status
        for i, node in enumerate(graph.nodes):
            if i in infected_set:
                node.status = "INFECTED"
            elif i in warning_set:
                node.status = "WARNING"
            else:
                node.status = "HEALTHY"

        infected_cnt = len(infected_set)
        threat_pct = (infected_cnt / float(total_nodes)) * 100.0
        status = "CRITICAL OUTBREAK" if threat_pct > 75.0 else "CONTAINMENT ACTIVE"

        return TelemetryData(
            step=self.step_counter,
            status=status,
            infected_nodes=infected_cnt,
            total_nodes=total_nodes,
            active_defenses=int(def_power * 5),
            threat_level_pct=threat_pct,
        )