#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"
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

const double kEps = 1e-12;

ImageMat imread_gray(const std::string& path) {
    int w, h, ch;
    unsigned char* data = stbi_load(path.c_str(), &w, &h, &ch, 1);
    if (!data) throw std::runtime_error("load fail: " + path);
    ImageMat img(h, w);
    for (int r = 0; r < h; ++r)
        for (int c = 0; c < w; ++c)
            img(r, c) = static_cast<double>(data[r * w + c]);
    stbi_image_free(data);
    return img;
}

ImageMat compute_density_map(const ImageMat& image, int sel) {
    int d1 = image.rows() / sel;
    int d2 = image.cols() / sel;
    ImageMat myu(d1, d2);
    for (int i = 0; i < d1; ++i)
        for (int j = 0; j < d2; ++j)
            myu(i, j) = image.block(i*sel, j*sel, sel, sel).sum() / (double)(sel*sel);
    return myu;
}

Tensor2D compute_initial_mapping(const ImageMat& myu_0, const ImageMat& myu_1) {
    int s1 = myu_0.rows();
    int s2 = myu_0.cols();
    
    Eigen::VectorXd a(s1);
    double cum0 = 0, cum1 = 0;
    bool first_corr = false;
    int idx1 = 0;
    for (int idx0 = 0; idx0 < s1; ++idx0) {
        cum0 += myu_0.row(idx0).sum();
        int last = idx1;
        while (cum1 < cum0 && idx1 < s1) { cum1 += myu_1.row(idx1).sum(); ++idx1; }
        if (idx1 < s1 && (idx1 - last) > 0) { --idx1; cum1 -= myu_1.row(std::max(0,idx1)).sum(); }
        else { if (first_corr) cum0 -= myu_0.row(idx0).sum(); else first_corr = true; }
        a(idx0) = idx1 + 1.0;
    }

    Eigen::VectorXd b(s2);
    cum0 = 0; cum1 = 0;
    first_corr = false;
    idx1 = 0;
    for (int idx0 = 0; idx0 < s2; ++idx0) {
        cum0 += myu_0.col(idx0).sum();
        int last = idx1;
        while (cum1 < cum0 && idx1 < s2) { cum1 += myu_1.col(idx1).sum(); ++idx1; }
        if (idx1 < s2 && (idx1 - last) > 0) { --idx1; cum1 -= myu_1.col(std::max(0,idx1)).sum(); }
        else { if (first_corr) cum0 -= myu_0.col(idx0).sum(); else first_corr = true; }
        b(idx0) = idx1 + 1.0;
    }

    Tensor2D u0;
    u0.first = Eigen::MatrixXd(s1, s2);
    u0.second = Eigen::MatrixXd(s1, s2);
    for (int i = 0; i < s1; ++i)
        for (int j = 0; j < s2; ++j) {
            u0.first(i,j) = a(i);
            u0.second(i,j) = b(j);
        }
    return u0;
}

Tensor2D rotate_data(const Tensor2D& v) {
    Tensor2D r;
    r.first = -v.second;
    r.second = v.first;
    return r;
}

ImageMat compute_divergence(const Tensor2D& v) {
    int s1 = v.first.rows(), s2 = v.first.cols();
    ImageMat d = ImageMat::Zero(s1, s2);
    for (int i = 1; i < s1-1; ++i)
        for (int j = 1; j < s2-1; ++j)
            d(i,j) = (v.second(i+1,j)-v.second(i-1,j))*0.5 + (v.first(i,j+1)-v.first(i,j-1))*0.5;
    return d;
}

Tensor2D compute_gradient(const ImageMat& v) {
    int s1 = v.rows(), s2 = v.cols();
    Tensor2D g;
    g.first = ImageMat::Zero(s1,s2);
    g.second = ImageMat::Zero(s1,s2);
    for (int i = 1; i < s1-1; ++i)
        for (int j = 1; j < s2-1; ++j) {
            g.first(i,j) = (v(i+1,j)-v(i-1,j))*0.5;
            g.second(i,j) = (v(i,j+1)-v(i,j-1))*0.5;
        }
    return g;
}

