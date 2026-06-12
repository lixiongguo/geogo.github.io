#include "MA/ma_power_diagram.hpp"

#include <geogram/basic/common.h>
#include <geogram/basic/geometry.h>
#include <geogram/basic/geometry_nd.h>
#include <geogram/basic/numeric.h>
#include <geogram/delaunay/delaunay.h>
#include <geogram/delaunay/delaunay_2d.h>
#include <geogram/numerics/predicates.h>

#include <algorithm>
#include <limits>
#include <sstream>
#include <string>

namespace MA {
namespace {

using namespace GEO;

using Vec2 = vec2;
using Poly = std::vector<Vec2>;

static Sign point_in_half_plane(const Vec2& p, const Vec2& q1, const Vec2& q2)
{
    return PCK::orient_2d(q1, q2, p);
}

static void clip_half_plane(const Poly& in, const Vec2& q1, const Vec2& q2, Poly& out)
{
    out.clear();
    if (in.empty()) return;
    if (in.size() == 1) {
        if (point_in_half_plane(in[0], q1, q2) == GEO::POSITIVE) out = in;
        return;
    }

    Vec2 prev = in.back();
    Sign prev_s = point_in_half_plane(prev, q1, q2);
    for (size_t i = 0; i < in.size(); ++i) {
        const Vec2 cur = in[i];
        const Sign cur_s = point_in_half_plane(cur, q1, q2);

        if (cur_s == GEO::POSITIVE) {
            if (prev_s != GEO::POSITIVE) {
                Vec2 hit;
                const Vec2 vp = prev - q1;
                const Vec2 vq = q2 - q1;
                const double denom = vp.x * vq.y - vp.y * vq.x;
                if (std::fabs(denom) > 1e-30) {
                    const double t = (vq.x * (q1.y - prev.y) - vq.y * (q1.x - prev.x)) / denom;
                    hit = Vec2((1.0 - t) * prev.x + t * cur.x, (1.0 - t) * prev.y + t * cur.y);
                    out.push_back(hit);
                }
            }
            out.push_back(cur);
        } else if (prev_s == GEO::POSITIVE) {
            Vec2 hit;
            const Vec2 vp = prev - q1;
            const Vec2 vq = q2 - q1;
            const double denom = vp.x * vq.y - vp.y * vq.x;
            if (std::fabs(denom) > 1e-30) {
                const double t = (vq.x * (q1.y - prev.y) - vq.y * (q1.x - prev.x)) / denom;
                hit = Vec2((1.0 - t) * prev.x + t * cur.x, (1.0 - t) * prev.y + t * cur.y);
                out.push_back(hit);
            }
        }
        prev = cur;
        prev_s = cur_s;
    }
}

static void clip_convex_polygon(const Poly& P, const Poly& clip, Poly& result)
{
    Poly src = P;
    Poly dst;
    Poly* a = &src;
    Poly* b = &dst;
    for (size_t i = 0; i < clip.size(); ++i) {
        const Vec2& p1 = clip[i];
        const Vec2& p2 = clip[(i + 1) % clip.size()];
        clip_half_plane(*a, p1, p2, *b);
        std::swap(a, b);
    }
    result = *a;
}

static Poly unit_square()
{
    return {
        Vec2(0.0, 0.0), Vec2(1.0, 0.0), Vec2(1.0, 1.0), Vec2(0.0, 1.0)
    };
}

class PowerDiagramBuilder {
public:
    explicit PowerDiagramBuilder(Delaunay& delaunay)
        : delaunay_(delaunay)
    {
    }

    Vec2 dual_vertex(index_t t) const
    {
        const index_t v1 = delaunay_.cell_to_v()[3 * t];
        const index_t v2 = delaunay_.cell_to_v()[3 * t + 1];
        const index_t v3 = delaunay_.cell_to_v()[3 * t + 2];
        const double* p1 = delaunay_.vertex_ptr(v1);
        const double* p2 = delaunay_.vertex_ptr(v2);
        const double* p3 = delaunay_.vertex_ptr(v3);
        const vec3 q1(p1[0], p1[1], p1[2]);
        const vec3 q2(p2[0], p2[1], p2[2]);
        const vec3 q3(p3[0], p3[1], p3[2]);
        const vec3 c = Geom::triangle_circumcenter(q1, q2, q3);
        return Vec2(c.x, c.y);
    }

    Vec2 infinite_vertex(index_t t, index_t e) const
    {
        const index_t lv1 = (e + 1) % 3;
        const index_t lv2 = (e + 2) % 3;
        const index_t v1 = delaunay_.cell_to_v()[3 * t + lv1];
        const index_t v2 = delaunay_.cell_to_v()[3 * t + lv2];
        const double* ptr1 = delaunay_.vertex_ptr(v1);
        const double* ptr2 = delaunay_.vertex_ptr(v2);
        Vec2 p1(ptr1[0], ptr1[1]);
        Vec2 p2(ptr2[0], ptr2[1]);
        Vec2 n = normalize(p2 - p1);
        n = Vec2(n.y, -n.x);
        return 0.5 * (p1 + p2) + 100000.0 * n;
    }

