#include "LineSearch.hpp"

#include "HarmonicHelpers.hpp"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>
#include <numeric>
#include <vector>

namespace p2p_harmonic {
namespace {

int matlabIndex(int i, int n) { return (i - 1 + n) % n; }  // 1-based next/prev wrap

}  // namespace

double maxtForPhiPsy(const Complex& fz, const Complex& gz, const Complex& dfz, const Complex& dgz) {
    const double a = std::norm(dfz) - std::norm(dgz);
    const double b = 2.0 * (std::conj(fz) * dfz - std::conj(gz) * dgz).real();
    const double c = std::norm(fz) - std::norm(gz);
    const double delta = b * b - 4.0 * a * c;

    double t = std::numeric_limits<double>::infinity();
    if (!(a > 0.0 && (delta < 0.0 || b > 0.0))) {
        t = (-b - std::sqrt(delta)) / a / 2.0;
    }
    return std::max(t, 0.0);
}

double lineSearchLocallyInjectiveHarmonicMap(const MatC& phipsyIn, const MatC& dppIn, const MatC& fzgz0,
                                             const MatC& dfzgz, double lsT, const VecC& fillDistanceSegments,
                                             const std::vector<VecC>& vCell, const MatC& E2, const MatX& L2,
                                             const Eigen::VectorXi& nextSampleInSameCage, bool verbose) {
    MatC phipsy = phipsyIn;
    MatC dpp = dppIn;
    Eigen::VectorXi nextSample = nextSampleInSameCage;

    std::vector<VecC> v = vCell;
    VecC boundary = concatenateBoundaries(v);
    const int nv = static_cast<int>(boundary.size());

    std::vector<int> cageSizes;
    for (const VecC& c : v) cageSizes.push_back(static_cast<int>(c.size()));

    std::vector<int> inextv(nv), iprevv(nv);
    if (v.size() > 1) {
        int offset = 0;
        for (int c = 0; c < static_cast<int>(v.size()); ++c) {
            const int sz = cageSizes[c];
            for (int i = 0; i < sz; ++i) {
                const int gi = offset + i;
                inextv[gi] = offset + (i + 1) % sz;
                iprevv[gi] = offset + (i - 1 + sz) % sz;
            }
            inextv[offset + sz - 1] = offset;
            iprevv[offset] = offset + sz - 1;
            offset += sz;
        }
    } else {
        for (int i = 0; i < nv; ++i) {
            inextv[i] = (i + 1) % nv;
            iprevv[i] = (i - 1 + nv) % nv;
        }
        nextSample = Eigen::VectorXi::LinSpaced(fzgz0.rows(), 1, fzgz0.rows());
        for (int i = 0; i < nextSample.size(); ++i) {
            nextSample[i] = matlabIndex(i + 2, nextSample.size());
        }
    }

    const double normdpp = dpp.norm();
    double ls_t = lsT;

    while (ls_t * normdpp > 1e-20) {
        MatC fzgzt = fzgz0 + ls_t * dfzgz;
        double argumentApprox = 0.0;
        for (int i = 0; i < fzgzt.rows(); ++i) {
            const int j = nextSample[i] - 1;
            argumentApprox += std::arg(fzgzt(j, 0) / fzgzt(i, 0));
        }
        if (argumentApprox < 1.0) break;
        ls_t *= 0.5;
    }

    auto diff = [](const VecC& x, const std::vector<int>& idx) {
        VecC out(idx.size());
        for (std::size_t i = 0; i < idx.size(); ++i) out[static_cast<Eigen::Index>(i)] = x[idx[i]];
        return out;
    };

    VecC vDiff(nv);
    for (int i = 0; i < nv; ++i) {
        vDiff[i] = boundary[inextv[i]] - boundary[i];
    }

    MatC dS(phipsy.rows(), 2);
    MatC ddS(phipsy.rows(), 2);
    for (int col = 0; col < 2; ++col) {
        VecC phiCol = phipsy.col(col);
        VecC dppCol = dpp.col(col);
        VecC dphi(nv), ddphi(nv);
        for (int i = 0; i < nv; ++i) {
            const Complex denom = boundary[inextv[i]] - boundary[i];
            dphi[i] = (phiCol[inextv[i]] - phiCol[i]) / denom;
            ddphi[i] = (dppCol[inextv[i]] - dppCol[i]) / denom;
        }
        for (int i = 0; i < nv; ++i) {
            dS(i, col) = (dphi[inextv[i]] - dphi[i]) / (boundary[inextv[inextv[i]]] - boundary[inextv[i]]);
            ddS(i, col) = (ddphi[inextv[i]] - ddphi[i]) / (boundary[inextv[inextv[i]]] - boundary[inextv[i]]);
        }
        const int logStart = nv;
        if (phipsy.rows() > logStart) {
            for (int r = logStart; r < phipsy.rows(); ++r) {
                dS(r, col) = phiCol[r];
                ddS(r, col) = dppCol[r];
            }
        }
    }

    MatX delta0 = L2.array().colwise() * dS.cwiseAbs().array();
    MatX delta1 = L2.array().colwise() * (dS + ls_t * ddS).cwiseAbs().array();
    const double ls_t0 = ls_t;

    MatC fzzgzz = E2 * phipsy;
    MatC dfzzgzz = E2 * dpp;

    while (true) {
        const bool sufficient = ls_t * normdpp > 1e-12;
        MatX deltaL = delta0 + (delta1 - delta0) * (ls_t / ls_t0);
        MatC fzgzt = fzgz0 + ls_t * dfzgz;
        MatC avgFz = (fzzgzz + ls_t * dfzzgzz);
        for (int i = 0; i < avgFz.rows(); ++i) {
            const int j = nextSample[i] - 1;
            avgFz.row(i) = 0.5 * (avgFz.row(i) + avgFz.row(j));
        }

        double minGlobalSigma2 = std::numeric_limits<double>::infinity();
        for (int i = 0; i < fzgzt.rows(); ++i) {
            const double minAbsFz = std::abs(fzgzt(i, 0)) - deltaL(i, 0) * fillDistanceSegments[i];
            const double maxAbsGz = std::abs(fzgzt(i, 1)) + deltaL(i, 1) * fillDistanceSegments[i];
            minGlobalSigma2 = std::min(minGlobalSigma2, minAbsFz - maxAbsGz);
        }

        if (sufficient && minGlobalSigma2 < 0.0) {
            ls_t *= 0.5;
            continue;
        }

        if (verbose) {
            std::cout << "line search t=" << ls_t << " minGlobal_sigma2=" << minGlobalSigma2 << '\n';
        }
        break;
    }

    return ls_t;
}

}  // namespace p2p_harmonic