Tensor2D compute_jacobian(const Tensor2D& v) {
    int s1 = v.first.rows(), s2 = v.first.cols();
    Tensor2D J;
    J.first = ImageMat::Zero(s1,s2);
    J.second = ImageMat::Zero(s1,s2);
    for (int i = 1; i < s1-1; ++i)
        for (int j = 1; j < s2-1; ++j) {
            J.first(i,j) = (v.first(i+1,j)-v.first(i-1,j))*0.5;
            J.second(i,j) = (v.second(i,j+1)-v.second(i,j-1))*0.5;
        }
    return J;
}

// Poisson solver struct
struct PoissonSolver5pt {
    int nx, ny;
    double h2;
    Eigen::SparseMatrix<double> L;
    Eigen::SparseLU<Eigen::SparseMatrix<double>> lu;

    PoissonSolver5pt(int nx_, int ny_, double square_edge_len)
        : nx(nx_), ny(ny_) {
        double h = square_edge_len / (nx - 1.0);
        h2 = h * h;
        int N = nx * ny;
        L.resize(N, N);
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
        lu.analyzePattern(L);
        lu.factorize(L);
    }
    Eigen::VectorXd solve(const Eigen::VectorXd& rhs) const {
        return lu.solve(rhs * h2);
    }
};

std::pair<Tensor2D,double> mult_components(const ImageMat& myu0, const Tensor2D& Du, const Tensor2D& gf) {
    int s1 = Du.first.rows(), s2 = Du.first.cols();
    Tensor2D ut;
    ut.first = ImageMat::Zero(s1,s2);
    ut.second = ImageMat::Zero(s1,s2);
    Tensor2D tmp;
    tmp.first = ImageMat::Zero(s1,s2);
    tmp.second = ImageMat::Zero(s1,s2);
    
    ImageMat mu = myu0;
    for (int i=0;i<s1;++i) for(int j=0;j<s2;++j) if(mu(i,j)<1.0) mu(i,j)=1.0;
    
    for (int i=1;i<s1-1;++i) for(int j=1;j<s2-1;++j) {
        double inv = 1.0/mu(i,j);
        ut.first(i,j) = inv * Du.first(i,j) * gf.first(i,j);
        ut.second(i,j) = inv * Du.second(i,j) * gf.second(i,j);
        tmp.first(i,j) = inv * gf.first(i,j);
        tmp.second(i,j) = inv * gf.second(i,j);
    }
    
    double minv = 1e100;
    for (int i=1;i<s1-1;++i) for(int j=1;j<s2-1;++j) {
        double a = std::abs(tmp.first(i,j)), b = std::abs(tmp.second(i,j));
        if(a>kEps) minv = std::min(minv, 1.0/a);
        if(b>kEps) minv = std::min(minv, 1.0/b);
    }
    return {ut, 0.5*minv};
}

double compute_mean_deformation_size(const Tensor2D& v, const Tensor2D& u) {
    int s1 = v.first.rows(), s2 = v.first.cols();
    double sum = 0; int cnt = 0;
    for (int i=1;i<s1-1;++i) for(int j=1;j<s2-1;++j) {
        double dx = v.first(i,j)-u.first(i,j);
        double dy = v.second(i,j)-u.second(i,j);
        sum += std::sqrt(dx*dx+dy*dy);
        ++cnt;
    }
    return cnt>0 ? sum/cnt : 0;
}

std::pair<Tensor2D,double> compute_ut(const Tensor2D& current_u, const ImageMat& myu_0, const ImageMat& myu_1, int sel) {
    // type=0: P = current_u
    auto P = rotate_data(current_u);
    auto divP = compute_divergence(P);
    int n1 = divP.rows(), n2 = divP.cols();
    
    Eigen::VectorXd rhs(n1*n2);
    for(int i=0;i<n1;++i) for(int j=0;j<n2;++j) rhs(i*n2+j) = -divP(i,j);
    
    PoissonSolver5pt poisson(n1, n2, (double)sel);
    auto fvec = poisson.solve(rhs);
    
    ImageMat f(n1,n2);
    for(int i=0;i<n1;++i) for(int j=0;j<n2;++j) f(i,j) = fvec(i*n2+j);
    
    auto gf = rotate_data(compute_gradient(f));
    auto Du = compute_jacobian(current_u);
    return mult_components(myu_0, Du, gf);
}

