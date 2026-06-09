#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <string>
#include <vector>

#include <Eigen/Core>
#include <Eigen/SparseCore>
#include <Eigen/SparseLU>
#include <imgui.h>
#include <polyscope/curve_network.h>
#include <polyscope/polyscope.h>
#include <polyscope/point_cloud.h>
#include <polyscope/surface_mesh.h>

namespace {

constexpr double kPi = 3.14159265358979323846;

Eigen::Vector3d vcross(const Eigen::Vector3d& a, const Eigen::Vector3d& b) {
    return {a.y() * b.z() - a.z() * b.y(),
            a.z() * b.x() - a.x() * b.z(),
            a.x() * b.y() - a.y() * b.x()};
}

// ── Lightweight Half-Edge Mesh ─────────────────────────────

struct HEMesh {
    struct HalfEdge {
        int toVertex = -1;
        int face     = -1;
        int opposite  = -1;   // index into halfEdges
        int next      = -1;   // index into halfEdges
    };

    struct Edge {
        int he0 = -1;          // first halfedge
        int he1 = -1;          // second halfedge (-1 if boundary)
    };

    struct Face {
        int he = -1;           // first halfedge
    };

    std::vector<Eigen::Vector3d> V;           // vertex positions
    std::vector<Face>            F;           // faces
    std::vector<HalfEdge>        HE;          // halfedges
    std::vector<Edge>            E;           // edges (deduplicated)
    std::vector<int>             boundaryLoops;

    bool build(const std::vector<Eigen::Vector3d>& vertices,
               const std::vector<std::array<int, 3>>& triFaces) {
        V = vertices;
        const int nV = static_cast<int>(V.size());
        const int nT = static_cast<int>(triFaces.size());

        // halfedges: 3 per triangle
        HE.resize(nT * 3);
        F.resize(nT);

        // Map undirected edge (minV, maxV) -> first halfedge index
        std::map<std::pair<int, int>, int> edgeMap;

        for (int t = 0; t < nT; ++t) {
            const auto& tf = triFaces[t];
            for (int k = 0; k < 3; ++k) {
                const int hi = t * 3 + k;
                const int vi = tf[k];
                const int vj = tf[(k + 1) % 3];
                HE[hi].toVertex = vj;
                HE[hi].face     = t;
                HE[hi].next     = t * 3 + (k + 1) % 3;

                auto key = std::make_pair(std::min(vi, vj), std::max(vi, vj));
                auto it  = edgeMap.find(key);
                if (it == edgeMap.end()) {
                    edgeMap[key] = hi;
                } else {
                    const int otherHi = it->second;
                    HE[hi].opposite      = otherHi;
                    HE[otherHi].opposite = hi;
                    edgeMap.erase(it);
                }
            }
            F[t].he = t * 3;
        }

        // Remaining entries in edgeMap are boundary edges
        for (auto& kv : edgeMap) {
            boundaryLoops.push_back(kv.second);
        }

        // Build deduplicated edges
        std::map<std::pair<int, int>, int> dedup;
        for (int hi = 0; hi < static_cast<int>(HE.size()); ++hi) {
            const int vi = HE[hi].toVertex;
            const int opp = HE[hi].opposite;
            const int vj = HE[opp >= 0 ? opp : HE[HE[hi].next].next].toVertex;
            auto key = std::make_pair(std::min(vi, vj), std::max(vi, vj));
            auto it = dedup.find(key);
            if (it == dedup.end()) {
                Edge e;
                e.he0 = hi;
                e.he1 = HE[hi].opposite;
                dedup[key] = static_cast<int>(E.size());
                E.push_back(e);
            }
        }
        return true;
    }

    bool isBoundaryEdge(int ei) const { return E[ei].he1 < 0; }
    bool isBoundaryFace(int fi) const { return false; } // all faces interior

    // ── vertex curvature (angle defect) ───────────
    double vertexCurvature(int vi) const {
        double sum = 0.0;
        for (int hi = 0; hi < static_cast<int>(HE.size()); ++hi) {
            if (HE[hi].toVertex == vi) {
                const int fi = HE[hi].face;
                if (fi < 0) continue;
                const int h0 = F[fi].he;
                const int i0 = HE[h0].toVertex;
                // find previous vertex
                int prevIdx = -1;
                for (int k = 0; k < 3; ++k) {
                    const int hidx = fi * 3 + k;
                    if (HE[hidx].toVertex == vi) {
                        prevIdx = HE[HE[hidx].next].toVertex;
                        break;
                    }
                }
                const Eigen::Vector3d& a = V[i0];
                const Eigen::Vector3d& b = V[vi];
                const Eigen::Vector3d& c = V[prevIdx];
                const Eigen::Vector3d u = (a - b).normalized();
                const Eigen::Vector3d v = (c - b).normalized();
                double dot = u.dot(v);
                dot = std::max(-1.0, std::min(1.0, dot));
                sum += std::acos(dot);
            }
        }
        return 2.0 * kPi - sum;
    }

