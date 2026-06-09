#include "Renderer.hpp"

#include <Eigen/Core>

#include <cmath>
#include <iostream>
#include <vector>

namespace {

const char* kMeshVs = R"(#version 330 core
layout(location = 0) in vec2 aPos;
layout(location = 1) in float aVal;
uniform mat3 uMvp;
out float vVal;
void main() {
    vec3 p = uMvp * vec3(aPos, 1.0);
    gl_Position = vec4(p.xy, 0.0, 1.0);
    vVal = aVal;
}
)";

const char* kMeshFs = R"(#version 330 core
in float vVal;
uniform float uMin;
uniform float uMax;
out vec4 fragColor;
vec3 jet(float t) {
    t = clamp(t, 0.0, 1.0);
    float r = clamp(1.5 - abs(4.0 * t - 3.0), 0.0, 1.0);
    float g = clamp(1.5 - abs(4.0 * t - 2.0), 0.0, 1.0);
    float b = clamp(1.5 - abs(4.0 * t - 1.0), 0.0, 1.0);
    return vec3(r, g, b);
}
void main() {
    float t = (vVal - uMin) / max(uMax - uMin, 1e-6);
    fragColor = vec4(jet(t), 1.0);
}
)";

const char* kLineVs = R"(#version 330 core
layout(location = 0) in vec2 aPos;
uniform mat3 uMvp;
void main() {
    vec3 p = uMvp * vec3(aPos, 1.0);
    gl_Position = vec4(p.xy, 0.0, 1.0);
}
)";

const char* kLineFs = R"(#version 330 core
uniform vec3 uColor;
out vec4 fragColor;
void main() { fragColor = vec4(uColor, 1.0); }
)";

Eigen::Matrix3f makeMvp(float xmin, float ymin, float xmax, float ymax, int w, int h, float scale, float tx,
                        float ty) {
    const float cx = 0.5f * (xmin + xmax) + tx;
    const float cy = 0.5f * (ymin + ymax) + ty;
    const float sx = (xmax - xmin) / scale;
    const float sy = (ymax - ymin) / scale;
    const float aspect = static_cast<float>(w) / static_cast<float>(h);

    Eigen::Matrix3f S = Eigen::Matrix3f::Identity();
    S(0, 0) = 2.f / std::max(sx, 1e-6f);
    S(1, 1) = 2.f / std::max(sy / aspect, 1e-6f);

    Eigen::Matrix3f T = Eigen::Matrix3f::Identity();
    T(0, 2) = -cx * S(0, 0);
    T(1, 2) = -cy * S(1, 1);

    return T * S;
}

}  // namespace

bool Renderer::init() {
    program_ = compileProgram(kMeshVs, kMeshFs);
    lineProgram_ = compileProgram(kLineVs, kLineFs);
    if (!program_ || !lineProgram_) return false;

    glGenVertexArrays(1, &vao_);
    glGenBuffers(1, &vboPos_);
    glGenBuffers(1, &vboVal_);
    glGenBuffers(1, &ebo_);
    glGenVertexArrays(1, &lineVao_);
    glGenBuffers(1, &lineVbo_);
    return true;
}

void Renderer::resize(int w, int h) {
    viewportW_ = std::max(w, 1);
    viewportH_ = std::max(h, 1);
}

unsigned Renderer::compileProgram(const char* vs, const char* fs) {
    auto compile = [](GLenum type, const char* src) {
        const unsigned s = glCreateShader(type);
        glShaderSource(s, 1, &src, nullptr);
        glCompileShader(s);
        int ok = 0;
        glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
        if (!ok) {
            char log[1024];
            glGetShaderInfoLog(s, 1024, nullptr, log);
            std::cerr << "Shader compile error: " << log << '\n';
            return 0u;
        }
        return s;
    };

    const unsigned v = compile(GL_VERTEX_SHADER, vs);
    const unsigned f = compile(GL_FRAGMENT_SHADER, fs);
    if (!v || !f) return 0;

    const unsigned p = glCreateProgram();
    glAttachShader(p, v);
    glAttachShader(p, f);
    glLinkProgram(p);
    glDeleteShader(v);
    glDeleteShader(f);

    int ok = 0;
    glGetProgramiv(p, GL_LINK_STATUS, &ok);
    if (!ok) {
        char log[1024];
        glGetProgramInfoLog(p, 1024, nullptr, log);
        std::cerr << "Program link error: " << log << '\n';
        return 0;
    }
    return p;
}

void Renderer::uploadMesh(const CauchyScene& scene) {
    const auto pos = scene.displayPositions();
    const auto vals = scene.scalarField();
    const int n = static_cast<int>(pos.rows());

    glBindVertexArray(vao_);
    glBindBuffer(GL_ARRAY_BUFFER, vboPos_);
    glBufferData(GL_ARRAY_BUFFER, static_cast<GLsizeiptr>(n * 2 * sizeof(float)), pos.data(), GL_DYNAMIC_DRAW);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, nullptr);

    glBindBuffer(GL_ARRAY_BUFFER, vboVal_);
    glBufferData(GL_ARRAY_BUFFER, static_cast<GLsizeiptr>(n * sizeof(float)), vals.data(), GL_DYNAMIC_DRAW);
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 1, GL_FLOAT, GL_FALSE, 0, nullptr);

    if (scene.mesh().faces.rows() > 0) {
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_);
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, static_cast<GLsizeiptr>(scene.mesh().faces.size() * sizeof(int)),
                     scene.mesh().faces.data(), GL_STATIC_DRAW);
    }
}

