
class DefenseAI:
    @staticmethod
    def execute_defense_turn(graph, defense_power: float):
        mitigation_events = []
        
        # 1. Identify high-risk nodes (healthy nodes adjacent to infected ones)
        at_risk_nodes = set()
        for edge in graph.edges:
            n1 = graph.nodes[edge.node1_idx]
            n2 = graph.nodes[edge.node2_idx]
            
            if (n1.status == "INFECTED" or n1.is_patient_zero) and n2.status == "HEALTHY":
                at_risk_nodes.add(n2)
            elif (n2.status == "INFECTED" or n2.is_patient_zero) and n1.status == "HEALTHY":
                at_risk_nodes.add(n1)

        # 2. Strategic Hardening: Boost defense on at-risk hubs (Servers, Routers first)
        hub_types = {"Server", "Router", "Firewall"}
        for node in at_risk_nodes:
            if node.device_type in hub_types and defense_power > 0.4:
                # Give critical infrastructure a defensive shield boost
                node.defense_boost = getattr(node, 'defense_boost', 0.0) + (defense_power * 0.2)
                mitigation_events.append(f"🛡️ AI Hardened critical node [{node.name}] against lateral movement.")

        # 3. Automatic Quarantine / Edge Severing
        # If defense power is high (> 0.7), automatically sever links from infected nodes to isolate outbreaks
        if defense_power >= 0.7:
            edges_to_disable = []
            for edge in graph.edges:
                n1 = graph.nodes[edge.node1_idx]
                n2 = graph.nodes[edge.node2_idx]
                
                # If one is infected and the other is healthy, cut the connection
                if ((n1.status == "INFECTED" or n1.is_patient_zero) and n2.status == "HEALTHY") or \
                   ((n2.status == "INFECTED" or n2.is_patient_zero) and n1.status == "HEALTHY"):
                    edges_to_disable.append(edge)

            # Limit quarantine actions per step so it doesn't instantly wipe the network graph
            quarantine_limit = max(1, int(len(edges_to_disable) * 0.5))
            for edge in edges_to_disable[:quarantine_limit]:
                edge.status = "QUARANTINED"
                mitigation_events.append(f"✂️ Firewall automatically severed link between Node {edge.node1_idx} and Node {edge.node2_idx}.")

        return mitigation_events