    // ── local face basis ──────────────────────────
    void faceBasis(int fi, Eigen::Vector3d& e1, Eigen::Vector3d& e2, Eigen::Vector3d& n) const {
        const int h0 = F[fi].he;
        const int h1 = HE[h0].next;
        const int h2 = HE[h1].next;
        const Eigen::Vector3d& p0 = V[HE[h0].toVertex];
        const Eigen::Vector3d& p1 = V[HE[h1].toVertex];
        const Eigen::Vector3d& p2 = V[HE[h2].toVertex];

        e1 = (p1 - p0);
        if (e1.norm() < 1e-12) e1 = Eigen::Vector3d::UnitX();
        e1.normalize();

        const Eigen::Vector3d d1 = p1 - p0;
        const Eigen::Vector3d d2 = p2 - p0;
        n = vcross(d1, d2);
        if (n.norm() < 1e-12) n = Eigen::Vector3d::UnitZ();
        n.normalize();

        e2 = vcross(n, e1);
        if (e2.norm() < 1e-12) e2 = Eigen::Vector3d::UnitY();
        e2.normalize();
    }

    // ── Levi-Civita transport angle across edge ───
    double lcTransport(int ei) const {
        const int hi = E[ei].he0;
        if (E[ei].he1 < 0) return 0.0;
        const int hj = E[ei].he1;
        const int fi = HE[hi].face;
        const int fj = HE[hj].face;

        Eigen::Vector3d e1i, e2i, ni;
        Eigen::Vector3d e1j, e2j, nj;
        faceBasis(fi, e1i, e2i, ni);
        faceBasis(fj, e1j, e2j, nj);

        const Eigen::Vector3d u = V[HE[hj].toVertex] - V[HE[hi].toVertex];
        const double thetaIJ = std::atan2(u.dot(e2i), u.dot(e1i));
        const double thetaJI = std::atan2(u.dot(e2j), u.dot(e1j));
        return -thetaIJ + thetaJI;
    }

