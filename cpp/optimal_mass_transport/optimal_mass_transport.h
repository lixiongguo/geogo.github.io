
#ifndef EIGEN_NO_DEBUG
#define EIGEN_NO_DEBUG
#endif

#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <Eigen/SparseLU>

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#include <string>
#include <vector>
#include <utility>
#include <cmath>
#include <algorithm>
#include <cstdio>

namespace omt {

// ─── Type Aliases ───────────────────────────────────────────────────────────
// Tensor2D: 2-channel 2D field.  .first = channel-0 (x), .second = channel-1 (y)
using Tensor2D  = std::pair<Eigen::MatrixXd, Eigen::MatrixXd>;
using ImageMat  = Eigen::MatrixXd;           // gray-scale double image

// ─── Constants ──────────────────────────────────────────────────────────────
template<typename T> inline T sqr(T x) { return x * x; }
constexpr double kEps = 1e-12;

// =============================================================================
// Poisson solver – 5-point stencil + SparseLU (replaces MATLAB's poicalc)
// =============================================================================
struct PoissonSolver5pt {
    int                nx, ny;          // grid dimensions (incl. boundary rows)
    double             h2;              // h^2 = (square_edge_len / (nx-1))^2
    Eigen::SparseMatrix<double> L;      // Laplacian (nx*ny × nx*ny)
    Eigen::SparseLU<Eigen::SparseMatrix<double>> lu;

    PoissonSolver5pt(int nx_, int ny_, double square_edge_len)
        : nx(nx_), ny(ny_)
    {
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
                    trips.emplace_back(row, row, 1.0);          // Dirichlet BC
                }
            }
        }
        L.setFromTriplets(trips.begin(), trips.end());
        L.makeCompressed();
        lu.analyzePattern(L);
        lu.factorize(L);
    }

    // solve -Δu = f  on the given grid
    Eigen::VectorXd solve(const Eigen::VectorXd& rhs) const {
        Eigen::VectorXd b = rhs * h2;   // scale right-hand side
        return lu.solve(b);
    }
};

// =============================================================================
// Image I/O
// =============================================================================
inline ImageMat imread_gray(const std::string& path) {
    int w, h, ch;
    unsigned char* data = stbi_load(path.c_str(), &w, &h, &ch, 1);
    if (!data) {
        throw std::runtime_error("Cannot open image: " + path);
    }
    ImageMat img(h, w);
    for (int r = 0; r < h; ++r)
        for (int c = 0; c < w; ++c)
            img(r, c) = static_cast<double>(data[r * w + c]);
    stbi_image_free(data);
    return img;
}

inline void imwrite_gray(const std::string& path, const ImageMat& img) {
    int h = static_cast<int>(img.rows());
    int w = static_cast<int>(img.cols());
    std::vector<unsigned char> buf(static_cast<size_t>(h * w));
    for (int r = 0; r < h; ++r)
        for (int c = 0; c < w; ++c) {
            double v = std::round(img(r, c));
            v = std::max(0.0, std::min(255.0, v));
            buf[static_cast<size_t>(r * w + c)] = static_cast<unsigned char>(v);
        }
    stbi_write_bmp(path.c_str(), w, h, 1, buf.data());
}

inline void imwrite_gray_jpg(const std::string& path, const ImageMat& img, int quality = 90) {
    int h = static_cast<int>(img.rows());
    int w = static_cast<int>(img.cols());
    std::vector<unsigned char> buf(static_cast<size_t>(h * w));
    for (int r = 0; r < h; ++r)
        for (int c = 0; c < w; ++c) {
            double v = std::round(img(r, c));
            v = std::max(0.0, std::min(255.0, v));
            buf[static_cast<size_t>(r * w + c)] = static_cast<unsigned char>(v);
        }
    stbi_write_jpg(path.c_str(), w, h, 1, buf.data(), quality);
}

