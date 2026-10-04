#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <algorithm>

namespace py = pybind11;

py::dict run_step_telemetry(int step_count, float infection_rate, float defense_strength) {
    py::dict metrics;
    
    int total_nodes = 100;
    
    int infected_nodes = std::min(total_nodes, static_cast<int>(step_count * infection_rate * 10));
    int active_defenses = std::min(total_nodes, static_cast<int>(step_count * defense_strength * 5));
    
    float threat_level = (float)infected_nodes / total_nodes * 100.0f;

    metrics["step"] = step_count;
    metrics["total_nodes"] = total_nodes;
    metrics["infected_nodes"] = infected_nodes;
    metrics["active_defenses"] = active_defenses;
    metrics["threat_level_pct"] = threat_level;
    metrics["status"] = (threat_level > 75.0f) ? "CRITICAL OUTBREAK" : "CONTAINMENT ACTIVE";

    return metrics;
}

PYBIND11_MODULE(sim_engine, m) {
    m.doc() = "C++ High-Performance Simulation Engine";
    m.def("run_step_telemetry", &run_step_telemetry, 
          "Executes step and returns structured telemetry data based on dynamic inputs", 
          py::arg("step_count"), py::arg("infection_rate"), py::arg("defense_strength"));
}
