#include "CauchyScene.hpp"
#include "DataLoader.hpp"
#include "Renderer.hpp"

#include <glad/gl.h>

#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>

namespace {

GLFWwindow* g_window = nullptr;
CauchyScene g_scene;
Renderer g_renderer;

float g_scale = 1.f;
float g_tx = 0.f;
float g_ty = 0.f;
bool g_wireframe = false;

int g_dragVirt = -1;
double g_lastMouseX = 0;
double g_lastMouseY = 0;
bool g_panning = false;

void cursorToFramebuffer(double cx, double cy, double& fbx, double& fby) {
    int ww = 1, wh = 1, fbw = 1, fbh = 1;
    glfwGetWindowSize(g_window, &ww, &wh);
    glfwGetFramebufferSize(g_window, &fbw, &fbh);
    fbx = cx * static_cast<double>(fbw) / static_cast<double>(std::max(ww, 1));
    fby = cy * static_cast<double>(fbh) / static_cast<double>(std::max(wh, 1));
}

void screenToWorld(double fbx, double fby, float& wx, float& wy) {
    int fbw = 1, fbh = 1;
    glfwGetFramebufferSize(g_window, &fbw, &fbh);

    float xmin, ymin, xmax, ymax;
    g_scene.computeBounds(xmin, ymin, xmax, ymax);
    const float cx = 0.5f * (xmin + xmax) + g_tx;
    const float cy = 0.5f * (ymin + ymax) + g_ty;
    const float sx = (xmax - xmin) / g_scale;
    const float sy = (ymax - ymin) / g_scale;
    const float aspect = static_cast<float>(fbw) / static_cast<float>(fbh);

    const float ndcX = static_cast<float>(fbx / fbw) * 2.f - 1.f;
    const float ndcY = 1.f - static_cast<float>(fby / fbh) * 2.f;

    wx = cx + ndcX * sx * 0.5f;
    wy = cy + ndcY * sy * 0.5f / aspect;
}

void updateTitle() {
    std::string title = "Cauchy Coordinates Viz | " + g_scene.modeLabel();
    title += " | [/] coeff  m mode  d deform  r reset  w wire";
    glfwSetWindowTitle(g_window, title.c_str());
}

void cycleMode() {
    switch (g_scene.mode()) {
        case VizMode::BasisAbs: g_scene.setMode(VizMode::BasisReal); break;
        case VizMode::BasisReal: g_scene.setMode(VizMode::BasisImag); break;
        case VizMode::BasisImag: g_scene.setMode(VizMode::PartitionUnity); break;
        case VizMode::PartitionUnity: g_scene.setMode(VizMode::DeformedMap); break;
        case VizMode::DeformedMap: g_scene.setMode(VizMode::BasisAbs); break;
    }
    updateTitle();
}

void keyCallback(GLFWwindow*, int key, int, int action, int) {
    if (action != GLFW_PRESS && action != GLFW_REPEAT) return;
    switch (key) {
        case GLFW_KEY_ESCAPE:
            glfwSetWindowShouldClose(g_window, GLFW_TRUE);
            break;
        case GLFW_KEY_LEFT_BRACKET:
            g_scene.nextCoefficient(-1);
            updateTitle();
            break;
        case GLFW_KEY_RIGHT_BRACKET:
            g_scene.nextCoefficient(1);
            updateTitle();
            break;
        case GLFW_KEY_M:
            cycleMode();
            break;
        case GLFW_KEY_D:
            g_scene.setMode(VizMode::DeformedMap);
            updateTitle();
            break;
        case GLFW_KEY_R:
            g_scene.resetPhi();
            updateTitle();
            break;
        case GLFW_KEY_W:
            g_wireframe = !g_wireframe;
            break;
        default:
            break;
    }
}

void mouseButtonCallback(GLFWwindow*, int button, int action, int mods) {
    (void)mods;
    double cx, cy, fbx, fby;
    glfwGetCursorPos(g_window, &cx, &cy);
    cursorToFramebuffer(cx, cy, fbx, fby);

    if (button == GLFW_MOUSE_BUTTON_MIDDLE) {
        g_panning = (action == GLFW_PRESS);
        g_lastMouseX = cx;
        g_lastMouseY = cy;
        return;
    }

    if (button == GLFW_MOUSE_BUTTON_LEFT && action == GLFW_PRESS && g_scene.mode() == VizMode::DeformedMap) {
        float wx, wy;
        screenToWorld(fbx, fby, wx, wy);
        float xmin, ymin, xmax, ymax;
        g_scene.computeBounds(xmin, ymin, xmax, ymax);
        const float pickR = 0.04f * std::max(xmax - xmin, ymax - ymin);
        g_dragVirt = g_scene.pickVirtualVertex(wx, wy, pickR);
    }
    if (action == GLFW_RELEASE) g_dragVirt = -1;
}

void cursorPosCallback(GLFWwindow*, double x, double y) {
    if (g_panning) {
        int ww = 1, wh = 1;
        glfwGetWindowSize(g_window, &ww, &wh);
        float xmin, ymin, xmax, ymax;
        g_scene.computeBounds(xmin, ymin, xmax, ymax);
        const float sx = (xmax - xmin) / g_scale;
        const float sy = (ymax - ymin) / g_scale;
        int fbw = 1, fbh = 1;
        glfwGetFramebufferSize(g_window, &fbw, &fbh);
        const float aspect = static_cast<float>(fbw) / static_cast<float>(fbh);
        g_tx -= static_cast<float>(x - g_lastMouseX) / static_cast<float>(std::max(ww, 1)) * sx;
        g_ty += static_cast<float>(y - g_lastMouseY) / static_cast<float>(std::max(wh, 1)) * sy / aspect;
        g_lastMouseX = x;
        g_lastMouseY = y;
        return;
    }

    if (g_dragVirt >= 0) {
        double fbx, fby;
        cursorToFramebuffer(x, y, fbx, fby);
        float wx, wy;
        screenToWorld(fbx, fby, wx, wy);
        g_scene.moveVirtualVertex(g_dragVirt, wx, wy);
        updateTitle();
    }
}

void scrollCallback(GLFWwindow*, double, double yoffset) {
    g_scale *= yoffset > 0 ? 0.9f : 1.1f;
    g_scale = std::max(0.2f, std::min(g_scale, 5.f));
}

void framebufferSizeCallback(GLFWwindow*, int w, int h) { g_renderer.resize(w, h); }

void printHelp() {
    std::cout <<
        "Cauchy Coordinates Visualizer\n"
        "  [ / ]     previous / next basis index\n"
        "  m         cycle visualization mode\n"
        "  d         deformation mode (drag red control points)\n"
        "  r         reset phi to identity\n"
        "  w         toggle wireframe\n"
        "  wheel     zoom   middle-drag pan\n";
}

}  // namespace

