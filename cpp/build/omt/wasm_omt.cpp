/**
 * wasm_omt.cpp — Optimal Mass Transport WASM binding
 * 
 * Exposes optimal transport image interpolation to JavaScript.
 * Input:  pixel data arrays (RGB/gray images) from JS
 * Output: interpolated frame pixel data back to JS
 */

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#ifndef EIGEN_NO_DEBUG
#define EIGEN_NO_DEBUG
#endif
#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <Eigen/SparseLU>

#include <emscripten.h>
#include <vector>
#include <string>
#include <utility>
#include <array>
#include <cmath>
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <chrono>

// =============================================================================
// Type aliases (matching optimal_mass_transport.h)
// =============================================================================
using Tensor2D  = std::pair<Eigen::MatrixXd, Eigen::MatrixXd>;
using ImageMat  = Eigen::MatrixXd;
using RGBImage  = std::array<ImageMat, 3>;

// =============================================================================
// Global state
// =============================================================================
static double                          g_lastTimeMs = 0.0;
static std::vector<unsigned char>      g_resultData;   // flat pixel data of all frames
static int                             g_frameW = 0;
static int                             g_frameH = 0;
static int                             g_frameCount = 0;

// =============================================================================
// Constants
// =============================================================================
template<typename T> inline T sqr(T x) { return x * x; }
constexpr double kEps = 1e-12;

// =============================================================================
// stb_image memory-based image loading (replaces file-based stbi_load)
// =============================================================================
inline ImageMat imread_from_memory(const unsigned char* buf, int len, int w, int h) {
    int outW, outH, ch;
    unsigned char* data = stbi_load_from_memory(buf, len, &outW, &outH, &ch, 1);
    if (!data) {
        // If stbi_load_from_memory fails, use the provided dimensions
        // (for raw pixel data passed directly)
        ImageMat img(h, w);
        for (int r = 0; r < h; ++r)
            for (int c = 0; c < w; ++c)
                img(r, c) = static_cast<double>(buf[r * w + c]);
        return img;
    }
    ImageMat img(outH, outW);
    for (int r = 0; r < outH; ++r)
        for (int c = 0; c < outW; ++c)
            img(r, c) = static_cast<double>(data[r * outW + c]);
    stbi_image_free(data);
    return img;
}

// =============================================================================
// Histogram equalisation
// =============================================================================
inline ImageMat histeq(const ImageMat& img) {
    int rows = static_cast<int>(img.rows());
    int cols = static_cast<int>(img.cols());
    int N = rows * cols;

    std::vector<int> hist(256, 0);
    for (int r = 0; r < rows; ++r)
        for (int c = 0; c < cols; ++c) {
            int v = static_cast<int>(std::round(img(r, c)));
            v = std::max(0, std::min(255, v));
            hist[static_cast<size_t>(v)]++;
        }

    std::vector<double> cdf(256, 0.0);
    double acc = 0;
    for (int i = 0; i < 256; ++i) {
        acc += static_cast<double>(hist[i]) / static_cast<double>(N);
        cdf[i] = acc;
    }

    ImageMat out(rows, cols);
    for (int r = 0; r < rows; ++r)
        for (int c = 0; c < cols; ++c) {
            int v = static_cast<int>(std::round(img(r, c)));
            v = std::max(0, std::min(255, v));
            out(r, c) = cdf[static_cast<size_t>(v)] * 255.0;
        }
    return out;
}

// =============================================================================
// Poisson solver – 5-point stencil + SparseLU
// =============================================================================
struct PoissonSolver5pt {
    int nx, ny;
    double h2;
    Eigen::SparseMatrix<double> L;
    Eigen::SparseLU<Eigen::SparseMatrix<double>> lu;

