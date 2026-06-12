#include "CauchyScene.hpp"

#include <algorithm>
#include <cmath>
#include <sstream>

namespace {

float complexAbs(const p2p_harmonic::Complex& z) {
    return static_cast<float>(std::abs(z));
}

}  // namespace

bool CauchyScene::loadFromTestdata(const std::string& repoRoot, const std::string& name) {
    const std::string prefix = repoRoot + "/cpp/p2p_harmonic/testdata/" + name;
    if (!loadTestdata(prefix, mesh_, boundary_)) return false;
    recomputePrep();
    return true;
}

bool CauchyScene::loadFromViewerDataset(const std::string& repoRoot, const std::string& dataset) {
    const std::string dir = repoRoot + "/data/" + dataset;
    if (!loadViewerDataset(dir, mesh_, boundary_)) return false;
    recomputePrep();
    return true;
}

void CauchyScene::recomputePrep() {
    p2p_harmonic::P2PHarmonicPrepInput input;
    input.cage = boundary_.cage;
    input.holes = boundary_.holes;
    input.meshVertices = meshToComplex(mesh_.vertices);
    input.params = boundary_.params;
    if (input.params.numEnergySamples <= 0) input.params.numEnergySamples = 1000;
    if (input.params.numVirtualVertices <= 0) input.params.numVirtualVertices = 1;

    prep_ = p2p_harmonic::p2pHarmonicPrep(input);
    deformed_.resize(mesh_.vertices.rows(), 2);
    resetPhi();
}

void CauchyScene::setMode(VizMode mode) {
    mode_ = mode;
    updateScalarField();
}

void CauchyScene::nextCoefficient(int delta) {
    const int n = numCoefficients();
    if (n <= 0) return;
    activeCoeff_ = (activeCoeff_ + delta) % n;
    if (activeCoeff_ < 0) activeCoeff_ += n;
    updateScalarField();
}

int CauchyScene::numCoefficients() const { return prep_.C.cols(); }

void CauchyScene::resetPhi() {
    prep_.phi = prep_.vv;
    prep_.psy = p2p_harmonic::VecC::Zero(prep_.numVirtualVertices);
    recomputeDeformation();
}

int CauchyScene::pickVirtualVertex(float wx, float wy, float radius) const {
    const float r2 = radius * radius;
    int best = -1;
    float bestD = r2;
    for (int i = 0; i < prep_.numVirtualVertices; ++i) {
        const float dx = static_cast<float>(prep_.phi[i].real()) - wx;
        const float dy = static_cast<float>(prep_.phi[i].imag()) - wy;
        const float d2 = dx * dx + dy * dy;
        if (d2 < bestD) {
            bestD = d2;
            best = i;
        }
    }
    return best;
}

void CauchyScene::moveVirtualVertex(int index, float wx, float wy) {
    if (index < 0 || index >= prep_.numVirtualVertices) return;
    prep_.phi[index] = p2p_harmonic::Complex(wx, wy);
    recomputeDeformation();
}

void CauchyScene::recomputeDeformation() {
    prep_.xp2pDeform = prep_.C * prep_.phi + (prep_.C * prep_.psy).conjugate();
    deformed_.resize(mesh_.vertices.rows(), 2);
    for (Eigen::Index i = 0; i < deformed_.rows(); ++i) {
        deformed_(i, 0) = static_cast<float>(prep_.xp2pDeform[i].real());
        deformed_(i, 1) = static_cast<float>(prep_.xp2pDeform[i].imag());
    }
    updateScalarField();
}

void CauchyScene::updateScalarField() {
    const int n = static_cast<int>(mesh_.vertices.rows());
    scalars_.assign(static_cast<std::size_t>(n), 0.f);

    switch (mode_) {
        case VizMode::BasisAbs:
            for (int i = 0; i < n; ++i) scalars_[static_cast<std::size_t>(i)] = complexAbs(prep_.C(i, activeCoeff_));
            break;
        case VizMode::BasisReal:
            for (int i = 0; i < n; ++i)
                scalars_[static_cast<std::size_t>(i)] = static_cast<float>(prep_.C(i, activeCoeff_).real());
            break;
        case VizMode::BasisImag:
            for (int i = 0; i < n; ++i)
                scalars_[static_cast<std::size_t>(i)] = static_cast<float>(prep_.C(i, activeCoeff_).imag());
            break;
        case VizMode::PartitionUnity: {
            for (int i = 0; i < n; ++i) {
                p2p_harmonic::Complex sum(0, 0);
                for (int j = 0; j < prep_.C.cols(); ++j) sum += prep_.C(i, j);
                scalars_[static_cast<std::size_t>(i)] = static_cast<float>(sum.real());
            }
            break;
        }
        case VizMode::DeformedMap:
            for (int i = 0; i < n; ++i) {
                const float dx = deformed_(i, 0) - mesh_.vertices(i, 0);
                const float dy = deformed_(i, 1) - mesh_.vertices(i, 1);
                scalars_[static_cast<std::size_t>(i)] = std::sqrt(dx * dx + dy * dy);
            }
            break;
    }

    fieldMin_ = *std::min_element(scalars_.begin(), scalars_.end());
    fieldMax_ = *std::max_element(scalars_.begin(), scalars_.end());
    if (std::abs(fieldMax_ - fieldMin_) < 1e-8f) fieldMax_ = fieldMin_ + 1.f;
}

Eigen::Matrix<float, Eigen::Dynamic, 2, Eigen::RowMajor> CauchyScene::displayPositions() const {
    if (mode_ == VizMode::DeformedMap) return deformed_;
    return mesh_.vertices;
}

std::vector<float> CauchyScene::scalarField() const { return scalars_; }

std::string CauchyScene::modeLabel() const {
    std::ostringstream oss;
    switch (mode_) {
        case VizMode::BasisAbs: oss << "|C[:, " << activeCoeff_ << "]|"; break;
        case VizMode::BasisReal: oss << "Re(C[:, " << activeCoeff_ << "])"; break;
        case VizMode::BasisImag: oss << "Im(C[:, " << activeCoeff_ << "])"; break;
        case VizMode::PartitionUnity: oss << "sum_j Re(C[i,j])"; break;
        case VizMode::DeformedMap: oss << "deformed map"; break;
    }
    return oss.str();
}

void CauchyScene::computeBounds(float& xmin, float& ymin, float& xmax, float& ymax) const {
    const auto pos = displayPositions();
    xmin = ymin = 1e30f;
    xmax = ymax = -1e30f;
    for (Eigen::Index i = 0; i < pos.rows(); ++i) {
        xmin = std::min(xmin, pos(i, 0));
        xmax = std::max(xmax, pos(i, 0));
        ymin = std::min(ymin, pos(i, 1));
        ymax = std::max(ymax, pos(i, 1));
    }
    for (const p2p_harmonic::VecC& loop : prep_.v) {
        for (Eigen::Index i = 0; i < loop.size(); ++i) {
            xmin = std::min(xmin, static_cast<float>(loop[i].real()));
            xmax = std::max(xmax, static_cast<float>(loop[i].real()));
            ymin = std::min(ymin, static_cast<float>(loop[i].imag()));
            ymax = std::max(ymax, static_cast<float>(loop[i].imag()));
        }
    }
    const float pad = 0.05f * std::max(xmax - xmin, ymax - ymin);
    xmin -= pad;
    xmax += pad;
    ymin -= pad;
    ymax += pad;
}
