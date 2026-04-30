/**
 * bounded_distortion_example.cpp
 * ==============================
 *
 * Example: Bounded Distortion Mesh Parameterization
 *
 * This example:
 *   1. Loads a triangle mesh from an OBJ file
 *   2. Computes an initial LSCM parameterization
 *   3. Refines it with bounded-distortion constraints (C = 10)
 *   4. Saves the resulting UV coordinates
 *
 * Usage:
 *   ./bounded_distortion input.obj output.obj [C] [max_iter]
 *
 * Dependencies:
 *   - Eigen 3.x (header-only)
 *   - libigl (for mesh I/O, optionally)
 *   - The bounded_distortion.h header in the same directory
 *
 * If libigl is not available, this file can also be used with a custom OBJ loader.
 */

#include "bounded_distortion.h"
#include <fstream>
#include <sstream>
#include <cassert>
#include <chrono>

// If libigl is available, use it for I/O:
#ifdef HAS_LIBIGL
  #include <igl/readOBJ.h>
  #include <igl/writeOBJ.h>
  #include <igl/boundary_loop.h>
  #include <igl/map_vertices_to_circle.h>
#endif

// ============================================================================
// Simple OBJ Reader (if libigl is not available)
// ============================================================================
#ifndef HAS_LIBIGL

bool read_obj(const std::string& filename,
              Eigen::MatrixXd& V,
              Eigen::MatrixXi& F)
{
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Cannot open: " << filename << std::endl;
        return false;
    }

    std::vector<Eigen::RowVector3d> verts;
    std::vector<Eigen::RowVector3i> faces;

    std::string line;
    while (std::getline(file, line)) {
        if (line.empty() || line[0] == '#') continue;

        std::istringstream iss(line);
        std::string type;
        iss >> type;

        if (type == "v") {
            double x, y, z;
            iss >> x >> y >> z;
            verts.emplace_back(x, y, z);
        } else if (type == "f") {
            int a, b, c;
            iss >> a >> b >> c;
            // OBJ is 1-indexed
            faces.emplace_back(a-1, b-1, c-1);
        }
    }

    if (verts.empty() || faces.empty()) {
        std::cerr << "No vertices or faces found in: " << filename << std::endl;
        return false;
    }

    V.resize(verts.size(), 3);
    for (size_t i = 0; i < verts.size(); ++i) V.row(i) = verts[i];

    F.resize(faces.size(), 3);
    for (size_t i = 0; i < faces.size(); ++i) F.row(i) = faces[i];

    return true;
}

bool write_obj(const std::string& filename,
               const Eigen::MatrixXd& V,
               const Eigen::MatrixXi& F,
               const Eigen::MatrixXd& UV)
{
    std::ofstream file(filename);
    if (!file.is_open()) return false;

    // Write 3D vertices
    for (int i = 0; i < V.rows(); ++i) {
        file << "v " << V(i,0) << " " << V(i,1) << " " << V(i,2) << "\n";
    }

    // Write UV coordinates
    for (int i = 0; i < UV.rows(); ++i) {
        file << "vt " << UV(i,0) << " " << UV(i,1) << "\n";
    }

    // Write faces with UV indices
    for (int i = 0; i < F.rows(); ++i) {
        file << "f "
             << F(i,0)+1 << "/" << F(i,0)+1 << " "
             << F(i,1)+1 << "/" << F(i,1)+1 << " "
             << F(i,2)+1 << "/" << F(i,2)+1 << "\n";
    }

    return true;
}

// Find boundary loop (simple: vertices incident to edges appearing only once)
void boundary_loop(const Eigen::MatrixXi& F,
                   Eigen::VectorXi& bnd)
{
    const int nV = F.maxCoeff() + 1;
    std::map<std::pair<int,int>, int> edge_count;

    for (int j = 0; j < F.rows(); ++j) {
        for (int k = 0; k < 3; ++k) {
            int a = F(j, k);
            int b = F(j, (k+1)%3);
            if (a > b) std::swap(a, b);
            edge_count[{a, b}]++;
        }
    }

    std::vector<int> bnd_vec;
    for (auto& [edge, count] : edge_count) {
        if (count == 1) {
            bnd_vec.push_back(edge.first);
            bnd_vec.push_back(edge.second);
        }
    }

    // Deduplicate and order
    std::sort(bnd_vec.begin(), bnd_vec.end());
    bnd_vec.erase(std::unique(bnd_vec.begin(), bnd_vec.end()), bnd_vec.end());

    bnd.resize(bnd_vec.size());
    for (size_t i = 0; i < bnd_vec.size(); ++i) bnd(i) = bnd_vec[i];
}