    PoissonSolver5pt(int nx_, int ny_, double square_edge_len)
        : nx(nx_), ny(ny_) {
        double h = square_edge_len / static_cast<double>(nx - 1);
        h2 = h * h;

        int N = nx * ny;
        L.resize(N, N);
        std::vector<Eigen::Triplet<double>> trips;
        trips.reserve(static_cast<size_t>(N) * 5);

        for (int i = 0; i < nx; ++i) {
            for (int j = 0; j < ny; ++j) {
                int row = i * ny + j;
                bool interior = (i > 0 && i < nx - 1 && j > 0 && j < ny - 1);
                if (interior) {
                    trips.emplace_back(row, row,               4.0);
                    trips.emplace_back(row, (i - 1) * ny + j, -1.0);
                    trips.emplace_back(row, (i + 1) * ny + j, -1.0);
                    trips.emplace_back(row, i * ny + (j - 1), -1.0);
                    trips.emplace_back(row, i * ny + (j + 1), -1.0);
                } else {
                    trips.emplace_back(row, row, 1.0);
                }
            }
        }
        L.setFromTriplets(trips.begin(), trips.end());
        L.makeCompressed();
        lu.analyzePattern(L);
        lu.factorize(L);
    }

    Eigen::VectorXd solve(const Eigen::VectorXd& rhs) const {
        Eigen::VectorXd b = rhs * h2;
        return lu.solve(b);
    }
};

// =============================================================================
// Core algorithm functions (from optimal_mass_transport.h, adapted)
// =============================================================================

inline ImageMat compute_density_map(const ImageMat& image, int square_edge_len) {
    int dsize1 = static_cast<int>(image.rows()) / square_edge_len;
    int dsize2 = static_cast<int>(image.cols()) / square_edge_len;
    ImageMat myu(dsize1, dsize2);
    for (int i = 0; i < dsize1; ++i)
        for (int j = 0; j < dsize2; ++j)
            myu(i, j) = image.block(i * square_edge_len, j * square_edge_len,
                                     square_edge_len, square_edge_len).sum()
                      / static_cast<double>(square_edge_len * square_edge_len);
    return myu;
}

inline double row_sum(const ImageMat& m, int r) {
    double s = 0.0;
    for (int c = 0; c < m.cols(); ++c) s += m(r, c);
    return s;
}
inline double col_sum(const ImageMat& m, int c) {
    double s = 0.0;
    for (int r = 0; r < m.rows(); ++r) s += m(r, c);
    return s;
}

inline Tensor2D compute_initial_mapping(const ImageMat& myu_0, const ImageMat& myu_1) {
    int s1 = static_cast<int>(myu_0.rows());
    int s2 = static_cast<int>(myu_0.cols());

    Eigen::VectorXd a(s1);
    Eigen::VectorXd a_int_0(s1), a_int_1(s1);
    double cum0 = 0.0, cum1 = 0.0;
    bool first_correction = false;
    int idx1 = 0;

    for (int idx0 = 0; idx0 < s1; ++idx0) {
        cum0 += row_sum(myu_0, idx0);
        int last = idx1;
        while (cum1 < cum0 && idx1 < s1) { cum1 += row_sum(myu_1, idx1); ++idx1; }
        if (idx1 < s1 && (idx1 - last) > 0) { --idx1; cum1 -= row_sum(myu_1, std::max(0, idx1)); }
        else { if (first_correction) cum0 -= row_sum(myu_0, idx0); else first_correction = true; }
        a_int_0(idx0) = cum0;
        a_int_1(idx0) = cum1;
        a(idx0) = static_cast<double>(idx1 + 1);
    }

    Eigen::VectorXd b(s2);
    cum0 = 0.0; cum1 = 0.0; first_correction = false; idx1 = 0;
    for (int idx0 = 0; idx0 < s2; ++idx0) {
        cum0 += col_sum(myu_0, idx0);
        int last = idx1;
        while (cum1 < cum0 && idx1 < s2) { cum1 += col_sum(myu_1, idx1); ++idx1; }
        if (idx1 < s2 && (idx1 - last) > 0) { --idx1; cum1 -= col_sum(myu_1, std::max(0, idx1)); }
        else { if (first_correction) cum0 -= col_sum(myu_0, idx0); else first_correction = true; }
        b(idx0) = static_cast<double>(idx1 + 1);
    }

    Tensor2D u0;
    u0.first  = Eigen::MatrixXd(s1, s2);
    u0.second = Eigen::MatrixXd(s1, s2);
    for (int i = 0; i < s1; ++i)
        for (int j = 0; j < s2; ++j) {
            u0.first(i, j)  = a(i);
            u0.second(i, j) = b(j);
        }
    return u0;
}