    int chi() const {
        return static_cast<int>(V.size()) - static_cast<int>(E.size()) + static_cast<int>(F.size());
    }
};

// ── Auto-singularity placement ────────────────────────────

std::vector<int> autoSingularity(const HEMesh& m, const Eigen::VectorXd& K, int N = 1) {
    const int nV = static_cast<int>(m.V.size());
    std::vector<int> q(nV, 0);
    const int target = N * m.chi();
    if (target == 0) return q;

    std::vector<std::pair<double, int>> ranked;
    for (int i = 0; i < nV; ++i)
        ranked.emplace_back(std::abs(K[i]), i);
    std::sort(ranked.begin(), ranked.end(),
              [](auto& a, auto& b) { return a.first > b.first; });

    const int sign = target > 0 ? 1 : -1;
    int need = std::abs(target);
    for (size_t i = 0; i < ranked.size() && need > 0; ++i) {
        q[ranked[i].second] = sign;
        need--;
    }
    return q;
}

// ── Trivial Connection (N=1) ───────────────────────────────

struct ConnectionResult {
    std::vector<double>         edgePhi;       // connection correction per edge
    std::vector<double>         faceAlpha;     // per-face angle (rad)
    std::vector<Eigen::Vector3d> faceVector;   // 3D vector per face
    std::vector<Eigen::Vector3d> faceCenters;  // face centers
    std::vector<int>            singularities; // per-vertex singularity index
    bool success = false;
};

ConnectionResult solveTrivialConnection(const HEMesh& m,
                                        const std::vector<int>& singularities) {
    ConnectionResult r;
    const int nV = static_cast<int>(m.V.size());
    const int nE = static_cast<int>(m.E.size());
    const int nF = static_cast<int>(m.F.size());

    r.singularities = singularities;

    // vertex curvature
    Eigen::VectorXd K(nV);
    for (int i = 0; i < nV; ++i) K[i] = m.vertexCurvature(i);

    // B: vertex-edge incidence (primal)
    std::vector<Eigen::Triplet<double>> trips;
    trips.reserve(nE * 2);
    for (int ei = 0; ei < nE; ++ei) {
        const int i = m.HE[m.E[ei].he0].toVertex;
        const int j = m.HE[m.E[ei].he0].opposite >= 0
                          ? m.HE[m.E[ei].he0].opposite
                          : -1;
        const int vj = (j >= 0) ? m.HE[j].toVertex : -1;
        if (vj < 0) continue;
        trips.emplace_back(i, ei, 1.0);
        trips.emplace_back(vj, ei, -1.0);
    }
    Eigen::SparseMatrix<double> B(nV, nE);
    B.setFromTriplets(trips.begin(), trips.end());

    // rhs = 2π * s - K
    Eigen::VectorXd rhs(nV);
    for (int i = 0; i < nV; ++i) rhs[i] = 2.0 * kPi * singularities[i] - K[i];

    // KKT: [ I  Bᵀ ] [ x ] = [ 0  ]
    //      [ B  0  ] [ λ ]   [ rhs ]
    const int Nsys = nE + nV;
    std::vector<Eigen::Triplet<double>> kkt;
    kkt.reserve(nE + 2 * B.nonZeros() + 1);
    for (int i = 0; i < nE; ++i) kkt.emplace_back(i, i, 1.0);
    for (int k = 0; k < B.outerSize(); ++k) {
        for (Eigen::SparseMatrix<double>::InnerIterator it(B, k); it; ++it) {
            kkt.emplace_back(it.col(), nE + it.row(), it.value());
            kkt.emplace_back(nE + it.row(), it.col(), it.value());
        }
    }
    kkt.emplace_back(nE, nE, 1e-12);  // gauge fix

    Eigen::SparseMatrix<double> KKT(Nsys, Nsys);
    KKT.setFromTriplets(kkt.begin(), kkt.end());

    Eigen::VectorXd b = Eigen::VectorXd::Zero(Nsys);
    b.tail(nV) = rhs;

    Eigen::SparseLU<Eigen::SparseMatrix<double>> solver;
    solver.analyzePattern(KKT);
    solver.factorize(KKT);
    if (solver.info() != Eigen::Success) return r;

    Eigen::VectorXd sol = solver.solve(b);
    if (solver.info() != Eigen::Success) return r;

    Eigen::VectorXd x = sol.head(nE);  // connection correction φ per edge
    r.edgePhi.assign(x.data(), x.data() + nE);

    // Propagate per-face angles via BFS on dual graph
    std::vector<double> alpha(nF, 0.0);
    std::vector<char> visited(nF, 0);
    std::queue<int> q;
    visited[0] = 1;
    q.push(0);

    while (!q.empty()) {
        const int fi = q.front(); q.pop();
        // iterate over 3 halfedges of this face
        for (int k = 0; k < 3; ++k) {
            const int hi = fi * 3 + k;
            const int op = m.HE[hi].opposite;
            if (op < 0) continue;  // boundary
            const int fj = m.HE[op].face;
            if (fj < 0 || visited[fj]) continue;

            // find which edge this halfedge belongs to
            const int vi = m.HE[hi].toVertex;
            const int vj = m.HE[m.HE[hi].next].toVertex;
            int ei = -1;
            for (int e = 0; e < nE; ++e) {
                const int a = m.HE[m.E[e].he0].toVertex;
                const int b = (m.E[e].he1 >= 0) ? m.HE[m.E[e].he1].toVertex : -1;
                if ((a == vi && b == vj) || (a == vj && b == vi)) {
                    ei = e;
                    break;
                }
            }
            assert(ei >= 0);

            const double sign = (hi == m.E[ei].he0) ? 1.0 : -1.0;
            const double tau = m.lcTransport(ei);
            const double conn = sign * x[ei];

            alpha[fj] = alpha[fi] + tau - conn;
            visited[fj] = 1;
            q.push(fj);
        }
    }
    r.faceAlpha = alpha;

    // Convert to 3D vectors
    r.faceVector.resize(nF);
    r.faceCenters.resize(nF);
    for (int fi = 0; fi < nF; ++fi) {
        Eigen::Vector3d e1, e2, n;
        m.faceBasis(fi, e1, e2, n);
        const double a = alpha[fi];
        r.faceVector[fi] = (std::cos(a) * e1 + std::sin(a) * e2).normalized();

        const int h0 = m.F[fi].he;
        const int v0 = m.HE[h0].toVertex;
        const int v1 = m.HE[m.HE[h0].next].toVertex;
        const int v2 = m.HE[m.HE[m.HE[h0].next].next].toVertex;
        r.faceCenters[fi] = (m.V[v0] + m.V[v1] + m.V[v2]) / 3.0;
    }
    r.success = true;
    return r;
}

// ── N-RoSy Trivial Connection ──────────────────────────────

struct NRosyResult {
    std::vector<double>          edgePhi;
    std::vector<double>          edgeJump;      // period jumps p (integer)
    std::vector<double>          edgeResidual;   // continuous part
    std::vector<std::vector<Eigen::Vector3d>> faceDirs; // N directions per face
    std::vector<Eigen::Vector3d> faceCenters;
    std::vector<Eigen::Vector3d> faceVectors;    // primary direction (k=0)
    std::vector<int>             singularitiesQ;
    int N;
    bool success = false;
};

NRosyResult solveNRosyConnection(const HEMesh& m,
                                  const std::vector<int>& qVals, int N) {
    NRosyResult r;
    r.N = N;
    const int nV = static_cast<int>(m.V.size());
    const int nE = static_cast<int>(m.E.size());
    const int nF = static_cast<int>(m.F.size());
    r.singularitiesQ = qVals;

    // vertex curvature
    Eigen::VectorXd K(nV);
    for (int i = 0; i < nV; ++i) K[i] = m.vertexCurvature(i);

    // B incidence
    std::vector<Eigen::Triplet<double>> trips;
    trips.reserve(nE * 2);
    for (int ei = 0; ei < nE; ++ei) {
        const int i = m.HE[m.E[ei].he0].toVertex;
        const int j = m.HE[m.E[ei].he0].opposite;
        if (j < 0) continue;
        const int vj = m.HE[j].toVertex;
        trips.emplace_back(i, ei, 1.0);
        trips.emplace_back(vj, ei, -1.0);
    }
    Eigen::SparseMatrix<double> B(nV, nE);
    B.setFromTriplets(trips.begin(), trips.end());

    // rhs = 2π * q/N - K
    Eigen::VectorXd rhs(nV);
    for (int i = 0; i < nV; ++i)
        rhs[i] = 2.0 * kPi * (static_cast<double>(qVals[i]) / N) - K[i];

    // KKT solve
    const int Nsys = nE + nV;
    std::vector<Eigen::Triplet<double>> kkt;
    kkt.reserve(nE + 2 * B.nonZeros() + 1);
    for (int i = 0; i < nE; ++i) kkt.emplace_back(i, i, 1.0);
    for (int k = 0; k < B.outerSize(); ++k) {
        for (Eigen::SparseMatrix<double>::InnerIterator it(B, k); it; ++it) {
            kkt.emplace_back(it.col(), nE + it.row(), it.value());
            kkt.emplace_back(nE + it.row(), it.col(), it.value());
        }
    }
    kkt.emplace_back(nE, nE, 1e-12);

    Eigen::SparseMatrix<double> KKT(Nsys, Nsys);
    KKT.setFromTriplets(kkt.begin(), kkt.end());
    Eigen::VectorXd b = Eigen::VectorXd::Zero(Nsys);
    b.tail(nV) = rhs;

    Eigen::SparseLU<Eigen::SparseMatrix<double>> solver;
    solver.analyzePattern(KKT);
    solver.factorize(KKT);
    if (solver.info() != Eigen::Success) return r;
    Eigen::VectorXd sol = solver.solve(b);
    if (solver.info() != Eigen::Success) return r;
    Eigen::VectorXd phi = sol.head(nE);

    // Period jumps
    const double period = 2.0 * kPi / N;
    std::vector<double> p(nE), residual(nE);
    for (int ei = 0; ei < nE; ++ei) {
        p[ei]       = std::round(phi[ei] / period);
        residual[ei]= phi[ei] - p[ei] * period;
    }
    r.edgePhi     = std::vector<double>(phi.data(), phi.data() + nE);
    r.edgeJump    = p;
    r.edgeResidual= residual;

    // Propagate angles
    std::vector<double> alpha(nF, 0.0);
    std::vector<char> visited(nF, 0);
    std::queue<int> qf;
    visited[0] = 1;
    qf.push(0);

    while (!qf.empty()) {
        const int fi = qf.front(); qf.pop();
        for (int k = 0; k < 3; ++k) {
            const int hi = fi * 3 + k;
            const int op = m.HE[hi].opposite;
            if (op < 0) continue;
            const int fj = m.HE[op].face;
            if (fj < 0 || visited[fj]) continue;

            // find edge
            const int vi = m.HE[hi].toVertex;
            const int vj = m.HE[m.HE[hi].next].toVertex;
            int ei = -1;
            for (int e = 0; e < nE; ++e) {
                const int a = m.HE[m.E[e].he0].toVertex;
                const int b = (m.E[e].he1 >= 0) ? m.HE[m.E[e].he1].toVertex : -1;
                if ((a == vi && b == vj) || (a == vj && b == vi)) { ei = e; break; }
            }
            assert(ei >= 0);

            const double sgn = (hi == m.E[ei].he0) ? 1.0 : -1.0;
            const double tau = m.lcTransport(ei);
            alpha[fj] = alpha[fi] + tau - sgn * residual[ei];
            visited[fj] = 1;
            qf.push(fj);
        }
    }

    // Generate N directions per face
    r.faceDirs.resize(nF);
    r.faceVectors.resize(nF);
    r.faceCenters.resize(nF);
    for (int fi = 0; fi < nF; ++fi) {
        Eigen::Vector3d e1, e2, n;
        m.faceBasis(fi, e1, e2, n);
        const double aMod = std::fmod(alpha[fi], period);
        const double baseAngle = (aMod < 0) ? aMod + period : aMod;

        r.faceDirs[fi].resize(N);
        for (int k = 0; k < N; ++k) {
            const double ak = baseAngle + k * period;
            r.faceDirs[fi][k] = (std::cos(ak) * e1 + std::sin(ak) * e2).normalized();
        }
        r.faceVectors[fi] = r.faceDirs[fi][0];

        const int h0 = m.F[fi].he;
        const int v0 = m.HE[h0].toVertex;
        const int v1 = m.HE[m.HE[h0].next].toVertex;
        const int v2 = m.HE[m.HE[m.HE[h0].next].next].toVertex;
        r.faceCenters[fi] = (m.V[v0] + m.V[v1] + m.V[v2]) / 3.0;
    }
    r.success = true;
    return r;
}

// ── Read simple OBJ (vertices + triangle faces only) ──────

bool readObj(const std::string& path,
             std::vector<Eigen::Vector3d>& V,
             std::vector<std::array<int, 3>>& F) {
    std::ifstream in(path);
    if (!in.is_open()) return false;
    std::string line;
    while (std::getline(in, line)) {
        if (line.empty() || line[0] == '#') continue;
        if (line[0] == 'v' && line[1] == ' ') {
            double x, y, z;
            if (sscanf(line.c_str(), "v %lf %lf %lf", &x, &y, &z) == 3)
                V.push_back({x, y, z});
        } else if (line[0] == 'f' && line[1] == ' ') {
            // Strip texture/normal indices: v//n → v, v/t/n → v
            auto strip = [](std::string& s) {
                for (char& ch : s) {
                    if (ch == '/') ch = ' ';
                }
            };
            strip(line);
            int a, b, c, d;
            int n = sscanf(line.c_str(), "f %d %d %d %d", &a, &b, &c, &d);
            if (n >= 3)
                F.push_back({a - 1, b - 1, c - 1});
        }
    }
    return !V.empty() && !F.empty();
}

// ── Generate a simple sphere mesh ─────────────────────────

void makeSphere(double radius, int lat, int lon,
                std::vector<Eigen::Vector3d>& V,
                std::vector<std::array<int, 3>>& F) {
    V.clear(); F.clear();
    V.push_back({0, 0, radius});   // north pole

    for (int i = 1; i < lat; ++i) {
        double phi = kPi * i / lat;
        double z = radius * std::cos(phi);
        double r = radius * std::sin(phi);
        for (int j = 0; j < lon; ++j) {
            double theta = 2.0 * kPi * j / lon;
            V.push_back({r * std::cos(theta), r * std::sin(theta), z});
        }
    }
    V.push_back({0, 0, -radius});   // south pole

    // north cap
    for (int j = 0; j < lon; ++j)
        F.push_back({0, 1 + j, 1 + (j + 1) % lon});

    // middle bands
    for (int i = 1; i < lat - 1; ++i) {
        for (int j = 0; j < lon; ++j) {
            int bl = 1 + (i - 1) * lon + j;
            int br = 1 + (i - 1) * lon + (j + 1) % lon;
            int tl = 1 + i * lon + j;
            int tr = 1 + i * lon + (j + 1) % lon;
            F.push_back({bl, br, tl});
            F.push_back({br, tr, tl});
        }
    }

    // south cap
    int south = 1 + (lat - 1) * lon;
    for (int j = 0; j < lon; ++j) {
        int b = 1 + (lat - 2) * lon + j;
        int c = 1 + (lat - 2) * lon + (j + 1) % lon;
        F.push_back({south, c, b});
    }
}

}  // namespace

