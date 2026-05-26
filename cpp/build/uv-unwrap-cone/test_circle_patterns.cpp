/**
 * Native test: CirclePatterns with Mosek QP (angle optimization) + Newton radii.
 * Usage: test_circle_patterns.exe model.obj [output.obj]
 */

#include <iostream>
#include <chrono>
#include <string>
#include "Mesh.h"
#include "CirclePatterns.h"

int main(int argc, char** argv)
{
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " model.obj [output.obj]\n";
        return 1;
    }

    Mesh mesh;
    if (!mesh.read(argv[1])) {
        std::cerr << "Failed to read mesh: " << argv[1] << "\n";
        return 1;
    }

    std::cout << "Vertices: " << mesh.vertices.size()
              << "  Faces: " << mesh.faces.size() << "\n";

    mesh.delaunayize();

    auto t0 = std::chrono::high_resolution_clock::now();
    CirclePatterns cp(mesh, NEWTON);
    cp.parameterize();
    auto t1 = std::chrono::high_resolution_clock::now();

    const double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
    const double qc = cp.computeQcError();
    std::cout << "CirclePatterns (Mosek + Newton) done in " << ms << " ms\n";
    std::cout << "QC error: " << qc << "\n";

    if (qc >= 1e5) {
        std::cerr << "Parameterization likely failed (QC error sentinel).\n";
        return 2;
    }

    const std::string out = (argc >= 3) ? argv[2] : "cp_output.obj";
    if (!mesh.write(out)) {
        std::cerr << "Failed to write: " << out << "\n";
        return 3;
    }
    std::cout << "Wrote UV mesh: " << out << "\n";
    return 0;
}
