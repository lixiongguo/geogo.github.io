#pragma once

#include "DataLoader.hpp"

#include "../p2p_harmonic/P2PHarmonicPrep.hpp"

#include <complex>
#include <string>
#include <vector>

enum class VizMode {
    BasisAbs,
    BasisReal,
    BasisImag,
    PartitionUnity,
    DeformedMap
};

class CauchyScene {
public:
    bool loadFromTestdata(const std::string& repoRoot, const std::string& name = "annulus");
    bool loadFromViewerDataset(const std::string& repoRoot, const std::string& dataset = "annulus");

    void recomputePrep();

    void setMode(VizMode mode);
    VizMode mode() const { return mode_; }

    void nextCoefficient(int delta);
    int activeCoefficient() const { return activeCoeff_; }
    int numCoefficients() const;

    void resetPhi();
    int pickVirtualVertex(float wx, float wy, float radius) const;
    void moveVirtualVertex(int index, float wx, float wy);
    void recomputeDeformation();

    const MeshData& mesh() const { return mesh_; }
    const p2p_harmonic::P2PHarmonicPrepResult& prep() const { return prep_; }

    Eigen::Matrix<float, Eigen::Dynamic, 2, Eigen::RowMajor> displayPositions() const;
    std::vector<float> scalarField() const;
    std::string modeLabel() const;

    float dataMin() const { return fieldMin_; }
    float dataMax() const { return fieldMax_; }

    void computeBounds(float& xmin, float& ymin, float& xmax, float& ymax) const;

private:
    void updateScalarField();

    MeshData mesh_;
    BoundaryData boundary_;
    p2p_harmonic::P2PHarmonicPrepResult prep_;

    VizMode mode_ = VizMode::BasisAbs;
    int activeCoeff_ = 0;
    float fieldMin_ = 0.f;
    float fieldMax_ = 1.f;

    std::vector<float> scalars_;
    Eigen::Matrix<float, Eigen::Dynamic, 2, Eigen::RowMajor> deformed_;
};
