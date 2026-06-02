/**
 * Emscripten wrapper for semi-discrete-ot.html
 * API matches existing assets/wasm/wasm_power_diagram.js
 */

#include <emscripten.h>
#include <cstring>
#include <string>
#include <vector>

#include "MA/ma_power_diagram.hpp"

namespace {

char* duplicate_cstr(const std::string& s)
{
    char* buf = static_cast<char*>(std::malloc(s.size() + 1));
    if (!buf) return nullptr;
    std::memcpy(buf, s.c_str(), s.size() + 1);
    return buf;
}

} // namespace

extern "C" {

EMSCRIPTEN_KEEPALIVE
char* compute_power_diagram_js(double* x, double* y, double* w, int n)
{
    if (!x || !y || !w || n < 1) {
        return duplicate_cstr("[]");
    }

    std::vector<double> xy(static_cast<size_t>(n) * 2);
    for (int i = 0; i < n; ++i) {
        xy[static_cast<size_t>(i) * 2] = x[i];
        xy[static_cast<size_t>(i) * 2 + 1] = y[i];
    }

    const auto cells = MA::compute_power_diagram(xy.data(), w, n, true);
    return duplicate_cstr(MA::power_diagram_to_json(cells));
}

EMSCRIPTEN_KEEPALIVE
void free_buffer(void* p)
{
    std::free(p);
}

EMSCRIPTEN_KEEPALIVE
int wasm_test()
{
    const double xy[] = {0.2, 0.2, 0.8, 0.2, 0.5, 0.8};
    const double w[] = {0.0, 0.0, 0.0};
    const auto cells = MA::compute_power_diagram(xy, w, 3, true);
    return static_cast<int>(cells.size()) >= 1 ? 1 : 0;
}

} // extern "C"