// ── Model Manager ───────────────────────────────────────

struct ModelInfo {
    std::string path;
    std::string name;
};

// ── Streamline Tracing ────────────────────────────────────

// Barycentric point-in-triangle test
bool pointInTriangle(const Eigen::Vector3d& p,
                     const Eigen::Vector3d& a,
                     const Eigen::Vector3d& b,
                     const Eigen::Vector3d& c,
                     Eigen::Vector3d& bary) {
    const Eigen::Vector3d v0 = c - a, v1 = b - a, v2 = p - a;
    const double d00 = v0.dot(v0), d01 = v0.dot(v1);
    const double d11 = v1.dot(v1), d20 = v2.dot(v0), d21 = v2.dot(v1);
    const double denom = d00 * d11 - d01 * d01;
    if (std::abs(denom) < 1e-14) return false;
    bary = {(d11 * d20 - d01 * d21) / denom,
            (d00 * d21 - d01 * d20) / denom,
            0.0};
    bary.z() = 1.0 - bary.x() - bary.y();
    return bary.x() >= -1e-6 && bary.y() >= -1e-6 && bary.z() >= -1e-6;
}

// Find which edge of a triangle a ray exits through
int exitingEdge(const Eigen::Vector3d& p, const Eigen::Vector3d& dir,
                const Eigen::Vector3d& a, const Eigen::Vector3d& b, const Eigen::Vector3d& c,
                double& tExit, double stepLen) {
    // Project to triangle plane and find intersection with edges
    const Eigen::Vector3d n = vcross(b - a, c - a);
    const double nLen = n.norm();
    if (nLen < 1e-12) return -1;
    const Eigen::Vector3d nn = n / nLen;

    // Project direction onto plane
    const Eigen::Vector3d d = (dir - dir.dot(nn) * nn).normalized();

    double tMin = 1e10;
    int bestEdge = -1;
    const std::array<std::pair<Eigen::Vector3d, Eigen::Vector3d>, 3> edges = {{
        {a, b}, {b, c}, {c, a}
    }};

    for (int ei = 0; ei < 3; ++ei) {
        const Eigen::Vector3d e = edges[ei].second - edges[ei].first;
        const Eigen::Vector3d perp = vcross(nn, e);
        const double denom = perp.dot(d);
        if (std::abs(denom) < 1e-12) continue;
        const double t = perp.dot(edges[ei].first - p) / denom;
        if (t > 1e-8 && t < tMin && t < stepLen * 2) {
            const Eigen::Vector3d hit = p + t * d;
            const double edgeLen = e.norm();
            if (edgeLen < 1e-12) continue;
            const double proj = (hit - edges[ei].first).dot(e) / (edgeLen * edgeLen);
            if (proj >= -1e-6 && proj <= 1.000001) {
                tMin = t;
                tExit = t;
                bestEdge = ei;
            }
        }
    }
    return bestEdge;
}

