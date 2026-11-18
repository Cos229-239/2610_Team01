import json
import csv
import os
from datetime import datetime

def export_simulation_summary(graph, filename=None):
    """
    Reads the final graph and simulation state, exporting
    a clean JSON report including manual override audit logs.
    """
    nodes_list = getattr(graph, "nodes", [])
    total_nodes = len(nodes_list)
    infected_nodes = sum(1 for node in nodes_list if getattr(node, "status", "") == "INFECTED")
    healthy_nodes = total_nodes - infected_nodes

    # Collect any manual quarantine override logs recorded on the graph
    override_logs = getattr(graph, "manual_override_logs", [])

    report_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_nodes": total_nodes,
        "infected_nodes": infected_nodes,
        "healthy_nodes": healthy_nodes,
        "containment_successful": infected_nodes == 0,
        "manual_override_audit_logs": override_logs,
        "nodes": [
            {
                "id": getattr(node, "id", i),
                "status": getattr(node, "status", "HEALTHY"),
                "is_patient_zero": getattr(node, "is_patient_zero", False),
            }
            for i, node in enumerate(nodes_list)
        ]
    }

    # Create reports directory at project root
    os.makedirs("reports", exist_ok=True)
    
    # Auto-generate a timestamped filename if none is explicitly provided
    if not filename or filename == "simulation_report.json":
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simulation_report_{timestamp_str}.json"
        
    filepath = os.path.join("reports", filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)
        
    return filepath


def export_graph_to_csv(graph, output_dir="reports/csv") -> str:
    """Exports network graph nodes and edges into separate CSV files."""
    os.makedirs(output_dir, exist_ok=True)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nodes_filepath = os.path.join(output_dir, f"network_nodes_{timestamp}.csv")
    edges_filepath = os.path.join(output_dir, f"network_edges_{timestamp}.csv")
    
    nodes_list = getattr(graph, "nodes", [])
    edges_list = getattr(graph, "edges", [])
    
    # 1. Export Nodes
    with open(nodes_filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Index", "ID", "Node_Type", "IP_Address", "Subnet", "Status", "Is_Patient_Zero", "X", "Y"])
        for idx, node in enumerate(nodes_list):
            writer.writerow([
                idx,
                getattr(node, "id", f"Node-{idx}"),
                getattr(node, "node_type", "PC"),
                getattr(node, "ip_address", ""),
                getattr(node, "subnet", ""),
                getattr(node, "status", "HEALTHY"),
                getattr(node, "is_patient_zero", False),
                getattr(node, "x", 0.0),
                getattr(node, "y", 0.0)
            ])
            
    # 2. Export Edges
    with open(edges_filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Source_Index", "Target_Index", "Status", "Is_Firewall", "Password", "Crack_Progress"])
        for edge in edges_list:
            writer.writerow([
                getattr(edge, "u", 0),
                getattr(edge, "v", 0),
                getattr(edge, "status", "HEALTHY"),
                getattr(edge, "is_firewall", False),
                getattr(edge, "password", ""),
                getattr(edge, "crack_progress", 0.0)
            ])
            
    return os.path.abspath(output_dir)


# --- Quick Test Classes and Execution ---
class MockNode:
    def __init__(self, id, status, is_patient_zero=False):
        self.id = id
        self.status = status
        self.is_patient_zero = is_patient_zero

class MockEdge:
    def __init__(self, u, v, status="HEALTHY", is_firewall=False, password="", crack_progress=0.0):
        self.u = u
        self.v = v
        self.status = status
        self.is_firewall = is_firewall
        self.password = password
        self.crack_progress = crack_progress

class MockGraph:
    def __init__(self, nodes, edges=None, manual_override_logs=None):
        self.nodes = nodes
        self.edges = edges or []
        self.manual_override_logs = manual_override_logs or []

if __name__ == "__main__":
    try:
        print("Starting test export with audit logs and CSV...")
        test_nodes = [
            MockNode(id="PC-1", status="HEALTHY", is_patient_zero=False),
            MockNode(id="Server-1", status="INFECTED", is_patient_zero=True),
            MockNode(id="Router-1", status="HEALTHY", is_patient_zero=False)
        ]
        
        test_edges = [
            MockEdge(u=0, v=1, status="INFECTED", is_firewall=False),
            MockEdge(u=1, v=2, status="HEALTHY", is_firewall=True, password="abc", crack_progress=0.5)
        ]
        
        sample_logs = [
            {
                "edge_index": 0,
                "node_u": 0,
                "node_v": 1,
                "action": "MANUAL_QUARANTINE_OVERRIDE",
                "status_restored": "HEALTHY"
            }
        ]
        
        test_graph = MockGraph(nodes=test_nodes, edges=test_edges, manual_override_logs=sample_logs)
        
        json_path = export_simulation_summary(test_graph)
        csv_dir = export_graph_to_csv(test_graph)
        
        print(f"SUCCESS! JSON Report created at: {os.path.abspath(json_path)}")
        print(f"SUCCESS! CSV Reports directory created at: {csv_dir}")
    except Exception as e:
        print(f"ERROR caught during export: {e}")