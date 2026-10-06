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
            f"[STEP {self.step}] {engine_tag} Status: {self.status}\n"
            f" ├── Infected Nodes: {self.infected_nodes}/{self.total_nodes}\n"
            f" ├── Active Defenses: {self.active_defenses}\n"
            f" └── Threat Level: {self.threat_level_pct:.1f}%\n\n"
        )


class SimulationEngine:
    def __init__(self):
        self.step_counter: int = 0

        if HAS_CPP_ENGINE and network_engine is not None:
            if hasattr(network_engine, "GraphManager"):
                self._cpp_engine = network_engine.GraphManager()
            elif hasattr(network_engine, "NetworkEngine"):
                self._cpp_engine = network_engine.NetworkEngine(20)
            else:
                self._cpp_engine = None
        else:
            self._cpp_engine = None

    def reset(self) -> None:
        self.step_counter = 0

    def sync_topology_to_cpp(self, graph: NetworkGraph) -> None:
        if not HAS_CPP_ENGINE or self._cpp_engine is None:
            return

        adj_list: Dict[str, List[str]] = {}
        for u, v in graph.edges:
            u_id = f"NODE-{u+1:02d}"
            v_id = f"NODE-{v+1:02d}"
            adj_list.setdefault(u_id, []).append(v_id)
            adj_list.setdefault(v_id, []).append(u_id)

        if hasattr(self._cpp_engine, "set_adjacency_list"):
            self._cpp_engine.set_adjacency_list(adj_list)

        if hasattr(network_engine, "Node") and hasattr(self._cpp_engine, "add_nodes"):
            cpp_nodes = [
                network_engine.Node(n.id, n.status, 0.0) for n in graph.nodes
            ]
            self._cpp_engine.add_nodes(cpp_nodes)

        if hasattr(self._cpp_engine, "set_total_nodes"):
            self._cpp_engine.set_total_nodes(graph.node_count)

    def step(
        self, graph: NetworkGraph, inf_rate: float, def_power: float
    ) -> TelemetryData:

        self.step_counter += 1
        total_nodes = graph.node_count

        if HAS_CPP_ENGINE and self._cpp_engine is not None:
            self.sync_topology_to_cpp(graph)

            if hasattr(self._cpp_engine, "run_step_telemetry"):
                res = self._cpp_engine.run_step_telemetry(
                    self.step_counter, inf_rate, def_power
                )
                infected_cnt = res.infected_nodes
                telemetry = TelemetryData(
                    step=res.step,
                    status=res.status,
                    infected_nodes=res.infected_nodes,
                    total_nodes=res.total_nodes,
                    active_defenses=res.active_defenses,
                    threat_level_pct=res.threat_level_pct,
                )
            elif hasattr(self._cpp_engine, "get_all_nodes"):
                cpp_nodes = self._cpp_engine.get_all_nodes()
                infected_cnt = sum(1 for n in cpp_nodes if n.status == "INFECTED")
                threat_pct = (infected_cnt / float(total_nodes or 1)) * 100.0
                status = (
                    "CRITICAL OUTBREAK" if threat_pct > 75.0 else "CONTAINMENT ACTIVE"
                )

                telemetry = TelemetryData(
                    step=self.step_counter,
                    status=status,
                    infected_nodes=infected_cnt,
                    total_nodes=total_nodes,
                    active_defenses=int(def_power * 5),
                    threat_level_pct=threat_pct,
                )
            else:
                effective_rate = max(0.05, inf_rate - (def_power * 0.8))
                infected_cnt = min(
                    total_nodes, max(1, int(self.step_counter * effective_rate * 2))
                )
                threat_pct = (infected_cnt / float(total_nodes or 1)) * 100.0
                telemetry = TelemetryData(
                    step=self.step_counter,
                    status="CONTAINMENT ACTIVE",
                    infected_nodes=infected_cnt,
                    total_nodes=total_nodes,
                    active_defenses=int(def_power * 5),
                    threat_level_pct=threat_pct,
                )
        else:
            effective_rate = max(0.05, inf_rate - (def_power * 0.8))
            infected_cnt = min(
                total_nodes, max(1, int(self.step_counter * effective_rate * 2))
            )
            threat_pct = (infected_cnt / float(total_nodes or 1)) * 100.0

            telemetry = TelemetryData(
                step=self.step_counter,
                status="CONTAINMENT ACTIVE",
                infected_nodes=infected_cnt,
                total_nodes=total_nodes,
                active_defenses=int(def_power * 5),
                threat_level_pct=threat_pct,
            )

        for i, node in enumerate(graph.nodes):
            if i < infected_cnt:
                node.status = "INFECTED"
            elif i < infected_cnt + 2:
                node.status = "WARNING"
            else:
                node.status = "HEALTHY"

        return telemetry