    index_t find_vertex(index_t t, index_t v) const
    {
        for (index_t lv = 0; lv < 3; ++lv) {
            if (delaunay_.cell_to_v()[3 * t + lv] == v) return lv;
        }
        geo_assert_not_reached;
        return 0;
    }

    void get_cell(index_t t0, index_t lv, Poly& cell) const
    {
        cell.clear();
        const index_t v = delaunay_.cell_to_v()[3 * t0 + lv];
        bool on_border = false;
        index_t t = t0;

        do {
            const index_t e = (lv + 1) % 3;
            const index_t neigh_t = delaunay_.cell_to_cell()[3 * t + e];
            if (neigh_t == NO_INDEX) {
                on_border = true;
                break;
            }
            cell.push_back(dual_vertex(t));
            t = neigh_t;
            lv = find_vertex(t, v);
        } while (t != t0);

        if (on_border) {
            cell.clear();
            cell.push_back(infinite_vertex(t, (lv + 1) % 3));
            for (;;) {
                cell.push_back(dual_vertex(t));
                const index_t e = (lv + 2) % 3;
                const index_t neigh_t = delaunay_.cell_to_cell()[3 * t + e];
                if (neigh_t == NO_INDEX) {
                    cell.push_back(infinite_vertex(t, e));
                    break;
                }
                t = neigh_t;
                lv = find_vertex(t, v);
            }
        }
    }

    void build_all(std::vector<Polygon2>& out, bool clip_square) const
    {
        const index_t nV = delaunay_.nb_vertices();
        std::vector<bool> visited(static_cast<size_t>(nV), false);
        out.clear();
        out.reserve(static_cast<size_t>(nV));

        const Poly border = unit_square();

        for (index_t t = 0; t < delaunay_.nb_cells(); ++t) {
            for (index_t lv = 0; lv < 3; ++lv) {
                const index_t v = delaunay_.cell_to_v()[3 * t + lv];
                if (visited[static_cast<size_t>(v)]) continue;
                visited[static_cast<size_t>(v)] = true;

                Poly cell;
                get_cell(t, lv, cell);

                if (clip_square && cell.size() >= 3) {
                    Poly clipped;
                    clip_convex_polygon(cell, border, clipped);
                    cell.swap(clipped);
                }

                if (cell.size() < 3) continue;

                Polygon2 poly;
                poly.xy.reserve(cell.size() * 2);
                for (const Vec2& p : cell) {
                    poly.push(p.x, p.y);
                }
                out.push_back(std::move(poly));
            }
        }
    }

private:
    Delaunay& delaunay_;
};

static void ensure_geogram_initialized()
{
    static bool done = false;
    if (!done) {
        GEO::initialize();
        done = true;
    }
}

} // namespace

std::vector<Polygon2> compute_power_diagram(
    const double* xy,
    const double* weights,
    int n,
    bool clip_unit_square)
{
    std::vector<Polygon2> empty;
    if (!xy || !weights || n < 1) return empty;

    ensure_geogram_initialized();

    double wMax = weights[0];
    for (int i = 1; i < n; ++i) {
        wMax = std::max(wMax, weights[i]);
    }
    if (wMax < 0.0) wMax = 0.0;

    std::vector<double> verts(static_cast<size_t>(n) * 3);
    for (int i = 0; i < n; ++i) {
        const double x = xy[i * 2];
        const double y = xy[i * 2 + 1];
        const double w = weights[i];
        const double lift = wMax - w;
        verts[static_cast<size_t>(i) * 3] = x;
        verts[static_cast<size_t>(i) * 3 + 1] = y;
        verts[static_cast<size_t>(i) * 3 + 2] =
            lift > 0.0 ? std::sqrt(lift) : 0.0;
    }

    Delaunay_var delaunay = Delaunay::create(3, "BPOW2d");
    if (!delaunay) return empty;

    delaunay->set_vertices(static_cast<index_t>(n), verts.data());

    Delaunay2d* del2d = dynamic_cast<Delaunay2d*>(delaunay.get());
    if (!del2d) return empty;

    if (del2d->has_empty_cells()) {
        return empty;
    }

    PowerDiagramBuilder builder(*delaunay);
    std::vector<Polygon2> cells;
    builder.build_all(cells, clip_unit_square);
    return cells;
}

std::string power_diagram_to_json(const std::vector<Polygon2>& cells)
{
    std::ostringstream os;
    os << '[';
    for (size_t ci = 0; ci < cells.size(); ++ci) {
        if (ci) os << ',';
        os << '[';
        const auto& xy = cells[ci].xy;
        for (size_t k = 0; k < xy.size(); ++k) {
            if (k) os << ',';
            os << xy[k];
        }
        os << ']';
    }
    os << ']';
    return os.str();
}

} // namespace MA
