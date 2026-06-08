#include "GeomUtils.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <numeric>
#include <vector>

namespace p2p_harmonic {
namespace {

constexpr double kEps = 1e-8;
constexpr double kPi = 3.14159265358979323846;

MatX complexToReal(const VecC& x) {
    MatX xy(x.size(), 2);
    for (Eigen::Index i = 0; i < x.size(); ++i) {
        xy(i, 0) = x[i].real();
        xy(i, 1) = x[i].imag();
    }
    return xy;
}

VecC realToComplex(const MatX& xy) {
    VecC out(xy.rows());
    for (Eigen::Index i = 0; i < xy.rows(); ++i) {
        out[i] = Complex(xy(i, 0), xy(i, 1));
    }
    return out;
}

double rowNorm(const Eigen::RowVector2d& r) { return r.norm(); }

Eigen::RowVector2d rowDiff(const MatX& x, int i, int j) {
    return x.row(i) - x.row(j);
}

int modIndex(int i, int n) {
    int r = i % n;
    return r < 0 ? r + n : r;
}

}  // namespace

double signedPolyArea(const MatX& xy) {
    const Eigen::Index n = xy.rows();
    double area = 0.0;
    for (Eigen::Index i = 0; i < n; ++i) {
        const Eigen::Index j = (i + 1) % n;
        area += xy(i, 0) * xy(j, 1) - xy(j, 0) * xy(i, 1);
    }
    return area * 0.5;
}

double signedPolyArea(const VecC& poly) { return signedPolyArea(complexToReal(poly)); }

bool inPolygon(const Complex& p, const VecC& boundary) {
    const MatX xy = complexToReal(boundary);
    const double px = p.real();
    const double py = p.imag();
    bool inside = false;
    const int n = static_cast<int>(xy.rows());
    for (int i = 0, j = n - 1; i < n; j = i++) {
        const double xi = xy(i, 0), yi = xy(i, 1);
        const double xj = xy(j, 0), yj = xy(j, 1);
        const bool intersect = ((yi > py) != (yj > py)) &&
                               (px < (xj - xi) * (py - yi) / ((yj - yi) + 0.0) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
}

VecC polygonOffset(const VecC& input, double d, bool useRelative) {
    MatX x = complexToReal(input);
    const int n0 = static_cast<int>(x.rows());

    std::vector<Complex> e(n0);
    std::vector<double> angles(n0);
    for (int i = 0; i < n0; ++i) {
        const int in = modIndex(i + 1, n0);
        e[i] = Complex(x(i, 0) - x(in, 0), x(i, 1) - x(in, 1));
        angles[i] = std::arg(e[i]);
    }

    std::vector<bool> iscorner(n0);
    for (int i = 0; i < n0; ++i) {
        const int ip = modIndex(i - 1, n0);
        iscorner[i] = std::abs(angles[i] - angles[ip]) > kEps;
    }

    Eigen::SparseMatrix<double> S;
    bool hasStraightEdges = false;
    for (bool c : iscorner) {
        if (!c) {
            hasStraightEdges = true;
            break;
        }
    }

    if (hasStraightEdges) {
        std::vector<int> cornids;
        for (int i = 0; i < n0; ++i) {
            if (iscorner[i]) cornids.push_back(i);
        }
        const int ncorn = static_cast<int>(cornids.size());

        std::vector<int> prevcorn(n0);
        int count = 0;
        for (int i = 0; i < n0; ++i) {
            if (iscorner[i]) ++count;
            prevcorn[i] = count == 0 ? ncorn : count;
        }

        std::vector<int> prevcornidsX(n0), nextcornidsX(n0);
        for (int i = 0; i < n0; ++i) {
            const int pc = prevcorn[i] - 1;
            const int nc = modIndex(prevcorn[i], ncorn);
            prevcornidsX[i] = cornids[pc];
            nextcornidsX[i] = cornids[nc];
        }

        std::vector<Eigen::Triplet<double>> triplets;
        triplets.reserve(n0 * 2);
        for (int i = 0; i < n0; ++i) {
            const double distNext = rowDiff(x, i, nextcornidsX[i]).norm();
            const double distSpan = rowDiff(x, prevcornidsX[i], nextcornidsX[i]).norm();
            const double w = distNext / distSpan;
            const int colPrev = prevcorn[i] - 1;
            const int colNext = modIndex(prevcorn[i], ncorn);
            triplets.emplace_back(i, colPrev, w);
            triplets.emplace_back(i, colNext, 1.0 - w);
        }

        S.resize(n0, ncorn);
        S.setFromTriplets(triplets.begin(), triplets.end());

        MatX xc(ncorn, 2);
        for (int i = 0; i < ncorn; ++i) xc.row(i) = x.row(cornids[i]);
        x = xc;
    }

    const int n = static_cast<int>(x.rows());
    MatX offs(n, 2);
    for (int i = 0; i < n; ++i) {
        const int i1 = modIndex(i - 1, n);
        const int i2 = i;
        const int i3 = modIndex(i + 1, n);

        const double A = x(i1, 0) * (x(i2, 1) - x(i3, 1)) + x(i2, 0) * (x(i3, 1) - x(i1, 1)) +
                         x(i3, 0) * (x(i1, 1) - x(i2, 1));

        Eigen::RowVector2d e1 = x.row(i) - x.row(modIndex(i + 1, n));
        Eigen::RowVector2d e2 = x.row(modIndex(i + n - 2, n)) - x.row(i);
        const double n1 = e1.norm();
        const double n2 = e2.norm();
        offs(i, 0) = (-e1(0) * n2 + e2(0) * n1) / A;
        offs(i, 1) = (-e1(1) * n2 + e2(1) * n1) / A;
    }

    double offsetDist = d;
    if (useRelative) {
        double minEdge = std::numeric_limits<double>::infinity();
        for (int i = 0; i < n; ++i) {
            minEdge = std::min(minEdge, rowDiff(x, i, modIndex(i + 1, n)).norm());
        }
        offsetDist = minEdge * d;
    }

    MatX p(n, 2);
    for (int i = 0; i < n; ++i) {
        p.row(i) = x.row(i) + offsetDist * offs.row(i);
    }

    if (hasStraightEdges) {
        p = S * p;
    }

    return realToComplex(p);
}

SpMatC subdivPolyMat(const VecC& x, int n) {
    const int nx = static_cast<int>(x.size());
    if (n <= nx) {
        SpMatC M(nx, nx);
        for (int i = 0; i < nx; ++i) M.insert(i, i) = Complex(1.0, 0.0);
        M.makeCompressed();
        return M;
    }

    std::vector<double> edgelens(nx);
    double sumLen = 0.0;
    for (int i = 0; i < nx; ++i) {
        const int in = modIndex(i + 1, nx);
        edgelens[i] = std::abs(x[i] - x[in]);
        sumLen += edgelens[i];
    }

    std::vector<int> edgesubs(nx);
    for (int i = 0; i < nx; ++i) {
        edgesubs[i] = static_cast<int>(std::ceil(edgelens[i] / sumLen * n));
        edgesubs[i] = std::max(edgesubs[i], 1);
    }

    std::vector<int> startingrows(nx + 1);
    startingrows[0] = 0;
    for (int i = 0; i < nx; ++i) startingrows[i + 1] = startingrows[i] + edgesubs[i];

    const int nRows = startingrows[nx];
    std::vector<Eigen::Triplet<Complex>> triplets;
    triplets.reserve(nRows * 2);

    for (int i = 0; i < nx; ++i) {
        const int in = modIndex(i + 1, nx);
        for (int r = startingrows[i]; r < startingrows[i + 1]; ++r) {
            const int local = startingrows[i + 1] - r;
            const double w0 = static_cast<double>(local) / edgesubs[i];
            triplets.emplace_back(r, i, Complex(w0, 0.0));
            triplets.emplace_back(r, in, Complex(1.0 - w0, 0.0));
        }
    }

    SpMatC M(nRows, nx);
    M.setFromTriplets(triplets.begin(), triplets.end());
    M.makeCompressed();
    return M;
}

VecC sampleOnPolygon(int n, const VecC& poly) {
    const SpMatC M = subdivPolyMat(poly, n);
    return M * poly;
}

Complex pointInPolygon(const VecC& boundary) {
    const int n = static_cast<int>(boundary.size());
    if (n < 3) {
        throw P2PHarmonicPrepError("pointInPolygon requires at least 3 boundary vertices");
    }

    // Fan triangulation from vertex 0; pick the interior circumcenter farthest from the boundary.
    Complex best(0.0, 0.0);
    double bestDist = -1.0;

    for (int i = 1; i < n - 1; ++i) {
        const Complex a = boundary[0];
        const Complex b = boundary[i];
        const Complex c = boundary[i + 1];

        const double d = 2.0 * (a.real() * (b.imag() - c.imag()) + b.real() * (c.imag() - a.imag()) +
                                 c.real() * (a.imag() - b.imag()));
        if (std::abs(d) < kEps) continue;

        const double ax2ay2 = a.real() * a.real() + a.imag() * a.imag();
        const double bx2by2 = b.real() * b.real() + b.imag() * b.imag();
        const double cx2cy2 = c.real() * c.real() + c.imag() * c.imag();

        const double ux = (ax2ay2 * (b.imag() - c.imag()) + bx2by2 * (c.imag() - a.imag()) +
                           cx2cy2 * (a.imag() - b.imag())) /
                          d;
        const double uy = (ax2ay2 * (c.real() - b.real()) + bx2by2 * (a.real() - c.real()) +
                           cx2cy2 * (b.real() - a.real())) /
                          d;
        const Complex cc(ux, uy);

        if (!inPolygon(cc, boundary)) continue;

        const double distA = std::abs(boundary[0] - cc);
        const double distB = std::abs(boundary[i] - cc);
        const double distC = std::abs(boundary[i + 1] - cc);
        const double dmin = std::min({distA, distB, distC});

        if (dmin > bestDist) {
            bestDist = dmin;
            best = cc;
        }
    }

    if (bestDist >= 0.0) return best;

    // Fallback: centroid shifted slightly inward.
    Complex centroid(0.0, 0.0);
    for (int i = 0; i < n; ++i) centroid += boundary[i];
    centroid /= static_cast<double>(n);
    if (inPolygon(centroid, boundary)) return centroid;

    for (int i = 0; i < n; ++i) {
        const int j = modIndex(i + 1, n);
        const Complex mid = 0.5 * (boundary[i] + boundary[j]);
        if (inPolygon(mid, boundary)) return mid;
    }

    throw P2PHarmonicPrepError("Failed to find an interior point for hole center");
}

bool polygonSelfIntersects(const VecC& poly) {
    const int n = static_cast<int>(poly.size());
    if (n < 4) return false;

    const MatX pts = complexToReal(poly);
    const int nSeg = n;

    auto segBBoxOverlap = [&](int i, int j) {
        const int i0 = i;
        const int i1 = modIndex(i + 1, n);
        const int j0 = j;
        const int j1 = modIndex(j + 1, n);

        const double minx1 = std::min(pts(i0, 0), pts(i1, 0));
        const double maxx1 = std::max(pts(i0, 0), pts(i1, 0));
        const double miny1 = std::min(pts(i0, 1), pts(i1, 1));
        const double maxy1 = std::max(pts(i0, 1), pts(i1, 1));

        const double minx2 = std::min(pts(j0, 0), pts(j1, 0));
        const double maxx2 = std::max(pts(j0, 0), pts(j1, 0));
        const double miny2 = std::min(pts(j0, 1), pts(j1, 1));
        const double maxy2 = std::max(pts(j0, 1), pts(j1, 1));

        return minx1 <= maxx2 && maxx1 >= minx2 && miny1 <= maxy2 && maxy1 >= miny2;
    };

    for (int i = 0; i < nSeg; ++i) {
        for (int j = i + 1; j < nSeg; ++j) {
            if (std::abs(i - j) < 2 || (i == 0 && j == nSeg - 1)) continue;
            if (!segBBoxOverlap(i, j)) continue;

            const int i0 = i, i1 = modIndex(i + 1, n);
            const int j0 = j, j1 = modIndex(j + 1, n);

            const Eigen::Vector2d p1(pts(i0, 0), pts(i0, 1));
            const Eigen::Vector2d p2(pts(i1, 0), pts(i1, 1));
            const Eigen::Vector2d p3(pts(j0, 0), pts(j0, 1));
            const Eigen::Vector2d p4(pts(j1, 0), pts(j1, 1));

            const Eigen::Vector2d d1 = p2 - p1;
            const Eigen::Vector2d d2 = p4 - p3;

            Eigen::Matrix2d A;
            A << d1(0), -d2(0), d1(1), -d2(1);
            const double det = d1(0) * (-d2(1)) - (-d2(0)) * d1(1);
            if (std::abs(det) < kEps) continue;

            const Eigen::Vector2d rhs = p3 - p1;
            const double t0 = (rhs(0) * A(1, 1) - A(0, 1) * rhs(1)) / det;
            const double t1 = (A(0, 0) * rhs(1) - rhs(0) * A(1, 0)) / det;
            if (t0 >= 0.0 && t0 < 1.0 && t1 >= 0.0 && t1 < 1.0) return true;
        }
    }
    return false;
}

}  // namespace p2p_harmonic
