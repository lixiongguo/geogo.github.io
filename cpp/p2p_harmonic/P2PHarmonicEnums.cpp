#include "P2PHarmonicTypes.hpp"

#include <algorithm>
#include <cctype>

namespace p2p_harmonic {
namespace {

std::string lower(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
    return s;
}

}  // namespace

HarmonicEnergyType energyTypeFromString(const std::string& name) {
    const std::string s = lower(name);
    if (s == "exp_symmdirichlet") return HarmonicEnergyType::Exp_SymmDirichlet;
    if (s == "amips") return HarmonicEnergyType::AMIPS;
    return HarmonicEnergyType::SymmDirichlet;
}

HarmonicSolverType solverTypeFromString(const std::string& name) {
    const std::string s = lower(name);
    if (s == "gradient descent") return HarmonicSolverType::GradientDescent;
    if (s == "newton") return HarmonicSolverType::Newton;
    if (s == "newton_spdh_fulleig") return HarmonicSolverType::Newton_SPDH_FullEig;
    if (s == "lbfgs") return HarmonicSolverType::LBFGS;
    return HarmonicSolverType::Newton_SPDH;
}

std::string toString(HarmonicEnergyType energy) {
    switch (energy) {
        case HarmonicEnergyType::Exp_SymmDirichlet: return "Exp_SymmDirichlet";
        case HarmonicEnergyType::AMIPS: return "AMIPS";
        default: return "SymmDirichlet";
    }
}

std::string toString(HarmonicSolverType solver) {
    switch (solver) {
        case HarmonicSolverType::GradientDescent: return "Gradient Descent";
        case HarmonicSolverType::Newton: return "Newton";
        case HarmonicSolverType::Newton_SPDH_FullEig: return "Newton_SPDH_FullEig";
        case HarmonicSolverType::LBFGS: return "LBFGS";
        default: return "Newton_SPDH";
    }
}

}  // namespace p2p_harmonic
