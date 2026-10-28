import time
from typing import List, Dict, Optional, Any


class DDoSAttack:
    """
    Simulates a volumetric DDoS (Distributed Denial of Service) flood attack.
    Floods target node buffers, draining defense parameters and compromising host status.
    """

    def __init__(self, botnet_size: int = 500, bandwidth_gbps: float = 25.0):
        self.botnet_size = botnet_size
        self.bandwidth_gbps = bandwidth_gbps

    def execute(self, target_node: Any) -> str:
        """
        Executes a volumetric SYN/UDP flood against the target node.
        """
        # Force node compromise/overwhelmed state
        if hasattr(target_node, "status"):
            target_node.status = "INFECTED"
        elif hasattr(target_node, "state"):
            target_node.state = "infected"

        # Drain defense rating if property exists
        if hasattr(target_node, "defense_power"):
            target_node.defense_power = max(0, getattr(target_node, "defense_power", 0) - 40)

        node_id = getattr(target_node, "id", "Unknown")
        log_msg = (
            f"🌊 [DDoS] Botnet swarm ({self.botnet_size} bots @ {self.bandwidth_gbps} Gbps) "
            f"overwhelmed Node {node_id}!"
        )

        if hasattr(target_node, "log_event"):
            target_node.log_event(log_msg)

        return log_msg


class MetasploitAttack:
    """
    Simulates a structured attack separating the initial breach mechanism (Exploit)
    from the executable action deployed after entry (Payload).
    """

    def __init__(self, exploit_name: str, payload_name: str, exploit_potency: int = 50):
        self.exploit_name = exploit_name  # e.g., "Buffer Overflow", "SMB Vulnerability"
        self.payload_name = payload_name  # e.g., "Botnet Agent", "Pivot Proxy", "Credential Harvester"
        self.exploit_potency = exploit_potency  # Power score tested against target firewall/defense

    def can_exploit(self, target_node: Any) -> bool:
        """
        Checks whether the exploit potency overcomes target firewall/defense power.
        """
        defense = getattr(target_node, "defense_power", 0)
        firewall_active = getattr(target_node, "firewall_active", False)
        
        # Effective defense power increases if an active firewall is present
        effective_defense = defense + (30 if firewall_active else 0)
        return self.exploit_potency >= effective_defense

    def execute(self, source_node: Any, target_node: Any) -> bool:
        """
        Attempts to breach the target node and deploy the configured payload.
        """
        if self.can_exploit(target_node):
            if hasattr(target_node, "status"):
                target_node.status = "INFECTED"
            if hasattr(target_node, "state"):
                target_node.state = "infected"

            target_node.active_payload = self.payload_name
            
            # Log telemetry event if node has a telemetry tracker
            if hasattr(target_node, "log_event"):
                target_node.log_event(
                    f"Breached by '{self.exploit_name}' from Node {getattr(source_node, 'id', 'Unknown')}. "
                    f"Payload deployed: {self.payload_name}"
                )
            return True
        return False


class GeraldTheSlightFrayer:
    """
    'Gerald the Slight Frayer' - Mock Rainbow Table Engine.
    Simulates pre-computed dictionary hash lookups to bypass slow brute-force iteration timers.
    """

    def __init__(self, rainbow_table: Optional[Dict[str, str]] = None):
        self.name = "Gerald the Slight Frayer"
        # Pre-computed dictionary: hash -> plaintext password
        self.rainbow_table = rainbow_table or {
            "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8": "password",
            "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918": "admin",
            "hash_abc123": "admin123",
            "hash_xyz789": "letmein123",
            "default_hash": "user_pass"
        }

    def crack_password(self, target_node: Any) -> bool:
        """
        Performs an instant rainbow table lookup on the target node's mock password hash.
        Bypasses slow brute-force timers if a hash match is found.
        """
        target_hash = getattr(target_node, "password_hash", None)

        if target_hash and target_hash in self.rainbow_table:
            target_node.password_cracked = True
            target_node.compromise_timer = 0
            
            if hasattr(target_node, "log_event"):
                target_node.log_event(
                    f"Credentials cracked instantly via {self.name}! "
                    f"Hash resolved: '{target_hash}' -> Plaintext: '{self.rainbow_table[target_hash]}'"
                )
            return True

        # Fallback if hash isn't in rainbow table: node must undergo standard brute-force
        return False


def get_pivoted_targets(source_node: Any, network_graph: Any) -> List[Any]:
    """
    Utility function for lateral movement / pivoting.
    If source_node has a 'Pivot Proxy' payload, it can reach nodes 2 hops away,
    jumping across intermediate subnet firewalls.
    """
    direct_neighbors = getattr(source_node, "neighbors", [])
    targets = list(direct_neighbors)

    # Check for pivot capabilities
    if getattr(source_node, "active_payload", None) == "Pivot Proxy":
        for neighbor in direct_neighbors:
            # Reaches second-degree nodes through the compromised neighbor bridge
            for sub_neighbor in getattr(neighbor, "neighbors", []):
                if sub_neighbor not in targets and sub_neighbor != source_node:
                    targets.append(sub_neighbor)

    return targets