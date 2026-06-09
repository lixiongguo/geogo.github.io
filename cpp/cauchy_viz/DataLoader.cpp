#include "DataLoader.hpp"

#include <filesystem>
#include <fstream>

namespace fs = std::filesystem;

namespace {

p2p_harmonic::VecC readComplexLoop(std::ifstream& in) {
    int n = 0;
    in >> n;
    p2p_harmonic::VecC v(n);
    for (int i = 0; i < n; ++i) {
        double re = 0, im = 0;
        in >> re >> im;
        v[i] = p2p_harmonic::Complex(re, im);
    }
    return v;
}

p2p_harmonic::VecC readComplexVectorFile(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("Cannot open " + path);
    int n = 0;
    in >> n;
    p2p_harmonic::VecC v(n);
    for (int i = 0; i < n; ++i) {
        double re = 0, im = 0;
        in >> re >> im;
        v[i] = p2p_harmonic::Complex(re, im);
    }
    return v;
}

std::vector<p2p_harmonic::VecC> readComplexCellFile(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("Cannot open " + path);
    int nCells = 0;
    in >> nCells;
    std::vector<p2p_harmonic::VecC> cells(static_cast<std::size_t>(nCells));
    for (int c = 0; c < nCells; ++c) {
        int n = 0;
        in >> n;
        cells[static_cast<std::size_t>(c)].resize(n);
        for (int i = 0; i < n; ++i) {
            double re = 0, im = 0;
            in >> re >> im;
            cells[static_cast<std::size_t>(c)][i] = p2p_harmonic::Complex(re, im);
        }
    }
    return cells;
}

}  // namespace

bool loadMeshText(const std::string& path, MeshData& mesh) {
    std::ifstream in(path);
    if (!in) return false;

    int nv = 0, nf = 0;
    in >> nv >> nf;
    mesh.vertices.resize(nv, 2);
    for (int i = 0; i < nv; ++i) {
        double x = 0, y = 0;
        in >> x >> y;
        mesh.vertices(i, 0) = static_cast<float>(x);
        mesh.vertices(i, 1) = static_cast<float>(y);
    }
    mesh.faces.resize(nf, 3);
    for (int i = 0; i < nf; ++i) {
        int a = 0, b = 0, c = 0;
        in >> a >> b >> c;
        mesh.faces(i, 0) = a;
        mesh.faces(i, 1) = b;
        mesh.faces(i, 2) = c;
    }
    return true;
}

bool loadBoundaryText(const std::string& path, BoundaryData& boundary) {
    std::ifstream in(path);
    if (!in) return false;
    boundary.cage = readComplexLoop(in);
    int nHoles = 0;
    in >> nHoles;
    boundary.holes.resize(static_cast<std::size_t>(nHoles));
    for (int h = 0; h < nHoles; ++h) boundary.holes[static_cast<std::size_t>(h)] = readComplexLoop(in);
    return true;
}

bool loadParamsText(const std::string& path, p2p_harmonic::P2PHarmonicPrepParams& params) {
    std::ifstream in(path);
    if (!in) return false;
    std::string key;
    while (in >> key) {
        if (key == "numEnergySamples") in >> params.numEnergySamples;
        else if (key == "numVirtualVertices") in >> params.numVirtualVertices;
        else if (key == "cage_offset") in >> params.cage_offset;
        else if (key == "p2p_weight") in >> params.p2p_weight;
        else if (key == "numIterations") in >> params.numIterations;
        else if (key == "energy_parameter") in >> params.energy_parameter;
        else if (key == "hessianSampleRate") in >> params.hessianSampleRate;
    }
    return true;
}

bool loadTestdata(const std::string& prefix, MeshData& mesh, BoundaryData& boundary) {
    try {
        boundary.cage = readComplexVectorFile(prefix + "_cage.txt");
        const auto holes = readComplexCellFile(prefix + "_holes.txt");
        boundary.holes = holes;
        const p2p_harmonic::VecC X = readComplexVectorFile(prefix + "_X.txt");

        boundary.params = p2p_harmonic::P2PHarmonicPrepParams{};
        boundary.params.numEnergySamples = 1000;
        boundary.params.numVirtualVertices = 79;
        boundary.params.cage_offset = 0.1;

        mesh.vertices.resize(X.size(), 2);
        for (Eigen::Index i = 0; i < X.size(); ++i) {
            mesh.vertices(i, 0) = static_cast<float>(X[i].real());
            mesh.vertices(i, 1) = static_cast<float>(X[i].imag());
        }
        mesh.faces.resize(0, 3);
        return true;
    } catch (...) {
        return false;
    }
}

bool loadViewerDataset(const std::string& directory, MeshData& mesh, BoundaryData& boundary) {
    const std::string meshPath = directory + "/mesh.txt";
    const std::string boundaryPath = directory + "/boundary.txt";
    const std::string paramsPath = directory + "/params.txt";
    if (!loadMeshText(meshPath, mesh)) return false;
    if (!loadBoundaryText(boundaryPath, boundary)) return false;
    loadParamsText(paramsPath, boundary.params);
    return true;
}

std::string findRepoRoot(int argc, char** argv) {
    std::vector<fs::path> candidates;
    if (argc > 1) candidates.emplace_back(argv[1]);
    candidates.emplace_back(".");
    candidates.emplace_back("..");
    candidates.emplace_back("../..");
    candidates.emplace_back("../../..");
    if (argc > 0 && argv[0]) {
        const fs::path exe = fs::absolute(fs::path(argv[0])).parent_path();
        candidates.push_back(exe);
        candidates.push_back(exe / "..");
        candidates.push_back(exe / "../..");
        candidates.push_back(exe / "../../..");
    }

    for (const fs::path& c : candidates) {
        if (fs::exists(c / "data" / "annulus" / "mesh.txt")) return fs::absolute(c).string();
        if (fs::exists(c / "cpp" / "p2p_harmonic" / "testdata" / "annulus_cage.txt"))
            return fs::absolute(c).string();
    }
    return ".";
}

p2p_harmonic::VecC meshToComplex(const Eigen::Matrix<float, Eigen::Dynamic, 2, Eigen::RowMajor>& xy) {
    p2p_harmonic::VecC out(xy.rows());
    for (Eigen::Index i = 0; i < xy.rows(); ++i) out[i] = p2p_harmonic::Complex(xy(i, 0), xy(i, 1));
    return out;
}
