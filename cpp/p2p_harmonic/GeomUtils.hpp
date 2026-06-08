#pragma once

#include "P2PHarmonicTypes.hpp"

namespace p2p_harmonic {

double signedPolyArea(const MatX& xy);
double signedPolyArea(const VecC& poly);

VecC polygonOffset(const VecC& x, double d, bool useRelative = true);

SpMatC subdivPolyMat(const VecC& x, int n);

VecC sampleOnPolygon(int n, const VecC& poly);

Complex pointInPolygon(const VecC& boundary);

bool polygonSelfIntersects(const VecC& poly);

bool inPolygon(const Complex& p, const VecC& boundary);

}  // namespace p2p_harmonic
