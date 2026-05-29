/**
 * principal_curvature_wasm.cpp
 *   Per-face / per-vertex principal curvature using project's own geometry module
 *   (replaces libigl-based version).
 *
 * API (backward-compatible with the old libigl wrapper):
 *   compute_principal_curvature(V_ptr, V_rows, F_ptr, F_rows) → int (0 ok)
 *   get_pc_pd1() / get_pc_pd2()  → double* (per-face, nF*3)
 *   get_pc_pv1() / get_pc_pv2()  → double* (per-face, nF)
 *   get_pc_num_faces()           → int
 *   get_pc_pd1_vert() / get_pc_pd2_vert() → double* (per-vertex, nV*3)
 *   get_pc_pv1_vert() / get_pc_pv2_vert() → double* (per-vertex, nV)
 *   get_pc_num_verts()           → int
 *   pc_dispose()                 → void
 */
#include <emscripten.h>
#include <Eigen/Dense>
#include <vector>
#include <cmath>

namespace {

// ================================================================
//  Weingarten-based principal curvature (per-face)
//  Adapted from geometry/PrincipalCurvatureField.cpp
//  (inline to keep this WASM target self-contained)
// ================================================================

void weingartenPrincipalCurvatures(
    const Eigen::MatrixXd& V,
    const Eigen::VectorXi& F,
    const Eigen::MatrixXd& vN,
    const Eigen::MatrixXd& fN,
    Eigen::MatrixXd& faceDirs,
    Eigen::MatrixXd& k1k2)
{
    const int nF = static_cast<int>(F.size() / 3);

    faceDirs.resize(nF, 3);
    k1k2.resize(nF, 2);

    for (int fi = 0; fi < nF; ++fi) {
        const int a = F(fi * 3);
        const int b = F(fi * 3 + 1);
        const int c = F(fi * 3 + 2);

        const Eigen::Vector3d p0 = V.row(a);
        const Eigen::Vector3d p1 = V.row(b);
        const Eigen::Vector3d p2 = V.row(c);

        // Face tangent basis
        const Eigen::Vector3d e1 = p1 - p0;
        const Eigen::Vector3d e2 = p2 - p0;
        const Eigen::Vector3d Nf = fN.row(fi);

        // Weingarten operator: dN in face tangent plane
        const Eigen::Vector3d dN1 = vN.row(b) - vN.row(a);
        const Eigen::Vector3d dN2 = vN.row(c) - vN.row(a);

        // Project dN onto tangent basis (discard normal component)
        const double dN1_u = dN1.dot(e1);
        const double dN1_v = dN1.dot(e2);
        const double dN2_u = dN2.dot(e1);
        const double dN2_v = dN2.dot(e2);

        // E, F, G: first fundamental form
        const double E = e1.dot(e1);
        const double F_ig = e1.dot(e2);
        const double G = e2.dot(e2);
        const double detI = E * G - F_ig * F_ig;
        if (std::abs(detI) < 1e-14) {
            // Degenerate face: pick any tangent direction
            faceDirs.row(fi) = e1.normalized();
            k1k2(fi, 0) = 0.0;
            k1k2(fi, 1) = 0.0;
            continue;
        }
        const double invDetI = 1.0 / detI;

        // Second fundamental form: L, M, N
        // Using dN · e = -de · N  (since d(N·e)=0 along surface)
        // → dN1 acts on e1,e2 gives L,M; dN2 acts gives M,N
        const double L = -(dN1.dot(e1));
        const double M1 = -(dN1.dot(e2));
        const double M2 = -(dN2.dot(e1));
        const double M = 0.5 * (M1 + M2);
        const double N_ig = -(dN2.dot(e2));

        // Shape operator S = I^{-1} * II  (in {e1,e2} basis)
        const double S11 = invDetI * (L * G - M * F_ig);
        const double S12 = invDetI * (M * G - N_ig * F_ig);
        const double S21 = invDetI * (M * E - L * F_ig);
        const double S22 = invDetI * (N_ig * E - M * F_ig);

        // Eigenvalues and eigenvectors of symmetric part (make symmetric)
        const double sAvg11 = S11;
        const double sAvg22 = S22;
        const double sAvg12 = 0.5 * (S12 + S21);

        // 2×2 eigenvalue decomposition of [s11 s12; s12 s22]
        const double trace = sAvg11 + sAvg22;
        const double det = sAvg11 * sAvg22 - sAvg12 * sAvg12;
        const double disc = std::sqrt(std::max(0.0, trace * trace - 4.0 * det));

        const double k1 = 0.5 * (trace + disc);  // larger magnitude (main curvature)
        const double k2 = 0.5 * (trace - disc);

        k1k2(fi, 0) = k1;
        k1k2(fi, 1) = k2;

        // Dominant direction (by |k|)
        const double dominantK = (std::abs(k1) >= std::abs(k2)) ? k1 : k2;
        double eigVecU, eigVecV;
        if (std::abs(k1 - k2) > 1e-10) {
            const double targetK = dominantK;
            if (std::abs(sAvg12) > 1e-14) {
                eigVecU = targetK - sAvg22;
                eigVecV = sAvg12;
            } else {
                eigVecU = 1.0;
                eigVecV = 0.0;
            }
        } else {
            // Umbilical point: any direction
            eigVecU = 1.0;
            eigVecV = 0.0;
        }

        // Normalize eigenvector in tangent basis
        double vLen = std::hypot(eigVecU, eigVecV);
        if (vLen < 1e-12) {
            eigVecU = 1.0;
            eigVecV = 0.0;
            vLen = 1.0;
        }
        eigVecU /= vLen;
        eigVecV /= vLen;

        // Map back to 3D
        faceDirs.row(fi) = (eigVecU * e1 + eigVecV * e2).normalized();
    }
}

} // anonymous namespace


