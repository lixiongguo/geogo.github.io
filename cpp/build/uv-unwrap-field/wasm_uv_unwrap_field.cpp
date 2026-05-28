/**
 * uv_unwrap_field WASM wrapper.
 *
 * Pipeline split:
 *  1) compute principal curvature initial face field
 *  2) smooth/denoise + matching
 *  3) QuadCover parameterization (simple/full)
 *
 * Mesh input is a triangle mesh via arrays (positions, faces). Internally written to a temp OBJ
 * and loaded by the existing Mesh reader to build halfedge connectivity.
 */

#include <emscripten.h>
#include <vector>
#include <string>
#include <sstream>
#include <cstdio>

#include "Mesh.h"
#include "MeshIO.h"
#include "uv_unwrap_field/QuadCover.h"
#include <emscripten/html5.h>

namespace {

class QuadCoverWasm : public QuadCover {
public:
    using QuadCover::QuadCover;
    using QuadCover::initMeshData;
    using QuadCover::estimatePrincipalCurvature;
    using QuadCover::computeFaceTheta;
    using QuadCover::syncFaceDirsFromTheta;
    using QuadCover::smoothCrossField;
    using QuadCover::computeMatching;
    using QuadCover::computeLayerShift;
    using QuadCover::faceDirs;
    using QuadCover::matching;
    using QuadCover::edgeList;
};

Mesh* g_mesh = nullptr;
QuadCoverWasm* g_qc = nullptr;
bool g_inited = false;

std::vector<double> g_face_dirs;     // nF*3
std::vector<int> g_matching;         // nE (quarter turns -2..2 etc)
std::vector<double> g_uv;            // nV*2
double g_last_time_ms = 0.0;

bool loadMeshFromArrays(const double* positions, int posLen, const int* faces, int faceLen) {
    if (g_qc) { delete g_qc; g_qc = nullptr; }
    if (g_mesh) { delete g_mesh; g_mesh = nullptr; }
    g_inited = false;
    g_face_dirs.clear();
    g_matching.clear();
    g_uv.clear();

    if (!positions || !faces) return false;
    if (posLen < 9 || faceLen < 3) return false;
    if (posLen % 3 != 0 || faceLen % 3 != 0) return false;

    const size_t nV = (size_t)posLen / 3;
    const size_t nF = (size_t)faceLen / 3;

    std::stringstream ss;
    for (size_t i = 0; i < nV; i++) {
        ss << "v " << positions[i * 3] << " " << positions[i * 3 + 1] << " " << positions[i * 3 + 2] << "\n";
    }
    for (size_t i = 0; i < nF; i++) {
        ss << "f " << faces[i * 3] + 1 << " " << faces[i * 3 + 1] + 1 << " " << faces[i * 3 + 2] + 1 << "\n";
    }

    const std::string obj = ss.str();
    FILE* fp = fopen("/tmp/uv_unwrap_field.obj", "wb");
    if (!fp) return false;
    fwrite(obj.c_str(), 1, obj.size(), fp);
    fclose(fp);

    g_mesh = new Mesh();
    if (!g_mesh->read("/tmp/uv_unwrap_field.obj")) {
        delete g_mesh;
        g_mesh = nullptr;
        return false;
    }

    g_qc = new QuadCoverWasm(*g_mesh);
    return true;
}

bool ensureInit() {
    if (!g_qc) return false;
    if (g_inited) return true;
    if (!g_qc->initMeshData()) return false;
    g_inited = true;
    return true;
}

void snapshotFaceDirs() {
    if (!g_qc) return;
    // IMPORTANT: QuadCover only stores interior faces in its matrices.
    // Using mesh->faces.size() can include boundary faces and cause Eigen out-of-bounds.
    const int nF = (int)g_qc->faceDirs.rows();
    g_face_dirs.resize((size_t)nF * 3);
    for (int fi = 0; fi < nF; ++fi) {
        g_face_dirs[fi * 3] = g_qc->faceDirs(fi, 0);
        g_face_dirs[fi * 3 + 1] = g_qc->faceDirs(fi, 1);
        g_face_dirs[fi * 3 + 2] = g_qc->faceDirs(fi, 2);
    }
}

void snapshotMatching() {
    if (!g_qc) return;
    const int nE = (int)g_qc->matching.size();
    g_matching.resize((size_t)nE);
    for (int ei = 0; ei < nE; ++ei) g_matching[ei] = (int)g_qc->matching[ei];
}

void snapshotUV() {
    if (!g_mesh) return;
    const int nV = (int)g_mesh->vertices.size();
    g_uv.resize((size_t)nV * 2);
    for (int vi = 0; vi < nV; ++vi) {
        g_uv[vi * 2] = g_mesh->vertices[vi].uv[0];
        g_uv[vi * 2 + 1] = g_mesh->vertices[vi].uv[1];
    }
}

} // namespace