inline Tensor2D rotate_data(const Tensor2D& v) {
    Tensor2D r;
    r.first  = -v.second;
    r.second =  v.first;
    return r;
}

inline ImageMat compute_divergence(const Tensor2D& v) {
    int s1 = static_cast<int>(v.first.rows());
    int s2 = static_cast<int>(v.first.cols());
    ImageMat div = ImageMat::Zero(s1, s2);
    for (int i = 1; i < s1 - 1; ++i)
        for (int j = 1; j < s2 - 1; ++j) {
            double dv_dx = (v.second(i + 1, j) - v.second(i - 1, j)) * 0.5;
            double dv_dy = (v.first(i, j + 1)  - v.first(i, j - 1))  * 0.5;
            div(i, j) = dv_dx + dv_dy;
        }
    return div;
}

inline Tensor2D compute_gradient(const ImageMat& v) {
    int s1 = static_cast<int>(v.rows());
    int s2 = static_cast<int>(v.cols());
    Tensor2D g;
    g.first  = Eigen::MatrixXd::Zero(s1, s2);
    g.second = Eigen::MatrixXd::Zero(s1, s2);
    for (int i = 1; i < s1 - 1; ++i)
        for (int j = 1; j < s2 - 1; ++j) {
            g.first(i, j)  = (v(i + 1, j) - v(i - 1, j)) * 0.5;
            g.second(i, j) = (v(i, j + 1) - v(i, j - 1)) * 0.5;
        }
    return g;
}

inline Tensor2D compute_jacobian(const Tensor2D& v) {
    int s1 = static_cast<int>(v.first.rows());
    int s2 = static_cast<int>(v.first.cols());
    Tensor2D J;
    J.first  = Eigen::MatrixXd::Zero(s1, s2);
    J.second = Eigen::MatrixXd::Zero(s1, s2);
    for (int i = 1; i < s1 - 1; ++i)
        for (int j = 1; j < s2 - 1; ++j) {
            J.first(i, j)  = (v.first(i + 1, j)  - v.first(i - 1, j))  * 0.5;
            J.second(i, j) = (v.second(i, j + 1) - v.second(i, j - 1)) * 0.5;
        }
    return J;
}

inline std::pair<Tensor2D, double> mult_components(
    const ImageMat& myu0, const Tensor2D& Du, const Tensor2D& gradient_f) 
{
    int s1 = static_cast<int>(Du.first.rows());
    int s2 = static_cast<int>(Du.first.cols());
    Tensor2D ut;
    ut.first  = Eigen::MatrixXd::Zero(s1, s2);
    ut.second = Eigen::MatrixXd::Zero(s1, s2);

    Tensor2D tmp;
    tmp.first  = Eigen::MatrixXd::Zero(s1, s2);
    tmp.second = Eigen::MatrixXd::Zero(s1, s2);

    ImageMat myu0_safe = myu0;
    for (int i = 0; i < s1; ++i)
        for (int j = 0; j < s2; ++j)
            if (myu0_safe(i, j) < 1.0) myu0_safe(i, j) = 1.0;

    for (int i = 1; i < s1 - 1; ++i)
        for (int j = 1; j < s2 - 1; ++j) {
            double inv_mu = 1.0 / myu0_safe(i, j);
            ut.first(i, j)   = inv_mu * Du.first(i, j)  * gradient_f.first(i, j);
            ut.second(i, j)  = inv_mu * Du.second(i, j) * gradient_f.second(i, j);
            tmp.first(i, j)  = inv_mu * gradient_f.first(i, j);
            tmp.second(i, j) = inv_mu * gradient_f.second(i, j);
        }

    double min_inv = std::numeric_limits<double>::max();
    for (int i = 1; i < s1 - 1; ++i)
        for (int j = 1; j < s2 - 1; ++j) {
            double abs_t1 = std::abs(tmp.first(i, j));
            double abs_t2 = std::abs(tmp.second(i, j));
            if (abs_t1 > kEps) min_inv = std::min(min_inv, 1.0 / abs_t1);
            if (abs_t2 > kEps) min_inv = std::min(min_inv, 1.0 / abs_t2);
        }
    double alpha = 0.5 * min_inv;
    return {ut, alpha};
}

