#include "engine.hpp"
#include <algorithm>

SimulationEngine::SimulationEngine() : current_step_(0) {}

void SimulationEngine::initialize_network(int num_nodes) {
    nodes_.clear();
    current_step_ = 0;
    for (int i = 1; i <= num_nodes; ++i) {
        std::string id = "NODE-0" + std::to_string(i);
        nodes_[id] = Node{
            id,
            "10.0.0." + std::to_string(i),
            (i % 2 == 0) ? "BlackArch Linux" : "Arch Linux",
            (i == 2) ? "INFECTED" : "HEALTHY",
            (i == 2) ? 88.0 : 5.0,
            true,
            false
        };
    }
}

void SimulationEngine::step(double infection_rate, double defense_power) {
    current_step_++;
    for (auto& [id, node] : nodes_) {
        if (node.isolated) continue;
        
        if (node.status == "INFECTED") {
            node.threat_level = std::min(100.0, node.threat_level + (5.0 * infection_rate));
        } else {
            node.threat_level = std::max(0.0, node.threat_level - (2.0 * defense_power));
        }
    }
}

void SimulationEngine::isolate_node(const std::string& node_id) {
    if (nodes_.count(node_id)) {
        nodes_[node_id].isolated = true;
        nodes_[node_id].status = "ISOLATED";
    }
}

int SimulationEngine::get_infected_count() const {
    int count = 0;
    for (const auto& [id, node] : nodes_) {
        if (node.status == "INFECTED") count++;
    }
    return count;
}

double SimulationEngine::get_network_threat_pct() const {
    if (nodes_.empty()) return 0.0;
    double total = 0.0;
    for (const auto& [id, node] : nodes_) {
        total += node.threat_level;
    }
    return total / nodes_.size();
}