extern "C" {

EMSCRIPTEN_KEEPALIVE
int load_mesh(double* pos, int posLen, int* faces, int faceLen) {
    return loadMeshFromArrays(pos, posLen, faces, faceLen) ? 0 : -1;
}

// -------- Step 1: principal curvature initial face field --------
EMSCRIPTEN_KEEPALIVE
int step1_compute_principal_field() {
    if (!ensureInit()) return -1;
    g_qc->estimatePrincipalCurvature();
    g_qc->computeFaceTheta();
    g_qc->syncFaceDirsFromTheta();
    snapshotFaceDirs();
    return 0;
}

// -------- Step 2: smoothing/denoise + matching --------
EMSCRIPTEN_KEEPALIVE
int step2_smooth_and_matching(int smoothIters) {
    if (!ensureInit()) return -1;
    g_qc->computeFaceTheta();
    g_qc->syncFaceDirsFromTheta();
    if (smoothIters > 0) g_qc->smoothCrossField(smoothIters);
    g_qc->computeMatching();
    snapshotFaceDirs();
    snapshotMatching();
    return 0;
}

// -------- Step 3: QuadCover parameterization --------
EMSCRIPTEN_KEEPALIVE
int step3_solve_quadcover(int full) {
    if (!ensureInit()) return -1;
    const double t0 = emscripten_get_now();
    bool ok = true;
    if (full) ok = g_qc->parameterizeFull();
    else { g_qc->parameterize(); ok = true; }
    g_last_time_ms = emscripten_get_now() - t0;
    if (!ok) return -2;
    snapshotUV();
    return 0;
}

EMSCRIPTEN_KEEPALIVE
double get_last_time_ms() { return g_last_time_ms; }

// ---------- results getters ----------
EMSCRIPTEN_KEEPALIVE
double* get_face_dirs() { return g_face_dirs.empty() ? nullptr : g_face_dirs.data(); }

EMSCRIPTEN_KEEPALIVE
int get_face_dirs_size() { return (int)g_face_dirs.size(); }

EMSCRIPTEN_KEEPALIVE
int* get_matching() { return g_matching.empty() ? nullptr : g_matching.data(); }

EMSCRIPTEN_KEEPALIVE
int get_matching_size() { return (int)g_matching.size(); }

EMSCRIPTEN_KEEPALIVE
double* get_uv_result() { return g_uv.empty() ? nullptr : g_uv.data(); }

EMSCRIPTEN_KEEPALIVE
int get_uv_result_size() { return (int)g_uv.size(); }

EMSCRIPTEN_KEEPALIVE
void dispose() {
    g_face_dirs.clear();
    g_matching.clear();
    g_uv.clear();
    g_last_time_ms = 0.0;
    g_inited = false;
    if (g_qc) { delete g_qc; g_qc = nullptr; }
    if (g_mesh) { delete g_mesh; g_mesh = nullptr; }
}

} // extern "C"

