#include "optimal_mass_transport.h"
#include <cstdio>

int main() {
    printf("=== Cameraman → Boat Transition via Optimal Transport ===\n\n");

    int square_edge = 4;     // 256/4 = 64×64 density map
    int P_type      = 1;     // with comparison term
    int eq_method   = 0;     // total-mass ratio
    int num_frames  = 8;

    const char* img0_path = "/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/assets/image/cameraman.png";
    const char* img1_path = "/tmp/boat_256.png";

    // Load original images
    auto image_0 = omt::imread_gray(img0_path);
    auto image_1 = omt::imread_gray(img1_path);
    printf("Image 0 (cameraman): %ld×%ld\n", image_0.rows(), image_0.cols());
    printf("Image 1 (boat):      %ld×%ld\n", image_1.rows(), image_1.cols());

    // Compute optimal transport map
    printf("\nComputing optimal mass transport...\n");
    auto optimal_u = omt::compute_optimal_mass_transport(
        img0_path, img1_path, square_edge, P_type, eq_method);

    // Generate transition series
    printf("\nGenerating %d-frame transition series...\n", num_frames);
    auto series = omt::create_image_series(optimal_u, image_0, image_1,
                                            square_edge, num_frames);

    // Save frames
    for (int i = 0; i < static_cast<int>(series.size()); ++i) {
        char fname[64];
        snprintf(fname, sizeof(fname), "output/cam2boat_%02d.bmp", i + 1);
        omt::imwrite_gray(fname, series[static_cast<size_t>(i)]);
        printf("  Frame %d/%d → %s  [%ld×%ld]\n",
               i + 1, num_frames, fname,
               series[i].rows(), series[i].cols());
    }

    printf("\nDone! Sequence saved to output/cam2boat_01~%02d.bmp\n", num_frames);
    return 0;
}
