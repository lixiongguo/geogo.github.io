#pragma once

#include <string>
#include <vector>

#include <Eigen/Core>

#include "../p2p_harmonic/P2PHarmonicTypes.hpp"

struct MeshData {
    Eigen::Matrix<float, Eigen::Dynamic, 2, Eigen::RowMajor> vertices;
    Eigen::Matrix<int, Eigen::Dynamic, 3, Eigen::RowMajor> faces;
};

struct BoundaryData {
    p2p_harmonic::VecC cage;
    std::vector<p2p_harmonic::VecC> holes;
    p2p_harmonic::P2PHarmonicPrepParams params;
};

struct DatasetPaths {
    std::string meshPath;
    std::string boundaryPath;
    std::string paramsPath;
};

bool loadMeshText(const std::string& path, MeshData& mesh);
bool loadBoundaryText(const std::string& path, BoundaryData& boundary);
bool loadParamsText(const std::string& path, p2p_harmonic::P2PHarmonicPrepParams& params);

bool loadTestdata(const std::string& prefix, MeshData& mesh, BoundaryData& boundary);
bool loadViewerDataset(const std::string& directory, MeshData& mesh, BoundaryData& boundary);

std::string findRepoRoot(int argc, char** argv);

p2p_harmonic::VecC meshToComplex(const Eigen::Matrix<float, Eigen::Dynamic, 2, Eigen::RowMajor>& xy);
