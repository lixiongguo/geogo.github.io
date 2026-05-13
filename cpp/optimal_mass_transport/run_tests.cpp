////////////////////////////////////////////////////////////////////////////////
// run_tests.cpp – 7 test cases from run_tests.m
//
// Usage: run_tests <test_type 1-7>
//
// Tests:
//   1 – initial mapping u0 (x-axis), test_u0_ax images
//   2 – initial mapping u0 (y-axis), test_u0_bxy images
//   3 – same as 2 but with histogram equalisation
//   4 – flame image deformation series (intensity mixing)
//   5 – cloud image deformation series (intensity mixing)
//   6 – water image deformation series (intensity mixing)
//   7 – cloud deformation without intensity mixing (both equalisation methods)
////////////////////////////////////////////////////////////////////////////////
#include "optimal_mass_transport.h"

#include <cstdio>
#include <cstdlib>
#include <string>
#include <sys/stat.h>

// Base directory for test images
static const std::string kImageDir =
    "../midas-journal-319-master/code_optimal_mass_transport/";
static const std::string kOutputDir = "output/";

// helper: construct full image path
static std::string img(const std::string& name) { return kImageDir + name; }
static std::string out(const std::string& name) { return kOutputDir + name; }

// ─────────────────────────────────────────────────────────────────────────────
void test_1() {
    printf("\n===== Test 1: initial mapping u0 (x-axis) =====\n");
    int square_edge = 12;

    auto image_0 = omt::imread_gray(img("test_u0_ax_1.bmp"));
    auto image_1 = omt::imread_gray(img("test_u0_ax_2.bmp"));

    auto myu_0 = omt::compute_density_map(image_0, square_edge);
    auto myu_1 = omt::compute_density_map(image_1, square_edge);

    auto u0 = omt::compute_initial_mapping(myu_0, myu_1);

    auto deformed = omt::transform(u0, image_1, square_edge);

    omt::imwrite_gray(out("test1_deformed.bmp"), deformed);
    printf("  Output: %s\n", out("test1_deformed.bmp").c_str());
}

void test_2() {
    printf("\n===== Test 2: initial mapping u0 (y-axis) =====\n");
    int square_edge = 16;

    auto image_0 = omt::imread_gray(img("test_u0_bxy_2.bmp"));
    auto image_1 = omt::imread_gray(img("test_u0_bxy_1.bmp"));

    auto myu_0 = omt::compute_density_map(image_0, square_edge);
    auto myu_1 = omt::compute_density_map(image_1, square_edge);

    auto u0 = omt::compute_initial_mapping(myu_0, myu_1);

    auto deformed = omt::transform(u0, image_1, square_edge);

    omt::imwrite_gray(out("test2_deformed.bmp"), deformed);
    printf("  Output: %s\n", out("test2_deformed.bmp").c_str());
}

void test_3() {
    printf("\n===== Test 3: initial mapping u0 (y-axis, histeq) =====\n");
    int square_edge = 16;

    auto image_0 = omt::imread_gray(img("test_u0_bxy_2.bmp"));
    auto image_1 = omt::imread_gray(img("test_u0_bxy_1.bmp"));

    image_0 = omt::histeq(image_0);
    image_1 = omt::histeq(image_1);

    auto myu_0 = omt::compute_density_map(image_0, square_edge);
    auto myu_1 = omt::compute_density_map(image_1, square_edge);

    auto u0 = omt::compute_initial_mapping(myu_0, myu_1);

    // re-read original images for the transform
    image_0 = omt::imread_gray(img("test_u0_bxy_2.bmp"));
    image_1 = omt::imread_gray(img("test_u0_bxy_1.bmp"));

    auto deformed = omt::transform(u0, image_1, square_edge);

    omt::imwrite_gray(out("test3_deformed.bmp"), deformed);
    printf("  Output: %s\n", out("test3_deformed.bmp").c_str());
}

void test_4() {
    printf("\n===== Test 4: flame image deformation series =====\n");
    int square_edge = 2;
    int P_type      = 1;
    int eq_method   = 0;

    auto optimal_u = omt::compute_optimal_mass_transport(
        img("flame_2.bmp"), img("flame_1.bmp"),
        square_edge, P_type, eq_method);

    auto image_0 = omt::imread_gray(img("flame_2.bmp"));
    auto image_1 = omt::imread_gray(img("flame_1.bmp"));

    int num_frames = 6;
    auto series = omt::create_image_series(optimal_u, image_0, image_1,
                                            square_edge, num_frames);

    for (int i = 0; i < static_cast<int>(series.size()); ++i) {
        std::string fname = "test4_frame_" + std::to_string(i + 1) + ".bmp";
        omt::imwrite_gray(out(fname), series[static_cast<size_t>(i)]);
        printf("  Frame %d → %s\n", i + 1, out(fname).c_str());
    }
}

