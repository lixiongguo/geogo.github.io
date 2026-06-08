#pragma once

#include "P2PHarmonicTypes.hpp"

namespace p2p_harmonic {

VecC distancePointToSegment(const Complex& p, const VecC& v1, const VecC& v2);

VecC concatenateBoundaries(const std::vector<VecC>& v);

MatX complexToRealBlock(const MatC& x);

MatX complexToRealVector(const VecC& x);

VecC realToComplexVector(const VecX& x);

MatX buildCtCr(const MatC& c2);

SpMatC buildNullspaceMatrix(int n, const std::vector<VecC>& v);

MatX buildNr(const SpMatC& N, int numBoundaries);

}  // namespace p2p_harmonic
