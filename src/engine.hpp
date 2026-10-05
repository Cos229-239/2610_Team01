#pragma once
#include <string>
#include <vector>
#include <map>

struct Node {
    std::string id;
    std::string ip;
    std::string os;
    std::string status; // "HEALTHY", "INFECTED", "ISOLATED"
    double threat_level;
    bool firewall_active;
    bool isolated;
};

class SimulationEngine {
public:
    SimulationEngine();
    void initialize_network(int num_nodes);
    void step(double infection_rate, double defense_power);
    void isolate_node(const std::string& node_id);
    
    int get_step_count() const { return current_step_; }
    int get_infected_count() const;
    int get_total_nodes() const { return static_cast<int>(nodes_.size()); }
    double get_network_threat_pct() const;

private:
    int current_step_;
    std::map<std::string, Node> nodes_;
};
