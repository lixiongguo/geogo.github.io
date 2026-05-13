#define STB_IMAGE_IMPLEMENTATION
#include "../deps/stb/stb_image.h"
#include <Eigen/Dense>
#include <cstdio>

using ImageMat = Eigen::MatrixXd;

int main() {
    int w, h, ch;
    unsigned char* data = stbi_load("../midas-journal-319-master/code_optimal_mass_transport/test_u0_ax_1.bmp", &w, &h, &ch, 1);
    ImageMat img(h, w);
    for (int r = 0; r < h; ++r)
        for (int c = 0; c < w; ++c)
            img(r, c) = static_cast<double>(data[r * w + c]);
    stbi_image_free(data);

    int sel = 12;
    int d1 = h / sel;  // 30
    int d2 = w / sel;  // 30

    // Test block
    for (int i = 0; i < d1; ++i) {
        for (int j = 0; j < d2; ++j) {
            printf("  block (%d,%d) start=(%d,%d) size=%dx%d, img=%dx%d\n",
                i, j, i*sel, j*sel, sel, sel, (int)img.rows(), (int)img.cols());
            fflush(stdout);
            double s = img.block(i*sel, j*sel, sel, sel).sum();
            printf("    sum=%.1f\n", s);
        }
    }
    printf("OK\n");
    return 0;
}
