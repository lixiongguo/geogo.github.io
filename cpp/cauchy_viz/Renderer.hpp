#pragma once

#include "CauchyScene.hpp"

#include <glad/gl.h>
#include <string>
#include <vector>

class Renderer {
public:
    bool init();
    void resize(int w, int h);

    void draw(const CauchyScene& scene, float scale, float tx, float ty, bool wireframe);

private:
    unsigned program_ = 0;
    unsigned lineProgram_ = 0;
    unsigned vao_ = 0;
    unsigned vboPos_ = 0;
    unsigned vboVal_ = 0;
    unsigned ebo_ = 0;
    unsigned lineVao_ = 0;
    unsigned lineVbo_ = 0;

    int viewportW_ = 1;
    int viewportH_ = 1;

    unsigned compileProgram(const char* vs, const char* fs);
    void uploadMesh(const CauchyScene& scene);
    void drawBoundaryLoops(const CauchyScene& scene, float scale, float tx, float ty);
    void drawVirtualHandles(const CauchyScene& scene, float scale, float tx, float ty);
};