inline double compute_mean_deformation_size(const Tensor2D& v, const Tensor2D& u) {
    int s1 = static_cast<int>(v.first.rows());
    int s2 = static_cast<int>(v.first.cols());
    double sum = 0.0;
    int cnt = 0;
    for (int i = 1; i < s1 - 1; ++i)
        for (int j = 1; j < s2 - 1; ++j) {
            double dx = v.first(i, j)  - u.first(i, j);
            double dy = v.second(i, j) - u.second(i, j);
            sum += std::sqrt(dx * dx + dy * dy);
            ++cnt;
        }
    return (cnt > 0) ? sum / static_cast<double>(cnt) : 0.0;
}

inline Tensor2D compute_p(const Tensor2D& u, const ImageMat& myu_0,
                           const ImageMat& myu_1, double pure_omt_ratio) {
    int s1 = static_cast<int>(myu_0.rows());
    int s2 = static_cast<int>(myu_0.cols());

    ImageMat mu0x = ImageMat::Zero(s1, s2);
    ImageMat mu0y = ImageMat::Zero(s1, s2);
    for (int i = 1; i < s1 - 1; ++i)
        for (int j = 1; j < s2 - 1; ++j) {
            mu0x(i, j) = (myu_0(i + 1, j) - myu_0(i - 1, j)) * 0.5;
            mu0y(i, j) = (myu_0(i, j + 1) - myu_0(i, j - 1)) * 0.5;
        }

    ImageMat mu0_safe = myu_0;
    for (int i = 0; i < s1; ++i)
        for (int j = 0; j < s2; ++j)
            if (mu0_safe(i, j) < 1.0) mu0_safe(i, j) = 1.0;

    Tensor2D P;
    P.first  = Eigen::MatrixXd::Zero(s1, s2);
    P.second = Eigen::MatrixXd::Zero(s1, s2);

    for (int i = 0; i < s1; ++i)
        for (int j = 0; j < s2; ++j) {
            int xl = std::max(0, std::min(s1 - 1,
                      static_cast<int>(std::round(u.first(i, j))) - 1));
            int yl = std::max(0, std::min(s2 - 1,
                      static_cast<int>(std::round(u.second(i, j))) - 1));
            double diff = sqr(mu0_safe(i, j) - myu_1(xl, yl));
            double inv_mu  = 1.0 / mu0_safe(i, j);
            double inv_mu2 = inv_mu * inv_mu;
            P.first(i, j)  = inv_mu2 * diff * mu0x(i, j)
                           + 2.0 * inv_mu * diff * mu0x(i, j)
                           + 2.0 * sqr(pure_omt_ratio) * u.first(i, j);
            P.second(i, j) = inv_mu2 * diff * mu0y(i, j)
                           + 2.0 * inv_mu * diff * mu0y(i, j)
                           + 2.0 * sqr(pure_omt_ratio) * u.second(i, j);
        }
    return P;
}

inline std::pair<Tensor2D, double> compute_ut(
    const Tensor2D& current_u, const ImageMat& myu_0,
    const ImageMat& myu_1, int square_edge_len, int type, double pure_omt_ratio) 
{
    Tensor2D P;
    if (type == 0) P = current_u;
    else           P = compute_p(current_u, myu_0, myu_1, pure_omt_ratio);

    P = rotate_data(P);
    ImageMat div_P = compute_divergence(P);

    int n1 = static_cast<int>(div_P.rows());
    int n2 = static_cast<int>(div_P.cols());
    Eigen::VectorXd minus_div_P(n1 * n2);
    for (int i = 0; i < n1; ++i)
        for (int j = 0; j < n2; ++j)
            minus_div_P(i * n2 + j) = -div_P(i, j);

    PoissonSolver5pt poisson(n1, n2, static_cast<double>(square_edge_len));
    Eigen::VectorXd f_vec = poisson.solve(minus_div_P);

    ImageMat f(n1, n2);
    for (int i = 0; i < n1; ++i)
        for (int j = 0; j < n2; ++j)
            f(i, j) = f_vec(i * n2 + j);

    Tensor2D grad_f = compute_gradient(f);
    grad_f = rotate_data(grad_f);
    Tensor2D Du = compute_jacobian(current_u);
    return mult_components(myu_0, Du, grad_f);
}

