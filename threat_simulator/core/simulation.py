from collections import deque
from dataclasses import dataclass
from typing import List, Set
from core.topology import NetworkGraph

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

    def _bfs_infection_spread(self, graph: NetworkGraph, depth_limit: int) -> Set[int]:
        if not graph.nodes:
            return set()

        start_idx = graph.get_patient_zero_index()
        adj = {i: [] for i in range(len(graph.nodes))}
        for edge in graph.edges:
            adj[edge.u].append(edge.v)
            adj[edge.v].append(edge.u)

        visited = {start_idx}
        queue = deque([(start_idx, 0)])
        infected_indices = set()

        while queue:
            curr, dist = queue.popleft()
            if dist > depth_limit:
                continue
            infected_indices.add(curr)

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

        effective_rate = max(0.1, inf_rate - (def_power * 0.7))
        bfs_depth = int(self.step_counter * effective_rate * 2)

        infected_set = self._bfs_infection_spread(graph, depth_limit=bfs_depth)
        warning_set = self._bfs_infection_spread(graph, depth_limit=bfs_depth + 1) - infected_set

        # 1. Update Node Statuses
        for i, node in enumerate(graph.nodes):
            if i in infected_set:

                if node.infection_step == -1:
                    node.infection_step = self.step_counter

                node.status = "INFECTED"

            elif i in warning_set:
                node.status = "WARNING"

            else:
                node.status = "HEALTHY"

        # 2. Update Edge Statuses (Highlight edges where infection flows)
        for edge in graph.edges:
            u_infected = edge.u in infected_set
            v_infected = edge.v in infected_set
            u_warning = edge.u in warning_set or u_infected
            v_warning = edge.v in warning_set or v_infected

            if u_infected and v_infected:
                edge.status = "INFECTED"  # Fully compromised connection
            elif u_warning and v_warning:
                edge.status = "WARNING"   # Threat spreading across edge
            else:
                edge.status = "HEALTHY"

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