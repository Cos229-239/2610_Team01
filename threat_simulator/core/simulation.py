import random
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
from core.node_types import NODE_TYPES
from core.topology import NetworkGraph, calculate_password_search_space
from core.threat_modules import MetasploitAttack, GeraldTheSlightFrayer

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
    events: List[str] = field(default_factory=list)

    def format_log(self) -> str:
        engine_tag = "[C++ Engine]" if HAS_CPP_ENGINE else "[Python Strategic Engine]"
        
        events_section = ""
        if self.events:
            events_section = " ── [Threat & Defense Actions]:\n" + "".join([f"    * {ev}\n" for ev in self.events]) + "\n"

        return (
            f"[STEP {self.step} | {self.sim_time_seconds}s] {engine_tag} Status: {self.status}\n"
            f" ├── Infection Power: {self.escalation_factor:.2f}x (Escalating)\n"
            f" ├── Infected: {self.infected_nodes}/{self.total_nodes}\n"
            f" ├── Recovered/Secured: {self.recovered_nodes}\n"
            f" ├── Active Defenses: {self.active_defenses}\n"
            f" └── Threat Level: {self.threat_level_pct:.1f}%\n"
            f"{events_section}\n"
        )


@dataclass
class SimSnapshot:
    step: int
    telemetry: TelemetryData
    nodes: List
    edges: List


class DefenseAI:
    """Intelligent Defense AI counterpart to counter the threat propagation model."""
    
    @staticmethod
    def execute_defense_turn(graph: NetworkGraph, defense_power: float, currently_infected: Set[int], adj: Dict[int, List[int]]) -> List[str]:
        mitigation_events = []
        
        # 1. Identify healthy nodes directly adjacent to infected nodes (At-Risk perimeter)
        at_risk_nodes = set()
        for inf_idx in currently_infected:
            for neighbor_idx in adj[inf_idx]:
                if graph.nodes[neighbor_idx].status in ("HEALTHY", "WARNING"):
                    at_risk_nodes.add(neighbor_idx)

        # 2. Dynamic Hardening: Prioritize high-value hubs (Servers, Routers, Firewalls)
        hub_types = {"Server", "Router", "Firewall"}
        for node_idx in at_risk_nodes:
            node = graph.nodes[node_idx]
            if getattr(node, "node_type", "PC") in hub_types and defense_power > 0.3:
                # Apply a temporary defensive shield bonus
                node.defense_boost = getattr(node, 'defense_boost', 0.0) + (defense_power * 0.25)
                mitigation_events.append(f"🛡️ Defense AI Hardened critical hub [{getattr(node, 'id', node_idx)}] against lateral movement.")

        # 3. Automated Quarantine / Edge Severing
        # If defense power is robust (>= 0.6), sever connections bridging infected and healthy nodes
        if defense_power >= 0.6:
            edges_to_quarantine = []
            for edge in graph.edges:
                u_inf = graph.nodes[edge.u].status == "INFECTED" or graph.nodes[edge.u].is_patient_zero
                v_inf = graph.nodes[edge.v].status == "INFECTED" or graph.nodes[edge.v].is_patient_zero
                
                # If one endpoint is infected and the other is clean, quarantine the link
                if (u_inf and not v_inf) or (v_inf and not u_inf):
                    if getattr(edge, "status", "") != "QUARANTINED" and not getattr(edge, "is_firewall", False):
                        edges_to_quarantine.append(edge)

            # Limit quarantines per turn to simulate gradual automated response bandwidth
            quarantine_limit = max(1, int(len(edges_to_quarantine) * 0.4))
            for edge in edges_to_quarantine[:quarantine_limit]:
                edge.status = "QUARANTINED"
                u_id = getattr(graph.nodes[edge.u], 'id', f"Node-{edge.u}")
                v_id = getattr(graph.nodes[edge.v], 'id', f"Node-{edge.v}")
                mitigation_events.append(f"✂️ Firewall AI automatically quarantined link between {u_id} and {v_id}.")

        return mitigation_events


