import customtkinter as ctk

class PacketInspectorModal(ctk.CTkToplevel):
    def __init__(self, master, pdu, graph):
        super().__init__(master)
        self.title(f"Wireshark-Lite ── Packet [{pdu.id}]")
        self.geometry("460x380")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.focus_force()

        # Cyber/Wireshark dark aesthetic
        self.configure(fg_color="#1e1e1e")

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="#2d2d2d", corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkLabel(
            header_frame, 
            text=f"📦 PDU Packet Analyzer — Protocol: {pdu.protocol}", 
            font=("Consolas", 13, "bold"),
            text_color="#69F0AE"
        ).pack(padx=15, pady=10, anchor="w")

        # Main Details Box (Terminal style text box)
        details_box = ctk.CTkTextbox(self, font=("Consolas", 12), fg_color="#141414", text_color="#d4d4d4")
        details_box.pack(fill="both", expand=True, padx=15, pady=15)

        # Resolve source and destination node IDs safely
        src_node = graph.nodes[pdu.src_node_idx] if 0 <= pdu.src_node_idx < len(graph.nodes) else None
        dst_node = graph.nodes[pdu.dst_node_idx] if 0 <= pdu.dst_node_idx < len(graph.nodes) else None
        src_id = getattr(src_node, 'id', pdu.src_node_idx)
        dst_id = getattr(dst_node, 'id', pdu.dst_node_idx)

        # Build simulated Wireshark inspection packet breakdown
        packet_info = (
            f"FRAME [{pdu.id}]: 142 bytes on wire\n"
            f"==================================================\n"
            f"Layer 2 (Data Link): Simulated Network Edge #{pdu.edge_idx}\n"
            f"Layer 3 (Network - IP):\n"
            f"    Source IP / Node ID:      {src_id} (Index {pdu.src_node_idx})\n"
            f"    Destination IP / Node ID: {dst_id} (Index {pdu.dst_node_idx})\n"
            f"    TTL (Time to Live):       64 hops\n"
            f"Layer 4 (Transport):\n"
            f"    Protocol Type:            {pdu.protocol}\n"
            f"    Packet Velocity (Speed):  {pdu.speed}\n"
            f"    Transit Progress:         {pdu.progress * 100:.1f}%\n"
            f"    Delivery Status:          {'Delivered' if pdu.delivered else 'In Transit'}\n"
            f"--------------------------------------------------\n"
            f"Payload / Data Dump:\n"
            f"    0000  {ord(pdu.protocol[0]):02x} {ord(pdu.protocol[1]) if len(pdu.protocol)>1 else 0:02x} "
            f"53 4d 42 20 45 78  ..SMB Ex\n"
            f"    0008  70 6c 6f 69 74 20 50 61  pload Pa\n"
            f"    [Active Threat Signature: {'Malware Payload' if pdu.protocol == 'INFECT' else 'Standard Probe'}]"
        )

        details_box.insert("1.0", packet_info)
        details_box.configure(state="disabled")

        # Close Button
        ctk.CTkButton(
            self, 
            text="Close Inspector", 
            fg_color="#333333", 
            hover_color="#444444", 
            command=self.destroy
        ).pack(pady=(0, 15))
