#include "P2PHarmonicPrep.hpp"

#include "CauchyCoordinates.hpp"
#include "GeomUtils.hpp"

#include <numeric>

namespace p2p_harmonic {
namespace {

double polygonPerimeter(const VecC& poly) {
    double sum = 0.0;
    const int n = static_cast<int>(poly.size());
    for (int i = 0; i < n; ++i) {
        const int in = (i + 1) % n;
        sum += std::abs(poly[i] - poly[in]);
    }
    return sum;
}

Eigen::VectorXi buildNextSampleInSameCage(const std::vector<int>& nSamplePerCage) {
    const int total = static_cast<int>(std::accumulate(nSamplePerCage.begin(), nSamplePerCage.end(), 0));
    Eigen::VectorXi next(total);

    for (int i = 0; i < total; ++i) {
        next[i] = (i + 1) % total + 1;  // 1-based, MATLAB style
    }

    int prefix = 0;
    for (std::size_t c = 0; c < nSamplePerCage.size(); ++c) {
        const int endIdx = prefix + nSamplePerCage[c] - 1;  // 0-based index of last sample in cage
        const int wrapTo = prefix + 1;                       // 1-based first sample in this cage
        next[endIdx] = wrapTo;
        prefix += nSamplePerCage[c];
    }

    return next;
}

VecC buildVirtualVertices(const std::vector<VecC>& v) {
    if (v.empty()) {
        throw P2PHarmonicPrepError("buildVirtualVertices: empty boundary list");
    }

    const int outerCount = static_cast<int>(v[0].size());
    int holeZeros = 0;
    for (std::size_t i = 1; i < v.size(); ++i) {
        holeZeros += static_cast<int>(v[i].size()) - 1;
    }

    VecC vv(outerCount + holeZeros);
    vv.head(outerCount) = v[0];
    vv.tail(holeZeros).setZero();
    return vv;
}

}  // namespace

P2PHarmonicPrepResult p2pHarmonicPrep(const P2PHarmonicPrepInput& input) {
    if (input.cage.size() == 0) {
        throw P2PHarmonicPrepError("p2pHarmonicPrep: cage is empty");
    }
    if (input.meshVertices.size() == 0) {
        throw P2PHarmonicPrepError("p2pHarmonicPrep: meshVertices is empty");
    }

    P2PHarmonicPrepResult result;
    result.params = input.params;
    result.numDenseEvaluationSamples = result.params.numEnergySamples;

    const int holeVertexCount = static_cast<int>(
        std::accumulate(input.holes.begin(), input.holes.end(), 0,
                        [](int acc, const VecC& h) { return acc + static_cast<int>(h.size()); }));

    const int outerSubdivCount = result.params.numVirtualVertices - holeVertexCount - 1;

    VecC offsetCage =
        sampleOnPolygon(outerSubdivCount, polygonOffset(input.cage, -result.params.cage_offset, false));

    std::vector<VecC> offsetHoles;
    offsetHoles.reserve(input.holes.size());
    for (const VecC& hole : input.holes) {
        offsetHoles.push_back(polygonOffset(hole, -result.params.cage_offset, false));
    }

    result.holeCenters.resize(input.holes.size());
    for (std::size_t i = 0; i < input.holes.size(); ++i) {
        result.holeCenters[i] = pointInPolygon(input.holes[i]);
    }

    result.v.clear();
    result.v.push_back(offsetCage);
    result.v.insert(result.v.end(), offsetHoles.begin(), offsetHoles.end());

    result.vv = buildVirtualVertices(result.v);
    result.numVirtualVertices = static_cast<int>(result.vv.size());

    std::vector<VecC> boundariesForSampling;
    boundariesForSampling.push_back(input.cage);
    boundariesForSampling.insert(boundariesForSampling.end(), input.holes.begin(), input.holes.end());

    double sumPerimeter = 0.0;
    std::vector<double> perimeters(boundariesForSampling.size());
    for (std::size_t i = 0; i < boundariesForSampling.size(); ++i) {
        perimeters[i] = polygonPerimeter(boundariesForSampling[i]);
        sumPerimeter += perimeters[i];
    }

    result.nSamplePerCage.resize(boundariesForSampling.size());
    std::vector<VecC> sampleCells;
    sampleCells.reserve(boundariesForSampling.size());

    for (std::size_t i = 0; i < boundariesForSampling.size(); ++i) {
        const int nSamples = static_cast<int>(std::ceil(
            perimeters[i] / sumPerimeter * result.params.numEnergySamples));
        sampleCells.push_back(sampleOnPolygon(nSamples, boundariesForSampling[i]));
        result.nSamplePerCage[i] = static_cast<int>(sampleCells.back().size());
    }

    const int totalSamples = static_cast<int>(std::accumulate(
        result.nSamplePerCage.begin(), result.nSamplePerCage.end(), 0));
    result.energySamples.resize(totalSamples);
    int offset = 0;
    for (const VecC& samples : sampleCells) {
        result.energySamples.segment(offset, samples.size()) = samples;
        offset += static_cast<int>(samples.size());
    }

    result.nextSampleInSameCage = buildNextSampleInSameCage(result.nSamplePerCage);

    result.C = cauchyCoordinates(result.v, input.meshVertices, result.holeCenters);
    result.D = derivativesOfCauchyCoord(result.v, input.meshVertices, result.holeCenters);

    if (signedPolyArea(input.cage) <= 0.0) {
        throw P2PHarmonicPrepError(
            "outer boundary vertex should be ordered CCW for proper Cauchy coordinates computation");
    }
    for (const VecC& hole : input.holes) {
        if (signedPolyArea(hole) >= 0.0) {
            throw P2PHarmonicPrepError(
                "inner boundary vertex should be ordered CW for proper Cauchy coordinates computation");
        }
    }

    std::vector<VecC> offsetBoundaries;
    offsetBoundaries.push_back(offsetCage);
    offsetBoundaries.insert(offsetBoundaries.end(), offsetHoles.begin(), offsetHoles.end());
    for (const VecC& boundary : offsetBoundaries) {
        if (polygonSelfIntersects(boundary)) {
            throw P2PHarmonicPrepError("offsetted outer/inner boundary should not self-intersect");
        }
    }

    result.p2pDeformationConverged = false;
    result.nloPreprocessed = false;
    result.needsPreprocessing = true;

    if (input.phi.size() == result.numVirtualVertices) {
        result.phi = input.phi;
        result.psy = input.psy.size() == result.numVirtualVertices ? input.psy : VecC::Zero(result.numVirtualVertices);
    } else {
        result.phi = result.vv;
        result.psy = VecC::Zero(result.numVirtualVertices);
    }

    result.xp2pDeform = result.C * result.phi + (result.C * result.psy).conjugate();
    return result;
}

}  // namespace p2p_harmonic
