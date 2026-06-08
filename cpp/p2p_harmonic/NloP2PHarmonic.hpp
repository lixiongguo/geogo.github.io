#pragma once

#include "P2PHarmonicTypes.hpp"

namespace p2p_harmonic {

struct NloP2PHarmonicInput {
    const MatC& D2;
    const MatC& C2;
    VecC bP2P;
    double lambda = 1e5;
    MatC phipsyIters;
    double energyParameter = 1.0;
    int numIterations = 3;
    HarmonicSolverType solver = HarmonicSolverType::Newton_SPDH;
    HarmonicEnergyType energyType = HarmonicEnergyType::SymmDirichlet;
    const Eigen::VectorXi& nextSampleInSameCage;
    double hessianSampleRate = 0.1;
    const VecC& fillDistanceSegments;
    const std::vector<VecC>& v;
    const MatC& E2;
    const MatX& L2;
    bool verboseLineSearch = false;
};

struct NloP2PHarmonicResult {
    MatC phipsyIters;
    MatX statsAll;
};

NloP2PHarmonicResult nloP2PHarmonic(const NloP2PHarmonicInput& input);

}  // namespace p2p_harmonic
