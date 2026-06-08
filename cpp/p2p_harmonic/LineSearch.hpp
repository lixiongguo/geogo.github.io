#pragma once

#include "P2PHarmonicTypes.hpp"

namespace p2p_harmonic {

double maxtForPhiPsy(const Complex& fz, const Complex& gz, const Complex& dfz, const Complex& dgz);

double lineSearchLocallyInjectiveHarmonicMap(const MatC& phipsy, const MatC& dpp, const MatC& fzgz0,
                                             const MatC& dfzgz, double lsT, const VecC& fillDistanceSegments,
                                             const std::vector<VecC>& v, const MatC& E2, const MatX& L2,
                                             const Eigen::VectorXi& nextSampleInSameCage, bool verbose = false);

}  // namespace p2p_harmonic