// ---- global state ----
static std::vector<double> g_pd1_face, g_pd2_face;
static std::vector<double> g_pv1_face, g_pv2_face;
static std::vector<double> g_pd1_vert, g_pd2_vert;
static std::vector<double> g_pv1_vert, g_pv2_vert;
static int g_nV = 0, g_nF = 0;


extern "C" {

EMSCRIPTEN_KEEPALIVE
int compute_principal_curvature(double* V_ptr, int V_rows, int* F_ptr, int F_rows) {
    g_pd1_face.clear(); g_pd2_face.clear();
    g_pv1_face.clear(); g_pv2_face.clear();
    g_pd1_vert.clear(); g_pd2_vert.clear();
    g_pv1_vert.clear(); g_pv2_vert.clear();
    g_nV = 0; g_nF = 0;

    if (!V_ptr || !F_ptr || V_rows < 3 || F_rows < 3) return -1;

    try {
        Eigen::Map<const Eigen::Matrix<double, Eigen::Dynamic, 3, Eigen::RowMajor>> V_map(V_ptr, V_rows, 3);
        Eigen::Map<const Eigen::Matrix<int, Eigen::Dynamic, 3, Eigen::RowMajor>> F_map(F_ptr, F_rows, 3);
        Eigen::MatrixXd V = V_map;
        Eigen::VectorXi F(F_rows * 3);
        for (int i = 0; i < F_rows; ++i)
            for (int j = 0; j < 3; ++j)
                F(i * 3 + j) = F_map(i, j);

        const int nV = V_rows;
        const int nF = F_rows;

        // ---- face normals ----
        Eigen::MatrixXd fN(nF, 3);
        for (int fi = 0; fi < nF; ++fi) {
            const Eigen::Vector3d p0 = V.row(F(fi * 3));
            const Eigen::Vector3d p1 = V.row(F(fi * 3 + 1));
            const Eigen::Vector3d p2 = V.row(F(fi * 3 + 2));
            Eigen::Vector3d n = (p1 - p0).cross(p2 - p0);
            const double nl = n.norm();
            if (nl > 1e-14) n /= nl;
            fN.row(fi) = n;
        }

        // ---- vertex normals (area-weighted face normals) ----
        Eigen::MatrixXd vN = Eigen::MatrixXd::Zero(nV, 3);
        for (int fi = 0; fi < nF; ++fi) {
            const int a = F(fi * 3), b = F(fi * 3 + 1), c = F(fi * 3 + 2);
            const Eigen::Vector3d p0 = V.row(a), p1 = V.row(b), p2 = V.row(c);
            const double area = 0.5 * (p1 - p0).cross(p2 - p0).norm();
            const Eigen::Vector3d nf = fN.row(fi);
            for (int v : {a, b, c})
                vN.row(v) += area * nf;
        }
        for (int i = 0; i < nV; ++i) {
            const double nl = vN.row(i).norm();
            if (nl > 1e-14) vN.row(i) /= nl;
        }

        // ---- per-face principal curvatures ----
        Eigen::MatrixXd faceDirs, k1k2;
        weingartenPrincipalCurvatures(V, F, vN, fN, faceDirs, k1k2);

        // Store per-face data
        g_nF = nF;
        g_pd1_face.resize(nF * 3);
        g_pd2_face.resize(nF * 3);
        g_pv1_face.resize(nF);
        g_pv2_face.resize(nF);
        for (int fi = 0; fi < nF; ++fi) {
            for (int j = 0; j < 3; ++j) {
                g_pd1_face[fi * 3 + j] = faceDirs(fi, j);
                g_pd2_face[fi * 3 + j] = faceDirs(fi, j);  // same dominant dir
            }
            g_pv1_face[fi] = k1k2(fi, 0);
            g_pv2_face[fi] = k1k2(fi, 1);
        }

        // ---- per-vertex: average neighboring face data ----
        g_nV = nV;
        g_pd1_vert.assign(nV * 3, 0.0);
        g_pd2_vert.assign(nV * 3, 0.0);
        g_pv1_vert.assign(nV, 0.0);
        g_pv2_vert.assign(nV, 0.0);
        std::vector<int> count(nV, 0);

        for (int fi = 0; fi < nF; ++fi) {
            const int a = F(fi * 3), b = F(fi * 3 + 1), c = F(fi * 3 + 2);
            for (int v : {a, b, c}) {
                count[v]++;
                for (int j = 0; j < 3; ++j) {
                    g_pd1_vert[v * 3 + j] += faceDirs(fi, j);
                    g_pd2_vert[v * 3 + j] += faceDirs(fi, j);
                }
                g_pv1_vert[v] += k1k2(fi, 0);
                g_pv2_vert[v] += k1k2(fi, 1);
            }
        }
        for (int i = 0; i < nV; ++i) {
            if (count[i] > 0) {
                const double inv = 1.0 / count[i];
                for (int j = 0; j < 3; ++j) {
                    g_pd1_vert[i * 3 + j] *= inv;
                    g_pd2_vert[i * 3 + j] *= inv;
                }
                g_pv1_vert[i] *= inv;
                g_pv2_vert[i] *= inv;
            }
        }

        return 0;
    } catch (...) {
        return -1;
    }
}

EMSCRIPTEN_KEEPALIVE double* get_pc_pd1()  { return g_pd1_face.empty() ? nullptr : g_pd1_face.data(); }
EMSCRIPTEN_KEEPALIVE double* get_pc_pd2()  { return g_pd2_face.empty() ? nullptr : g_pd2_face.data(); }
EMSCRIPTEN_KEEPALIVE double* get_pc_pv1()  { return g_pv1_face.empty() ? nullptr : g_pv1_face.data(); }
EMSCRIPTEN_KEEPALIVE double* get_pc_pv2()  { return g_pv2_face.empty() ? nullptr : g_pv2_face.data(); }
EMSCRIPTEN_KEEPALIVE int     get_pc_num_faces() { return g_nF; }

EMSCRIPTEN_KEEPALIVE double* get_pc_pd1_vert() { return g_pd1_vert.empty() ? nullptr : g_pd1_vert.data(); }
EMSCRIPTEN_KEEPALIVE double* get_pc_pd2_vert() { return g_pd2_vert.empty() ? nullptr : g_pd2_vert.data(); }
EMSCRIPTEN_KEEPALIVE double* get_pc_pv1_vert() { return g_pv1_vert.empty() ? nullptr : g_pv1_vert.data(); }
EMSCRIPTEN_KEEPALIVE double* get_pc_pv2_vert() { return g_pv2_vert.empty() ? nullptr : g_pv2_vert.data(); }
EMSCRIPTEN_KEEPALIVE int     get_pc_num_verts() { return g_nV; }

EMSCRIPTEN_KEEPALIVE
void pc_dispose() {
    g_pd1_face.clear(); g_pd1_face.shrink_to_fit();
    g_pd2_face.clear(); g_pd2_face.shrink_to_fit();
    g_pv1_face.clear(); g_pv1_face.shrink_to_fit();
    g_pv2_face.clear(); g_pv2_face.shrink_to_fit();
    g_pd1_vert.clear(); g_pd1_vert.shrink_to_fit();
    g_pd2_vert.clear(); g_pd2_vert.shrink_to_fit();
    g_pv1_vert.clear(); g_pv1_vert.shrink_to_fit();
    g_pv2_vert.clear(); g_pv2_vert.shrink_to_fit();
    g_nV = 0; g_nF = 0;
}

} // extern "C"