// Trace a single streamline from a seed point
std::vector<Eigen::Vector3d> traceStreamline(
    const Eigen::Vector3d& seed,
    const std::vector<Eigen::Vector3d>& V,
    const std::vector<std::array<int, 3>>& F,
    const std::vector<Eigen::Vector3d>& faceVecs,
    const HEMesh& mesh,
    int maxSteps, double stepLen) {

    std::vector<Eigen::Vector3d> points;

    // Find starting face
    int currentFace = -1;
    Eigen::Vector3d seedPt = seed;
    for (int fi = 0; fi < int(F.size()); ++fi) {
        const auto& tf = F[fi];
        Eigen::Vector3d bary;
        if (pointInTriangle(seedPt, V[tf[0]], V[tf[1]], V[tf[2]], bary)) {
            currentFace = fi;
            break;
        }
    }
    if (currentFace < 0) return points;

    points.push_back(seedPt);

    for (int step = 0; step < maxSteps; ++step) {
        const auto& tf = F[currentFace];
        const Eigen::Vector3d& a = V[tf[0]];
        const Eigen::Vector3d& b = V[tf[1]];
        const Eigen::Vector3d& c = V[tf[2]];

        // Get vector direction at current face
        Eigen::Vector3d dir = faceVecs[currentFace];
        if (dir.norm() < 1e-8) break;

        double tExit = stepLen;
        int edgeIdx = exitingEdge(seedPt, dir, a, b, c, tExit, stepLen);
        if (edgeIdx < 0) tExit = stepLen;

        // Step forward
        Eigen::Vector3d n = vcross(b - a, c - a).normalized();
        Eigen::Vector3d dProj = (dir - dir.dot(n) * n).normalized();
        seedPt = seedPt + dProj * tExit;
        points.push_back(seedPt);

        if (edgeIdx < 0) break;  // stuck inside

        // Find neighbor face across this edge
        const int h0 = mesh.F[currentFace].he;
        int he = h0;
        int nextFace = -1;
        // The edge indices in our triangle: 0=AB, 1=BC, 2=CA
        // The halfedges in face: h0=AB, h0+1=BC, h0+2=CA
        const int heIdx = h0 + edgeIdx;
        if (heIdx < int(mesh.HE.size())) {
            const int opp = mesh.HE[heIdx].opposite;
            if (opp >= 0) nextFace = mesh.HE[opp].face;
        }

        if (nextFace < 0 || nextFace >= int(faceVecs.size())) break;
        currentFace = nextFace;
    }
    return points;
}

