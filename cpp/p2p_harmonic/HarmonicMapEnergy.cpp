#include "HarmonicMapEnergy.hpp"

#include <cmath>

namespace p2p_harmonic {
namespace {

MatX permuteHessian(const MatX& h, int m) {
    std::vector<int> perm(4 * m);
    for (int i = 0; i < m; ++i) perm[i] = i;
    for (int i = 0; i < m; ++i) perm[m + i] = 2 * m + i;
    for (int i = 0; i < m; ++i) perm[2 * m + i] = m + i;
    for (int i = 0; i < m; ++i) perm[3 * m + i] = 3 * m + i;

    MatX out(4 * m, 4 * m);
    for (int i = 0; i < 4 * m; ++i) {
        for (int j = 0; j < 4 * m; ++j) {
            out(i, j) = 4.0 * h(perm[i], perm[j]);
        }
    }
    return out;
}

MatX assembleBlock(const MatX& DR, const MatX& DI, const MatX& DRDI, const VecX& sA, const VecX& sB,
                   const VecX& sC, const VecX& sD) {
    const int n = static_cast<int>(sA.size());
    MatX top = DR, bottom = DR;
    for (int i = 0; i < n; ++i) {
        top.row(i) *= sA[i];
        top.row(i) += DI.row(i) * sB[i];
        bottom.row(i) *= sC[i];
        bottom.row(i) += DI.row(i) * sD[i];
    }
    MatX rhs(2 * n, DR.cols());
    rhs << top, bottom;
    return DRDI.transpose() * rhs;
}

}  // namespace

HarmonicMapEnergyResult harmonicMapIsometryicEnergy(const MatC& D, const VecC& phi, const VecC& psy,
                                                    bool spdHessian, HarmonicEnergyType energyType,
                                                    double energyParam) {
    HarmonicMapEnergyResult result;
    const int nSamples = static_cast<int>(D.rows());
    const int m = static_cast<int>(D.cols());

    const VecC fz = D * phi;
    const VecC gz = D * psy;
    const VecX fz2 = fz.cwiseAbs2();
    const VecX gz2 = gz.cwiseAbs2();
    const VecX diff = fz2 - gz2;
    const VecX invDiff = diff.cwiseInverse();
    const VecX invDiff2 = invDiff.array().square();
    const VecX invDiff3 = invDiff2.array() * invDiff.array();
    const VecX invDiff4 = invDiff2.array().square();

    VecX evec(nSamples);
    switch (energyType) {
        case HarmonicEnergyType::Exp_SymmDirichlet:
            evec = ((fz2 + gz2).array() * (1.0 + invDiff2.array())).abs().unaryExpr(
                [energyParam](double x) { return std::exp(energyParam * x); });
            break;
        case HarmonicEnergyType::AMIPS: {
            const VecX inner =
                (energyParam * 2.0 * (fz2 + gz2).array() + 1.0).cwiseQuotient(diff.array()) - diff.array();
            evec = inner.unaryExpr([](double x) { return std::exp(x); });
            break;
        }
        default:
            evec = ((fz2 + gz2).array() * (1.0 + invDiff2.array())).abs();
            break;
    }
    result.energy = evec.sum();

    MatX alphas(nSamples, 2);
    switch (energyType) {
        case HarmonicEnergyType::Exp_SymmDirichlet:
            alphas.col(0) = (1.0 - invDiff3.cwiseProduct(fz2 + 3.0 * gz2)).cwiseProduct(evec) * energyParam;
            alphas.col(1) = (1.0 + invDiff3.cwiseProduct(3.0 * fz2 + gz2)).cwiseProduct(evec) * energyParam;
            break;
        case HarmonicEnergyType::AMIPS:
            alphas.col(0) = (1.0 - (4.0 * energyParam * gz2.array() + 1.0).matrix().cwiseProduct(invDiff2)) *
                            evec;
            alphas.col(1) =
                -(1.0 - (4.0 * energyParam * fz2.array() + 1.0).matrix().cwiseProduct(invDiff2)).cwiseProduct(evec);
            break;
        default:
            alphas.col(0) = 1.0 - invDiff3.cwiseProduct(fz2 + 3.0 * gz2);
            alphas.col(1) = 1.0 + invDiff3.cwiseProduct(3.0 * fz2 + gz2);
            break;
    }

    result.gradient.resize(2 * m);
    result.gradient.head(m) = 2.0 * D.adjoint() * (fz.cwiseProduct(alphas.col(0).cast<Complex>()));
    result.gradient.tail(m) =
        2.0 * (D.adjoint() * (gz.cwiseProduct(alphas.col(1).cast<Complex>()))).conjugate();

    MatX betas(nSamples, 3);
    betas.col(0) = 2.0 * (fz2 + 5.0 * gz2).cwiseProduct(invDiff4);
    betas.col(1) = 2.0 * (5.0 * fz2 + gz2).cwiseProduct(invDiff4);
    betas.col(2) = -6.0 * (fz2 + gz2).cwiseProduct(invDiff4);

    if (energyType == HarmonicEnergyType::Exp_SymmDirichlet) {
        betas.col(0) = alphas.col(0).cwiseProduct(alphas.col(0)).cwiseQuotient(evec) +
                       betas.col(0).cwiseProduct(evec) * energyParam;
        betas.col(1) = alphas.col(0).cwiseProduct(alphas.col(1)).cwiseQuotient(evec) +
                       betas.col(1).cwiseProduct(evec) * energyParam;
        betas.col(2) = alphas.col(0).cwiseProduct(alphas.col(1)).cwiseQuotient(evec) +
                       betas.col(2).cwiseProduct(evec) * energyParam;
    } else if (energyType == HarmonicEnergyType::AMIPS) {
        betas.col(0) = 2.0 * (4.0 * energyParam * gz2.array() + 1.0).matrix().cwiseProduct(invDiff3);
        betas.col(1) = 2.0 * (4.0 * energyParam * fz2.array() + 1.0).matrix().cwiseProduct(invDiff3);
        betas.col(2) = -0.5 * (betas.col(0) + betas.col(1));
        betas.col(0) = alphas.col(0).cwiseProduct(alphas.col(0)).cwiseQuotient(evec) +
                       betas.col(0).cwiseProduct(evec);
        betas.col(1) = alphas.col(0).cwiseProduct(alphas.col(1)).cwiseQuotient(evec) +
                       betas.col(1).cwiseProduct(evec);
        betas.col(2) = alphas.col(1).cwiseProduct(alphas.col(1)).cwiseQuotient(evec) +
                       betas.col(2).cwiseProduct(evec);
    }

    if (spdHessian) {
        if (energyType == HarmonicEnergyType::SymmDirichlet ||
            energyType == HarmonicEnergyType::Exp_SymmDirichlet) {
            for (int i = 0; i < nSamples; ++i) {
                if (alphas(i, 0) < 0.0) {
                    betas(i, 0) += alphas(i, 0) / (2.0 * fz2[i]);
                    alphas(i, 0) = 0.0;
                }
            }
        } else {
            for (int i = 0; i < nSamples; ++i) {
                if (gz2[i] <= 1e-50) continue;
                const double s1 = alphas(i, 0) + 2.0 * betas(i, 0) * fz2[i] + 2.0 * betas(i, 2) * gz2[i];
                const double s2 = alphas(i, 1) + 2.0 * betas(i, 1) * gz2[i] + 2.0 * betas(i, 2) * fz2[i];
                const double root = std::sqrt((s1 + s2) * (s1 + s2) + 16.0 * betas(i, 2) * betas(i, 2) * fz2[i] * gz2[i]);
                const double l3 = std::max(0.5 * (s1 + s2 + root), 0.0);
                const double l4 = std::max(0.5 * (s1 + s2 - root), 0.0);
                const double t1 = (l3 + l4 - 2.0 * alphas(i, 0) - 4.0 * betas(i, 0) * fz2[i]) /
                                  (4.0 * betas(i, 2) * gz2[i]);
                alphas(i, 0) = std::max(alphas(i, 0), 0.0) * 4.0;
                alphas(i, 1) = std::max(alphas(i, 1), 0.0) * 4.0;
                betas(i, 0) = (l3 + l4) - alphas(i, 0) / (2.0 * fz2[i]);
                betas(i, 1) = (l3 * t1 * t1 + l4 * t1 * t1) - alphas(i, 1) / (2.0 * gz2[i]);
                betas(i, 2) = l3 * t1 + l4 * t1;
            }
        }
    }

    const VecX fzR = fz.real(), fzI = fz.imag(), gzR = gz.real(), gzI = gz.imag();
    VecX ss1a(nSamples), ss1b(nSamples), ss1c(nSamples), ss1d(nSamples);
    VecX ss2a(nSamples), ss2b(nSamples), ss2c(nSamples), ss2d(nSamples);
    VecX ss3a(nSamples), ss3b(nSamples), ss3c(nSamples), ss3d(nSamples);
    for (int i = 0; i < nSamples; ++i) {
        ss1a[i] = fzR[i] * fzR[i] * betas(i, 0) + 0.5 * alphas(i, 0);
        ss1b[i] = fzR[i] * fzI[i] * betas(i, 0);
        ss1c[i] = fzR[i] * fzI[i] * betas(i, 0);
        ss1d[i] = fzI[i] * fzI[i] * betas(i, 0) + 0.5 * alphas(i, 0);

        ss2a[i] = gzR[i] * gzR[i] * betas(i, 1) + 0.5 * alphas(i, 1);
        ss2b[i] = gzR[i] * gzI[i] * betas(i, 1);
        ss2c[i] = gzR[i] * gzI[i] * betas(i, 1);
        ss2d[i] = gzI[i] * gzI[i] * betas(i, 1) + 0.5 * alphas(i, 1);

        ss3a[i] = fzR[i] * gzR[i] * betas(i, 2);
        ss3b[i] = fzR[i] * gzI[i] * betas(i, 2);
        ss3c[i] = fzI[i] * gzR[i] * betas(i, 2);
        ss3d[i] = fzI[i] * gzI[i] * betas(i, 2);
    }

    MatX Dreal(D.real()), Dimag(D.imag());
    MatX DR(nSamples, 2 * m), DI(nSamples, 2 * m);
    DR << Dreal, -Dimag;
    DI << Dimag, Dreal;
    MatX DRDI(2 * nSamples, 2 * m);
    DRDI << DR, DI;

    MatX h = MatX::Zero(4 * m, 4 * m);
    h.topLeftCorner(2 * m, 2 * m) = assembleBlock(DR, DI, DRDI, ss1a, ss1b, ss1c, ss1d);
    h.bottomRightCorner(2 * m, 2 * m) = assembleBlock(DR, DI, DRDI, ss2a, ss2b, ss2c, ss2d);
    h.topRightCorner(2 * m, 2 * m) = assembleBlock(DR, DI, DRDI, ss3a, ss3b, ss3c, ss3d);
    h.bottomLeftCorner(2 * m, 2 * m) = h.topRightCorner(2 * m, 2 * m).transpose();

    result.hessian = permuteHessian(h, m);
    return result;
}

}  // namespace p2p_harmonic
