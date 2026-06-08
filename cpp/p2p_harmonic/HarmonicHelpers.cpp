#include "HarmonicHelpers.hpp"

#include <cmath>
#include <numeric>
#include <vector>

namespace p2p_harmonic {

VecC distancePointToSegment(const Complex& p, const VecC& v1, const VecC& v2) {
    const int n = static_cast<int>(v1.size());
    VecC d(n);
    for (int i = 0; i < n; ++i) {
        const Complex seg = v2[i] - v1[i];
        const Complex pv = p - v1[i];
        const double denom = std::norm(seg);
        double t = 0.0;
        if (denom > 0.0) {
            t = (pv * std::conj(seg)).real() / denom;
        }
        const Complex proj = (Complex(1.0, 0.0) - t) * v1[i] + t * v2[i];
        d[i] = std::abs(p - proj);
        if (t <= 0.0) d[i] = std::abs(p - v1[i]);
        if (t >= 1.0) d[i] = std::abs(p - v2[i]);
    }
    return d;
}

VecC concatenateBoundaries(const std::vector<VecC>& v) {
    const int total = static_cast<int>(std::accumulate(v.begin(), v.end(), 0,
                                                       [](int acc, const VecC& b) {
                                                           return acc + static_cast<int>(b.size());
                                                       }));
    VecC out(total);
    int offset = 0;
    for (const VecC& b : v) {
        out.segment(offset, b.size()) = b;
        offset += static_cast<int>(b.size());
    }
    return out;
}

MatX complexToRealBlock(const MatC& x) {
    const int n = static_cast<int>(x.rows());
    const int m = static_cast<int>(x.cols());
    MatX out(2 * n, 2 * m);
    out.topLeftCorner(n, m) = x.real();
    out.topRightCorner(n, m) = -x.imag();
    out.bottomLeftCorner(n, m) = x.imag();
    out.bottomRightCorner(n, m) = x.real();
    return out;
}

MatX complexToRealVector(const VecC& x) {
    const int n = static_cast<int>(x.size());
    MatX out(2 * n, 1);
    out.head(n) = x.real();
    out.tail(n) = x.imag();
    return out;
}

VecC realToComplexVector(const VecX& x) {
    const int n = static_cast<int>(x.size()) / 2;
    VecC out(n);
    for (int i = 0; i < n; ++i) {
        out[i] = Complex(x[i], x[i + n]);
    }
    return out;
}

MatX buildCtCr(const MatC& c2) {
    const int nP2P = static_cast<int>(c2.rows());
    const int n = static_cast<int>(c2.cols());
    MatC wide(nP2P, 2 * n);
    wide.leftCols(n) = c2;
    wide.rightCols(n) = c2.conjugate();
    const MatC ctC = wide.adjoint() * wide;
    MatX ctCr = complexToRealBlock(ctC);
    const int dim = 2 * n;
    ctCr.block(0, dim, 3 * dim / 2, dim) *= -1.0;
    ctCr.block(dim, 0, dim, 3 * dim / 2) *= -1.0;
    return ctCr;
}

SpMatC buildNullspaceMatrix(int n, const std::vector<VecC>& v) {
    if (v.size() <= 1) {
        SpMatC N(2 * n, 2 * n - 1);
        for (int i = 0; i < 2 * n - 1; ++i) {
            N.insert(i, i) = Complex(1.0, 0.0);
        }
        N.makeCompressed();
        return N;
    }

    const int cageSz = static_cast<int>(v[0].size());
    const int nHoles = static_cast<int>(v.size()) - 1;
    std::vector<bool> isFreeVar(2 * n, true);
    if (n + cageSz - 1 >= 0 && n + cageSz - 1 < 2 * n) {
        isFreeVar[n + cageSz - 1] = false;
    }
    for (int k = 1 - nHoles; k <= 0; ++k) {
        const int idx = 2 * n + k - 1;  // MATLAB 2*n+(1-nHoles:0)
        if (idx >= 0 && idx < 2 * n) isFreeVar[idx] = false;
    }

    int nFree = 0;
    for (bool f : isFreeVar) {
        if (f) ++nFree;
    }

    std::vector<Eigen::Triplet<Complex>> triplets;
    triplets.reserve(nFree + nHoles);
    int col = 0;
    for (int row = 0; row < 2 * n; ++row) {
        if (isFreeVar[row]) {
            triplets.emplace_back(row, col++, Complex(1.0, 0.0));
        }
    }
    for (int i = 0; i < nHoles; ++i) {
        triplets.emplace_back(2 * n - nHoles + i, nFree + i, Complex(1.0, 0.0));
    }

    SpMatC N(2 * n, nFree + nHoles);
    N.setFromTriplets(triplets.begin(), triplets.end());
    N.makeCompressed();
    return N;
}

MatX buildNr(const SpMatC& N, int numBoundaries) {
    const int rows = static_cast<int>(N.rows());
    const int cols = static_cast<int>(N.cols());
    MatX Nr = MatX::Zero(2 * rows, 2 * cols);
    Nr.topLeftCorner(rows, cols) = N.real();
    Nr.bottomRightCorner(rows, cols) = N.real();
    if (numBoundaries > 1) {
        const int tail = numBoundaries - 2;
        if (tail > 0) {
            Nr.bottomRows(tail) = -Nr.bottomRows(tail);
        }
    }
    return Nr;
}

}  // namespace p2p_harmonic