// Generate and register streamlines for a vector field
void addStreamlines(
    const std::string& name,
    const std::vector<Eigen::Vector3d>& V,
    const std::vector<std::array<int, 3>>& F,
    const std::vector<Eigen::Vector3d>& faceVecs,
    const std::vector<Eigen::Vector3d>& faceCenters,
    const HEMesh& mesh,
    int numSeeds, double stepLen, int maxSteps,
    const glm::vec3& color) {

    std::vector<Eigen::Vector3d> allNodes;
    std::vector<std::array<size_t, 2>> allEdges;

    // Seed from random face centers
    std::mt19937 rng(42);
    std::uniform_int_distribution<int> dist(0, int(faceCenters.size()) - 1);

    for (int s = 0; s < numSeeds; ++s) {
        const int fi = dist(rng);
        // Trace forward
        auto fwd = traceStreamline(faceCenters[fi], V, F, faceVecs, mesh, maxSteps, stepLen);
        // Trace backward
        std::vector<Eigen::Vector3d> negVecs = faceVecs;
        for (auto& v : negVecs) v = -v;
        auto bwd = traceStreamline(faceCenters[fi], V, F, negVecs, mesh, maxSteps, stepLen);
        std::reverse(bwd.begin(), bwd.end());

        // Merge: bwd... + seed + fwd...
        if (fwd.size() < 2 && bwd.size() < 2) continue;

        std::vector<Eigen::Vector3d> curve;
        for (auto& p : bwd) curve.push_back(p);
        if (!fwd.empty()) {
            if (!bwd.empty() && (bwd.back() - fwd[0]).norm() > stepLen * 0.5)
                curve.push_back(faceCenters[fi]);
            for (size_t i = 0; i < fwd.size(); ++i)
                curve.push_back(fwd[i]);
        }

        if (curve.size() < 2) continue;

        // Convert to edge list
        size_t base = allNodes.size();
        for (auto& p : curve) allNodes.push_back(p);
        for (size_t i = 0; i + 1 < curve.size(); ++i)
            allEdges.push_back({base + i, base + i + 1});
    }

    if (!allNodes.empty()) {
        auto* cn = polyscope::registerCurveNetwork(name, allNodes, allEdges);
        cn->setRadius(0.002);
        cn->setColor(color);
    }
}