class SimulationEngine:
    def __init__(self):
        self.step_counter: int = 0
        self.total_recovered_count: int = 0
        self.history: List[SimSnapshot] = []
        self.history_index: int = -1
        # Initialize threat module instances
        self.msf_module = MetasploitAttack("SMB Buffer Overflow", "Pivot Proxy", exploit_potency=45)
        self.gerald_module = GeraldTheSlightFrayer()

    def reset(self) -> None:
        self.step_counter = 0
        self.total_recovered_count = 0
        self.history.clear()
        self.history_index = -1

    def _record_snapshot(self, graph: NetworkGraph, telemetry: TelemetryData):
        snap = SimSnapshot(
            step=self.step_counter,
            telemetry=telemetry,
            nodes=deepcopy(graph.nodes),
            edges=deepcopy(graph.edges),
        )
        if self.history_index < len(self.history) - 1:
            self.history = self.history[: self.history_index + 1]
        self.history.append(snap)
        self.history_index = len(self.history) - 1

    def restore_snapshot(self, index: int, graph: NetworkGraph) -> Optional[TelemetryData]:
        if not (0 <= index < len(self.history)):
            return None
        snap = self.history[index]
        graph.nodes = deepcopy(snap.nodes)
        graph.edges = deepcopy(snap.edges)
        self.history_index = index
        self.step_counter = snap.step
        return snap.telemetry

    def can_step_back(self) -> bool:
        return self.history_index > 0

    def can_step_forward(self) -> bool:
        return self.history_index < len(self.history) - 1

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
        resistance = (type_cfg.defense_multiplier if type_cfg else 1.0) + getattr(node, 'defense_boost', 0.0)
        uninfected_neighbors = sum(
            1 for n in adj[target_idx] if n not in infected_set
        )
        device_weight = (
            2.5 if device_type == "Router" else (1.5 if device_type == "Modem" else 1.0)
        )
        return ((uninfected_neighbors + 1) * device_weight) / max(0.5, resistance)

    def trigger_metasploit_manual(self, graph: NetworkGraph, target_node_idx: Optional[int] = None) -> List[str]:
        events = []
        currently_infected = [i for i, node in enumerate(graph.nodes) if node.status == "INFECTED" or node.is_patient_zero]
        
        if not currently_infected:
            return ["Metasploit: No infected nodes available to pivot from."]

        target_idx = target_node_idx if target_node_idx is not None else currently_infected[0]
        target_idx = max(0, min(target_idx, len(graph.nodes) - 1))
        target_node = graph.nodes[target_idx]
        target_node.status = "INFECTED"

        for inf_idx in currently_infected:
            inf_node = graph.nodes[inf_idx]
            node_id = getattr(inf_node, 'id', f"Node-{inf_idx}")
            target_id = getattr(target_node, 'id', f"Node-{target_idx}")
            events.append(f"Metasploit: Manual lateral pivot & exploit executed from {node_id} to {target_id}")
            
        return events

    def trigger_gerald_manual(self, graph: NetworkGraph) -> List[str]:
        events = []
        firewalls_found = False

        for edge in graph.edges:
            if getattr(edge, "is_firewall", False):
                firewalls_found = True
                req_attempts = getattr(edge, "required_attempts", 0)
                if req_attempts <= 0:
                    req_attempts = calculate_password_search_space(edge.password)
                    edge.required_attempts = req_attempts

                edge.crack_attempts = getattr(edge, "crack_attempts", 0) + 35000
                edge.crack_progress = min(1.0, edge.crack_attempts / max(1, req_attempts))
                
                target_name = getattr(graph.nodes[edge.v], 'id', f"Node-{edge.v}")
                events.append(f"Gerald: Manual hash crack burst on Node {target_name} ({int(edge.crack_progress * 100)}%)")

                if edge.crack_progress >= 1.0:
                    edge.is_firewall = False
                    edge.crack_progress = 0.0
                    edge.crack_attempts = 0
                    edge.password = ""
                    edge.status = "INFECTED"
                    events.append(f"Gerald: Firewall breached and password cracked on Node {target_name}!")

        if not firewalls_found:
            events.append("Gerald: No active firewalls remaining in topology.")
            
        return events

    def trigger_ddos_manual(self, graph: NetworkGraph, target_node_idx: int = 0) -> List[str]:
        events = []
        if not graph.nodes:
            return ["DDoS: No nodes available in topology."]
        
        target_idx = min(target_node_idx, len(graph.nodes) - 1)
        target_node = graph.nodes[target_idx]
        node_id = getattr(target_node, 'id', f"Node-{target_idx}")
        
        target_node.status = "INFECTED"
        events.append(f"DDoS: Massive volumetric flood targeted and overwhelmed Node {node_id}.")
        return events

    def trigger_nuke_all(self, graph: NetworkGraph) -> List[str]:
        events = []
        events.extend(self.trigger_metasploit_manual(graph))
        events.extend(self.trigger_gerald_manual(graph))
        events.extend(self.trigger_ddos_manual(graph, target_node_idx=0))
        
        bombed = 0
        for node in graph.nodes:
            if getattr(node, 'status', 'HEALTHY') == "HEALTHY":
                node.status = "INFECTED"
                bombed += 1
                if bombed >= 3:
                    break
                    
        events.append(f"💣 Logic Bomb detonated - forcibly infected {bombed} additional node(s).")
        events.append("☢ NUKE SALVO COMPLETE")
        return events

    def step(
        self,
        graph: NetworkGraph,
        inf_rate: float,
        def_power: float,
        ai_mode: str = "Strategic AI",
    ) -> TelemetryData:
        """Executes a single simulation tick with automated Defense AI and threat escalation."""
        self.step_counter += 1
        total_nodes = graph.node_count
        step_events: List[str] = []

        if total_nodes == 0:
            telemetry = TelemetryData(
                self.step_counter,
                "NO NODES",
                0, 0, 0, 0, 0.0,
                escalation_factor=1.0,
                sim_time_seconds=self.step_counter,
                events=["No active nodes found in simulation topology."]
            )
            self._record_snapshot(graph, telemetry)
            return telemetry

        # -------------------------------------------------------------
        # CAPTURE-BASED 100X THREAT ESCALATION
        # -------------------------------------------------------------
        currently_infected = {
            i
            for i, node in enumerate(graph.nodes)
            if node.status == "INFECTED" or node.is_patient_zero
        }
        if not currently_infected and graph.nodes:
            p0_idx = graph.get_patient_zero_index()
            graph.nodes[p0_idx].status = "INFECTED"
            currently_infected.add(p0_idx)

        infected_cnt = len(currently_infected)
        capture_ratio = infected_cnt / float(max(1, total_nodes))

        time_escalation = 1.0 + min(0.5, self.step_counter * 0.02)
        capture_escalation = 1.0 + (99.0 * (capture_ratio ** 1.5))
        escalation_factor = min(100.0, time_escalation * capture_escalation)
        effective_inf_rate = min(1.0, inf_rate * (escalation_factor ** 0.35))

        defense_fatigue = max(0.2, 1.0 - (self.step_counter * 0.015))
        effective_def_power = def_power * defense_fatigue

        # 1. Build Adjacency Map (Excludes Intact Active Firewalls & Quarantined Edges)
        adj: Dict[int, List[int]] = {i: [] for i in range(total_nodes)}
        for edge in graph.edges:
            if getattr(edge, "is_firewall", False) or getattr(edge, "status", "") == "QUARANTINED":
                continue
            if edge.u < total_nodes and edge.v < total_nodes:
                adj[edge.u].append(edge.v)
                adj[edge.v].append(edge.u)

        # -------------------------------------------------------------
        # PHASE 1: EXECUTE AUTOMATED DEFENSE AI TURN
        # -------------------------------------------------------------
        defense_events = DefenseAI.execute_defense_turn(graph, effective_def_power, currently_infected, adj)
        step_events.extend(defense_events)

        # -------------------------------------------------------------
        # PHASE A: INFECTION SPREAD
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
                max_breaches = max(1, int(effective_inf_rate * (4 + int(escalation_factor * 0.1))))
                best_target_idx, _ = ranked_targets[0]
                best_node = graph.nodes[best_target_idx]
                device_type = getattr(best_node, "node_type", "PC")
                type_cfg = NODE_TYPES.get(device_type, NODE_TYPES["PC"])
                type_mult = (type_cfg.defense_multiplier if type_cfg else 1.0) + getattr(best_node, 'defense_boost', 0.0)
                attack_pressure = effective_inf_rate * (
                    1.0 + 0.5 * attack_candidates[best_target_idx]
                )
                block_chance = max(
                    0.05,
                    min(
                        0.85,
                        (effective_def_power * 0.6 * type_mult)
                        - (attack_pressure * 0.2),
                    ),
                )
                if (
                    random.random() < attack_pressure
                    and random.random() >= block_chance
                ):
                    newly_infected.add(best_target_idx)
                    step_events.append(f"Strategic AI: Successfully breached high-priority target Node {getattr(best_node, 'id', best_target_idx)}")
                for target_idx, _ in ranked_targets[1:]:
                    if len(newly_infected) >= max_breaches:
                        break
                    t_node = graph.nodes[target_idx]
                    t_type = getattr(t_node, "node_type", "PC")
                    t_cfg = NODE_TYPES.get(t_type, NODE_TYPES["PC"])
                    t_mult = (t_cfg.defense_multiplier if t_cfg else 1.0) + getattr(t_node, 'defense_boost', 0.0)
                    t_block = min(0.90, effective_def_power * 0.7 * t_mult)
                    if (
                        random.random() < effective_inf_rate
                        and random.random() >= t_block
                    ):
                        newly_infected.add(target_idx)
            else:
                for target_idx in attack_candidates:
                    t_node = graph.nodes[target_idx]
                    t_type = getattr(t_node, "node_type", "PC")
                    t_cfg = NODE_TYPES.get(t_type, NODE_TYPES["PC"])
                    t_mult = (t_cfg.defense_multiplier if t_cfg else 1.0) + getattr(t_node, 'defense_boost', 0.0)
                    block_chance = min(0.90, effective_def_power * 0.75 * t_mult)
                    if (
                        random.random() < effective_inf_rate
                        and random.random() >= block_chance
                    ):
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
                    step_events.append(f"Defense AI: Patient Zero neutralized at Node {getattr(node, 'id', inf_idx)}!")
            else:
                if random.random() < recovery_chance:
                    recovered_this_step.add(inf_idx)
                    step_events.append(f"Defense AI: Node {getattr(node, 'id', inf_idx)} successfully sanitized and recovered.")

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
            if getattr(edge, "status", "") == "QUARANTINED":
                continue
            if getattr(edge, "is_firewall", False) and getattr(
                edge, "crack_progress", 0.0
            ) > 0.0:
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
        elif escalation_factor > 25.0:
            status_text = "OVERWHELMING BOTNET ESCALATION"
        elif threat_pct > 75.0:
            status_text = "CRITICAL OUTBREAK"
        else:
            status_text = f"{ai_mode.upper()} OUTBREAK IN PROGRESS"

        telemetry = TelemetryData(
            step=self.step_counter,
            status=status_text,
            infected_nodes=infected_cnt,
            recovered_nodes=self.total_recovered_count,
            total_nodes=total_nodes,
            active_defenses=int(effective_def_power * 10),
            threat_level_pct=threat_pct,
            escalation_factor=escalation_factor,
            sim_time_seconds=self.step_counter,
            events=step_events[:15],
        )

        self._record_snapshot(graph, telemetry)
        return telemetry