inline Tensor2D gradient_descent(const Tensor2D& u0_in, const ImageMat& myu_0,
                                  const ImageMat& myu_1, int square_edge_len, int type) {
    int s1 = static_cast<int>(u0_in.first.rows());
    int s2 = static_cast<int>(u0_in.first.cols());

    Tensor2D current_u;
    current_u.first  = Eigen::MatrixXd::Zero(s1, s2);
    current_u.second = Eigen::MatrixXd::Zero(s1, s2);

    Tensor2D last_ut;
    last_ut.first  = Eigen::MatrixXd::Zero(s1, s2);
    last_ut.second = Eigen::MatrixXd::Zero(s1, s2);

    for (int i = 0; i < s1; ++i)
        for (int j = 0; j < s2; ++j) {
            current_u.first(i, j)  = u0_in.first(i, j)  - static_cast<double>(i + 1);
            current_u.second(i, j) = u0_in.second(i, j) - static_cast<double>(j + 1);
        }

    constexpr int max_iter = 8;
    constexpr double pure_omt = 0.3;
    constexpr double conv_thr = 0.08;

    int iter = 1;
    bool stop_flag = false;

    while (!stop_flag && iter <= max_iter) {
        auto [ut, alpha] = compute_ut(current_u, myu_0, myu_1,
                                       square_edge_len, type, pure_omt);
        for (int i = 0; i < s1; ++i)
            for (int j = 0; j < s2; ++j) {
                current_u.first(i, j)  -= alpha * ut.first(i, j);
                current_u.second(i, j) -= alpha * ut.second(i, j);
            }
        ++iter;
        double size_ut = compute_mean_deformation_size(ut, last_ut);
        if (size_ut < conv_thr) stop_flag = true;
        last_ut = ut;
    }

    Tensor2D u;
    u.first  = Eigen::MatrixXd(s1, s2);
    u.second = Eigen::MatrixXd(s1, s2);
    for (int i = 0; i < s1; ++i)
        for (int j = 0; j < s2; ++j) {
            u.first(i, j)  = static_cast<double>(i + 1) + current_u.first(i, j);
            u.second(i, j) = static_cast<double>(j + 1) + current_u.second(i, j);
        }
    return u;
}

inline Tensor2D compute_image_deformation_map(const Tensor2D& u_myu,
                                               const ImageMat& image, int square_edge_len) {
    int img_h = static_cast<int>(image.rows());
    int img_w = static_cast<int>(image.cols());
    int d_h   = static_cast<int>(u_myu.first.rows());
    int d_w   = static_cast<int>(u_myu.first.cols());

    Tensor2D u_img;
    u_img.first  = Eigen::MatrixXd::Zero(img_h, img_w);
    u_img.second = Eigen::MatrixXd::Zero(img_h, img_w);

    for (int i = 0; i < d_h; ++i)
        for (int j = 0; j < d_w; ++j) {
            double x_loc = 1.0 + (u_myu.first(i, j)  - 1.0) * square_edge_len;
            double y_loc = 1.0 + (u_myu.second(i, j) - 1.0) * square_edge_len;
            int pi = i * square_edge_len;
            int pj = j * square_edge_len;
            if (pi < img_h && pj < img_w) {
                u_img.first(pi, pj)  = x_loc;
                u_img.second(pi, pj) = y_loc;
            }
        }

    int ul_x = 0, ul_y = 0, x_cnt = 1, y_cnt = 1;
    for (int i = 0; i < img_h - square_edge_len; ++i) {
        y_cnt = 1; ul_y = 0;
        for (int j = 0; j < img_w - square_edge_len; ++j) {
            if (u_img.first(i, j) < kEps) {
                double rx = static_cast<double>(i - ul_x) / square_edge_len;
                double ry = static_cast<double>(j - ul_y) / square_edge_len;
                int ulx_nx = std::min(ul_x + square_edge_len, img_h - 1);
                int uly_ny = std::min(ul_y + square_edge_len, img_w - 1);
                double x_loc = (1.0 - rx) * u_img.first(ul_x, ul_y)
                             + rx        * u_img.first(ulx_nx, ul_y);
                double y_loc = (1.0 - ry) * u_img.second(ul_x, ul_y)
                             + ry        * u_img.second(ul_x, uly_ny);
                x_loc = std::max(1.0, std::min(static_cast<double>(img_h), x_loc));
                y_loc = std::max(1.0, std::min(static_cast<double>(img_w), y_loc));
                u_img.first(i, j)  = x_loc;
                u_img.second(i, j) = y_loc;
            }
            ++y_cnt;
            if (y_cnt > square_edge_len) { ul_y += square_edge_len; y_cnt = 1; }
        }
        ++x_cnt;
        if (x_cnt > square_edge_len) { ul_x += square_edge_len; x_cnt = 1; }
    }

    for (int i = 0; i < img_h; ++i)
        for (int j = 0; j < img_w; ++j)
            if (u_img.first(i, j) < kEps) {
                u_img.first(i, j)  = static_cast<double>(i + 1);
                u_img.second(i, j) = static_cast<double>(j + 1);
            }
    return u_img;
}

