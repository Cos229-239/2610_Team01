
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class NodeTypeConfig:
    name: str
    symbol: str
    color: str
    radius: int
    defense_multiplier: float  # Modifies node resistance to infection
    layer: int = 3             # OSI Layer (Layer 2 Switching vs Layer 3 Routing/Host)
    default_ports: int = 4     # Number of physical interfaces available
    supported_protocols: List[str] = field(default_factory=lambda: ["IP", "ICMP", "ARP"])


# Registry of supported network device types
NODE_TYPES: Dict[str, NodeTypeConfig] = {
    "PC": NodeTypeConfig(
        name="PC",
        symbol="💻",
        color="#29B6F6",  # Light Blue
        radius=9,
        defense_multiplier=1.0,  # Standard susceptibility
        layer=3,
        default_ports=1,
        supported_protocols=["IP", "ICMP", "ARP", "TCP", "UDP"],
    ),
    "Laptop": NodeTypeConfig(
        name="Laptop",
        symbol="💻",
        color="#26A69A",  # Teal
        radius=9,
        defense_multiplier=0.9,  # Slightly higher mobility risk
        layer=3,
        default_ports=1,
        supported_protocols=["IP", "ICMP", "ARP", "TCP", "UDP"],
    ),
    "Server": NodeTypeConfig(
        name="Server",
        symbol="🖥️",
        color="#26C6DA",  # Cyan
        radius=14,
        defense_multiplier=2.2,  # Enterprise hardened
        layer=3,
        default_ports=2,
        supported_protocols=["IP", "ICMP", "ARP", "TCP", "UDP", "HTTP", "SSH"],
    ),
    "Switch": NodeTypeConfig(
        name="Switch",
        symbol="🔀",
        color="#7E57C2",  # Deep Purple
        radius=11,
        defense_multiplier=1.8,  # L2 Hardware forwarding
        layer=2,
        default_ports=24,
        supported_protocols=["ETHERNET", "ARP", "STP"],
    ),
    "Router": NodeTypeConfig(
        name="Router",
        symbol="📡",
        color="#AB47BC",  # Purple
        radius=12,
        defense_multiplier=1.5,  # Gateway security
        layer=3,
        default_ports=4,
        supported_protocols=["IP", "ICMP", "ARP", "RIP", "OSPF"],
    ),
    "Modem": NodeTypeConfig(
        name="Modem",
        symbol="🌐",
        color="#FFA726",  # Orange
        radius=11,
        defense_multiplier=1.2,  # Edge translation
        layer=2,
        default_ports=2,
        supported_protocols=["PPP", "DOCSIS"],
    ),
    "Firewall": NodeTypeConfig(
        name="Firewall",
        symbol="🛡️",
        color="#EF5350",  # Red-Orange
        radius=13,
        defense_multiplier=3.0,  # Strict inspection barrier
        layer=3,
        default_ports=4,
        supported_protocols=["IP", "ICMP", "ARP", "NAT", "SPI"],
    ),
}