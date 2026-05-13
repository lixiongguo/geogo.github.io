// Quick debug: test image loading and density map
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"
#include <cstdio>
#include <Eigen/Dense>

int main() {
    printf("Starting...\n");
    const char* path = "../midas-journal-319-master/code_optimal_mass_transport/test_u0_ax_1.bmp";
    
    int w, h, ch;
    unsigned char* data = stbi_load(path, &w, &h, &ch, 1);
    if (!data) {
        printf("Failed to load image: %s\n", path);
        return 1;
    }
    printf("Loaded: %d x %d\n", w, h);
    
    Eigen::MatrixXd img(h, w);
    for (int r = 0; r < h; ++r)
        for (int c = 0; c < w; ++c)
            img(r, c) = static_cast<double>(data[r * w + c]);
    
    printf("Matrix: %ld x %ld, sum=%.2f\n", img.rows(), img.cols(), img.sum());
    
    stbi_image_free(data);
    
    // Test density map
    int sel = 12;
    int d1 = h / sel;
    int d2 = w / sel;
    printf("Density map size: %d x %d\n", d1, d2);
    
    Eigen::MatrixXd myu = Eigen::MatrixXd::Zero(d1, d2);
    for (int i = 0; i < d1; ++i)
        for (int j = 0; j < d2; ++j)
            myu(i, j) = img.block(i * sel, j * sel, sel, sel).sum() / (double)(sel * sel);
    
    printf("Density map OK, sum=%.2f\n", myu.sum());
    return 0;
}
