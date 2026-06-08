#include "P2PHarmonicPrep.hpp"

#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

namespace {

using namespace p2p_harmonic;

VecC readComplexVector(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("Cannot open " + path);

    int n = 0;
    in >> n;
    VecC v(n);
    for (int i = 0; i < n; ++i) {
        double re = 0.0, im = 0.0;
        in >> re >> im;
        v[i] = Complex(re, im);
    }
    return v;
}

std::vector<VecC> readComplexCell(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("Cannot open " + path);

    int nCells = 0;
    in >> nCells;
    std::vector<VecC> cells(nCells);
    for (int c = 0; c < nCells; ++c) {
        int n = 0;
        in >> n;
        cells[c].resize(n);
        for (int i = 0; i < n; ++i) {
            double re = 0.0, im = 0.0;
            in >> re >> im;
            cells[c][i] = Complex(re, im);
        }
    }
    return cells;
}

struct ExpectedMetrics {
    int numVirtualVertices = 0;
    int energySamples = 0;
    int cRows = 0;
    int cCols = 0;
    int dRows = 0;
    int dCols = 0;
    double xp2pDeformNorm = 0.0;
};

ExpectedMetrics readExpected(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("Cannot open " + path);

    ExpectedMetrics e;
    std::string key;
    while (in >> key) {
        if (key == "numVirtualVertices") in >> e.numVirtualVertices;
        else if (key == "energySamples") in >> e.energySamples;
        else if (key == "C") in >> e.cRows >> e.cCols;
        else if (key == "D") in >> e.dRows >> e.dCols;
        else if (key == "XP2PDeformNorm") in >> e.xp2pDeformNorm;
    }
    return e;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const std::string dataset = argc > 1 ? argv[1] : "annulus";
        const std::string base = std::string("testdata/") + dataset + "_";

        P2PHarmonicPrepInput input;
        input.cage = readComplexVector(base + "cage.txt");
        input.holes = readComplexCell(base + "holes.txt");
        input.meshVertices = readComplexVector(base + "X.txt");
        input.params.numEnergySamples = 1000;
        input.params.numVirtualVertices = 79;
        input.params.cage_offset = 0.1;

        const ExpectedMetrics expected = readExpected(base + "expected.txt");
        const P2PHarmonicPrepResult result = p2pHarmonicPrep(input);

        const double xp2pNorm = result.xp2pDeform.norm();
        const bool ok =
            result.numVirtualVertices == expected.numVirtualVertices &&
            result.energySamples.size() == expected.energySamples &&
            result.C.rows() == expected.cRows && result.C.cols() == expected.cCols &&
            result.D.rows() == expected.dRows && result.D.cols() == expected.dCols &&
            std::abs(xp2pNorm - expected.xp2pDeformNorm) < 1e-6 * std::max(1.0, expected.xp2pDeformNorm);

        std::cout << "Dataset: " << dataset << '\n'
                  << "  numVirtualVertices = " << result.numVirtualVertices
                  << " (expected " << expected.numVirtualVertices << ")\n"
                  << "  energySamples      = " << result.energySamples.size()
                  << " (expected " << expected.energySamples << ")\n"
                  << "  C                  = " << result.C.rows() << " x " << result.C.cols()
                  << " (expected " << expected.cRows << " x " << expected.cCols << ")\n"
                  << "  D                  = " << result.D.rows() << " x " << result.D.cols()
                  << " (expected " << expected.dRows << " x " << expected.dCols << ")\n"
                  << "  XP2PDeform norm    = " << xp2pNorm
                  << " (expected " << expected.xp2pDeformNorm << ")\n"
                  << (ok ? "PASS\n" : "FAIL\n");

        return ok ? 0 : 1;
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << '\n';
        return 1;
    }
}
