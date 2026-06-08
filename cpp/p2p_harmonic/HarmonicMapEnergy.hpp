#pragma once

#include "P2PHarmonicTypes.hpp"

namespace p2p_harmonic {

struct HarmonicMapEnergyResult {
    double energy = 0.0;
    VecC gradient;   // 2n complex stacked [g_phi; g_psy]
    MatX hessian;    // 4n x 4n real
};

HarmonicMapEnergyResult harmonicMapIsometryicEnergy(const MatC& D, const VecC& phi, const VecC& psy,
                                                    bool spdHessian, HarmonicEnergyType energyType,
                                                    double energyParam);

}  // namespace p2p_harmonic
