#include "Lbfgs.hpp"

namespace p2p_harmonic {

MatC lbfgsIter(const MatX& invH0, const MatC& g, const MatC& x) {
    const int k = static_cast<int>(x.cols());
    MatC s = x.leftCols(k - 1) - x.rightCols(k - 1);
    MatC t = g.leftCols(k - 1) - g.rightCols(k - 1);

    VecX rho(k - 1);
    for (int i = 0; i < k - 1; ++i) {
        rho[i] = (s.col(i).dot(t.col(i)));
    }

    MatC q = -g.col(0);
    VecX alpha = VecX::Zero(k - 1);
    for (int i = 0; i < k - 1; ++i) {
        if (rho[i] == 0.0) break;
        alpha[i] = s.col(i).dot(q) / rho[i];
        q -= alpha[i] * t.col(i);
    }

    MatC r = invH0 * q;
    for (int i = k - 2; i >= 0; --i) {
        if (rho[i] == 0.0) break;
        const double beta = t.col(i).dot(r) / rho[i];
        r += s.col(i) * (alpha[i] - beta);
    }
    return r;
}

}  // namespace p2p_harmonic
