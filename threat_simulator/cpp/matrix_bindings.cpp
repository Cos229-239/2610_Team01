#include <pybind11/pybind11.h>
#include <pybind11/numpy.h> // REQUIRED for direct NumPy integration
#include <vector>

namespace py = pybind11;

class MatrixGraph {
public:
    // Process an Adjacency Matrix directly from a 2D NumPy array
    void process_adjacency_matrix(py::array_t<int> input_matrix) {
        // Request buffer info from NumPy
        py::buffer_info buf = input_matrix.request();

        if (buf.ndim != 2) {
            throw std::runtime_error("Adjacency matrix must be 2-dimensional");
        }

        size_t rows = buf.shape[0];
        size_t cols = buf.shape[1];

        // Direct raw pointer access without copying memory
        auto ptr = static_cast<int*>(buf.ptr);

        for (size_t i = 0; i < rows; ++i) {
            for (size_t j = 0; j < cols; ++j) {
                int edge_weight = ptr[i * cols + j];
                // Perform graph calculations using raw C++ memory pointers
            }
        }
    }

    // Return a 2D NumPy array generated directly in C++
    py::array_t<int> generate_distance_matrix(size_t n) {
        // Allocate 2D buffer (n x n)
        auto result = py::array_t<int>({ n, n });
        py::buffer_info buf = result.request();
        auto ptr = static_cast<int*>(buf.ptr);

        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j < n; ++j) {
                ptr[i * n + j] = (i == j) ? 0 : static_cast<int>(i + j);
            }
        }
        return result;
    }
};

PYBIND11_MODULE(matrix_engine, m) {
    py::class_<MatrixGraph>(m, "MatrixGraph")
        .def(py::init<>())
        .def("process_adjacency_matrix", &MatrixGraph::process_adjacency_matrix)
        .def("generate_distance_matrix", &MatrixGraph::generate_distance_matrix);
}