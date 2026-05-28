/**
 * wasm_uv_unwrap_simple.cpp — LSCM + Tutte + SCP + QC error for uv-unwrap.html
 */

#include <emscripten.h>
#include <vector>
#include <string>
#include <sstream>
#include <chrono>
#include <cstdio>
#include <cmath>
#include <limits>

#include "Mesh.h"
#include "MeshIO.h"
#include "Lscm.h"
#include "Tutte.h"
#include "Scp.h"
#include "LinAbf.h"
#include "AbfPlusPlus.h"
#include "CirclePatterns.h"
#include "Cetm.h"
#include "RicciFlow.h"
#include "ARAP.h"
#include "HolomorphicOneForm.h"
#include "QcError.h"
#include "topology/TreeCotreeBasis.h"

static Mesh* g_mesh = nullptr;
static double g_lastTimeMs = 0.0;
static int g_cpFallbackToCetm = 0;
static std::vector<double> g_uv_result;
static std::vector<double> g_qc_errors;
static std::vector<double> g_qc_colors;
static std::vector<int> g_homology_edge_pairs; // [v0,v1, v0,v1, ...] (2g edges)
static int g_homology_genus = 0;

static bool isClosedMesh(const Mesh& m) {
    if (!m.boundaries.empty()) return false;
    for (EdgeCIter e = m.edges.begin(); e != m.edges.end(); ++e) {
        if (e->isBoundary()) return false;
    }
    return true;
}

static int computeGenusClosed(const Mesh& m) {
    const int nV = (int)m.vertices.size();
    const int nE = (int)m.edges.size();
    int nF = 0;
    for (FaceCIter f = m.faces.begin(); f != m.faces.end(); ++f) {
        if (!f->isBoundary()) ++nF;
    }
    const int chi = nV - nE + nF;
    const int g = (2 - chi) / 2;
    return g < 0 ? 0 : g;
}

static void computeHomologyBasisEdgesTreeCotree() {
    g_homology_edge_pairs.clear();
    g_homology_genus = 0;
    if (!g_mesh) return;
    if (!isClosedMesh(*g_mesh)) return;

    const int nV = (int)g_mesh->vertices.size();
    int nF = 0;
    for (FaceCIter f = g_mesh->faces.begin(); f != g_mesh->faces.end(); ++f) {
        if (!f->isBoundary()) ++nF;
    }
    const int genus = computeGenusClosed(*g_mesh);
    g_homology_genus = genus;
    if (genus <= 0) return;

    std::vector<topology::TreeCotreeBasis::Edge> edges;
    edges.reserve(g_mesh->edges.size());
    for (EdgeCIter e = g_mesh->edges.begin(); e != g_mesh->edges.end(); ++e) {
        if (e->isBoundary()) continue;
        const int a = e->he->vertex->index;
        const int b = e->he->flip->vertex->index;
        const int v0 = std::min(a, b);
        const int v1 = std::max(a, b);
        const int f0 = e->he->face->index;
        const int f1 = e->he->flip->face->index;
        topology::TreeCotreeBasis::Edge te;
        te.v0 = v0;
        te.v1 = v1;
        te.f0 = f0;
        te.f1 = f1;
        edges.push_back(te);
    }

    auto findEdge = [&](int a, int b) -> int {
        int v0 = std::min(a, b);
        int v1 = std::max(a, b);
        for (int ei = 0; ei < (int)edges.size(); ++ei) {
            if (edges[ei].v0 == v0 && edges[ei].v1 == v1) return ei;
        }
        return -1;
    };

    auto edgeSign = [&](int from, int to) -> int {
        int ei = findEdge(from, to);
        if (ei < 0) return 0;
        if (from == edges[ei].v0 && to == edges[ei].v1) return +1;
        if (from == edges[ei].v1 && to == edges[ei].v0) return -1;
        return 0;
    };

    // Build basis cycles (2g of them). For visualization we return one representative edge per cycle:
    // the first signed edge entry is always the chosen remaining edge in TreeCotreeBasis.
    auto cycles = topology::TreeCotreeBasis::buildClosedMeshBasis(nV, nF, edges, genus, findEdge, edgeSign);
    const int target = 2 * genus;
    for (int i = 0; i < (int)cycles.size() && i < target; ++i) {
        if (cycles[i].empty()) continue;
        const int eIdx = cycles[i][0].first;
        if (eIdx < 0 || eIdx >= (int)edges.size()) continue;
        g_homology_edge_pairs.push_back(edges[eIdx].v0);
        g_homology_edge_pairs.push_back(edges[eIdx].v1);
    }
}