// =============================================================================
// histeq – histogram equalisation (replicates MATLAB's histeq for [0,255])
// =============================================================================
inline ImageMat histeq(const ImageMat& img) {
    int rows = static_cast<int>(img.rows());
    int cols = static_cast<int>(img.cols());
    int N = rows * cols;

    // histogram
    std::vector<int> hist(256, 0);
    for (int r = 0; r < rows; ++r)
        for (int c = 0; c < cols; ++c) {
            int v = static_cast<int>(std::round(img(r, c)));
            v = std::max(0, std::min(255, v));
            hist[static_cast<size_t>(v)]++;
        }

    // CDF
    std::vector<double> cdf(256, 0.0);
    double acc = 0;
    for (int i = 0; i < 256; ++i) {
        acc += static_cast<double>(hist[i]) / static_cast<double>(N);
        cdf[i] = acc;
    }

    // map
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
// Core algorithm functions
// =============================================================================

// --- compute_density_map ----------------------------------------------------
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

// --- compute_initial_mapping ------------------------------------------------
// 1-D Monge-Kantorovich along x then y → separable initial map
// helper: manual row/col sum to avoid Eigen block-sum assertion
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

    // ---- x-axis (rows) ------------------------------------------------------
    Eigen::VectorXd a(s1);
    Eigen::VectorXd a_int_0(s1), a_int_1(s1);
    double cum0 = 0.0, cum1 = 0.0;
    bool first_correction = false;
    int idx1 = 0;

    for (int idx0 = 0; idx0 < s1; ++idx0) {
        cum0 += row_sum(myu_0, idx0);
        int last = idx1;
        while (cum1 < cum0 && idx1 < s1) {
            cum1 += row_sum(myu_1, idx1);
            ++idx1;
        }
        if (idx1 < s1 && (idx1 - last) > 0) {
            --idx1;
            cum1 -= row_sum(myu_1, std::max(0, idx1));
        } else {
            if (first_correction)
                cum0 -= row_sum(myu_0, idx0);
            else
                first_correction = true;
        }
        a_int_0(idx0) = cum0;
        a_int_1(idx0) = cum1;
        a(idx0)        = static_cast<double>(idx1 + 1);   // keep 1-based
    }

    // ---- y-axis (cols) ------------------------------------------------------
    Eigen::VectorXd b(s2);
    Eigen::VectorXd b_int_0(s2), b_int_1(s2);
    cum0 = 0.0; cum1 = 0.0;
    first_correction = false;
    idx1 = 0;

    for (int idx0 = 0; idx0 < s2; ++idx0) {
        cum0 += col_sum(myu_0, idx0);
        int last = idx1;
        while (cum1 < cum0 && idx1 < s2) {
            cum1 += col_sum(myu_1, idx1);
            ++idx1;
        }
        if (idx1 < s2 && (idx1 - last) > 0) {
            --idx1;
            cum1 -= col_sum(myu_1, std::max(0, idx1));
        } else {
            if (first_correction)
                cum0 -= col_sum(myu_0, idx0);
            else
                first_correction = true;
        }
        b_int_0(idx0) = cum0;
        b_int_1(idx0) = cum1;
        b(idx0)        = static_cast<double>(idx1 + 1);
    }

    // ---- build u0 -----------------------------------------------------------
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

// --- rotate_data ------------------------------------------------------------
// 90° counter-clockwise rotation of a 2D vector field
inline Tensor2D rotate_data(const Tensor2D& v) {
    Tensor2D r;
    r.first  = -v.second;
    r.second =  v.first;
    return r;
}

// --- compute_divergence -----------------------------------------------------
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

// --- compute_gradient -------------------------------------------------------
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

// --- compute_jacobian -------------------------------------------------------
// diagonal approximation
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

// --- mult_components --------------------------------------------------------
// combine myu0, Du (jacobian), gradient_f → ut + adaptive step alpha
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

    // alpha = 0.5 * min(1/|tmp|)  over all non-eps entries
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

// --- compute_mean_deformation_size ------------------------------------------
inline double compute_mean_deformation_size(const Tensor2D& v, const Tensor2D& u) {
    int s1 = static_cast<int>(v.first.rows());
    int s2 = static_cast<int>(v.first.cols());
    double sum = 0.0;
    int    cnt = 0;
    for (int i = 1; i < s1 - 1; ++i)
        for (int j = 1; j < s2 - 1; ++j) {
            double dx = v.first(i, j)  - u.first(i, j);
            double dy = v.second(i, j) - u.second(i, j);
            sum += std::sqrt(dx * dx + dy * dy);
            ++cnt;
        }
    return (cnt > 0) ? sum / static_cast<double>(cnt) : 0.0;
}

// --- computeP ---------------------------------------------------------------
inline Tensor2D compute_p(const Tensor2D& u,
                           const ImageMat& myu_0,
                           const ImageMat& myu_1,
                           double pure_omt_ratio)
{
    int s1 = static_cast<int>(myu_0.rows());
    int s2 = static_cast<int>(myu_0.cols());

    // gradient of myu_0 (central differences, boundary = 0)
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

// --- compute_ut -------------------------------------------------------------
// one gradient-descent step — compute velocity field ut and step alpha
inline std::pair<Tensor2D, double>
compute_ut(const Tensor2D& current_u,
           const ImageMat&   myu_0,
           const ImageMat&   myu_1,
           int               square_edge_len,
           int               type,
           double            pure_omt_ratio)
{
    Tensor2D P;
    if (type == 0) {
        P = current_u;
    } else {
        P = compute_p(current_u, myu_0, myu_1, pure_omt_ratio);
    }

    P = rotate_data(P);

    ImageMat div_P = compute_divergence(P);

    int n1 = static_cast<int>(div_P.rows());
    int n2 = static_cast<int>(div_P.cols());

    // flatten & negate
    Eigen::VectorXd minus_div_P(n1 * n2);
    for (int i = 0; i < n1; ++i)
        for (int j = 0; j < n2; ++j)
            minus_div_P(i * n2 + j) = -div_P(i, j);

    // solve Poisson
    PoissonSolver5pt poisson(n1, n2, static_cast<double>(square_edge_len));
    Eigen::VectorXd f_vec = poisson.solve(minus_div_P);

    // reshape back to matrix
    ImageMat f(n1, n2);
    for (int i = 0; i < n1; ++i)
        for (int j = 0; j < n2; ++j)
            f(i, j) = f_vec(i * n2 + j);

    Tensor2D grad_f = compute_gradient(f);
    grad_f = rotate_data(grad_f);

    Tensor2D Du = compute_jacobian(current_u);

    return mult_components(myu_0, Du, grad_f);
}

// --- gradient_descent -------------------------------------------------------
inline Tensor2D gradient_descent(const Tensor2D& u0_in,
                                  const ImageMat&   myu_0,
                                  const ImageMat&   myu_1,
                                  int               square_edge_len,
                                  int               type)
{
    int s1 = static_cast<int>(u0_in.first.rows());
    int s2 = static_cast<int>(u0_in.first.cols());

    Tensor2D current_u;
    current_u.first  = Eigen::MatrixXd::Zero(s1, s2);
    current_u.second = Eigen::MatrixXd::Zero(s1, s2);

    Tensor2D last_ut;
    last_ut.first  = Eigen::MatrixXd::Zero(s1, s2);
    last_ut.second = Eigen::MatrixXd::Zero(s1, s2);

    // centre u0 (subtract own coordinates → displacement field)
    for (int i = 0; i < s1; ++i)
        for (int j = 0; j < s2; ++j) {
            current_u.first(i, j)  = u0_in.first(i, j)  - static_cast<double>(i + 1);
            current_u.second(i, j) = u0_in.second(i, j) - static_cast<double>(j + 1);
        }

    constexpr int    max_iter   = 8;
    constexpr double pure_omt   = 0.3;
    constexpr double conv_thr   = 0.08;

    int  iter      = 1;
    bool stop_flag = false;

    while (!stop_flag && iter <= max_iter) {
        auto [ut, alpha] = compute_ut(current_u, myu_0, myu_1,
                                       square_edge_len, type, pure_omt);

        // update
        for (int i = 0; i < s1; ++i)
            for (int j = 0; j < s2; ++j) {
                current_u.first(i, j)  -= alpha * ut.first(i, j);
                current_u.second(i, j) -= alpha * ut.second(i, j);
            }

        ++iter;

        double size_ut = compute_mean_deformation_size(ut, last_ut);
        printf("  iter %d  |ut| = %.6f  thresh = %.6f\n", iter - 1, size_ut, conv_thr);

        if (size_ut < conv_thr)
            stop_flag = true;

        last_ut = ut;
    }

    if (stop_flag)
        printf("  stopped: ut converged (small deformations)\n");
    else
        printf("  stopped: maximum iterations reached\n");

    // restore absolute coordinates
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

// --- compute_image_deformation_map ------------------------------------------
// upsample density-level map → pixel-level map (linear interpolation)
inline Tensor2D
compute_image_deformation_map(const Tensor2D& u_myu,
                               const ImageMat& image,
                               int             square_edge_len)
{
    int img_h = static_cast<int>(image.rows());
    int img_w = static_cast<int>(image.cols());
    int d_h   = static_cast<int>(u_myu.first.rows());
    int d_w   = static_cast<int>(u_myu.first.cols());

    Tensor2D u_img;
    u_img.first  = Eigen::MatrixXd::Zero(img_h, img_w);
    u_img.second = Eigen::MatrixXd::Zero(img_h, img_w);

    // seed nodal values
    for (int i = 0; i < d_h; ++i) {
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
    }

    // linear interpolation within each block
    int ul_x = 0, ul_y = 0;
    int x_cnt = 1, y_cnt = 1;

    for (int i = 0; i < img_h - square_edge_len; ++i) {
        y_cnt  = 1;
        ul_y   = 0;
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
            if (y_cnt > square_edge_len) {
                ul_y   += square_edge_len;
                y_cnt   = 1;
            }
        }
        ++x_cnt;
        if (x_cnt > square_edge_len) {
            ul_x   += square_edge_len;
            x_cnt   = 1;
        }
    }

    // boundary completion — assume small deformation
    for (int i = 0; i < img_h; ++i)
        for (int j = 0; j < img_w; ++j)
            if (u_img.first(i, j) < kEps) {
                u_img.first(i, j)  = static_cast<double>(i + 1);
                u_img.second(i, j) = static_cast<double>(j + 1);
            }

    return u_img;
}

// --- transform (no intensity mixing) ----------------------------------------
inline ImageMat transform(const Tensor2D& u,
                           const ImageMat& image_1,
                           int             square_edge_len)
{
    Tensor2D u_img = compute_image_deformation_map(u, image_1, square_edge_len);

    int h = static_cast<int>(image_1.rows());
    int w = static_cast<int>(image_1.cols());
    ImageMat deformed = ImageMat::Zero(h, w);

    for (int i = 0; i < h; ++i)
        for (int j = 0; j < w; ++j) {
            int xl = std::max(0, std::min(h - 1,
                       static_cast<int>(std::round(u_img.first(i, j))) - 1));
            int yl = std::max(0, std::min(w - 1,
                       static_cast<int>(std::round(u_img.second(i, j))) - 1));
            deformed(i, j) = image_1(xl, yl);
        }

    // crop boundary
    int crop = square_edge_len + 4;
    int new_h = std::max(1, h - crop);
    int new_w = std::max(1, w - crop);
    return deformed.block(0, 0, new_h, new_w);
}

// --- transform_intensity (with intensity mixing) ----------------------------
inline ImageMat transform_intensity(const Tensor2D& u,
                                     const ImageMat& image_0,
                                     const ImageMat& image_1,
                                     int             square_edge_len,
                                     double          t)
{
    Tensor2D u_img = compute_image_deformation_map(u, image_1, square_edge_len);

    int h = static_cast<int>(image_1.rows());
    int w = static_cast<int>(image_1.cols());
    ImageMat deformed = ImageMat::Zero(h, w);

    for (int i = 0; i < h; ++i)
        for (int j = 0; j < w; ++j) {
            int xl = std::max(0, std::min(h - 1,
                       static_cast<int>(std::round(u_img.first(i, j))) - 1));
            int yl = std::max(0, std::min(w - 1,
                       static_cast<int>(std::round(u_img.second(i, j))) - 1));
            deformed(i, j) = (1.0 - t) * image_0(i, j) + t * image_1(xl, yl);
        }

    // crop boundary
    int crop = square_edge_len + 4;
    int new_h = std::max(1, h - crop);
    int new_w = std::max(1, w - crop);
    return deformed.block(0, 0, new_h, new_w);
}

// --- create_image_series ----------------------------------------------------
inline std::vector<ImageMat>
create_image_series(const Tensor2D& optimal_u,
                     const ImageMat& image_0,
                     const ImageMat& image_1,
                     int             square_edge_len,
                     int             num_frames)
{
    int s1 = static_cast<int>(optimal_u.first.rows());
    int s2 = static_cast<int>(optimal_u.first.cols());

    // delta_u per frame
    Tensor2D delta_u;
    delta_u.first  = Eigen::MatrixXd(s1, s2);
    delta_u.second = Eigen::MatrixXd(s1, s2);

    for (int i = 0; i < s1; ++i)
        for (int j = 0; j < s2; ++j) {
            delta_u.first(i, j)  = (optimal_u.first(i, j)  - static_cast<double>(i + 1))
                                   / static_cast<double>(num_frames);
            delta_u.second(i, j) = (optimal_u.second(i, j) - static_cast<double>(j + 1))
                                   / static_cast<double>(num_frames);
        }

    std::vector<ImageMat> series;
    series.reserve(static_cast<size_t>(num_frames));

    for (int f = num_frames; f >= 1; --f) {
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

        double t = static_cast<double>(f) / static_cast<double>(num_frames);
        series.push_back(transform_intensity(u_frame, image_0, image_1,
                                              square_edge_len, t));
    }
    return series;
}

// --- compute_optimal_mass_transport (top-level entry) -----------------------
inline Tensor2D
compute_optimal_mass_transport(const std::string& img0_path,
                                const std::string& img1_path,
                                int                square_edge_len,
                                int                P_type,
                                int                equalization_method)
{
    ImageMat image_0 = imread_gray(img0_path);
    ImageMat image_1 = imread_gray(img1_path);

    printf("Image sizes: %ld×%ld  %ld×%ld\n",
           image_0.rows(), image_0.cols(),
           image_1.rows(), image_1.cols());

    // equalisation
    if (equalization_method == 0) {
        double sum0 = image_0.sum();
        double sum1 = image_1.sum();
        if (sum0 > kEps)
            image_0 *= (sum1 / sum0);
    } else if (equalization_method == 1) {
        image_0 = histeq(image_0);
        image_1 = histeq(image_1);
    } else {
        throw std::runtime_error("Invalid equalization_method");
    }

    // verify same total mass
    double mass_diff = std::abs(image_0.sum() - image_1.sum());
    if (mass_diff < 1.0)
        printf("total mass is (approximately) equal (diff = %.2f)\n", mass_diff);

    ImageMat myu_0 = compute_density_map(image_0, square_edge_len);
    ImageMat myu_1 = compute_density_map(image_1, square_edge_len);

    printf("Density maps: %ld×%ld\n", myu_0.rows(), myu_0.cols());

    Tensor2D u0 = compute_initial_mapping(myu_0, myu_1);
    printf("Initial mapping computed.\n");

    Tensor2D u = gradient_descent(u0, myu_0, myu_1, square_edge_len, P_type);
    return u;
}

} // namespace omt
