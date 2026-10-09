import random
from dataclasses import dataclass
from typing import Dict, List, Set
from core.node_types import NODE_TYPES
from core.topology import NetworkGraph

# Attempt C++ module import with graceful fallback
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
    recovered_nodes: int
    total_nodes: int
    active_defenses: int
    threat_level_pct: float
    sim_time_seconds: int = 0

    def format_log(self) -> str:
        engine_tag = "[C++ Engine]" if HAS_CPP_ENGINE else "[Python Engine]"
        return (
            f"[STEP {self.step} | {self.sim_time_seconds}s] {engine_tag} Status: {self.status}\n"
            f" ├── Infected: {self.infected_nodes}/{self.total_nodes}\n"
            f" ├── Recovered/Secured: {self.recovered_nodes}\n"
            f" ├── Active Defenses: {self.active_defenses}\n"
            f" └── Threat Level: {self.threat_level_pct:.1f}%\n\n"
        )


class SimulationEngine:
    def __init__(self):
        self.step_counter: int = 0
        self.total_recovered_count: int = 0

    def reset(self) -> None:
        self.step_counter = 0
        self.total_recovered_count = 0

    def step(
        self, graph: NetworkGraph, inf_rate: float, def_power: float
    ) -> TelemetryData:
        """Executes a single simulation tick with defense blocking, node recovery,

        and Patient Zero elimination mechanics.
        """
        self.step_counter += 1
        total_nodes = graph.node_count

        if total_nodes == 0:
            return TelemetryData(
                self.step_counter,
                "NO NODES",
                0,
                0,
                0,
                0,
                0.0,
                sim_time_seconds=self.step_counter,
            )

        # 1. Build Adjacency Map
        adj: Dict[int, List[int]] = {i: [] for i in range(total_nodes)}
        for edge in graph.edges:
            if edge.u < total_nodes and edge.v < total_nodes:
                adj[edge.u].append(edge.v)
                adj[edge.v].append(edge.u)

        # 2. Identify Currently Infected Nodes
        currently_infected = {
            i
            for i, node in enumerate(graph.nodes)
            if node.status == "INFECTED" or node.is_patient_zero
        }

        # -------------------------------------------------------------
        # PHASE A: INFECTION SPREAD WITH DEFENSE BLOCK CHANCES
        # -------------------------------------------------------------
        newly_infected = set()

        for inf_idx in currently_infected:
            for neighbor_idx in adj[inf_idx]:
                neighbor_node = graph.nodes[neighbor_idx]

                if neighbor_node.status in (
                    "HEALTHY",
                    "WARNING",
                ) and not neighbor_node.is_patient_zero:
                    device_type = getattr(neighbor_node, "node_type", "PC")
                    type_cfg = NODE_TYPES.get(device_type, NODE_TYPES["PC"])
                    type_mult = type_cfg.defense_multiplier if type_cfg else 1.0

                    block_chance = min(0.90, def_power * 0.75 * type_mult)
                    spread_chance = inf_rate

                    if random.random() < spread_chance:
                        if random.random() >= block_chance:
                            newly_infected.add(neighbor_idx)

        # -------------------------------------------------------------
        # PHASE B: RETAKING & NEUTRALIZING INFECTED NODES (INCLUDING P0)
        # -------------------------------------------------------------
        recovered_this_step = set()
        recovery_chance = max(0.02, def_power * 0.35)

        for inf_idx in list(currently_infected):
            node = graph.nodes[inf_idx]

            # Special Patient Zero Defense Counterattack Logic:
            if node.is_patient_zero:
                # Calculate how many healthy neighbors are applying counter-pressure
                healthy_neighbors = sum(
                    1
                    for n_idx in adj[inf_idx]
                    if graph.nodes[n_idx].status == "HEALTHY"
                )
                neighbor_support = (
                    healthy_neighbors / max(1, len(adj[inf_idx]))
                    if adj[inf_idx]
                    else 1.0
                )

                # Patient Zero requires stronger defense power & surrounding pressure to neutralize
                p0_neutralize_chance = (
                    def_power * 0.25
                ) * neighbor_support

                if random.random() < p0_neutralize_chance:
                    node.is_patient_zero = False  # Strip origin status
                    recovered_this_step.add(inf_idx)
            else:
                # Standard node retake roll
                if random.random() < recovery_chance:
                    recovered_this_step.add(inf_idx)

        # Apply state updates
        for idx in newly_infected:
            graph.nodes[idx].status = "INFECTED"

        for idx in recovered_this_step:
            graph.nodes[idx].status = "HEALTHY"
            currently_infected.discard(idx)
            self.total_recovered_count += 1

        currently_infected.update(newly_infected)

        # -------------------------------------------------------------
        # PHASE C: UPDATE EDGE & WARNING STATES
        # -------------------------------------------------------------
        for inf_idx in currently_infected:
            for neighbor_idx in adj[inf_idx]:
                if graph.nodes[neighbor_idx].status == "HEALTHY":
                    graph.nodes[neighbor_idx].status = "WARNING"

        # Reset warnings for nodes that have no infected neighbors
        for i, node in enumerate(graph.nodes):
            if node.status == "WARNING":
                has_infected_neighbor = any(
                    graph.nodes[n_idx].status == "INFECTED" for n_idx in adj[i]
                )
                if not has_infected_neighbor:
                    node.status = "HEALTHY"

        # Update Edge Statuses
        for edge in graph.edges:
            u_inf = graph.nodes[edge.u].status == "INFECTED"
            v_inf = graph.nodes[edge.v].status == "INFECTED"

            if u_inf and v_inf:
                edge.status = "INFECTED"
            elif u_inf or v_inf:
                edge.status = "WARNING"
            else:
                edge.status = "HEALTHY"

        infected_cnt = len(currently_infected)
        threat_pct = (infected_cnt / float(total_nodes)) * 100.0

        if infected_cnt == 0:
            status_text = "THREAT NEUTRALIZED - ALL CLEAN"
        elif threat_pct > 75.0:
            status_text = "CRITICAL OUTBREAK"
        elif threat_pct < 20.0:
            status_text = "DEFENSE RETAKING DOMAIN"
        else:
            status_text = "OUTBREAK IN PROGRESS"

        return TelemetryData(
            step=self.step_counter,
            status=status_text,
            infected_nodes=infected_cnt,
            recovered_nodes=self.total_recovered_count,
            total_nodes=total_nodes,
            active_defenses=int(def_power * 10),
            threat_level_pct=threat_pct,
            sim_time_seconds=self.step_counter,
        )