#pragma once

#include <complex>
#include <vector>
#include <stdexcept>

#include <Eigen/Core>
#include <Eigen/Sparse>

namespace p2p_harmonic {

using Complex = std::complex<double>;
using VecC = Eigen::VectorXcd;
using MatC = Eigen::MatrixXcd;
using VecX = Eigen::VectorXd;
using MatX = Eigen::MatrixXd;
using SpMatC = Eigen::SparseMatrix<Complex>;

enum class HarmonicEnergyType { SymmDirichlet = 0, Exp_SymmDirichlet = 1, AMIPS = 2 };

enum class HarmonicSolverType {
    GradientDescent,
    Newton,
    Newton_SPDH,
    Newton_SPDH_FullEig,
    LBFGS
};

struct P2PHarmonicPrepParams {
    double cage_offset = 1e-1;
    int numVirtualVertices = 1;
    int numEnergySamples = 10000;
    double p2p_weight = 1e5;
    int numIterations = 3;
    double energy_parameter = 1.0;
    double hessianSampleRate = 0.1;
};

struct P2PHarmonicPrepInput {
    VecC cage;
    std::vector<VecC> holes;
    VecC meshVertices;  // X in MATLAB
    VecC phi;           // optional; empty => initialize from vv
    VecC psy;
    P2PHarmonicPrepParams params;
};

struct P2PHarmonicPrepResult {
    P2PHarmonicPrepParams params;
    int numDenseEvaluationSamples = 0;

    std::vector<VecC> v;
    VecC vv;
    int numVirtualVertices = 0;

    VecC energySamples;
    std::vector<int> nSamplePerCage;
    Eigen::VectorXi nextSampleInSameCage;  // 1-based indices (MATLAB compatible)

    MatC C;
    MatC D;

    VecC holeCenters;
    VecC phi;
    VecC psy;
    VecC xp2pDeform;  // XP2PDeform

    bool p2pDeformationConverged = false;
    bool nloPreprocessed = false;
    bool needsPreprocessing = true;
};

// Runtime caches built after prep (p2p_harmonic.m needsPreprocessing block).
struct P2PHarmonicRuntimeData {
    MatC D2;                         // DerivativeOfCauchyCoordinatesAtEnergySamples
    MatC E2;                         // SoDerivativeOfCauchyCoordinatesAtEnergySamples
    MatX L2;                         // Lipschitz constants per sample / basis
    VecC fillDistanceSegments;
    MatC cauchyAtP2P;                // CauchyCoordinatesAtP2Phandles (C2)

    Eigen::VectorXi p2pVertexIds;    // 1-based mesh vertex ids (MATLAB P2PVtxIds)
    VecC p2pTargets;                 // P2PCurrentPositions (complex)

    MatC phipsyIters;                // nVirt x (2 * history)
    bool nloPreprocessed = false;
    bool needsPreprocessing = true;

    MatX statsAll;  // (nIter+1) x 8
};

struct P2PHarmonicDeformInput {
    HarmonicSolverType solver = HarmonicSolverType::Newton_SPDH;
    HarmonicEnergyType energy = HarmonicEnergyType::SymmDirichlet;
    bool verboseLineSearch = false;
};

struct P2PHarmonicDeformResult {
    VecC phi;
    VecC psy;
    VecC xp2pDeform;
    VecC deformedP2PPositions;
    bool converged = false;
    MatX statsAll;
};

class P2PHarmonicPrepError : public std::runtime_error {
public:
    explicit P2PHarmonicPrepError(const std::string& msg) : std::runtime_error(msg) {}
};

HarmonicEnergyType energyTypeFromString(const std::string& name);
HarmonicSolverType solverTypeFromString(const std::string& name);
std::string toString(HarmonicEnergyType energy);
std::string toString(HarmonicSolverType solver);

}  // namespace p2p_harmonic