static bool loadMesh(const double* positions, int posLen,
                     const int* faces, int faceLen)
{
    if (g_mesh) { delete g_mesh; g_mesh = nullptr; }
    if (posLen < 9 || faceLen < 3) return false;

    g_mesh = new Mesh();
    const size_t nV = posLen / 3;
    const size_t nF = faceLen / 3;

    std::stringstream ss;
    for (size_t i = 0; i < nV; i++)
        ss << "v " << positions[i * 3] << " " << positions[i * 3 + 1] << " " << positions[i * 3 + 2] << "\n";
    for (size_t i = 0; i < nF; i++)
        ss << "f " << faces[i * 3] + 1 << " " << faces[i * 3 + 1] + 1 << " " << faces[i * 3 + 2] + 1 << "\n";

    const std::string str = ss.str();
    FILE* fp = fopen("/tmp/uv_simple.obj", "wb");
    if (!fp) return false;
    fwrite(str.c_str(), 1, str.size(), fp);
    fclose(fp);

    if (!g_mesh->read("/tmp/uv_simple.obj")) {
        delete g_mesh;
        g_mesh = nullptr;
        return false;
    }
    return true;
}

static void extractUV()
{
    g_uv_result.clear();
    if (!g_mesh) return;
    g_uv_result.reserve(g_mesh->vertices.size() * 2);

    double minU = std::numeric_limits<double>::infinity();
    double maxU = -std::numeric_limits<double>::infinity();
    double minV = std::numeric_limits<double>::infinity();
    double maxV = -std::numeric_limits<double>::infinity();

    for (const auto& v : g_mesh->vertices) {
        if (v.uv.x() < minU) minU = v.uv.x();
        if (v.uv.x() > maxU) maxU = v.uv.x();
        if (v.uv.y() < minV) minV = v.uv.y();
        if (v.uv.y() > maxV) maxV = v.uv.y();
    }

    const double rU = std::max(maxU - minU, 1e-10);
    const double rV = std::max(maxV - minV, 1e-10);
    for (const auto& v : g_mesh->vertices) {
        g_uv_result.push_back((v.uv.x() - minU) / rU);
        g_uv_result.push_back((v.uv.y() - minV) / rV);
    }
}