// Map boundary to circle
void map_vertices_to_circle(const Eigen::MatrixXd& V,
                            const Eigen::VectorXi& bnd,
                            Eigen::MatrixXd& bnd_uv)
{
    const int nB = bnd.size();
    bnd_uv.resize(nB, 2);

    // Simple: place on unit circle in order
    for (int k = 0; k < nB; ++k) {
        double angle = 2.0 * M_PI * k / nB;
        bnd_uv(k, 0) = std::cos(angle);
        bnd_uv(k, 1) = std::sin(angle);
    }
}

#endif  // HAS_LIBIGL

// ============================================================================
// Main
// ============================================================================

int main(int argc, char* argv[])
{
    if (argc < 3) {
        std::cout << "Usage: " << argv[0]
                  << " input.obj output.obj [C=10.0] [max_iter=50]" << std::endl;
        std::cout << "  C          - distortion bound (sigma1/sigma2 <= C)" << std::endl;
        std::cout << "  max_iter   - maximum local-global iterations" << std::endl;
        return 1;
    }

    std::string input_file  = argv[1];
    std::string output_file = argv[2];
    double C        = (argc > 3) ? std::stod(argv[3]) : 10.0;
    int max_iter    = (argc > 4) ? std::stoi(argv[4]) : 50;

    std::cout << "=== Bounded Distortion Parameterization ===" << std::endl;
    std::cout << "Input:      " << input_file << std::endl;
    std::cout << "Output:     " << output_file << std::endl;
    std::cout << "C (bound):  " << C << std::endl;
    std::cout << "Max iter:   " << max_iter << std::endl;

    // --- Load mesh ---
    bdm::MatrixXd V, bnd_uv;
    bdm::MatrixXi F;
    bdm::VectorXi bnd;

#ifdef HAS_LIBIGL
    if (!igl::readOBJ(input_file, V, F)) {
        std::cerr << "Failed to read: " << input_file << std::endl;
        return 1;
    }
    igl::boundary_loop(F, bnd);
    igl::map_vertices_to_circle(V, bnd, bnd_uv);
#else
    if (!read_obj(input_file, V, F)) {
        std::cerr << "Failed to read: " << input_file << std::endl;
        return 1;
    }
    boundary_loop(F, bnd);
    map_vertices_to_circle(V, bnd, bnd_uv);
#endif

    std::cout << "Vertices:   " << V.rows() << std::endl;
    std::cout << "Faces:      " << F.rows() << std::endl;
    std::cout << "Boundary:   " << bnd.size() << std::endl;

    // --- Compute initial LSCM map ---
    std::cout << "\nComputing LSCM initial map..." << std::endl;
    bdm::MatrixXd U_init;
    bdm::lscm_initial_map(V, F, bnd, bnd_uv, U_init);

    // Check initial distortion
    {
        std::vector<bdm::Eigen::Matrix2d> Pinv;
        bdm::compute_local_frames(V, F, Pinv);
        std::vector<bdm::Eigen::Matrix2d> J_init;
        bdm::compute_jacobians(U_init, F, Pinv, J_init);

        double max_K, avg_K;
        bdm::VectorXd face_areas(F.rows());
        for (int j = 0; j < F.rows(); ++j) {
            face_areas(j) = 0.5 * (V.row(F(j,1)) - V.row(F(j,0)))
                                   .cross(V.row(F(j,2)) - V.row(F(j,0))).norm();
        }
        bdm::compute_distortion_stats(J_init, max_K, avg_K, &face_areas);
        std::cout << "Initial LSCM - max_K: " << max_K << ", avg_K: " << avg_K << std::endl;
    }

    // --- Bounded distortion optimization ---
    std::cout << "\nRunning bounded distortion optimization..." << std::endl;

    bdm::BDOptions options;
    options.C = C;
    options.max_iter = max_iter;
    options.verbose = true;
    options.use_arap = false;  // Use LSCM energy

    bdm::BDResult result;

    auto start = std::chrono::high_resolution_clock::now();
    bdm::bounded_distortion_map(V, F, bnd, bnd_uv, U_init, options, result);
    auto end = std::chrono::high_resolution_clock::now();

    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    std::cout << "\nTime: " << duration << " ms" << std::endl;
    std::cout << "Iterations: " << result.iterations << std::endl;
    std::cout << "Converged:  " << (result.converged ? "yes" : "no") << std::endl;

    // --- Results ---
    if (!result.energy_history.empty()) {
        std::cout << "\nFinal energy:           " << result.energy_history.back() << std::endl;
        std::cout << "Final max distortion:   " << result.max_distortion_history.back() << std::endl;
        std::cout << "Final avg distortion:   " << result.avg_distortion_history.back() << std::endl;
    }

    // --- Save ---
#ifdef HAS_LIBIGL
    igl::writeOBJ(output_file, V, F, Eigen::MatrixXd(), Eigen::MatrixXd(),
                  result.U, F);
#else
    write_obj(output_file, V, F, result.U);
#endif

    std::cout << "\nSaved to: " << output_file << std::endl;

    return 0;
}