// ── Compute & visualize vector fields for a given mesh ───

void computeAndShow(const std::vector<Eigen::Vector3d>& V,
                    const std::vector<std::array<int, 3>>& F,
                    const HEMesh& mesh) {
    // Remove old structures
    polyscope::removeAllStructures();

    // ── N=1 Trivial Connection Vector Field ──────────
    std::vector<int> sing1(mesh.V.size(), 0);
    {
        Eigen::VectorXd K(mesh.V.size());
        for (size_t i = 0; i < mesh.V.size(); ++i) K[int(i)] = mesh.vertexCurvature(int(i));
        sing1 = autoSingularity(mesh, K, 1);
    }

    int sumS = 0;
    for (int s : sing1) sumS += s;
    std::cout << "  N=1 singularities: " << sumS << " / χ=" << mesh.chi() << "\n";

    auto r1 = solveTrivialConnection(mesh, sing1);
    if (r1.success) {
        auto* ps1 = polyscope::registerSurfaceMesh("vector_field_N1", V, F);
        auto* q1 = ps1->addFaceVectorQuantity("field", r1.faceVector);
        q1->setVectorLengthScale(0.06);
        q1->setVectorRadius(0.003);
        q1->setVectorColor({0.2, 0.6, 0.9});

        // N=1 streamlines
        addStreamlines("streamlines_N1", V, F, r1.faceVector, r1.faceCenters,
                       mesh, 60, 0.03, 100, {0.3f, 0.7f, 1.0f});

        std::vector<Eigen::Vector3d> singPos;
        for (size_t i = 0; i < sing1.size(); ++i)
            if (sing1[i] != 0) singPos.push_back(V[i]);
        if (!singPos.empty()) {
            auto* pc1 = polyscope::registerPointCloud("singularities_N1", singPos);
            pc1->setPointRadius(0.02);
            pc1->setPointColor(glm::vec3{1.0f, 0.2f, 0.2f});
        }
    }

    // ── N=4 N-RoSy Field ─────────────────────────────
    const int N = 4;
    std::vector<int> singN(mesh.V.size(), 0);
    {
        Eigen::VectorXd K(mesh.V.size());
        for (size_t i = 0; i < mesh.V.size(); ++i) K[int(i)] = mesh.vertexCurvature(int(i));
        singN = autoSingularity(mesh, K, N);
    }

    int sumQ = 0;
    for (int q : singN) sumQ += q;
    std::cout << "  N=4 singularities: " << sumQ << " / expected=" << N * mesh.chi() << "\n";

    auto rN = solveNRosyConnection(mesh, singN, N);
    if (rN.success) {
        auto* psN = polyscope::registerSurfaceMesh("nrosy_field_N4", V, F);
        for (int k = 0; k < N; ++k) {
            std::vector<Eigen::Vector3d> dirs;
            dirs.reserve(rN.faceDirs.size());
            for (auto& dset : rN.faceDirs) dirs.push_back(dset[k]);
            auto* qk = psN->addFaceVectorQuantity("direction_" + std::to_string(k), dirs);
            qk->setVectorLengthScale(0.05);
            qk->setVectorRadius(0.002);
            qk->setEnabled(k == 0);
        }
        auto* qp = psN->addFaceVectorQuantity("primary", rN.faceVectors);
        qp->setVectorLengthScale(0.06);
        qp->setVectorRadius(0.003);
        qp->setVectorColor({0.9, 0.6, 0.2});

        // N=4 streamlines
        addStreamlines("streamlines_N4", V, F, rN.faceVectors, rN.faceCenters,
                       mesh, 40, 0.03, 80, {1.0f, 0.6f, 0.2f});

        std::vector<Eigen::Vector3d> singPosN;
        for (size_t i = 0; i < singN.size(); ++i)
            if (singN[i] != 0) singPosN.push_back(V[i]);
        if (!singPosN.empty()) {
            auto* pc4 = polyscope::registerPointCloud("singularities_N4", singPosN);
            pc4->setPointRadius(0.02);
            pc4->setPointColor(glm::vec3{1.0f, 0.3f, 0.0f});
        }
    }
}