extern "C" {

EMSCRIPTEN_KEEPALIVE
int solve_lscm(double* pos, int posLen, int* faces, int faceLen, int anchor0, int anchor1) {
    (void)anchor0;
    (void)anchor1;
    if (!loadMesh(pos, posLen, faces, faceLen)) return -1;
    auto t0 = std::chrono::high_resolution_clock::now();
    g_mesh->delaunayize();
    g_mesh->parameterize(LSCM);
    auto t1 = std::chrono::high_resolution_clock::now();
    g_lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV();
    computeHomologyBasisEdgesTreeCotree();
    return 0;
}

EMSCRIPTEN_KEEPALIVE
int solve_tutte_circle(double* pos, int posLen, int* faces, int faceLen) {
    if (!loadMesh(pos, posLen, faces, faceLen)) return -1;
    auto t0 = std::chrono::high_resolution_clock::now();
    g_mesh->delaunayize();
    Tutte p(*g_mesh, TutteBoundary::CIRCLE);
    p.parameterize();
    auto t1 = std::chrono::high_resolution_clock::now();
    g_lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV();
    computeHomologyBasisEdgesTreeCotree();
    return 0;
}

EMSCRIPTEN_KEEPALIVE
int solve_tutte_square(double* pos, int posLen, int* faces, int faceLen) {
    if (!loadMesh(pos, posLen, faces, faceLen)) return -1;
    auto t0 = std::chrono::high_resolution_clock::now();
    g_mesh->delaunayize();
    Tutte p(*g_mesh, TutteBoundary::SQUARE);
    p.parameterize();
    auto t1 = std::chrono::high_resolution_clock::now();
    g_lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV();
    computeHomologyBasisEdgesTreeCotree();
    return 0;
}

EMSCRIPTEN_KEEPALIVE
int solve_scp(double* pos, int posLen, int* faces, int faceLen) {
    if (!loadMesh(pos, posLen, faces, faceLen)) return -1;
    auto t0 = std::chrono::high_resolution_clock::now();
    g_mesh->delaunayize();
    Scp p(*g_mesh);
    p.parameterize();
    auto t1 = std::chrono::high_resolution_clock::now();
    g_lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV();
    computeHomologyBasisEdgesTreeCotree();
    return 0;
}

EMSCRIPTEN_KEEPALIVE
int solve_linabf(double* pos, int posLen, int* faces, int faceLen) {
    if (!loadMesh(pos, posLen, faces, faceLen)) return -1;
    auto t0 = std::chrono::high_resolution_clock::now();
    g_mesh->delaunayize();
    LinAbf p(*g_mesh);
    p.parameterize();
    auto t1 = std::chrono::high_resolution_clock::now();
    g_lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV();
    computeHomologyBasisEdgesTreeCotree();
    return 0;
}

EMSCRIPTEN_KEEPALIVE
int solve_abfpp(double* pos, int posLen, int* faces, int faceLen) {
    if (!loadMesh(pos, posLen, faces, faceLen)) return -1;
    auto t0 = std::chrono::high_resolution_clock::now();
    g_mesh->delaunayize();
    AbfPlusPlus p(*g_mesh);
    p.parameterize();
    auto t1 = std::chrono::high_resolution_clock::now();
    g_lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV();
    computeHomologyBasisEdgesTreeCotree();
    return 0;
}

EMSCRIPTEN_KEEPALIVE
int solve_arap(double* pos, int posLen, int* faces, int faceLen, int maxIter) {
    if (!loadMesh(pos, posLen, faces, faceLen)) return -1;
    auto t0 = std::chrono::high_resolution_clock::now();
    g_mesh->delaunayize();
    ARAP p(*g_mesh, maxIter > 0 ? maxIter : 8);
    p.parameterize();
    auto t1 = std::chrono::high_resolution_clock::now();
    g_lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV();
    computeHomologyBasisEdgesTreeCotree();
    return 0;
}

EMSCRIPTEN_KEEPALIVE
int solve_cp(double* pos, int posLen, int* faces, int faceLen, int optScheme) {
    if (!loadMesh(pos, posLen, faces, faceLen)) return -1;
    g_cpFallbackToCetm = 0;
    auto t0 = std::chrono::high_resolution_clock::now();
    g_mesh->delaunayize();
    CirclePatterns p(*g_mesh, optScheme);
    p.parameterize();
    // On WASM builds CirclePatterns may run without MOSEK backend.
    // Fall back to CETM if UV collapsed after parameterization.
    double minU = std::numeric_limits<double>::infinity();
    double maxU = -std::numeric_limits<double>::infinity();
    double minV = std::numeric_limits<double>::infinity();
    double maxV = -std::numeric_limits<double>::infinity();
    for (const auto& v : g_mesh->vertices) {
        minU = std::min(minU, v.uv.x());
        maxU = std::max(maxU, v.uv.x());
        minV = std::min(minV, v.uv.y());
        maxV = std::max(maxV, v.uv.y());
    }
    if ((maxU - minU) < 1e-12 && (maxV - minV) < 1e-12) {
        g_cpFallbackToCetm = 1;
        Cetm fallback(*g_mesh, optScheme);
        fallback.parameterize();
    }
    auto t1 = std::chrono::high_resolution_clock::now();
    g_lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV();
    computeHomologyBasisEdgesTreeCotree();
    return 0;
}

EMSCRIPTEN_KEEPALIVE
int solve_cetm(double* pos, int posLen, int* faces, int faceLen, int optScheme) {
    if (!loadMesh(pos, posLen, faces, faceLen)) return -1;
    auto t0 = std::chrono::high_resolution_clock::now();
    g_mesh->delaunayize();
    Cetm p(*g_mesh, optScheme);
    p.parameterize();
    auto t1 = std::chrono::high_resolution_clock::now();
    g_lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV();
    computeHomologyBasisEdgesTreeCotree();
    return 0;
}

EMSCRIPTEN_KEEPALIVE
int solve_ricci(double* pos, int posLen, int* faces, int faceLen, int optScheme) {
    if (!loadMesh(pos, posLen, faces, faceLen)) return -1;
    auto t0 = std::chrono::high_resolution_clock::now();
    g_mesh->delaunayize();
    RicciFlow p(*g_mesh, optScheme);
    p.parameterize();
    auto t1 = std::chrono::high_resolution_clock::now();
    g_lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV();
    computeHomologyBasisEdgesTreeCotree();
    return 0;
}

EMSCRIPTEN_KEEPALIVE
int solve_hof(double* pos, int posLen, int* faces, int faceLen) {
    if (!loadMesh(pos, posLen, faces, faceLen)) return -1;
    auto t0 = std::chrono::high_resolution_clock::now();
    g_mesh->delaunayize();
    HolomorphicOneForm p(*g_mesh);
    p.parameterize();
    auto t1 = std::chrono::high_resolution_clock::now();
    g_lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV();
    computeHomologyBasisEdgesTreeCotree();
    return 0;
}

EMSCRIPTEN_KEEPALIVE int is_closed_mesh() {
    if (!g_mesh) return 0;
    return isClosedMesh(*g_mesh) ? 1 : 0;
}

EMSCRIPTEN_KEEPALIVE int get_homology_genus() {
    return g_homology_genus;
}

EMSCRIPTEN_KEEPALIVE int* get_homology_edge_pairs() {
    return g_homology_edge_pairs.empty() ? nullptr : g_homology_edge_pairs.data();
}

EMSCRIPTEN_KEEPALIVE int get_homology_edge_pairs_size() {
    return static_cast<int>(g_homology_edge_pairs.size());
}

EMSCRIPTEN_KEEPALIVE double* get_uv_result() {
    return g_uv_result.empty() ? nullptr : g_uv_result.data();
}

EMSCRIPTEN_KEEPALIVE int get_uv_result_size() {
    return static_cast<int>(g_uv_result.size());
}

EMSCRIPTEN_KEEPALIVE double get_last_time_ms() {
    return g_lastTimeMs;
}

EMSCRIPTEN_KEEPALIVE int get_cp_fallback_to_cetm() {
    return g_cpFallbackToCetm;
}

EMSCRIPTEN_KEEPALIVE
int load_mesh_with_uv(double* pos, int posLen, int* faces, int faceLen,
                      double* uvs, int uvLen) {
    if (!loadMesh(pos, posLen, faces, faceLen)) return -1;
    const int nV = posLen / 3;
    if (uvLen < nV * 2) return -1;
    for (int i = 0; i < nV; i++) {
        g_mesh->vertices[i].uv = Eigen::Vector2d(uvs[i * 2], uvs[i * 2 + 1]);
    }
    return 0;
}

EMSCRIPTEN_KEEPALIVE
int compute_qc_error() {
    if (!g_mesh) return -1;
    g_qc_errors.clear();
    g_qc_colors.clear();
    int nFaces = 0;

    for (FaceCIter f = g_mesh->faces.begin(); f != g_mesh->faces.end(); f++) {
        if (f->isBoundary()) continue;
        nFaces++;

        std::vector<Eigen::Vector3d> p, q;
        HalfEdgeCIter he = f->he;
        do {
            p.push_back(he->vertex->position);
            q.push_back(Eigen::Vector3d(he->vertex->uv.x(), he->vertex->uv.y(), 0));
            he = he->next;
        } while (he != f->he);

        const double err = QuasiConformalError::compute(p, q);
        g_qc_errors.push_back(err);

        const Eigen::Vector3d col = QuasiConformalError::color(err);
        g_qc_colors.push_back(col.x());
        g_qc_colors.push_back(col.y());
        g_qc_colors.push_back(col.z());
    }

    return nFaces;
}

EMSCRIPTEN_KEEPALIVE double* get_qc_errors() {
    return g_qc_errors.empty() ? nullptr : g_qc_errors.data();
}

EMSCRIPTEN_KEEPALIVE int get_qc_errors_size() {
    return static_cast<int>(g_qc_errors.size());
}

EMSCRIPTEN_KEEPALIVE double* get_qc_colors() {
    return g_qc_colors.empty() ? nullptr : g_qc_colors.data();
}

EMSCRIPTEN_KEEPALIVE int get_qc_colors_size() {
    return static_cast<int>(g_qc_colors.size());
}

EMSCRIPTEN_KEEPALIVE void dispose() {
    if (g_mesh) { delete g_mesh; g_mesh = nullptr; }
    g_cpFallbackToCetm = 0;
    g_uv_result.clear();
    g_uv_result.shrink_to_fit();
    g_qc_errors.clear();
    g_qc_colors.clear();
    g_homology_edge_pairs.clear();
    g_homology_edge_pairs.shrink_to_fit();
    g_homology_genus = 0;
}

} // extern "C"