int main(int argc, char** argv) {
    printHelp();

    const std::string repo = findRepoRoot(argc, argv);
    bool useViewer = true;
    for (int i = 1; i < argc; ++i) {
        if (std::string(argv[i]) == "--testdata") useViewer = false;
    }

    if (useViewer) {
        if (!g_scene.loadFromViewerDataset(repo, "annulus")) {
            std::cerr << "Viewer dataset missing, falling back to testdata.\n";
            if (!g_scene.loadFromTestdata(repo, "annulus")) {
                std::cerr << "Failed to load dataset from " << repo << '\n';
                return 1;
            }
        }
    } else if (!g_scene.loadFromTestdata(repo, "annulus")) {
        std::cerr << "Failed to load testdata from " << repo << '\n';
        return 1;
    }

    std::cout << "Loaded mesh: " << g_scene.mesh().vertices.rows() << " vertices, "
              << g_scene.mesh().faces.rows() << " faces\n";
    std::cout << "Cauchy matrix: " << g_scene.prep().C.rows() << " x " << g_scene.prep().C.cols() << '\n';

    if (!glfwInit()) return 1;

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    g_window = glfwCreateWindow(1280, 960, "Cauchy Coordinates Viz", nullptr, nullptr);
    if (!g_window) {
        glfwTerminate();
        return 1;
    }

    glfwMakeContextCurrent(g_window);
    glfwSwapInterval(1);

    if (!gladLoadGL(reinterpret_cast<GLADloadfunc>(glfwGetProcAddress))) {
        std::cerr << "GLAD init failed\n";
        return 1;
    }

    if (!g_renderer.init()) {
        std::cerr << "Renderer init failed\n";
        return 1;
    }

    int w, h;
    glfwGetFramebufferSize(g_window, &w, &h);
    g_renderer.resize(w, h);

    glfwSetKeyCallback(g_window, keyCallback);
    glfwSetMouseButtonCallback(g_window, mouseButtonCallback);
    glfwSetCursorPosCallback(g_window, cursorPosCallback);
    glfwSetScrollCallback(g_window, scrollCallback);
    glfwSetFramebufferSizeCallback(g_window, framebufferSizeCallback);

    updateTitle();

    while (!glfwWindowShouldClose(g_window)) {
        g_renderer.draw(g_scene, g_scale, g_tx, g_ty, g_wireframe);
        glfwSwapBuffers(g_window);
        glfwPollEvents();
    }

    glfwDestroyWindow(g_window);
    glfwTerminate();
    return 0;
}
