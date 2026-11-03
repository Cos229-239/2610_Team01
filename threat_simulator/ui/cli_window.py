import customtkinter as ctk
from typing import Dict, Any, Callable


class CiscoCLITerminal(ctk.CTkToplevel):
    def __init__(self, parent, node_data: Dict[str, Any], execute_cmd_cb: Callable[[str, str], str]):
        super().__init__(parent)
        self.node_id = node_data.get("id", "Node")
        self.ip_address = node_data.get("ip_address", "0.0.0.0")
        self.subnet = node_data.get("subnet", "255.255.255.0")
        self.node_type = node_data.get("node_type", "Router")
        self.execute_cmd_cb = execute_cmd_cb

        # Window Setup
        self.title(f"Terminal - {self.node_id} ({self.node_type})")
        self.geometry("640x420")
        self.resizable(True, True)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        # Terminal Header
        self.prompt_symbol = "Router#" if self.node_type in ["Router", "Switch", "Firewall"] else "C:\\>"

        # Console Text Area
        self.console = ctk.CTkTextbox(
            self,
            font=("Consolas", 12),
            fg_color="#0D1117",
            text_color="#00FF66",
            wrap="word"
        )
        self.console.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        # Initial Banner Output
        self.console.insert("end", f"Cisco IOS Software, {self.node_type} Technical Support\n")
        self.console.insert("end", f"Hardware ID: {self.node_id} | IP: {self.ip_address} | Subnet: {self.subnet}\n")
        self.console.insert("end", "Type 'help' or '?' for available CLI commands.\n\n")
        self.console.insert("end", f"{self.prompt_symbol} ")

        # Entry Input Bar Frame
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(input_frame, text="CLI Input:", font=("Consolas", 11, "bold")).pack(side="left", padx=(0, 5))

        self.entry = ctk.CTkEntry(
            input_frame,
            font=("Consolas", 12),
            placeholder_text="Enter command (e.g., ping 192.168.1.1)..."
        )
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self._on_submit)
        self.entry.focus_set()

    def _on_submit(self, event=None):
        cmd_str = self.entry.get().strip()
        self.entry.delete(0, "end")

        if not cmd_str:
            return

        self.console.insert("end", f"{cmd_str}\n")
        
        # Local Command Processing & Callback Execution
        output = self._process_command(cmd_str)
        if output:
            self.console.insert("end", f"{output}\n")

        self.console.insert("end", f"\n{self.prompt_symbol} ")
        self.console.see("end")

    def _process_command(self, cmd_str: str) -> str:
        tokens = cmd_str.split()
        base_cmd = tokens[0].lower()

        if base_cmd in ["help", "?"]:
            return (
                "Supported Commands:\n"
                "  ping <ip>                   - Send ICMP Echo Request\n"
                "  show ip interface brief     - Display local interface IP configuration\n"
                "  show ip route               - Display Routing Table\n"
                "  show mac-address-table      - Display Layer-2 Switching CAM Table\n"
                "  ipconfig / show ip          - Display Node IP Configuration\n"
                "  clear                       - Clear console screen"
            )

        if base_cmd == "clear":
            self.console.delete("1.0", "end")
            return ""

        if base_cmd in ["ipconfig", "show ip"]:
            return f"Interface FastEthernet0/0\n  IP Address: {self.ip_address}\n  Subnet Mask: {self.subnet}"

        # Delegate network-wide commands (e.g. ping execution) to callback
        return self.execute_cmd_cb(self.node_id, cmd_str)