Tensor2D gradient_descent(const Tensor2D& u0_in, const ImageMat& myu_0, const ImageMat& myu_1, int sel) {
    int s1 = u0_in.first.rows(), s2 = u0_in.first.cols();
    
    Tensor2D cur;
    cur.first = ImageMat::Zero(s1,s2);
    cur.second = ImageMat::Zero(s1,s2);
    
    Tensor2D last_ut;
    last_ut.first = ImageMat::Zero(s1,s2);
    last_ut.second = ImageMat::Zero(s1,s2);
    
    for(int i=0;i<s1;++i) for(int j=0;j<s2;++j) {
        cur.first(i,j) = u0_in.first(i,j) - (i+1.0);
        cur.second(i,j) = u0_in.second(i,j) - (j+1.0);
    }
    
    const int max_iter = 8;
    const double conv_thr = 0.08;
    int iter = 1;
    bool stop = false;
    
    while(!stop && iter <= max_iter) {
        auto [ut, alpha] = compute_ut(cur, myu_0, myu_1, sel);
        for(int i=0;i<s1;++i) for(int j=0;j<s2;++j) {
            cur.first(i,j) -= alpha * ut.first(i,j);
            cur.second(i,j) -= alpha * ut.second(i,j);
        }
        ++iter;
        double size_ut = compute_mean_deformation_size(ut, last_ut);
        printf("  iter %d |ut|=%.6f alpha=%.6f\n", iter-1, size_ut, alpha); fflush(stdout);
        if(size_ut < conv_thr) stop = true;
        last_ut = ut;
    }
    
    Tensor2D u;
    u.first = Eigen::MatrixXd(s1,s2);
    u.second = Eigen::MatrixXd(s1,s2);
    for(int i=0;i<s1;++i) for(int j=0;j<s2;++j) {
        u.first(i,j) = (i+1.0) + cur.first(i,j);
        u.second(i,j) = (j+1.0) + cur.second(i,j);
    }
    return u;
}

Tensor2D compute_image_deformation_map(const Tensor2D& u_myu, const ImageMat& image, int sel) {
    int ih = image.rows(), iw = image.cols();
    int dh = u_myu.first.rows(), dw = u_myu.first.cols();
    
    Tensor2D ui;
    ui.first = ImageMat::Zero(ih, iw);
    ui.second = ImageMat::Zero(ih, iw);
    
    for(int i=0;i<dh;++i) for(int j=0;j<dw;++j) {
        double xl = 1.0 + (u_myu.first(i,j)-1.0)*sel;
        double yl = 1.0 + (u_myu.second(i,j)-1.0)*sel;
        int pi = i*sel, pj = j*sel;
        if(pi<ih && pj<iw) { ui.first(pi,pj)=xl; ui.second(pi,pj)=yl; }
    }
    
    int ulx=0, uy=0, xc=1, yc=1;
    for(int i=0;i<ih-sel;++i) {
        yc=1; uy=0;
        for(int j=0;j<iw-sel;++j) {
            if(ui.first(i,j)<kEps) {
                double rx = (double)(i-ulx)/sel;
                double ry = (double)(j-uy)/sel;
                int nx = std::min(ulx+sel, ih-1);
                int ny = std::min(uy+sel, iw-1);
                double xl = (1-rx)*ui.first(ulx,uy) + rx*ui.first(nx,uy);
                double yl = (1-ry)*ui.second(ulx,uy) + ry*ui.second(ulx,ny);
                xl = std::max(1.0, std::min((double)ih, xl));
                yl = std::max(1.0, std::min((double)iw, yl));
                ui.first(i,j)=xl; ui.second(i,j)=yl;
            }
            if(++yc>sel) { uy+=sel; yc=1; }
        }
        if(++xc>sel) { ulx+=sel; xc=1; }
    }
    
    for(int i=0;i<ih;++i) for(int j=0;j<iw;++j)
        if(ui.first(i,j)<kEps) { ui.first(i,j)=i+1.0; ui.second(i,j)=j+1.0; }
    return ui;
}

