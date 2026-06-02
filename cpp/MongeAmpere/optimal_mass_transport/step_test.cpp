#define STB_IMAGE_IMPLEMENTATION
#include "../deps/stb/stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "../deps/stb/stb_image_write.h"
#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <Eigen/SparseLU>
#include <cstdio>
#include <cmath>
#include <vector>
#include <utility>
#include <algorithm>

using Tensor2D = std::pair<Eigen::MatrixXd, Eigen::MatrixXd>;
using ImageMat = Eigen::MatrixXd;

ImageMat imread_gray(const std::string& path) {
    int w, h, ch;
    unsigned char* data = stbi_load(path.c_str(), &w, &h, &ch, 1);
    ImageMat img(h, w);
    for (int r = 0; r < h; ++r)
        for (int c = 0; c < w; ++c)
            img(r, c) = static_cast<double>(data[r * w + c]);
    stbi_image_free(data);
    return img;
}

int main() {
    printf("Step 1: load image\n"); fflush(stdout);
    auto img = imread_gray("../midas-journal-319-master/code_optimal_mass_transport/test_u0_ax_1.bmp");
    printf("  rows=%ld cols=%ld sum=%.1f\n", img.rows(), img.cols(), img.sum()); fflush(stdout);

    printf("Step 2: density map\n"); fflush(stdout);
    int sel = 12;
    int d1 = img.rows() / sel;
    int d2 = img.cols() / sel;
    ImageMat myu(d1, d2);
    for (int i = 0; i < d1; ++i)
        for (int j = 0; j < d2; ++j)
            myu(i, j) = img.block(i*sel, j*sel, sel, sel).sum() / (sel*sel);
    printf("  density %ldx%ld ok\n", myu.rows(), myu.cols()); fflush(stdout);

    printf("Step 3: poisson test\n"); fflush(stdout);
    int nx = d1, ny = d2;
    int N = nx * ny;
    double h = (double)sel / (nx - 1);
    double h2 = h * h;
    printf("  N=%d h2=%.6f\n", N, h2); fflush(stdout);

    Eigen::SparseMatrix<double> L(N, N);
    std::vector<Eigen::Triplet<double>> trips;
    for (int i = 0; i < nx; ++i)
        for (int j = 0; j < ny; ++j) {
            int row = i * ny + j;
            if (i > 0 && i < nx-1 && j > 0 && j < ny-1) {
                trips.emplace_back(row, row, 4.0);
                trips.emplace_back(row, (i-1)*ny+j, -1.0);
                trips.emplace_back(row, (i+1)*ny+j, -1.0);
                trips.emplace_back(row, i*ny+(j-1), -1.0);
                trips.emplace_back(row, i*ny+(j+1), -1.0);
            } else {
                trips.emplace_back(row, row, 1.0);
            }
        }
    L.setFromTriplets(trips.begin(), trips.end());
    L.makeCompressed();
    printf("  L built, nnz=%ld\n", L.nonZeros()); fflush(stdout);

    Eigen::SparseLU<Eigen::SparseMatrix<double>> lu;
    printf("  analyzing pattern...\n"); fflush(stdout);
    lu.analyzePattern(L);
    printf("  factorizing...\n"); fflush(stdout);
    lu.factorize(L);
    printf("  done!\n"); fflush(stdout);

    Eigen::VectorXd rhs = Eigen::VectorXd::Random(N) * h2;
    Eigen::VectorXd sol = lu.solve(rhs);
    printf("  solved OK, norm=%.6f\n", sol.norm()); fflush(stdout);

    printf("All steps passed!\n");
    return 0;
}
