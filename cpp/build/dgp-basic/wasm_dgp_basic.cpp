/**
 * wasm_dgp_basic.cpp — basic DG processing: gaussian curvature + principal curvature field.
 *
 * Exports:
 *   load_mesh(posPtr, posLen, facesPtr, faceLen) -> int (0 ok)
 *   is_closed_mesh() -> int (1 closed, 0 not)
 *
 *   compute_gauss_curvature_per_area() -> int (0 ok)
 *   get_gc_result() -> double*
 *   get_gc_result_size() -> int
 *
 *   compute_principal_curvature_field() -> int (0 ok)
 *   get_pc_field() -> double*  (nF*3 doubles; per-face unit direction)
 *   get_pc_field_size() -> int
 *
 *   dispose() -> void
 */

#include <emscripten.h>
#include <vector>
#include <sstream>
#include <cstdio>

#include "Mesh.h"
#include "MeshIO.h"

#include "GaussianCurvature.h"
#include "PrincipalCurvatureField.h"

static Mesh* g_mesh = nullptr;
static std::vector<double> g_gc;
static std::vector<double> g_pc;
static std::vector<double> g_pc_k1k2;

static bool loadMesh(const double* positions, int posLen, const int* faces, int faceLen) {
    if (g_mesh) { delete g_mesh; g_mesh = nullptr; }
    g_gc.clear();
    g_pc.clear();
    g_pc_k1k2.clear();
    if (!positions || !faces) return false;
    if (posLen < 9 || faceLen < 3) return false;

    g_mesh = new Mesh();
    const size_t nV = (size_t)posLen / 3;
    const size_t nF = (size_t)faceLen / 3;

    std::stringstream ss;
    for (size_t i = 0; i < nV; i++)
        ss << "v " << positions[i * 3] << " " << positions[i * 3 + 1] << " " << positions[i * 3 + 2] << "\n";
    for (size_t i = 0; i < nF; i++)
        ss << "f " << faces[i * 3] + 1 << " " << faces[i * 3 + 1] + 1 << " " << faces[i * 3 + 2] + 1 << "\n";

    const std::string str = ss.str();
    FILE* fp = fopen("/tmp/dgp_basic.obj", "wb");
    if (!fp) return false;
    fwrite(str.c_str(), 1, str.size(), fp);
    fclose(fp);

    if (!g_mesh->read("/tmp/dgp_basic.obj")) {
        delete g_mesh;
        g_mesh = nullptr;
        return false;
    }
    return true;
}

static bool isClosedMesh(const Mesh& m) {
    if (!m.boundaries.empty()) return false;
    for (EdgeCIter e = m.edges.begin(); e != m.edges.end(); ++e) {
        if (e->isBoundary()) return false;
    }
    return true;
}

extern "C" {

EMSCRIPTEN_KEEPALIVE
int load_mesh(double* pos, int posLen, int* faces, int faceLen) {
    return loadMesh(pos, posLen, faces, faceLen) ? 0 : -1;
}

EMSCRIPTEN_KEEPALIVE
int is_closed_mesh() {
    if (!g_mesh) return 0;
    return isClosedMesh(*g_mesh) ? 1 : 0;
}

EMSCRIPTEN_KEEPALIVE
int compute_gauss_curvature_per_area() {
    if (!g_mesh) return -1;
    Eigen::VectorXd K = geometry::gaussianCurvaturePerArea(*g_mesh);
    g_gc.assign(K.data(), K.data() + K.size());
    return 0;
}

EMSCRIPTEN_KEEPALIVE
double* get_gc_result() { return g_gc.empty() ? nullptr : g_gc.data(); }

EMSCRIPTEN_KEEPALIVE
int get_gc_result_size() { return (int)g_gc.size(); }

EMSCRIPTEN_KEEPALIVE
int compute_principal_curvature_field() {
    if (!g_mesh) return -1;

    // Extract V/F and vertex normals / face normals in the same way QuadCover expects.
    const int nV = (int)g_mesh->vertices.size();
    int nF = 0;
    for (FaceCIter f = g_mesh->faces.begin(); f != g_mesh->faces.end(); ++f) {
        if (!f->isBoundary()) ++nF;
    }
    if (nV < 3 || nF < 1) return -1;

    Eigen::MatrixXd V(nV, 3);
    Eigen::VectorXi F(nF * 3);
    for (VertexCIter v = g_mesh->vertices.begin(); v != g_mesh->vertices.end(); ++v) {
        V.row(v->index) = v->position;
    }
    int fi = 0;
    for (FaceCIter f = g_mesh->faces.begin(); f != g_mesh->faces.end(); ++f) {
        if (f->isBoundary()) continue;
        F[fi * 3] = f->he->vertex->index;
        F[fi * 3 + 1] = f->he->next->vertex->index;
        F[fi * 3 + 2] = f->he->next->next->vertex->index;
        ++fi;
    }
    nF = fi;

    // Vertex normals (angle-weighted) via existing Vertex::normal()
    Eigen::MatrixXd vN(nV, 3);
    for (VertexCIter v = g_mesh->vertices.begin(); v != g_mesh->vertices.end(); ++v) {
        vN.row(v->index) = v->normal();
    }

    Eigen::MatrixXd fN(nF, 3);
    for (int fidx = 0; fidx < nF; ++fidx) {
        const int a = F[fidx * 3];
        const int b = F[fidx * 3 + 1];
        const int c = F[fidx * 3 + 2];
        const Eigen::Vector3d p0 = V.row(a);
        const Eigen::Vector3d p1 = V.row(b);
        const Eigen::Vector3d p2 = V.row(c);
        Eigen::Vector3d fn = (p1 - p0).cross(p2 - p0);
        const double len = fn.norm();
        if (len > 1e-14) fn /= len;
        fN.row(fidx) = fn;
    }

    Eigen::MatrixXd dirs, k1k2;
    PrincipalCurvatureField::estimateFromWeingartenWithCurvatures(V, F, vN, fN, dirs, k1k2);
    g_pc.resize((size_t)nF * 3);
    g_pc_k1k2.resize((size_t)nF * 2);
    for (int fidx = 0; fidx < nF; ++fidx) {
        g_pc[fidx * 3] = dirs(fidx, 0);
        g_pc[fidx * 3 + 1] = dirs(fidx, 1);
        g_pc[fidx * 3 + 2] = dirs(fidx, 2);
        g_pc_k1k2[fidx * 2] = k1k2(fidx, 0);
        g_pc_k1k2[fidx * 2 + 1] = k1k2(fidx, 1);
    }
    return 0;
}

EMSCRIPTEN_KEEPALIVE
double* get_pc_field() { return g_pc.empty() ? nullptr : g_pc.data(); }

EMSCRIPTEN_KEEPALIVE
int get_pc_field_size() { return (int)g_pc.size(); }

EMSCRIPTEN_KEEPALIVE
double* get_pc_k1k2() { return g_pc_k1k2.empty() ? nullptr : g_pc_k1k2.data(); }

EMSCRIPTEN_KEEPALIVE
int get_pc_k1k2_size() { return (int)g_pc_k1k2.size(); }

EMSCRIPTEN_KEEPALIVE
void dispose() {
    if (g_mesh) { delete g_mesh; g_mesh = nullptr; }
    g_gc.clear();
    g_gc.shrink_to_fit();
    g_pc.clear();
    g_pc.shrink_to_fit();
    g_pc_k1k2.clear();
    g_pc_k1k2.shrink_to_fit();
}

} // extern "C"

