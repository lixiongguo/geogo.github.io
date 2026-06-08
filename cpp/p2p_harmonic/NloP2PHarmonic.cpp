#include "NloP2PHarmonic.hpp"

#include "HarmonicHelpers.hpp"
#include "HarmonicMapEnergy.hpp"
#include "Lbfgs.hpp"
#include "LineSearch.hpp"

#include <Eigen/Eigenvalues>
#include <cmath>
#include <iostream>

namespace p2p_harmonic {
namespace {

constexpr double kLsBeta = 0.5;
constexpr double kLsAlpha = 0.2;

VecX diffCols(const MatX& x) { return x.col(0) - x.col(1); }

double isometryEnergy(const MatX& fzgz2, HarmonicEnergyType energyType, double mu) {
    const VecX sumCols = fzgz2.rowwise().sum();
    const VecX diff = diffCols(fzgz2);
    const VecX base = sumCols.cwiseProduct(1.0 + diff.cwiseInverse().array().square());
    switch (energyType) {
        case HarmonicEnergyType::Exp_SymmDirichlet:
            return base.cwiseAbs().unaryExpr([mu](double x) { return std::exp(mu * x); }).sum();
        case HarmonicEnergyType::AMIPS: {
            const VecX inner = (mu * 2.0 * sumCols.array() + 1.0).cwiseQuotient(diff.array()) - diff.array();
            return inner.unaryExpr([](double x) { return std::exp(x); }).sum();
        }
        default:
            if (mu == 1.0) return base.sum();
            return base.cwiseAbs().unaryExpr([mu](double x) { return std::pow(x, mu); }).sum();
    }
}

VecC gradIso(const MatC& D2, const MatC& fzgz, const MatX& fzgz2, HarmonicEnergyType energyType, double mu) {
    const VecX diff = diffCols(fzgz2);
    const VecX sumCols = fzgz2.rowwise().sum();
    const VecX invDiff3 = diff.cwiseInverse().array().cube();
    VecX evecScale = VecX::Ones(fzgz.rows());

    Complex scale1, scale2;
    switch (energyType) {
        case HarmonicEnergyType::Exp_SymmDirichlet: {
            const VecX base = sumCols.cwiseProduct(1.0 + diff.cwiseInverse().array().square());
            evecScale = base.cwiseAbs().unaryExpr([mu](double x) { return mu * std::exp(mu * x); });
            scale1 = Complex(1.0, 0.0);
            scale2 = Complex(1.0, 0.0);
            break;
        }
        case HarmonicEnergyType::AMIPS: {
            const VecX inner = (mu * 2.0 * sumCols.array() + 1.0).cwiseQuotient(diff.array()) - diff.array();
            evecScale = inner.unaryExpr([](double x) { return std::exp(x); });
            scale1 = Complex(1.0, 0.0);
            scale2 = Complex(1.0, 0.0);
            break;
        }
        default:
            if (mu != 1.0) {
                const VecX base = sumCols.cwiseProduct(1.0 + diff.cwiseInverse().array().square());
                evecScale = mu * base.cwiseAbs().array().pow(mu - 1.0);
            }
            break;
    }

    const int n = static_cast<int>(D2.cols());
    VecC out(2 * n);
    MatC fzAlpha1(fzgz.rows(), 1), gzAlpha2(fzgz.rows(), 1);

    if (energyType == HarmonicEnergyType::AMIPS) {
        fzAlpha1 = fzgz.col(0).cwiseProduct(
            (1.0 - (4.0 * mu * fzgz2.col(1).array() + 1.0).matrix().cwiseProduct(diff.cwiseInverse().square()))
                .cwiseProduct(evecScale)
                .cast<Complex>());
        gzAlpha2 = fzgz.col(1).cwiseProduct(
            (-(1.0 - (4.0 * mu * fzgz2.col(0).array() + 1.0).matrix().cwiseProduct(diff.cwiseInverse().square()))
                  .cwiseProduct(evecScale))
                .cast<Complex>());
    } else {
        const VecX termA = 1.0 + invDiff3.cwiseProduct(fzgz2.col(0) + 3.0 * fzgz2.col(1));
        const VecX termB = 1.0 - invDiff3.cwiseProduct(3.0 * fzgz2.col(0) + fzgz2.col(1));
        fzAlpha1 = fzgz.col(0).cwiseProduct((termA.cwiseProduct(evecScale)).cast<Complex>());
        gzAlpha2 = fzgz.col(1).cwiseProduct((termB.cwiseProduct(evecScale)).cast<Complex>());
    }

    out.head(n) = 2.0 * D2.adjoint() * fzAlpha1;
    out.tail(n) = (2.0 * D2.adjoint() * gzAlpha2).conjugate();
    return out;
}

double p2pEnergy(const MatC& fg, const VecC& bP2P) {
    const VecC mapped = fg.col(0) + fg.col(1).conjugate();
    return (mapped - bP2P).squaredNorm();
}

MatC gradP2PMatrix(const MatC& C2, const VecC& bP2P) {
    const int n = static_cast<int>(C2.cols());
    const int nP2P = static_cast<int>(C2.rows());
    MatC ct(2 * n, nP2P);
    ct.topRows(n) = C2.adjoint();
    for (int j = 0; j < nP2P; ++j) {
        for (int i = 0; i < n; ++i) ct(n + i, j) = std::conj(C2(j, i));
    }
    MatC ctC = ct * C2;
    MatC rhs(2 * n, n + 1);
    rhs.leftCols(n) = ctC;
    rhs.col(n) = -bP2P;
    return 2.0 * ct * rhs;
}

VecC gradP2P(const MatC& gradMat, const VecC& phi, const VecC& psy) {
    MatC fg(2, 1);
    fg(0, 0) = phi;
    fg(1, 0) = psy;
    // gradMat is 2n x (n+1) acting on [phi; conj(psy); 1] - use explicit formula
    const int n = static_cast<int>(phi.size());
    VecC out(2 * n);
    out.head(n) = gradMat.topLeftCorner(n, n) * phi + gradMat.block(0, n, n, 1);
    out.tail(n) = gradMat.block(n, 0, n, n) * psy.conjugate() + gradMat.block(n, n, n, 1);
    return out;
}

double totalEnergy(const MatX& fzgz2, const MatC& fg, const VecC& bP2P, double lambda, HarmonicEnergyType energyType,
                   double mu) {
    return isometryEnergy(fzgz2, energyType, mu) + p2pEnergy(fg, bP2P) * lambda;
}

MatX selectHessianSamples(const MatC& D2, double hessianSampleRate) {
    const int stride = std::max(1, static_cast<int>(std::ceil(1.0 / hessianSampleRate)));
    std::vector<int> rows;
    const int maxRow = static_cast<int>(D2.rows()) - stride / 2;
    for (int r = 0; r < maxRow; r += stride) rows.push_back(r);
    MatC out(rows.size(), D2.cols());
    for (std::size_t i = 0; i < rows.size(); ++i) out.row(static_cast<Eigen::Index>(i)) = D2.row(rows[i]);
    return out;
}

NloP2PHarmonicResult runNewtonLike(const NloP2PHarmonicInput& in) {
    NloP2PHarmonicResult result;
    const int n = static_cast<int>(in.D2.cols());
    const int nIter = in.numIterations;
    const double mu = in.energyParameter;
    const MatC gradP2PMat = gradP2PMatrix(in.C2, in.bP2P);
    const MatX ctCr = buildCtCr(in.C2);
    const SpMatC N = buildNullspaceMatrix(n, in.v);
    const MatX Nr = buildNr(N, static_cast<int>(in.v.size()));

    VecC phi = in.phipsyIters.col(0);
    VecC psy = in.phipsyIters.col(1);
    MatC fzgz0 = in.D2 * (MatC) (MatC(2, 1) << phi, psy).finished();
    // fix: multiply per column
    fzgz0.col(0) = in.D2 * phi;
    fzgz0.col(1) = in.D2 * psy;
    MatX fzgz2 = fzgz0.cwiseAbs2();

    MatC fgP2P(n, 2);
    fgP2P.col(0) = in.C2 * phi;
    fgP2P.col(1) = in.C2 * psy;

    result.statsAll = MatX::Zero(nIter + 1, 8);
    double e = totalEnergy(fzgz2, fgP2P, in.bP2P, in.lambda, in.energyType, mu);
    result.statsAll(0, 6) = p2pEnergy(fgP2P, in.bP2P) * in.lambda;
    result.statsAll(0, 7) = e;

    const MatC Dhess = selectHessianSamples(in.D2, in.hessianSampleRate);
    const double hessScale = static_cast<double>(Dhess.rows()) / in.D2.rows();

    for (int it = 0; it < nIter; ++it) {
        const auto t0 = std::chrono::steady_clock::now();

        VecC g = gradIso(in.D2, fzgz0, fzgz2, in.energyType, mu) + gradP2P(gradP2PMat, phi, psy) * in.lambda;

        VecC dpp(2 * n);
        if (in.solver == HarmonicSolverType::GradientDescent) {
            dpp = -g;
        } else {
            const bool spd = in.solver == HarmonicSolverType::Newton_SPDH ||
                             in.solver == HarmonicSolverType::Newton_SPDH_FullEig;
            auto energy = harmonicMapIsometryicEnergy(Dhess, phi, psy, spd, in.energyType, mu);
            MatX h = energy.hessian / hessScale;
            if (in.solver == HarmonicSolverType::Newton_SPDH_FullEig) {
                Eigen::SelfAdjointEigenSolver<MatX> es(h);
                VecX evals = es.eigenvalues();
                for (int i = 0; i < evals.size(); ++i) evals[i] = std::max(evals[i], 0.0);
                h = es.eigenvectors() * evals.asDiagonal() * es.eigenvectors().transpose();
            }
            MatX M = h + 2.0 * in.lambda * ctCr;
            VecC gAdj = g;
            gAdj.tail(n) = gAdj.tail(n).conjugate();
            VecX gReal = complexToRealVector(gAdj);
            MatX reduced = Nr.transpose() * M * Nr;
            VecX rhs = Nr.transpose() * (-gReal);
            VecX sol = reduced.ldlt().solve(rhs);
            dpp = realToComplexVector(Nr * sol);
        }

        if (in.solver == HarmonicSolverType::GradientDescent) {
            dpp.tail(n) = dpp.tail(n).conjugate();
        }

        const double dppdotg = complexToRealVector(dpp).dot(complexToRealVector(g));
        const double normdpp = dpp.norm();

        MatC dfzgz(in.D2.rows(), 2);
        MatC dppMat(n, 2);
        dppMat.col(0) = dpp.head(n);
        dppMat.col(1) = dpp.tail(n);
        dfzgz = in.D2 * dppMat;
        MatC dfgP2P = in.C2 * dppMat;

        double ls_t = 1.0;
        for (int i = 0; i < fzgz0.rows(); ++i) {
            ls_t = std::min(ls_t, maxtForPhiPsy(fzgz0(i, 0), fzgz0(i, 1), dfzgz(i, 0), dfzgz(i, 1)) * 0.8);
        }

        auto evalEnergy = [&](double t) {
            return totalEnergy((fzgz0 + t * dfzgz).cwiseAbs2(), fgP2P + t * dfgP2P, in.bP2P, in.lambda, in.energyType,
                               mu);
        };

        double e_new = evalEnergy(ls_t);
        while (ls_t * normdpp > 1e-12 && e_new > e + kLsAlpha * ls_t * dppdotg) {
            ls_t *= kLsBeta;
            e_new = evalEnergy(ls_t);
        }
        e = e_new;

        ls_t = lineSearchLocallyInjectiveHarmonicMap((MatC)(MatC(n, 2) << phi, psy).finished(), dppMat, fzgz0, dfzgz,
                                                     ls_t, in.fillDistanceSegments, in.v, in.E2, in.L2,
                                                     in.nextSampleInSameCage, in.verboseLineSearch);
        e = evalEnergy(ls_t);

        const auto t1 = std::chrono::steady_clock::now();
        result.statsAll(it + 1, 4) =
            std::chrono::duration<double, std::milli>(t1 - t0).count();
        result.statsAll(it + 1, 6) = p2pEnergy(fgP2P + ls_t * dfgP2P, in.bP2P) * in.lambda;
        result.statsAll(it + 1, 7) = e;

        if (ls_t * normdpp < 1e-12) break;

        phi += ls_t * dpp.head(n);
        psy += ls_t * dpp.tail(n);
        fzgz0 += ls_t * dfzgz;
        fzgz2 = fzgz0.cwiseAbs2();
        fgP2P += ls_t * dfgP2P;
    }

    result.phipsyIters = in.phipsyIters;
    result.phipsyIters.col(0) = phi;
    result.phipsyIters.col(1) = psy;
    return result;
}

}  // namespace

NloP2PHarmonicResult nloP2PHarmonic(const NloP2PHarmonicInput& input) {
    switch (input.solver) {
        case HarmonicSolverType::LBFGS:
            // LBFGS shares most logic; fall through to Newton-like for now with simplified path
        case HarmonicSolverType::GradientDescent:
        case HarmonicSolverType::Newton:
        case HarmonicSolverType::Newton_SPDH:
        case HarmonicSolverType::Newton_SPDH_FullEig:
            return runNewtonLike(input);
        default:
            throw P2PHarmonicPrepError("Unsupported solver in CPU nloP2PHarmonic");
    }
}

}  // namespace p2p_harmonic
