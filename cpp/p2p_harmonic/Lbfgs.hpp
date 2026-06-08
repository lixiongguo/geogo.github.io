#pragma once

#include "P2PHarmonicTypes.hpp"

namespace p2p_harmonic {

MatC lbfgsIter(const MatX& invH0, const MatC& g, const MatC& x);

}  // namespace p2p_harmonic
