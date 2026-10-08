#include <pybind11/pybind11.h>
#include <pybind11/stl.h>  // REQUIRED: Enables STL <-> Python conversions
#include <vector>
#include <unordered_map>
#include <string>

namespace py = pybind11;

struct Node {
    std::string id;
    std::string status;
    double threat_value;
};

class GraphManager {
private:
    // Adjacency List: Map node ID -> List of neighbor Node IDs
    std::unordered_map<std::string, std::vector<std::string>> adj_list;
    std::unordered_map<std::string, Node> nodes;

public:
    // Accept adjacency list from Python dict[str, list[str]]
    void set_adjacency_list(const std::unordered_map<std::string, std::vector<std::string>>& graph) {
        adj_list = graph;
    }

    // Return adjacency list back to Python as a dict
    std::unordered_map<std::string, std::vector<std::string>> get_adjacency_list() const {
        return adj_list;
    }

    // Pass custom structs via vectors (Python list of objects/dicts)
    void add_nodes(const std::vector<Node>& node_list) {
        for (const auto& node : node_list) {
            nodes[node.id] = node;
        }
    }

    std::vector<Node> get_all_nodes() const {
        std::vector<Node> result;
        for (const auto& [id, node] : nodes) {
            result.push_back(node);
        }
        return result;
    }
};

PYBIND11_MODULE(network_engine, m) {
    py::class_<Node>(m, "Node")
        .def(py::init<std::string, std::string, double>(),
            py::arg("id"), py::arg("status") = "HEALTHY", py::arg("threat_value") = 0.0)
        .def_readwrite("id", &Node::id)
        .def_readwrite("status", &Node::status)
        .def_readwrite("threat_value", &Node::threat_value);

    py::class_<GraphManager>(m, "GraphManager")
        .def(py::init<>())
        .def("set_adjacency_list", &GraphManager::set_adjacency_list)
        .def("get_adjacency_list", &GraphManager::get_adjacency_list)
        .def("add_nodes", &GraphManager::add_nodes)
        .def("get_all_nodes", &GraphManager::get_all_nodes);
}