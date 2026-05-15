#!/usr/bin/env bash
# Build PyMongeAmpere under WSL (Ubuntu). Run from WSL:
#   cd /mnt/c/.../cpp/ma_ot && bash build_wsl.sh
#
# One-time deps (needs sudo). libx11-dev is optional — PyMongeAmpere is patched here
# so CMake does not require X11; add libx11-dev only if the linker complains about X*.
#   sudo apt-get update
#   sudo apt-get install -y build-essential cmake python3-dev python3-numpy \
#     libeigen3-dev libcgal-dev libgmp-dev libmpfr-dev
#
# Eigen must be the distro package: bundled cpp/deps/eigen-* is often incomplete
# (missing signature_of_eigen3_matrix_library) and will fail this project's FindEigen3.cmake.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export MA_DIR="${SCRIPT_DIR}/MongeAmpere"
BUILD_DIR="${SCRIPT_DIR}/PyMongeAmpere-build-wsl"

if [[ ! -d "${SCRIPT_DIR}/PyMongeAmpere" ]]; then
  echo "Missing PyMongeAmpere clone. Run: git clone https://github.com/mrgt/PyMongeAmpere.git"
  exit 1
fi
if [[ ! -d "${MA_DIR}/include/MA" ]]; then
  echo "Missing MongeAmpere clone. Run: git clone https://github.com/mrgt/MongeAmpere.git"
  exit 1
fi

preflight_fail() {
  echo ""
  echo "Install dependencies inside this WSL distro, then re-run this script:"
  echo "  sudo apt-get update"
  echo "  sudo apt-get install -y build-essential cmake python3-dev python3-numpy \\"
  echo "    libeigen3-dev libcgal-dev libgmp-dev libmpfr-dev"
  echo "Optional if the linker errors on X11 symbols: libx11-dev"
  exit 1
}

if [[ ! -f /usr/include/eigen3/signature_of_eigen3_matrix_library ]]; then
  echo "Eigen3 dev package missing (expected /usr/include/eigen3/signature_of_eigen3_matrix_library)."
  preflight_fail
fi

if ! find /usr/lib /usr/share -name CGALConfig.cmake -print -quit 2>/dev/null | grep -q .; then
  echo "CGAL dev package missing (CGALConfig.cmake not found under /usr)."
  preflight_fail
fi

EIGEN3_INCLUDE_DIR="/usr/include/eigen3"

cd "${SCRIPT_DIR}/PyMongeAmpere"
git submodule update --init --recursive

rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"
echo "Using Eigen3 from: ${EIGEN3_INCLUDE_DIR}"
cmake ../PyMongeAmpere \
  -DCMAKE_BUILD_TYPE=Release \
  -DPYTHON_EXECUTABLE="$(command -v python3)" \
  -DEIGEN3_INCLUDE_DIR="${EIGEN3_INCLUDE_DIR}"
cmake --build . -j"$(nproc)"

echo
echo "Build finished. Python module should be under:"
echo "  ${BUILD_DIR}"
echo "Run reflector from WSL with the same repo checkout, e.g.:"
echo "  cd ../reflector-master && python3 reflecteur.py --help"