// ── Main ─────────────────────────────────────────────

int main(int argc, char** argv) {
    polyscope::init();
    polyscope::options::groundPlaneMode = polyscope::GroundPlaneMode::ShadowOnly;
    polyscope::options::buildGui = true;

    // ── Discover models ─────────────────────────────
    const std::vector<std::string> modelDirs = {
        "../../../assets/Models2",
        "../assets/Models2",
        "../../assets/Models2",
    };

    std::vector<ModelInfo> models;
    models.push_back({"__sphere__", "⚪ Sphere (built-in)"});

    for (const auto& dir : modelDirs) {
        if (std::filesystem::is_directory(dir)) {
            for (const auto& entry : std::filesystem::directory_iterator(dir)) {
                if (entry.path().extension() == ".obj")
                    models.push_back({entry.path().string(),
                                      entry.path().filename().string()});
            }
            std::sort(models.begin() + 1, models.end(),
                      [](auto& a, auto& b) { return a.name < b.name; });
            break;
        }
    }

    if (models.size() == 1)
        std::cerr << "Warning: No Models2 directory found!\n";

    // ── State ────────────────────────────────────────
    int currentIdx = 0;
    bool needReload = true;

    // ── UI callback with dropdown ────────────────────
    polyscope::state::userCallback = [&]() {
        ImGui::PushItemWidth(280);
        if (ImGui::BeginCombo("##model", models[currentIdx].name.c_str())) {
            for (int i = 0; i < int(models.size()); ++i) {
                bool isSel = (i == currentIdx);
                if (ImGui::Selectable(models[i].name.c_str(), &isSel)) {
                    currentIdx = i;
                    needReload = true;
                }
                if (isSel) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }
        ImGui::PopItemWidth();

        if (needReload) {
            std::vector<Eigen::Vector3d> V;
            std::vector<std::array<int, 3>> F;

            if (models[currentIdx].path == "__sphere__") {
                makeSphere(1.0, 20, 40, V, F);
                std::cout << "[Sphere] ";
            } else {
                readObj(models[currentIdx].path, V, F);
                std::cout << "[" << models[currentIdx].name << "] ";
            }
            std::cout << V.size() << "v " << F.size() << "f\n";

            HEMesh mesh;
            mesh.build(V, F);
            computeAndShow(V, F, mesh);
            polyscope::view::resetCameraToHomeView();
            needReload = false;
        }
    };

    polyscope::view::lookAt({2.2, 1.0, 1.5}, {0, 0, 0});
    polyscope::show();
    return 0;
}
