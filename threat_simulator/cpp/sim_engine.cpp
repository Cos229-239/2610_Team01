#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>

namespace py = pybind11;

class SimulationEngine {
public:
    float defense_power = 0.5f;

    SimulationEngine() {}

    py::dict deploy_federal_intervention(float defense_val, int active_count) {
        defense_power = defense_val;
        
        py::dict metrics;
        metrics["message"] = "Federal intervention successfully deployed. Network isolated across " + std::to_string(active_count) + " nodes.";
        metrics["status"] = "SECURED";
        metrics["defense_power"] = defense_power;
        return metrics;
    }
};

PYBIND11_MODULE(sim_engine, m) {
    m.doc() = "C++ Simulation Engine Backend for Threat Simulator";

    py::class_<SimulationEngine>(m, "SimulationEngine")
        .def(py::init<>())
        .def_readwrite("defense_power", &SimulationEngine::defense_power)
        .def("deploy_federal_intervention", &SimulationEngine::deploy_federal_intervention,
             py::arg("defense_power"), py::arg("active_count"));
}