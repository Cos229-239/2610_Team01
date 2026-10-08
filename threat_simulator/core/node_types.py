from dataclasses import dataclass
from typing import Dict


@dataclass
class NodeTypeConfig:
    name: str
    symbol: str
    color: str
    radius: int
    defense_multiplier: float  # Modifies node resistance to infection


# Registry of supported network device types
NODE_TYPES: Dict[str, NodeTypeConfig] = {
    "PC": NodeTypeConfig(
        name="PC",
        symbol="💻",
        color="#29B6F6",  # Light Blue
        radius=9,
        defense_multiplier=1.0,  # Standard susceptibility
    ),
    "Router": NodeTypeConfig(
        name="Router",
        symbol="📡",
        color="#AB47BC",  # Purple
        radius=12,
        defense_multiplier=1.5,  # Higher resistance
    ),
    "Modem": NodeTypeConfig(
        name="Modem",
        symbol="🌐",
        color="#FFA726",  # Orange
        radius=11,
        defense_multiplier=1.2,  # Moderate resistance
    ),
}
