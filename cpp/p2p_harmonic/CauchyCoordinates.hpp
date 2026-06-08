#pragma once

#include "P2PHarmonicTypes.hpp"

namespace p2p_harmonic {

MatC cauchyCoordinates(const std::vector<VecC>& cage, const VecC& z, const VecC& holeCenters);

MatC cauchyCoordinatesSingle(const VecC& cage, const VecC& z);

MatC derivativesOfCauchyCoord(const std::vector<VecC>& cage, const VecC& z, const VecC& holeCenters);

MatC derivativesOfCauchyCoordSingle(const VecC& cage, const VecC& z);

MatC secondDerivativesOfCauchyCoord(const std::vector<VecC>& cage, const VecC& z, const VecC& holeCenters);

MatC secondDerivativesOfCauchyCoordSingle(const VecC& cage, const VecC& z);

void derivativesOfCauchyCoordWithSecond(const std::vector<VecC>& cage, const VecC& z, const VecC& holeCenters,
                                        MatC& D, MatC& E);

}  // namespace p2p_harmonic
