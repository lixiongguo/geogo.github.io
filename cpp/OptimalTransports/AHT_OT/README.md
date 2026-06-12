# AHT_OT — Optimal Mass Transport (Haker–Angenent–Tannenbaum)

C++17 implementation of the **2D AHT algorithm** (§7.2–7.4 in
[_最优传输的流体力学观点_](../../_posts/1.Parameterization/5.最优传输方法/最优传输的流体力学观点.md)).

## Layout

```
AHT_OT/
├── include/aht_ot/     # C++ library
├── src/stb_impl.cpp    # stb_image implementation unit
└── examples/           # run_aht_ot, transition_demo, run_tests
```

## Build

```bash
cd cpp/AHT_OT
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

## Usage

```bash
./build/Release/run_aht_ot image0.png image1.png 8 result.bmp
./build/Release/transition_demo image0.png image1.png 8 8
./build/Release/run_tests 1 testdata/    # needs Midas journal BMPs
```

## API vs old `omt::` port

| Old (`optimal_mass_transport.h`) | New (`aht_ot::`) |
|:---|:---|
| `compute_optimal_mass_transport(...)` | `solve_files(...).optimal_map` |
| `transform` | `transform` / `warp_image` |
| `create_image_series` | `create_morph_sequence` |
| `create_image_series_rgb` | `create_morph_sequence_rgb` |
| hardcoded `max_iter=8` | `AHTOptions::max_iterations` |
| non-local flow only | `FlowType::NonLocal` / `Local` |

## Also see

- `cpp/MongeAmpere/optimal_mass_transport/` — same algorithm + original MATLAB scripts
