/**
 * wasm_unified_solver.cpp — Circle Pattern / CETM / Ricci Flow for uv_unwrap_cone_global.html
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
#include "CirclePatternsWasm.h"
#include "Cetm.h"
#include "RicciFlow.h"

struct SolverState {
    Mesh* mesh = nullptr;
    std::vector<double> uv;
    double lastTimeMs = 0.0;
};

static SolverState g_cp;
static SolverState g_cetm;
static SolverState g_ricci;

static bool loadMesh(SolverState& state, const double* positions, int posLen,
                     const int* faces, int faceLen)
{
    if (state.mesh) {
        delete state.mesh;
        state.mesh = nullptr;
    }
    if (posLen < 9 || faceLen < 3) return false;

    state.mesh = new Mesh();
    const size_t nV = static_cast<size_t>(posLen / 3);
    const size_t nF = static_cast<size_t>(faceLen / 3);

    std::stringstream ss;
    for (size_t i = 0; i < nV; i++) {
        ss << "v " << positions[i * 3] << " "
           << positions[i * 3 + 1] << " "
           << positions[i * 3 + 2] << "\n";
    }
    for (size_t i = 0; i < nF; i++) {
        ss << "f " << faces[i * 3] + 1 << " "
           << faces[i * 3 + 1] + 1 << " "
           << faces[i * 3 + 2] + 1 << "\n";
    }

    const std::string str = ss.str();
    FILE* fp = fopen("/tmp/uv_cone.obj", "wb");
    if (!fp) return false;
    fwrite(str.c_str(), 1, str.size(), fp);
    fclose(fp);

    if (!state.mesh->read("/tmp/uv_cone.obj")) {
        delete state.mesh;
        state.mesh = nullptr;
        return false;
    }
    return true;
}

static void extractUV(SolverState& state)
{
    state.uv.clear();
    if (!state.mesh) return;

    double minU = std::numeric_limits<double>::infinity();
    double maxU = -std::numeric_limits<double>::infinity();
    double minV = std::numeric_limits<double>::infinity();
    double maxV = -std::numeric_limits<double>::infinity();

    for (const auto& v : state.mesh->vertices) {
        minU = std::min(minU, v.uv.x());
        maxU = std::max(maxU, v.uv.x());
        minV = std::min(minV, v.uv.y());
        maxV = std::max(maxV, v.uv.y());
    }

    const double rU = std::max(maxU - minU, 1e-10);
    const double rV = std::max(maxV - minV, 1e-10);
    state.uv.reserve(state.mesh->vertices.size() * 2);
    for (const auto& v : state.mesh->vertices) {
        state.uv.push_back((v.uv.x() - minU) / rU);
        state.uv.push_back((v.uv.y() - minV) / rV);
    }
}

static void disposeState(SolverState& state)
{
    if (state.mesh) {
        delete state.mesh;
        state.mesh = nullptr;
    }
    state.uv.clear();
    state.uv.shrink_to_fit();
    state.lastTimeMs = 0.0;
}

extern "C" {

// ---- Circle Pattern (WASM, no Mosek) ----

EMSCRIPTEN_KEEPALIVE
int solve_cp(double* pos, int posLen, int* faces, int faceLen, int optScheme,
             int* coneIdx, int coneIdxLen, double* coneAngles, int coneAnglesLen)
{
    if (!loadMesh(g_cp, pos, posLen, faces, faceLen)) return -1;

    auto t0 = std::chrono::high_resolution_clock::now();
    g_cp.mesh->delaunayize();

    CirclePatternsWasm cp(*g_cp.mesh, optScheme);
    if (coneIdx && coneAngles && coneIdxLen > 0 && coneAnglesLen > 0) {
        const int n = std::min(coneIdxLen, coneAnglesLen);
        std::vector<int> idx(coneIdx, coneIdx + n);
        std::vector<double> ang(coneAngles, coneAngles + n);
        cp.setConeSingulars(idx, ang);
    }
    cp.parameterize();

    auto t1 = std::chrono::high_resolution_clock::now();
    g_cp.lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV(g_cp);
    return 0;
}

EMSCRIPTEN_KEEPALIVE double* get_cp_uv_result() {
    return g_cp.uv.empty() ? nullptr : g_cp.uv.data();
}
EMSCRIPTEN_KEEPALIVE int get_cp_uv_result_size() {
    return static_cast<int>(g_cp.uv.size());
}
EMSCRIPTEN_KEEPALIVE double get_cp_last_time_ms() {
    return g_cp.lastTimeMs;
}
EMSCRIPTEN_KEEPALIVE void cp_dispose() {
    disposeState(g_cp);
}

// ---- CETM ----

EMSCRIPTEN_KEEPALIVE
int solve_cetm(double* pos, int posLen, int* faces, int faceLen, int optScheme)
{
    if (!loadMesh(g_cetm, pos, posLen, faces, faceLen)) return -1;

    auto t0 = std::chrono::high_resolution_clock::now();
    g_cetm.mesh->delaunayize();
    Cetm cetm(*g_cetm.mesh, optScheme);
    cetm.parameterize();
    auto t1 = std::chrono::high_resolution_clock::now();

    g_cetm.lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV(g_cetm);
    return 0;
}

EMSCRIPTEN_KEEPALIVE double* get_cetm_uv_result() {
    return g_cetm.uv.empty() ? nullptr : g_cetm.uv.data();
}
EMSCRIPTEN_KEEPALIVE int get_cetm_uv_result_size() {
    return static_cast<int>(g_cetm.uv.size());
}
EMSCRIPTEN_KEEPALIVE double get_cetm_last_time_ms() {
    return g_cetm.lastTimeMs;
}
EMSCRIPTEN_KEEPALIVE void cetm_dispose() {
    disposeState(g_cetm);
}

// ---- Ricci Flow ----

EMSCRIPTEN_KEEPALIVE
int solve_ricci(double* pos, int posLen, int* faces, int faceLen, int optScheme)
{
    if (!loadMesh(g_ricci, pos, posLen, faces, faceLen)) return -1;

    auto t0 = std::chrono::high_resolution_clock::now();
    g_ricci.mesh->delaunayize();
    RicciFlow rf(*g_ricci.mesh, optScheme);
    rf.parameterize();
    auto t1 = std::chrono::high_resolution_clock::now();

    g_ricci.lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();
    extractUV(g_ricci);
    return 0;
}

EMSCRIPTEN_KEEPALIVE double* get_ricci_uv_result() {
    return g_ricci.uv.empty() ? nullptr : g_ricci.uv.data();
}
EMSCRIPTEN_KEEPALIVE int get_ricci_uv_result_size() {
    return static_cast<int>(g_ricci.uv.size());
}
EMSCRIPTEN_KEEPALIVE double get_ricci_last_time_ms() {
    return g_ricci.lastTimeMs;
}
EMSCRIPTEN_KEEPALIVE void ricci_dispose() {
    disposeState(g_ricci);
}

} // extern "C"
