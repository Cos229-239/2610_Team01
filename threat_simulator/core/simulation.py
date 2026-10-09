import random
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
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
    escalation_factor: float = 1.0
    sim_time_seconds: int = 0

    def format_log(self) -> str:
        engine_tag = "[C++ Engine]" if HAS_CPP_ENGINE else "[Python Strategic Engine]"
        return (
            f"[STEP {self.step} | {self.sim_time_seconds}s] {engine_tag} Status: {self.status}\n"
            f" ├── Infection Power: {self.escalation_factor:.2f}x (Escalating)\n"
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

    def _calculate_target_priority(
        self,
        target_idx: int,
        graph: NetworkGraph,
        adj: Dict[int, List[int]],
        infected_set: Set[int],
    ) -> float:
        """Scores candidate targets to find optimal path for network infection."""
        node = graph.nodes[target_idx]
        device_type = getattr(node, "node_type", "PC")
        type_cfg = NODE_TYPES.get(device_type, NODE_TYPES["PC"])
        resistance = type_cfg.defense_multiplier if type_cfg else 1.0

        uninfected_neighbors = sum(
            1 for n in adj[target_idx] if n not in infected_set
        )
        device_weight = (
            2.5 if device_type == "Router" else (1.5 if device_type == "Modem" else 1.0)
        )

        return ((uninfected_neighbors + 1) * device_weight) / max(0.5, resistance)

    def step(
        self,
        graph: NetworkGraph,
        inf_rate: float,
        def_power: float,
        ai_mode: str = "Strategic AI",
    ) -> TelemetryData:
        """Executes a single simulation tick with dynamic password cracking and escalating infection potency."""
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
                escalation_factor=1.0,
                sim_time_seconds=self.step_counter,
            )

        # -------------------------------------------------------------
        # ESCALATION CALCULATION: Threat grows stronger over time
        # Increases by +5% per tick, capping at 2.5x base power
        # -------------------------------------------------------------
        escalation_factor = 1.0 + min(1.5, self.step_counter * 0.05)
        effective_inf_rate = min(1.0, inf_rate * escalation_factor)

        # Defense fatigue under persistent infection
        defense_fatigue = max(0.4, 1.0 - (self.step_counter * 0.015))
        effective_def_power = def_power * defense_fatigue

        # -------------------------------------------------------------
        # ADAPTIVE FIREWALL PASSWORD CRACKING PHASE
        # -------------------------------------------------------------
        for edge in graph.edges:
            if getattr(edge, "is_firewall", False):
                u_inf = graph.nodes[edge.u].status == "INFECTED"
                v_inf = graph.nodes[edge.v].status == "INFECTED"

                # If an infected node borders this firewall barrier, apply cracking pressure
                if u_inf or v_inf:
                    # Crack speed scales with current infection rate and escalation multiplier
                    crack_speed = (effective_inf_rate * 0.15) * escalation_factor
                    edge.crack_progress = min(1.0, getattr(edge, "crack_progress", 0.0) + crack_speed)

                    # When cracking hits 100%, breach and disarm the firewall barrier
                    if edge.crack_progress >= 1.0:
                        edge.is_firewall = False
                        edge.crack_progress = 0.0
                        edge.password = ""
                        edge.status = "INFECTED"

        # 1. Build Adjacency Map (Excludes Intact Active Firewalls)
        adj: Dict[int, List[int]] = {i: [] for i in range(total_nodes)}
        for edge in graph.edges:
            # Skip edge if firewall is active and unbroken
            if getattr(edge, "is_firewall", False):
                continue

            if edge.u < total_nodes and edge.v < total_nodes:
                adj[edge.u].append(edge.v)
                adj[edge.v].append(edge.u)

        # 2. Identify Currently Infected Nodes
        currently_infected = {
            i
            for i, node in enumerate(graph.nodes)
            if node.status == "INFECTED" or node.is_patient_zero
        }

        if not currently_infected and graph.nodes:
            p0_idx = graph.get_patient_zero_index()
            graph.nodes[p0_idx].status = "INFECTED"
            currently_infected.add(p0_idx)

        # -------------------------------------------------------------
        # PHASE A: INFECTION SPREAD (WITH ESCALATED POWER)
        # -------------------------------------------------------------
        attack_candidates: Dict[int, int] = {}
        for inf_idx in currently_infected:
            for neighbor_idx in adj[inf_idx]:
                if (
                    graph.nodes[neighbor_idx].status in ("HEALTHY", "WARNING")
                    and not graph.nodes[neighbor_idx].is_patient_zero
                ):
                    attack_candidates[neighbor_idx] = (
                        attack_candidates.get(neighbor_idx, 0) + 1
                    )

        newly_infected = set()

        if attack_candidates:
            if ai_mode == "Strategic AI":
                ranked_targets: List[Tuple[int, float]] = [
                    (
                        t_idx,
                        self._calculate_target_priority(
                            t_idx, graph, adj, currently_infected
                        ),
                    )
                    for t_idx in attack_candidates
                ]
                ranked_targets.sort(key=lambda x: x[1], reverse=True)

                max_breaches = max(1, int(effective_inf_rate * 4))

                best_target_idx, _ = ranked_targets[0]
                best_node = graph.nodes[best_target_idx]
                device_type = getattr(best_node, "node_type", "PC")
                type_cfg = NODE_TYPES.get(device_type, NODE_TYPES["PC"])
                type_mult = type_cfg.defense_multiplier if type_cfg else 1.0

                attack_pressure = effective_inf_rate * (
                    1.0 + 0.5 * attack_candidates[best_target_idx]
                )
                block_chance = max(
                    0.05,
                    min(0.85, (effective_def_power * 0.6 * type_mult) - (attack_pressure * 0.2)),
                )

                if (
                    random.random() < attack_pressure
                    and random.random() >= block_chance
                ):
                    newly_infected.add(best_target_idx)

                for target_idx, _ in ranked_targets[1:]:
                    if len(newly_infected) >= max_breaches:
                        break
                    t_node = graph.nodes[target_idx]
                    t_type = getattr(t_node, "node_type", "PC")
                    t_cfg = NODE_TYPES.get(t_type, NODE_TYPES["PC"])
                    t_mult = t_cfg.defense_multiplier if t_cfg else 1.0
                    t_block = min(0.90, effective_def_power * 0.7 * t_mult)

                    if random.random() < effective_inf_rate and random.random() >= t_block:
                        newly_infected.add(target_idx)

            else:
                for target_idx in attack_candidates:
                    t_node = graph.nodes[target_idx]
                    t_type = getattr(t_node, "node_type", "PC")
                    t_cfg = NODE_TYPES.get(t_type, NODE_TYPES["PC"])
                    t_mult = t_cfg.defense_multiplier if t_cfg else 1.0
                    block_chance = min(0.90, effective_def_power * 0.75 * t_mult)

                    if random.random() < effective_inf_rate and random.random() >= block_chance:
                        newly_infected.add(target_idx)

        # -------------------------------------------------------------
        # PHASE B: RETAKING & NEUTRALIZING INFECTED NODES
        # -------------------------------------------------------------
        recovered_this_step = set()
        recovery_chance = max(0.02, effective_def_power * 0.35)

        for inf_idx in list(currently_infected):
            node = graph.nodes[inf_idx]

            if node.is_patient_zero:
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
                p0_neutralize_chance = (effective_def_power * 0.25) * neighbor_support

                if random.random() < p0_neutralize_chance:
                    node.is_patient_zero = False
                    recovered_this_step.add(inf_idx)
            else:
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
        # PHASE C: UPDATE WARNINGS & EDGE HIGHLIGHTS
        # -------------------------------------------------------------
        for inf_idx in currently_infected:
            for neighbor_idx in adj[inf_idx]:
                if graph.nodes[neighbor_idx].status == "HEALTHY":
                    graph.nodes[neighbor_idx].status = "WARNING"

        for i, node in enumerate(graph.nodes):
            if node.status == "WARNING":
                has_infected_neighbor = any(
                    graph.nodes[n_idx].status == "INFECTED" for n_idx in adj[i]
                )
                if not has_infected_neighbor:
                    node.status = "HEALTHY"

        for edge in graph.edges:
            # Highlight firewall edges as warning when actively being cracked
            if getattr(edge, "is_firewall", False) and getattr(edge, "crack_progress", 0.0) > 0.0:
                edge.status = "WARNING"
            else:
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
        elif escalation_factor > 1.8:
            status_text = "MUTATED THREAT ESCALATION"
        elif threat_pct > 75.0:
            status_text = "CRITICAL OUTBREAK"
        else:
            status_text = f"{ai_mode.upper()} OUTBREAK IN PROGRESS"

        return TelemetryData(
            step=self.step_counter,
            status=status_text,
            infected_nodes=infected_cnt,
            recovered_nodes=self.total_recovered_count,
            total_nodes=total_nodes,
            active_defenses=int(effective_def_power * 10),
            threat_level_pct=threat_pct,
            escalation_factor=escalation_factor,
            sim_time_seconds=self.step_counter,
        )