ImageMat transform(const Tensor2D& u, const ImageMat& img1, int sel) {
    auto ui = compute_image_deformation_map(u, img1, sel);
    int h=img1.rows(), w=img1.cols();
    ImageMat def = ImageMat::Zero(h,w);
    for(int i=0;i<h;++i) for(int j=0;j<w;++j) {
        int xl = std::max(0,std::min(h-1,(int)std::round(ui.first(i,j))-1));
        int yl = std::max(0,std::min(w-1,(int)std::round(ui.second(i,j))-1));
        def(i,j) = img1(xl,yl);
    }
    int crop = sel+4;
    return def.block(0,0,std::max(1,h-crop),std::max(1,w-crop));
}

#define CHECK(msg) do { printf("%s\n", msg); fflush(stdout); } while(0)

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);
    const std::string base = "../midas-journal-319-master/code_optimal_mass_transport/";
    int sel = 12;

    CHECK("=== Step 1: Load ===");
    auto img0 = imread_gray(base+"test_u0_ax_1.bmp");
    auto img1 = imread_gray(base+"test_u0_ax_2.bmp");

    CHECK("=== Step 2: Density ===");
    auto mu0 = compute_density_map(img0, sel);
    auto mu1 = compute_density_map(img1, sel);

    CHECK("=== Step 3: Initial mapping ===");
    auto u0 = compute_initial_mapping(mu0, mu1);
    CHECK("  u0 computed ok");

    CHECK("=== Step 4a: centre u0 ===");
    int ss1 = u0.first.rows(), ss2 = u0.first.cols();
    Tensor2D cur;
    cur.first = ImageMat::Zero(ss1,ss2);
    cur.second = ImageMat::Zero(ss1,ss2);
    for(int i=0;i<ss1;++i) for(int j=0;j<ss2;++j) {
        cur.first(i,j) = u0.first(i,j) - (i+1.0);
        cur.second(i,j) = u0.second(i,j) - (j+1.0);
    }
    CHECK("  centred ok");

    CHECK("=== Step 4b: compute_ut test ===");
    auto P = rotate_data(cur);
    CHECK("  rotate ok");
    auto divP = compute_divergence(P);
    CHECK("  divergence ok");
    int nn1 = divP.rows(), nn2 = divP.cols();
    Eigen::VectorXd rhs(nn1*nn2);
    for(int i=0;i<nn1;++i) for(int j=0;j<nn2;++j) rhs(i*nn2+j) = -divP(i,j);
    CHECK("  rhs built ok");

    CHECK("  building Poisson solver...");
    PoissonSolver5pt poisson(nn1, nn2, (double)sel);
    CHECK("  Poisson solver built ok");

    auto fvec = poisson.solve(rhs);
    CHECK("  Poisson solved ok");

    ImageMat f(nn1,nn2);
    for(int i=0;i<nn1;++i) for(int j=0;j<nn2;++j) f(i,j) = fvec(i*nn2+j);
    CHECK("  f reshaped ok");

    auto gf = rotate_data(compute_gradient(f));
    CHECK("  gradient ok");
    auto Du = compute_jacobian(cur);
    CHECK("  jacobian ok");
    auto [ut,alpha] = mult_components(mu0, Du, gf);
    CHECK("  mult_components ok");
    printf("  alpha=%.6f\n", alpha);

    CHECK("=== Step 4c: Gradient descent ===");
    auto optimal_u = gradient_descent(u0, mu0, mu1, sel);

    CHECK("=== Step 5: Transform ===");
    auto deformed = transform(optimal_u, img1, sel);
    printf("  deformed %ldx%ld\n", deformed.rows(), deformed.cols());

    // Save
    std::vector<unsigned char> buf(deformed.rows()*deformed.cols());
    for(int i=0;i<deformed.rows();++i) for(int j=0;j<deformed.cols();++j) {
        double v = std::max(0.0, std::min(255.0, std::round(deformed(i,j))));
        buf[i*deformed.cols()+j] = (unsigned char)v;
    }
    stbi_write_bmp("output/test1_full.bmp", deformed.cols(), deformed.rows(), 1, buf.data());
    printf("  Saved to output/test1_full.bmp\n");

    printf("=== DONE ===\n");
    return 0;
}
