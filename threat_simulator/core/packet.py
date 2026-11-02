import uuid
from typing import Dict, Any, Optional

class Packet:
    def __init__(
        self,
        src_ip: str,
        dst_ip: str,
        src_mac: str,
        dst_mac: str,
        protocol: str = "ICMP", # ICMP (Ping), ARP, TCP, UDP
        payload: Optional[Dict[str, Any]] = None,
        ttl: int = 64
    ):
        self.id = str(uuid.uuid4())[:8]
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.protocol = protocol
        self.payload = payload or {}
        self.ttl = ttl
        
        # PDU Tracking
        self.current_edge_idx: Optional[int] = None
        self.progress: float = 0.0  # 0.0 (source) to 1.0 (destination)