void test_5() {
    printf("\n===== Test 5: cloud image deformation series =====\n");
    int square_edge = 4;
    int P_type      = 1;
    int eq_method   = 0;

    auto optimal_u = omt::compute_optimal_mass_transport(
        img("cloud_2.bmp"), img("cloud_1.bmp"),
        square_edge, P_type, eq_method);

    auto image_0 = omt::imread_gray(img("cloud_2.bmp"));
    auto image_1 = omt::imread_gray(img("cloud_1.bmp"));

    int num_frames = 6;
    auto series = omt::create_image_series(optimal_u, image_0, image_1,
                                            square_edge, num_frames);

    for (int i = 0; i < static_cast<int>(series.size()); ++i) {
        std::string fname = "test5_frame_" + std::to_string(i + 1) + ".bmp";
        omt::imwrite_gray(out(fname), series[static_cast<size_t>(i)]);
        printf("  Frame %d → %s\n", i + 1, out(fname).c_str());
    }
}

void test_6() {
    printf("\n===== Test 6: water image deformation series =====\n");
    int square_edge = 2;
    int P_type      = 1;
    int eq_method   = 0;

    auto optimal_u = omt::compute_optimal_mass_transport(
        img("water_1.jpg"), img("water_2.jpg"),
        square_edge, P_type, eq_method);

    auto image_0 = omt::imread_gray(img("water_1.jpg"));
    auto image_1 = omt::imread_gray(img("water_2.jpg"));

    int num_frames = 6;
    auto series = omt::create_image_series(optimal_u, image_0, image_1,
                                            square_edge, num_frames);

    for (int i = 0; i < static_cast<int>(series.size()); ++i) {
        std::string fname = "test6_frame_" + std::to_string(i + 1) + ".jpg";
        omt::imwrite_gray_jpg(out(fname), series[static_cast<size_t>(i)]);
        printf("  Frame %d → %s\n", i + 1, out(fname).c_str());
    }
}

void test_7() {
    printf("\n===== Test 7: cloud deformation (no intensity mixing) =====\n");
    int square_edge = 4;
    int P_type      = 1;

    // --- method 0: total-mass ratio equalisation ---
    printf("\n  --- equalization_method = 0 (total-mass ratio) ---\n");
    auto optimal_u_0 = omt::compute_optimal_mass_transport(
        img("cloud_1.bmp"), img("cloud_2.bmp"),
        square_edge, P_type, 0);

    auto image_0_0 = omt::imread_gray(img("cloud_1.bmp"));
    auto image_1_0 = omt::imread_gray(img("cloud_2.bmp"));

    auto deformed_0 = omt::transform(optimal_u_0, image_1_0, square_edge);
    omt::imwrite_gray(out("test7_deformed_eq0.bmp"), deformed_0);
    printf("  Output: %s\n", out("test7_deformed_eq0.bmp").c_str());

    // --- method 1: histogram equalisation ---
    printf("\n  --- equalization_method = 1 (histeq) ---\n");
    auto optimal_u_1 = omt::compute_optimal_mass_transport(
        img("cloud_1.bmp"), img("cloud_2.bmp"),
        square_edge, P_type, 1);

    auto image_0_1 = omt::imread_gray(img("cloud_1.bmp"));
    auto image_1_1 = omt::imread_gray(img("cloud_2.bmp"));

    auto deformed_1 = omt::transform(optimal_u_1, image_1_1, square_edge);
    omt::imwrite_gray(out("test7_deformed_eq1.bmp"), deformed_1);
    printf("  Output: %s\n", out("test7_deformed_eq1.bmp").c_str());
}

// ─────────────────────────────────────────────────────────────────────────────
int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: run_tests <test_type 1-7>\n");
        return 1;
    }

    int test_type = std::atoi(argv[1]);

    // ensure output directory exists
    mkdir(kOutputDir.c_str(), 0755);

    try {
        switch (test_type) {
            case 1: test_1(); break;
            case 2: test_2(); break;
            case 3: test_3(); break;
            case 4: test_4(); break;
            case 5: test_5(); break;
            case 6: test_6(); break;
            case 7: test_7(); break;
            default:
                fprintf(stderr, "Invalid test type: %d (must be 1–7)\n", test_type);
                return 1;
        }
    } catch (const std::exception& e) {
        fprintf(stderr, "Error: %s\n", e.what());
        return 1;
    }

    printf("\nDone.\n");
    return 0;
}