// =============================================================================
// External C API for JavaScript
// =============================================================================
extern "C" {

/**
 * Compute optimal transport image interpolation series.
 *
 * Params:
 *   data0, len0, w0, h0  — image 0: raw RGBA pixel data (or gray), width, height
 *   data1, len1, w1, h1  — image 1: raw RGBA pixel data (or gray), width, height
 *   num_channels          — 1 (gray) or 3 (RGB) or 4 (RGBA)
 *   square_edge_len       — block size for density map (default 4)
 *   num_frames            — number of interpolation frames (e.g. 8)
 *   equalization_method   — 0: mass ratio, 1: histogram equalisation
 *
 * Returns: 0 on success, negative on error.
 * Results stored in g_resultData, g_frameW, g_frameH, g_frameCount.
 */
EMSCRIPTEN_KEEPALIVE
int solve_omt_series(
    unsigned char* data0, int len0, int w0, int h0,
    unsigned char* data1, int len1, int w1, int h1,
    int num_channels, int square_edge_len, int num_frames,
    int equalization_method)
{
    // Clear previous results
    g_resultData.clear();
    g_frameW = g_frameH = g_frameCount = 0;

    if (w0 != w1 || h0 != h1) return -1;  // images must be same size
    if (w0 <= 0 || h0 <= 0) return -2;
    if (num_frames < 2) return -3;
    if (num_channels < 1 || num_channels > 4) return -4;

    auto t0 = std::chrono::high_resolution_clock::now();

    try {
        int W = w0, H = h0;
        int ch = num_channels;

        // Convert to ImageMat per channel
        std::vector<ImageMat> img0ch(ch), img1ch(ch);
        for (int k = 0; k < ch; ++k) {
            img0ch[k] = ImageMat::Zero(H, W);
            img1ch[k] = ImageMat::Zero(H, W);
        }

        for (int r = 0; r < H; ++r) {
            for (int c = 0; c < W; ++c) {
                int idx = (r * W + c) * ch;
                for (int k = 0; k < ch; ++k) {
                    img0ch[k](r, c) = static_cast<double>(data0[idx + k]);
                    img1ch[k](r, c) = static_cast<double>(data1[idx + k]);
                }
            }
        }

        // Compute OT map once using grayscale average of all channels
        ImageMat gray0(H, W), gray1(H, W);
        for (int r = 0; r < H; ++r)
            for (int c = 0; c < W; ++c) {
                double s0 = 0, s1 = 0;
                for (int k = 0; k < ch; ++k) {
                    s0 += img0ch[k](r, c);
                    s1 += img1ch[k](r, c);
                }
                gray0(r, c) = s0 / ch;
                gray1(r, c) = s1 / ch;
            }

        // Equalisation
        if (equalization_method == 0) {
            double sum0 = gray0.sum(), sum1 = gray1.sum();
            if (sum0 > kEps) gray0 *= (sum1 / sum0);
        } else {
            gray0 = histeq(gray0);
            gray1 = histeq(gray1);
        }

        ImageMat myu_0 = compute_density_map(gray0, square_edge_len);
        ImageMat myu_1 = compute_density_map(gray1, square_edge_len);

        Tensor2D u0 = compute_initial_mapping(myu_0, myu_1);
        Tensor2D optimal_u = gradient_descent(u0, myu_0, myu_1, square_edge_len, 1);

        // Generate interpolation series
        int s1 = static_cast<int>(optimal_u.first.rows());
        int s2 = static_cast<int>(optimal_u.first.cols());

        Tensor2D delta_u;
        delta_u.first  = Eigen::MatrixXd(s1, s2);
        delta_u.second = Eigen::MatrixXd(s1, s2);
        for (int i = 0; i < s1; ++i)
            for (int j = 0; j < s2; ++j) {
                delta_u.first(i, j)  = (optimal_u.first(i, j)  - (i + 1.0)) / num_frames;
                delta_u.second(i, j) = (optimal_u.second(i, j) - (j + 1.0)) / num_frames;
            }

        int crop = square_edge_len + 4;
        int outH = std::max(1, H - crop);
        int outW = std::max(1, W - crop);

        // Allocate result buffer
        g_resultData.resize(static_cast<size_t>(num_frames) * outH * outW * 4);  // RGBA output
        g_frameW = outW;
        g_frameH = outH;
        g_frameCount = num_frames;

        for (int f = num_frames; f >= 1; --f) {
            // Compute frame deformation
            Tensor2D u_frame;
            u_frame.first  = Eigen::MatrixXd(s1, s2);
            u_frame.second = Eigen::MatrixXd(s1, s2);
            for (int i = 0; i < s1; ++i)
                for (int j = 0; j < s2; ++j) {
                    u_frame.first(i, j)  = optimal_u.first(i, j)
                        - (f - 1) * delta_u.first(i, j);
                    u_frame.second(i, j) = optimal_u.second(i, j)
                        - (f - 1) * delta_u.second(i, j);
                }

            Tensor2D u_img = compute_image_deformation_map(u_frame, img1ch[0], square_edge_len);
            double t_val = static_cast<double>(f) / num_frames;

            // Interpolate each channel
            int frameIdx = num_frames - f;
            unsigned char* outFrame = g_resultData.data() + frameIdx * outW * outH * 4;

            for (int r = 0; r < outH; ++r) {
                for (int c = 0; c < outW; ++c) {
                    int xl = std::max(0, std::min(H - 1,
                        static_cast<int>(std::round(u_img.first(r, c))) - 1));
                    int yl = std::max(0, std::min(W - 1,
                        static_cast<int>(std::round(u_img.second(r, c))) - 1));

                    int outIdx = (r * outW + c) * 4;
                    for (int k = 0; k < ch; ++k) {
                        double v = (1.0 - t_val) * img0ch[k](r, c) + t_val * img1ch[k](xl, yl);
                        v = std::max(0.0, std::min(255.0, v));
                        outFrame[outIdx + k] = static_cast<unsigned char>(v);
                    }
                    // Set alpha channel
                    for (int k = ch; k < 4; ++k) {
                        outFrame[outIdx + k] = 255;
                    }
                }
            }
        }

        auto t1 = std::chrono::high_resolution_clock::now();
        g_lastTimeMs = std::chrono::duration<double, std::milli>(t1 - t0).count();

    } catch (const std::exception& e) {
        // printf("OT exception: %s\n", e.what());
        return -100;
    } catch (...) {
        return -101;
    }

    return 0;
}

EMSCRIPTEN_KEEPALIVE
double get_omt_last_time_ms() { return g_lastTimeMs; }

EMSCRIPTEN_KEEPALIVE
unsigned char* get_omt_result_data() {
    return g_resultData.empty() ? nullptr : g_resultData.data();
}

EMSCRIPTEN_KEEPALIVE
int get_omt_result_size() {
    return static_cast<int>(g_resultData.size());
}

EMSCRIPTEN_KEEPALIVE
int get_omt_frame_width() { return g_frameW; }

EMSCRIPTEN_KEEPALIVE
int get_omt_frame_height() { return g_frameH; }

EMSCRIPTEN_KEEPALIVE
int get_omt_frame_count() { return g_frameCount; }

EMSCRIPTEN_KEEPALIVE
void omt_dispose() {
    g_resultData.clear();
    g_resultData.shrink_to_fit();
    g_frameW = g_frameH = g_frameCount = 0;
}

} // extern "C"
