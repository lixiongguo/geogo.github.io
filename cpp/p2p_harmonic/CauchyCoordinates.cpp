#include "CauchyCoordinates.hpp"

#include <cmath>
#include <numeric>
#include <vector>

namespace p2p_harmonic {
namespace {

constexpr Complex kOneOver2PiI(0.0, 1.0 / (2.0 * 3.14159265358979323846));

int modIndex(int i, int n) {
    int r = i % n;
    return r < 0 ? r + n : r;
}

std::vector<bool> removeTwoCoeffPerHoleFlags(const std::vector<int>& cageSizes) {
    const int total = static_cast<int>(std::accumulate(cageSizes.begin(), cageSizes.end(), 0));
    std::vector<bool> flags(total, true);
    if (cageSizes.size() <= 1) return flags;

    int cum = 0;
    for (std::size_t k = 0; k + 1 < cageSizes.size(); ++k) {
        cum += cageSizes[k];
        if (cum < total) flags[cum] = false;
        if (cum + 1 < total) flags[cum + 1] = false;
    }
    return flags;
}

MatC applyColumnFlags(const MatC& M, const std::vector<bool>& flags) {
    int kept = 0;
    for (bool f : flags) {
        if (f) ++kept;
    }
    MatC out(M.rows(), kept);
    int col = 0;
    for (int j = 0; j < static_cast<int>(flags.size()); ++j) {
        if (flags[j]) out.col(col++) = M.col(j);
    }
    return out;
}

}  // namespace

MatC cauchyCoordinatesSingle(const VecC& cage, const VecC& z) {
    const int nb = static_cast<int>(cage.size());
    const int np = static_cast<int>(z.size());
    MatC C(np, nb);

    VecC Aj(nb), Ajp(nb);
    for (int j = 0; j < nb; ++j) {
        const int jm = modIndex(j - 1, nb);
        const int jp = modIndex(j + 1, nb);
        Aj[j] = cage[j] - cage[jm];
        Ajp[j] = cage[jp] - cage[j];
    }

    for (int p = 0; p < np; ++p) {
        for (int j = 0; j < nb; ++j) {
            const int jm = modIndex(j - 1, nb);
            const int jp = modIndex(j + 1, nb);

            const Complex Bj = cage[j] - z[p];
            const Complex Bjp = cage[jp] - z[p];
            const Complex Bjm = cage[jm] - z[p];

            const Complex term1 = Bjp * (std::log(Bjp / Bj) / Ajp[j]);
            const Complex term2 = Bjm * (std::log(Bj / Bjm) / Aj[j]);
            C(p, j) = kOneOver2PiI * (term1 - term2);
        }
    }
    return C;
}

MatC cauchyCoordinates(const std::vector<VecC>& cage, const VecC& z, const VecC& holeCenters) {
    if (cage.empty()) {
        throw P2PHarmonicPrepError("cauchyCoordinates: empty cage list");
    }

    std::vector<int> cageSizes;
    cageSizes.reserve(cage.size());
    int totalCols = 0;
    for (const VecC& c : cage) {
        cageSizes.push_back(static_cast<int>(c.size()));
        totalCols += static_cast<int>(c.size());
    }

    const int np = static_cast<int>(z.size());
    MatC C(np, totalCols);
    int offset = 0;
    for (const VecC& c : cage) {
        const MatC block = cauchyCoordinatesSingle(c, z);
        C.block(0, offset, np, block.cols()) = block;
        offset += static_cast<int>(block.cols());
    }

    if (cage.size() > 1) {
        const std::vector<bool> flags = removeTwoCoeffPerHoleFlags(cageSizes);
        C = applyColumnFlags(C, flags);

        if (holeCenters.size() == 0) {
            throw P2PHarmonicPrepError("cauchyCoordinates: holeCenters required for multiply-connected domain");
        }

        const int baseCols = C.cols();
        C.conservativeResize(np, baseCols + holeCenters.size());
        for (int p = 0; p < np; ++p) {
            for (int h = 0; h < holeCenters.size(); ++h) {
                C(p, baseCols + h) = std::log(std::abs(z[p] - holeCenters[h]));
            }
        }
    }

    return C;
}

MatC derivativesOfCauchyCoordSingle(const VecC& cage, const VecC& z) {
    const int nb = static_cast<int>(cage.size());
    const int np = static_cast<int>(z.size());
    MatC D(np, nb);

    VecC Aj(nb), Ajp(nb);
    for (int j = 0; j < nb; ++j) {
        const int jm = modIndex(j - 1, nb);
        const int jp = modIndex(j + 1, nb);
        Aj[j] = cage[j] - cage[jm];
        Ajp[j] = cage[jp] - cage[j];
    }

    for (int p = 0; p < np; ++p) {
        for (int j = 0; j < nb; ++j) {
            const int jm = modIndex(j - 1, nb);
            const int jp = modIndex(j + 1, nb);

            const Complex Bj = cage[j] - z[p];
            const Complex Bjp = cage[jp] - z[p];
            const Complex Bjm = cage[jm] - z[p];

            D(p, j) = kOneOver2PiI * (std::log(Bj / Bjm) / Aj[j] - std::log(Bjp / Bj) / Ajp[j]);
        }
    }
    return D;
}

MatC derivativesOfCauchyCoord(const std::vector<VecC>& cage, const VecC& z, const VecC& holeCenters) {
    if (cage.empty()) {
        throw P2PHarmonicPrepError("derivativesOfCauchyCoord: empty cage list");
    }

    std::vector<int> cageSizes;
    cageSizes.reserve(cage.size());
    int totalCols = 0;
    for (const VecC& c : cage) {
        cageSizes.push_back(static_cast<int>(c.size()));
        totalCols += static_cast<int>(c.size());
    }

    const int np = static_cast<int>(z.size());
    MatC D(np, totalCols);
    int offset = 0;
    for (const VecC& c : cage) {
        const MatC block = derivativesOfCauchyCoordSingle(c, z);
        D.block(0, offset, np, block.cols()) = block;
        offset += static_cast<int>(block.cols());
    }

    if (cage.size() > 1) {
        const std::vector<bool> flags = removeTwoCoeffPerHoleFlags(cageSizes);
        D = applyColumnFlags(D, flags);

        if (holeCenters.size() == 0) {
            throw P2PHarmonicPrepError("derivativesOfCauchyCoord: holeCenters required for multiply-connected domain");
        }

        const int baseCols = D.cols();
        D.conservativeResize(np, baseCols + holeCenters.size());
        for (int p = 0; p < np; ++p) {
            for (int h = 0; h < holeCenters.size(); ++h) {
                D(p, baseCols + h) = Complex(1.0, 0.0) / (z[p] - holeCenters[h]);
            }
        }
    }

    return D;
}

MatC secondDerivativesOfCauchyCoordSingle(const VecC& cage, const VecC& z) {
    const int nb = static_cast<int>(cage.size());
    const int np = static_cast<int>(z.size());
    MatC E(np, nb);

    for (int p = 0; p < np; ++p) {
        for (int j = 0; j < nb; ++j) {
            const int jm = modIndex(j - 1, nb);
            const int jp = modIndex(j + 1, nb);

            const Complex Bj = cage[j] - z[p];
            const Complex Bjp = cage[jp] - z[p];
            const Complex Bjm = cage[jm] - z[p];

            E(p, j) = kOneOver2PiI * (Bjp - Bjm) / (Bjm * Bj * Bjp);
        }
    }
    return E;
}

MatC secondDerivativesOfCauchyCoord(const std::vector<VecC>& cage, const VecC& z, const VecC& holeCenters) {
    if (cage.empty()) {
        throw P2PHarmonicPrepError("secondDerivativesOfCauchyCoord: empty cage list");
    }

    std::vector<int> cageSizes;
    cageSizes.reserve(cage.size());
    int totalCols = 0;
    for (const VecC& c : cage) {
        cageSizes.push_back(static_cast<int>(c.size()));
        totalCols += static_cast<int>(c.size());
    }

    const int np = static_cast<int>(z.size());
    MatC E(np, totalCols);
    int offset = 0;
    for (const VecC& c : cage) {
        const MatC block = secondDerivativesOfCauchyCoordSingle(c, z);
        E.block(0, offset, np, block.cols()) = block;
        offset += static_cast<int>(block.cols());
    }

    if (cage.size() > 1) {
        const std::vector<bool> flags = removeTwoCoeffPerHoleFlags(cageSizes);
        E = applyColumnFlags(E, flags);

        if (holeCenters.size() == 0) {
            throw P2PHarmonicPrepError("secondDerivativesOfCauchyCoord: holeCenters required");
        }

        const int baseCols = E.cols();
        E.conservativeResize(np, baseCols + holeCenters.size());
        for (int p = 0; p < np; ++p) {
            for (int h = 0; h < holeCenters.size(); ++h) {
                const Complex diff = z[p] - holeCenters[h];
                E(p, baseCols + h) = Complex(-1.0, 0.0) / (diff * diff);
            }
        }
    }

    return E;
}

void derivativesOfCauchyCoordWithSecond(const std::vector<VecC>& cage, const VecC& z, const VecC& holeCenters,
                                        MatC& D, MatC& E) {
    D = derivativesOfCauchyCoord(cage, z, holeCenters);
    E = secondDerivativesOfCauchyCoord(cage, z, holeCenters);
}

}  // namespace p2p_harmonic
