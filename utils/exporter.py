import json
import os
from datetime import datetime

def export_simulation_summary(graph, filename=None):
    """
    Reads the final graph and simulation state, exporting
    a clean JSON report without touching any UI code.
    """
    nodes_list = getattr(graph, "nodes", [])
    total_nodes = len(nodes_list)
    infected_nodes = sum(1 for node in nodes_list if getattr(node, "status", "") == "INFECTED")
    healthy_nodes = total_nodes - infected_nodes

    report_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_nodes": total_nodes,
        "infected_nodes": infected_nodes,
        "healthy_nodes": healthy_nodes,
        "containment_successful": infected_nodes == 0,
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
    
    with open(filepath, "w") as f:
        json.dump(report_data, f, indent=4)
        
    return filepath

# --- Quick Test Classes and Execution ---
class MockNode:
    def __init__(self, id, status, is_patient_zero=False):
        self.id = id
        self.status = status
        self.is_patient_zero = is_patient_zero

class MockGraph:
    def __init__(self, nodes):
        self.nodes = nodes

if __name__ == "__main__":
    try:
        print("Starting test export...")
        test_nodes = [
            MockNode(id=1, status="HEALTHY", is_patient_zero=False),
            MockNode(id=2, status="INFECTED", is_patient_zero=True),
            MockNode(id=3, status="HEALTHY", is_patient_zero=False)
        ]
        test_graph = MockGraph(nodes=test_nodes)
        
        path = export_simulation_summary(test_graph)
        print(f"SUCCESS! File created at absolute path: {os.path.abspath(path)}")
    except Exception as e:
        print(f"ERROR caught during export: {e}")