void Renderer::drawBoundaryLoops(const CauchyScene& scene, float scale, float tx, float ty) {
    float xmin, ymin, xmax, ymax;
    scene.computeBounds(xmin, ymin, xmax, ymax);
    const Eigen::Matrix3f mvp = makeMvp(xmin, ymin, xmax, ymax, viewportW_, viewportH_, scale, tx, ty);

    glUseProgram(lineProgram_);
    glUniformMatrix3fv(glGetUniformLocation(lineProgram_, "uMvp"), 1, GL_FALSE, mvp.data());
    glBindVertexArray(lineVao_);
    glBindBuffer(GL_ARRAY_BUFFER, lineVbo_);
    glEnableVertexAttribArray(0);

    const auto drawLoop = [&](const p2p_harmonic::VecC& poly, float r, float g, float b) {
        if (poly.size() == 0) return;
        std::vector<float> pts(static_cast<std::size_t>(poly.size() + 1) * 2);
        for (Eigen::Index i = 0; i < poly.size(); ++i) {
            pts[static_cast<std::size_t>(i) * 2] = static_cast<float>(poly[i].real());
            pts[static_cast<std::size_t>(i) * 2 + 1] = static_cast<float>(poly[i].imag());
        }
        pts[static_cast<std::size_t>(poly.size()) * 2] = static_cast<float>(poly[0].real());
        pts[static_cast<std::size_t>(poly.size()) * 2 + 1] = static_cast<float>(poly[0].imag());
        glBufferData(GL_ARRAY_BUFFER, static_cast<GLsizeiptr>(pts.size() * sizeof(float)), pts.data(), GL_DYNAMIC_DRAW);
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, nullptr);
        glUniform3f(glGetUniformLocation(lineProgram_, "uColor"), r, g, b);
        glLineWidth(2.f);
        glDrawArrays(GL_LINE_STRIP, 0, static_cast<GLsizei>(poly.size() + 1));
    };

    for (std::size_t k = 0; k < scene.prep().v.size(); ++k) {
        const float r = k == 0 ? 0.1f : 0.2f;
        const float g = k == 0 ? 0.1f : 0.2f;
        const float b = k == 0 ? 0.1f : 0.85f;
        drawLoop(scene.prep().v[k], r, g, b);
    }
}

void Renderer::drawVirtualHandles(const CauchyScene& scene, float scale, float tx, float ty) {
    if (scene.mode() != VizMode::DeformedMap) return;

    float xmin, ymin, xmax, ymax;
    scene.computeBounds(xmin, ymin, xmax, ymax);
    const Eigen::Matrix3f mvp = makeMvp(xmin, ymin, xmax, ymax, viewportW_, viewportH_, scale, tx, ty);

    std::vector<float> pts(static_cast<std::size_t>(scene.prep().numVirtualVertices) * 2);
    for (int i = 0; i < scene.prep().numVirtualVertices; ++i) {
        pts[static_cast<std::size_t>(i) * 2] = static_cast<float>(scene.prep().phi[i].real());
        pts[static_cast<std::size_t>(i) * 2 + 1] = static_cast<float>(scene.prep().phi[i].imag());
    }

    glUseProgram(lineProgram_);
    glUniformMatrix3fv(glGetUniformLocation(lineProgram_, "uMvp"), 1, GL_FALSE, mvp.data());
    glBindVertexArray(lineVao_);
    glBindBuffer(GL_ARRAY_BUFFER, lineVbo_);
    glBufferData(GL_ARRAY_BUFFER, static_cast<GLsizeiptr>(pts.size() * sizeof(float)), pts.data(), GL_DYNAMIC_DRAW);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, nullptr);
    glUniform3f(glGetUniformLocation(lineProgram_, "uColor"), 1.f, 0.2f, 0.1f);
    glPointSize(8.f);
    glDrawArrays(GL_POINTS, 0, scene.prep().numVirtualVertices);
}

void Renderer::draw(const CauchyScene& scene, float scale, float tx, float ty, bool wireframe) {
    float xmin, ymin, xmax, ymax;
    scene.computeBounds(xmin, ymin, xmax, ymax);
    const Eigen::Matrix3f mvp = makeMvp(xmin, ymin, xmax, ymax, viewportW_, viewportH_, scale, tx, ty);

    glViewport(0, 0, viewportW_, viewportH_);
    glClearColor(0.97f, 0.97f, 0.98f, 1.f);
    glClear(GL_COLOR_BUFFER_BIT);

    uploadMesh(scene);

    glUseProgram(program_);
    glUniformMatrix3fv(glGetUniformLocation(program_, "uMvp"), 1, GL_FALSE, mvp.data());
    glUniform1f(glGetUniformLocation(program_, "uMin"), scene.dataMin());
    glUniform1f(glGetUniformLocation(program_, "uMax"), scene.dataMax());

    glBindVertexArray(vao_);
    const int n = static_cast<int>(scene.displayPositions().rows());

    if (scene.mesh().faces.rows() > 0) {
        if (wireframe) glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
        glDrawElements(GL_TRIANGLES, static_cast<GLsizei>(scene.mesh().faces.size() * 3), GL_UNSIGNED_INT, nullptr);
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
    } else {
        glPointSize(6.f);
        glDrawArrays(GL_POINTS, 0, n);
    }

    drawBoundaryLoops(scene, scale, tx, ty);
    drawVirtualHandles(scene, scale, tx, ty);
}
