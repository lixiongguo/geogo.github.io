"""
Geometry processing + deformation algorithms for the Deformation Lab.

This is a faithful NumPy/SciPy port of the JavaScript implementation found in
`deformation-lab.html`:

  * Ruppert Delaunay refinement     (ruppert_refine)
  * Polygon grid meshing            (make_poly_mesh)
  * Moving Least Squares deformation (apply_mls)
  * As-Rigid-As-Possible deformation (ARAP)
  * Bounded-Distortion Harmonic Map  (BDHM)

All meshes use:
    V : float64 ndarray of shape (N, 2)   -- vertex positions
    F : int32   ndarray of shape (M, 3)   -- triangle indices
"""

import math
import numpy as np

try:
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import splu
    _HAVE_SCIPY = True
except Exception:  # pragma: no cover
    _HAVE_SCIPY = False


# ============================================================
#  Small geometric helpers (used by the Ruppert refinement)
# ============================================================
def _bbox(pts):
    pts = np.asarray(pts, dtype=np.float64)
    return [float(pts[:, 0].min()), float(pts[:, 1].min()),
            float(pts[:, 0].max()), float(pts[:, 1].max())]


def point_in_poly(x, y, poly):
    """Even-odd ray casting test. `poly` is an (n,2) list/array."""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i][0], poly[i][1]
        xj, yj = poly[j][0], poly[j][1]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


# ============================================================
#  Polygon grid meshing  (port of makePolyMesh)
# ============================================================
def make_poly_mesh(outer, holes, max_across=38):
    outer = [list(p) for p in outer]
    holes = [[list(p) for p in h] for h in (holes or [])]
    minX, minY, maxX, maxY = _bbox(outer)
    w, h = maxX - minX, maxY - minY
    cell = max(w, h) / max_across
    nx = max(2, round(w / cell) + 1)
    ny = max(2, round(h / cell) + 1)

    def X(i):
        return minX + (i / (nx - 1)) * w

    def Y(j):
        return minY + (j / (ny - 1)) * h

    def ix(i, j):
        return j * nx + i

    def region(x, y):
        if not point_in_poly(x, y, outer):
            return False
        for hl in holes:
            if point_in_poly(x, y, hl):
                return False
        return True

    Vall = [[X(i), Y(j)] for j in range(ny) for i in range(nx)]
    Fall = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            a, b = ix(i, j), ix(i + 1, j)
            c, d = ix(i, j + 1), ix(i + 1, j + 1)
            for tri in ([a, b, d], [a, d, c]):
                cx = (Vall[tri[0]][0] + Vall[tri[1]][0] + Vall[tri[2]][0]) / 3.0
                cy = (Vall[tri[0]][1] + Vall[tri[1]][1] + Vall[tri[2]][1]) / 3.0
                if region(cx, cy):
                    Fall.append(tri)

    used = set()
    for f in Fall:
        used.update(f)
    remap = {}
    V = []
    for v in range(len(Vall)):
        if v in used:
            remap[v] = len(V)
            V.append(Vall[v])
    F = [[remap[v] for v in f] for f in Fall]
    return (np.array(V, dtype=np.float64),
            np.array(F, dtype=np.int32),
            [minX, minY, maxX, maxY])


# ============================================================
#  Ruppert Delaunay refinement  (port of ruppertRefine)
# ============================================================
def _circumcenter(a, b, c):
    ax, ay = a
    bx, by = b
    cx, cy = c
    D = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(D) < 1e-12:
        return None
    a2, b2, c2 = ax * ax + ay * ay, bx * bx + by * by, cx * cx + cy * cy
    ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / D
    uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / D
    return [ux, uy]


def _circumradius(a, b, c):
    ab = math.hypot(b[0] - a[0], b[1] - a[1])
    bc = math.hypot(c[0] - b[0], c[1] - b[1])
    ca = math.hypot(a[0] - c[0], a[1] - c[1])
    s = (ab + bc + ca) / 2
    area = math.sqrt(max(0.0, s * (s - ab) * (s - bc) * (s - ca)))
    if area < 1e-12:
        return math.inf
    return (ab * bc * ca) / (4 * area)


def _shortest_edge(a, b, c):
    return min(math.hypot(b[0] - a[0], b[1] - a[1]),
               math.hypot(c[0] - b[0], c[1] - b[1]),
               math.hypot(a[0] - c[0], a[1] - c[1]))


def _min_angle(a, b, c):
    ab = math.hypot(b[0] - a[0], b[1] - a[1])
    bc = math.hypot(c[0] - b[0], c[1] - b[1])
    ca = math.hypot(a[0] - c[0], a[1] - c[1])

    def clamp(v):
        return max(-1.0, min(1.0, v))

    A = math.acos(clamp((ab * ab + ca * ca - bc * bc) / (2 * ab * ca + 1e-12)))
    B = math.acos(clamp((ab * ab + bc * bc - ca * ca) / (2 * ab * bc + 1e-12)))
    C = math.acos(clamp((bc * bc + ca * ca - ab * ab) / (2 * bc * ca + 1e-12)))
    return min(A, B, C)


def _edge_key(a, b):
    return (a, b) if a < b else (b, a)


def _extract_boundary_edges(faces):
    ec = {}
    for a, b, c in faces:
        for u, v in ((a, b), (b, c), (c, a)):
            k = _edge_key(u, v)
            ec[k] = ec.get(k, 0) + 1
    return set(k for k, cnt in ec.items() if cnt == 1)


def _encroaches(p, u, v, P):
    pu, pv = P[u], P[v]
    mx, my = (pu[0] + pv[0]) / 2, (pu[1] + pv[1]) / 2
    dx, dy = p[0] - mx, p[1] - my
    hl = math.hypot(pv[0] - pu[0], pv[1] - pu[1]) / 2
    return (dx * dx + dy * dy) < hl * hl * 1.001


def _incircle(ax, ay, bx, by, cx, cy, dx, dy):
    adx, ady = ax - dx, ay - dy
    bdx, bdy = bx - dx, by - dy
    cdx, cdy = cx - dx, cy - dy
    al = adx * adx + ady * ady
    bl = bdx * bdx + bdy * bdy
    cl = cdx * cdx + cdy * cdy
    return (al * (bdx * cdy - bdy * cdx) -
            bl * (adx * cdy - ady * cdx) +
            cl * (adx * bdy - ady * bdx))


def _orient(ax, ay, bx, by, cx, cy):
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def _build_edge_face_map(tris):
    m = {}
    for fi, (a, b, c) in enumerate(tris):
        for u, v in ((a, b), (b, c), (c, a)):
            m.setdefault(_edge_key(u, v), []).append(fi)
    return m


def _find_face_with_edge(tris, u, v):
    for fi, (a, b, c) in enumerate(tris):
        if (a == u or b == u or c == u) and (a == v or b == v or c == v):
            return fi
    return -1


def ruppert_refine(positions, faces, min_angle_deg, max_iter=200):
    """Port of the JS ruppertRefine. positions:(N,2), faces:(M,3)."""
    target = min_angle_deg * math.pi / 180.0
    B = 1.0 / math.sin(target * 0.5)
    pos = [[float(p[0]), float(p[1])] for p in positions]
    tri = [[int(f[0]), int(f[1]), int(f[2])] for f in faces]
    boundary = _extract_boundary_edges(tri)

    for fi in range(len(tri)):
        a, b, c = tri[fi]
        if _orient(pos[a][0], pos[a][1], pos[b][0], pos[b][1],
                   pos[c][0], pos[c][1]) < 0:
            tri[fi] = [a, c, b]

    for _ in range(max_iter):
        worst, worst_ang = -1, math.inf
        for fi in range(len(tri)):
            a, b, c = tri[fi]
            ang = _min_angle(pos[a], pos[b], pos[c])
            if ang < worst_ang:
                worst_ang, worst = ang, fi
        if worst < 0 or worst_ang >= target:
            break
        a, b, c = tri[worst]
        R = _circumradius(pos[a], pos[b], pos[c])
        l = _shortest_edge(pos[a], pos[b], pos[c])
        if R / l < B and worst_ang >= target * 0.6:
            break
        cc = _circumcenter(pos[a], pos[b], pos[c])
        if cc is None:
            continue

        encroached = False
        for ek in list(boundary):
            u, v = ek
            if _encroaches(cc, u, v, pos):
                encroached = True
                pu, pv = pos[u], pos[v]
                mid = [(pu[0] + pv[0]) / 2, (pu[1] + pv[1]) / 2]
                new_idx = len(pos)
                pos.append(mid)
                boundary.discard(ek)
                boundary.add(_edge_key(u, new_idx))
                boundary.add(_edge_key(v, new_idx))
                f_idx = _find_face_with_edge(tri, u, v)
                if f_idx >= 0:
                    v0, v1, v2 = tri[f_idx]
                    other = next(x for x in (v0, v1, v2) if x != u and x != v)
                    tri[f_idx] = [u, other, new_idx]
                    tri.append([v, new_idx, other])
                break
        if encroached:
            continue

        new_idx = len(pos)
        pos.append(cc)
        tri[worst] = [a, b, new_idx]
        tri.append([b, c, new_idx])
        tri.append([c, a, new_idx])

        flipped = True
        while flipped:
            flipped = False
            efm = _build_edge_face_map(tri)
            for k, arr in efm.items():
                if len(arr) != 2:
                    continue
                u, v = k
                f0, f1 = tri[arr[0]], tri[arr[1]]
                others = [x for x in f0 if x != u and x != v]
                others += [x for x in f1 if x != u and x != v]
                if len(others) != 2:
                    continue
                p, q = others
                ic = _incircle(pos[u][0], pos[u][1], pos[v][0], pos[v][1],
                               pos[p][0], pos[p][1], pos[q][0], pos[q][1])
                if ic > 1e-10:
                    tri[arr[0]] = [u, p, q]
                    tri[arr[1]] = [v, q, p]
                    flipped = True

    return (np.array(pos, dtype=np.float64),
            np.array(tri, dtype=np.int32))


# ============================================================
#  Moving Least Squares deformation (vectorised port of applyMLS)
# ============================================================
def apply_mls(original, control_indices, control_current, alpha, mode):
    """
    original         : (N,2) rest positions
    control_indices  : iterable of vertex indices that are pinned/handled
    control_current  : dict idx -> (x, y) target position
    alpha            : weight exponent (1.0 in the UI)
    mode             : 'similarity' | 'affine' | 'rigid'
    """
    V = np.asarray(original, dtype=np.float64)
    n = V.shape[0]
    result = V.copy()
    cp = list(control_indices)
    if not cp:
        return result
    P = V[cp]                                   # (m,2) rest control
    Q = np.array([control_current[i] for i in cp], dtype=np.float64)  # (m,2)

    # weights for every vertex against every control point
    diff = V[:, None, :] - P[None, :, :]        # (n,m,2)
    d2 = np.einsum('nmk,nmk->nm', diff, diff)   # (n,m)
    w = 1.0 / np.power(d2 + 1e-10, alpha)        # (n,m)
    sumW = w.sum(axis=1, keepdims=True)          # (n,1)
    sumW = np.where(sumW < 1e-12, 1.0, sumW)

    pstar = (w @ P) / sumW                        # (n,2)
    qstar = (w @ Q) / sumW                        # (n,2)
    phat = P[None, :, :] - pstar[:, None, :]      # (n,m,2)
    qhat = Q[None, :, :] - qstar[:, None, :]      # (n,m,2)
    vp = V - pstar                                # (n,2)

    if mode == 'affine':
        Phi = np.einsum('nm,nmi,nmj->nij', w, phat, phat)   # (n,2,2)
        W = np.einsum('nm,nmi,nmj->nij', w, qhat, phat)     # (n,2,2)
        det = Phi[:, 0, 0] * Phi[:, 1, 1] - Phi[:, 0, 1] * Phi[:, 1, 0]
        good = np.abs(det) >= 1e-10
        invPhi = np.zeros_like(Phi)
        d = np.where(good, det, 1.0)
        invPhi[:, 0, 0] = Phi[:, 1, 1] / d
        invPhi[:, 0, 1] = -Phi[:, 0, 1] / d
        invPhi[:, 1, 0] = -Phi[:, 1, 0] / d
        invPhi[:, 1, 1] = Phi[:, 0, 0] / d
        M = np.einsum('nij,njk->nik', W, invPhi)            # (n,2,2)
        mapped = np.einsum('nij,nj->ni', M, vp) + qstar
        result = np.where(good[:, None], mapped, result)
    else:
        aNum = np.einsum('nm,nmk,nmk->n', w, phat, qhat)
        bNum = np.einsum('nm,nmk,nmk->n', w, phat,
                         qhat[:, :, ::-1] * np.array([1.0, -1.0]))
        # bNum = sum w (phx*qhy - phy*qhx)
        mu = np.einsum('nm,nmk,nmk->n', w, phat, phat)
        good = mu >= 1e-10
        mu_safe = np.where(good, mu, 1.0)
        if mode == 'rigid':
            scale = np.sqrt(aNum * aNum + bNum * bNum) / mu_safe
            scale_safe = np.where(scale > 1e-10, scale, 1.0)
            a = np.where(scale > 1e-10, aNum / (mu_safe * scale_safe), 1.0)
            b = np.where(scale > 1e-10, bNum / (mu_safe * scale_safe), 0.0)
        else:   # similarity
            a = aNum / mu_safe
            b = bNum / mu_safe
        mx = a * vp[:, 0] - b * vp[:, 1] + qstar[:, 0]
        my = b * vp[:, 0] + a * vp[:, 1] + qstar[:, 1]
        mapped = np.stack([mx, my], axis=1)
        result = np.where(good[:, None], mapped, result)

    # pin the control vertices exactly to their targets
    for i in cp:
        result[i] = control_current[i]
    return result


# ============================================================
#  ARAP deformation (port of buildARAPSystem / arapIterate)
# ============================================================
def _svd_rotation_2x2(a, b, c, d):
    """Vectorised closed-form rotation extraction (port of svdRotation2x2)."""
    E = (a + d) * 0.5
    F = (a - d) * 0.5
    G = (c + b) * 0.5
    H = (c - b) * 0.5
    Q = np.sqrt(E * E + H * H)
    R2 = np.sqrt(F * F + G * G)
    s1 = Q + R2
    big = s1 > 1e-10
    vx = np.where(big, G, 0.0)
    vy = np.where(big, s1 - F, 1.0)
    vn = np.sqrt(vx * vx + vy * vy)
    vn = np.where(vn == 0, 1.0, vn)
    s1_safe = np.where(big, s1, 1.0)
    cos1 = np.where(big, (a * vx / vn + b * vy / vn) / s1_safe, 0.0)
    sin1 = np.where(big, (c * vx / vn + d * vy / vn) / s1_safe, 0.0)
    R = np.empty((a.shape[0], 2, 2), dtype=np.float64)
    R[:, 0, 0] = cos1
    R[:, 0, 1] = -sin1
    R[:, 1, 0] = sin1
    R[:, 1, 1] = cos1
    return R


class ARAP:
    """As-Rigid-As-Possible deformation with a cached cotangent system."""

    def __init__(self, rest, faces):
        self.rest = np.asarray(rest, dtype=np.float64)
        self.faces = np.asarray(faces, dtype=np.int64)
        self.n = self.rest.shape[0]
        self._build()

    def _build(self):
        rest, F, n = self.rest, self.faces, self.n
        i, j, k = F[:, 0], F[:, 1], F[:, 2]
        pi, pj, pk = rest[i], rest[j], rest[k]
        area2 = np.abs((pj[:, 0] - pi[:, 0]) * (pk[:, 1] - pi[:, 1]) -
                       (pk[:, 0] - pi[:, 0]) * (pj[:, 1] - pi[:, 1]))
        area2 = np.maximum(area2, 1e-10)

        # cotangent at the opposite vertex for each of the 3 edges
        def cot(a_idx, b_idx, o_idx):
            pa, pb, po = rest[a_idx], rest[b_idx], rest[o_idx]
            d1 = pa - po
            d2 = pb - po
            return (d1[:, 0] * d2[:, 0] + d1[:, 1] * d2[:, 1]) / area2

        w0 = cot(i, j, k)   # edge (i,j) opposite k
        w1 = cot(j, k, i)   # edge (j,k) opposite i
        w2 = cot(k, i, j)   # edge (k,i) opposite j
        self.face_w = np.stack([w0, w1, w2], axis=1)   # (M,3)

        # accumulate symmetric edge weights
        ea = np.concatenate([i, j, k])
        eb = np.concatenate([j, k, i])
        ew = np.concatenate([w0, w1, w2])
        lo = np.minimum(ea, eb)
        hi = np.maximum(ea, eb)
        key = lo.astype(np.int64) * n + hi.astype(np.int64)
        uk, inv = np.unique(key, return_inverse=True)
        wsum = np.zeros(uk.shape[0])
        np.add.at(wsum, inv, ew)
        ui = (uk // n).astype(np.int64)
        uj = (uk % n).astype(np.int64)

        # Build Laplacian L (symmetric) with +1e-6 diagonal regularisation
        rows = np.concatenate([ui, uj])
        cols = np.concatenate([uj, ui])
        vals = np.concatenate([-wsum, -wsum])
        diag = np.zeros(n)
        np.add.at(diag, ui, wsum)
        np.add.at(diag, uj, wsum)
        diag += 1e-6
        rows = np.concatenate([rows, np.arange(n)])
        cols = np.concatenate([cols, np.arange(n)])
        vals = np.concatenate([vals, diag])

        if not _HAVE_SCIPY:
            raise RuntimeError('SciPy is required for ARAP')
        L = coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsc()
        self.solve = splu(L).solve

    def iterate(self, control_indices, control_current, guess):
        rest, F = self.rest, self.faces
        n = self.n
        cur = np.asarray(guess, dtype=np.float64).copy()
        ci = list(control_indices)
        for c in ci:
            cur[c] = control_current[c]

        i, j, k = F[:, 0], F[:, 1], F[:, 2]
        ccur = (cur[i] + cur[j] + cur[k]) / 3.0
        crest = (rest[i] + rest[j] + rest[k]) / 3.0
        s = np.stack([cur[i] - ccur, cur[j] - ccur, cur[k] - ccur], axis=1)  # (M,3,2)
        r = np.stack([rest[i] - crest, rest[j] - crest, rest[k] - crest], axis=1)
        Cov = np.einsum('mvi,mvj->mij', s, r)   # (M,2,2)
        a = Cov[:, 0, 0]
        b = Cov[:, 0, 1]
        c = Cov[:, 1, 0]
        d = Cov[:, 1, 1]
        R = _svd_rotation_2x2(a, b, c, d)        # (M,2,2)

        bx = np.zeros(n)
        by = np.zeros(n)
        edges = [(i, j, rest[i], rest[j], self.face_w[:, 0]),
                 (j, k, rest[j], rest[k], self.face_w[:, 1]),
                 (k, i, rest[k], rest[i], self.face_w[:, 2])]
        for va, vb, pa, pb, cot_w in edges:
            v = pa - pb                          # (M,2) rest edge
            rv = np.einsum('mij,mj->mi', R, v)   # (M,2)
            cx = cot_w * rv[:, 0]
            cy = cot_w * rv[:, 1]
            np.add.at(bx, va, cx)
            np.add.at(bx, vb, -cx)
            np.add.at(by, va, cy)
            np.add.at(by, vb, -cy)

        nx = self.solve(bx)
        ny = self.solve(by)
        cur[:, 0] = nx
        cur[:, 1] = ny
        for c in ci:
            cur[c] = control_current[c]
        return cur


# ============================================================
#  BDHM -- Bounded Distortion Harmonic Map
#  (vectorised port of the bdhm* routines)
# ============================================================
DEFAULT_BDHM_OPT = dict(
    distortion_bound=2.0,
    min_alpha_real=1e-4,
    lscm_weight=0.0,
    distortion_penalty=1.5e3,
    positivity_penalty=1.5e3,
    reference_weight=2e-4,
    smoothness_weight=0.35,
    initial_step=6e-2,
    bound_on=True,
)


class BDHM:
    def __init__(self, meshV, meshF, opt):
        self.opt = opt
        self.rest = np.asarray(meshV, dtype=np.float64).copy()   # (N,2)
        self.F = np.asarray(meshF, dtype=np.int64)               # (M,3)
        self.nV = self.rest.shape[0]
        self.nF = self.F.shape[0]
        self._build_static()
        self.U = self.rest.copy()

    # ---- static precomputation ----
    def _build_static(self):
        rest, F = self.rest, self.F
        a, b, c = F[:, 0], F[:, 1], F[:, 2]
        p0 = rest[a]
        z = np.zeros((self.nF, 3), dtype=np.complex128)
        z[:, 0] = 0
        z[:, 1] = (rest[b, 0] - p0[:, 0]) + 1j * (rest[b, 1] - p0[:, 1])
        z[:, 2] = (rest[c, 0] - p0[:, 0]) + 1j * (rest[c, 1] - p0[:, 1])
        self.baseZ = z
        self.faceArea = 0.5 * np.abs(z[:, 1].real * z[:, 2].imag -
                                     z[:, 1].imag * z[:, 2].real)
        self.idMaps = self._face_linear_maps(np.zeros(self.nF))
        self.maps = self.idMaps.copy()

        # unique undirected edges
        ea = np.concatenate([a, b, c])
        eb = np.concatenate([b, c, a])
        lo = np.minimum(ea, eb)
        hi = np.maximum(ea, eb)
        key = lo * self.nV + hi
        uk = np.unique(key)
        self.edges = np.stack([uk // self.nV, uk % self.nV], axis=1).astype(np.int64)

    def _face_linear_maps(self, theta):
        """theta:(F,) -> maps:(F,4,6)."""
        rot = np.cos(theta) + 1j * np.sin(theta)        # (F,)
        zz = rot[:, None] * self.baseZ                  # (F,3)
        M = np.empty((self.nF, 3, 3), dtype=np.complex128)
        M[:, :, 0] = zz
        M[:, :, 1] = np.conj(zz)
        M[:, :, 2] = 1.0
        inv = np.linalg.inv(M)                          # (F,3,3)
        maps = np.zeros((self.nF, 4, 6), dtype=np.float64)
        for l in range(3):
            ca = inv[:, 0, l]
            cb = inv[:, 1, l]
            xc, yc = 2 * l, 2 * l + 1
            maps[:, 0, xc] = ca.real
            maps[:, 0, yc] = -ca.imag
            maps[:, 1, xc] = ca.imag
            maps[:, 1, yc] = ca.real
            maps[:, 2, xc] = cb.real
            maps[:, 2, yc] = -cb.imag
            maps[:, 3, xc] = cb.imag
            maps[:, 3, yc] = cb.real
        return np.nan_to_num(maps, nan=0.0, posinf=0.0, neginf=0.0)

    def _local_uv(self, U):
        """U:(N,2) -> lu:(F,6)."""
        lu = np.empty((self.nF, 6), dtype=np.float64)
        for l in range(3):
            lu[:, 2 * l] = U[self.F[:, l], 0]
            lu[:, 2 * l + 1] = U[self.F[:, l], 1]
        return lu

    def kappa(self):
        b = self.opt['distortion_bound']
        return (b - 1) / (b + 1)

    def sync_uv(self, src):
        self.U = np.asarray(src, dtype=np.float64).copy()

    def align_frames(self):
        lu = self._local_uv(self.U)
        y = np.einsum('frk,fk->fr', self.idMaps, lu)    # (F,4)
        ang = np.arctan2(y[:, 1], y[:, 0])
        self.maps = self._face_linear_maps(ang)

    # ---- energy + gradient ----
    def energy_grad(self, U, want_grad):
        opt = self.opt
        k = self.kappa()
        eps = 1e-12
        E = 0.0
        grad = np.zeros((self.nV, 2)) if want_grad else None
        dp = opt['distortion_penalty'] if opt['bound_on'] else 0.0
        pp = opt['positivity_penalty'] if opt['bound_on'] else 0.0

        lu = self._local_uv(U)
        y = np.einsum('frk,fk->fr', self.maps, lu)       # (F,4)
        aRe = y[:, 0]
        bRe = y[:, 2]
        bIm = y[:, 3]
        bN = np.hypot(bRe, bIm)
        dy = np.zeros((self.nF, 4))

        if opt['lscm_weight'] > 0:
            w = opt['lscm_weight'] * self.faceArea
            E += np.sum(w * (bRe * bRe + bIm * bIm))
            dy[:, 2] += 2 * w * bRe
            dy[:, 3] += 2 * w * bIm

        cone = bN - k * aRe
        m = (dp > 0) & (cone > 0)
        if np.any(m):
            E += dp * np.sum((cone[m]) ** 2)
            dy[m, 0] += dp * (-2 * k * cone[m])
            bn_ok = m & (bN > eps)
            dy[bn_ok, 2] += dp * (2 * cone[bn_ok] * bRe[bn_ok] / bN[bn_ok])
            dy[bn_ok, 3] += dp * (2 * cone[bn_ok] * bIm[bn_ok] / bN[bn_ok])

        posv = opt['min_alpha_real'] - aRe
        mp = (pp > 0) & (posv > 0)
        if np.any(mp):
            E += pp * np.sum(posv[mp] ** 2)
            dy[mp, 0] += pp * (-2 * posv[mp])

        if want_grad:
            contrib = np.einsum('fr,frk->fk', dy, self.maps)   # (F,6)
            for l in range(3):
                np.add.at(grad, (self.F[:, l], 0), contrib[:, 2 * l])
                np.add.at(grad, (self.F[:, l], 1), contrib[:, 2 * l + 1])

        if opt['reference_weight'] > 0:
            w = opt['reference_weight']
            d = U - self.rest
            E += w * np.sum(d * d)
            if want_grad:
                grad += 2 * w * d

        if opt['smoothness_weight'] > 0:
            w = opt['smoothness_weight']
            a = self.edges[:, 0]
            b = self.edges[:, 1]
            dx = (U[a, 0] - U[b, 0]) - (self.rest[a, 0] - self.rest[b, 0])
            dyv = (U[a, 1] - U[b, 1]) - (self.rest[a, 1] - self.rest[b, 1])
            E += w * np.sum(dx * dx + dyv * dyv)
            if want_grad:
                np.add.at(grad, (a, 0), 2 * w * dx)
                np.add.at(grad, (b, 0), -2 * w * dx)
                np.add.at(grad, (a, 1), 2 * w * dyv)
                np.add.at(grad, (b, 1), -2 * w * dyv)

        return (E, grad) if want_grad else E

    def _apply_anchors(self, U, controls):
        for idx, t in controls.items():
            U[idx, 0] = t[0]
            U[idx, 1] = t[1]

    def optimize_step(self, controls, max_steps):
        """controls: dict idx -> (x,y). Returns number of GD steps taken."""
        self._apply_anchors(self.U, controls)
        self.align_frames()
        cidx = np.array(list(controls.keys()), dtype=np.int64) if controls else None
        steps = 0
        for _ in range(max_steps):
            E, grad = self.energy_grad(self.U, True)
            if cidx is not None and cidx.size:
                grad[cidx] = 0.0
            gn = float(np.sum(grad * grad))
            if gn < 1e-16:
                break
            step = self.opt['initial_step']
            ok = False
            for t in range(24):
                cand = self.U - step * grad
                self._apply_anchors(cand, controls)
                if self.energy_grad(cand, False) <= E or t == 23:
                    self.U = cand
                    ok = True
                    break
                step *= 0.5
            steps += 1
            if not ok:
                break
        return steps

    def compute_stats(self):
        lu = self._local_uv(self.U)
        y = np.einsum('frk,fk->fr', self.idMaps, lu)
        aA = np.hypot(y[:, 0], y[:, 1])
        bA = np.hypot(y[:, 2], y[:, 3])
        smax = aA + bA
        smin = aA - bA
        J = aA * aA - bA * bA
        with np.errstate(divide='ignore', invalid='ignore'):
            K = np.where(smin > 1e-9, smax / smin, np.inf)
        Kf = K[np.isfinite(K)]
        kmax = float(Kf.max()) if Kf.size else math.inf
        if not np.all(np.isfinite(K)):
            kmax = math.inf
        return dict(kmax=max(1.0, kmax),
                    jmin=float(J.min()),
                    flip=int(np.sum(J <= 0)))


# ============================================================
#  Per-triangle conformal distortion vertex colours
#  (port of distortionColors)
# ============================================================
def distortion_colors(pos, faces, rest):
    pos = np.asarray(pos, dtype=np.float64)
    rest = np.asarray(rest, dtype=np.float64)
    F = np.asarray(faces, dtype=np.int64)
    i, j, k = F[:, 0], F[:, 1], F[:, 2]
    pi, pj, pk = rest[i], rest[j], rest[k]
    qi, qj, qk = pos[i], pos[j], pos[k]
    e1 = pj - pi
    e2 = pk - pi
    f1 = qj - qi
    f2 = qk - qi
    detE = e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]
    good = np.abs(detE) >= 1e-12
    invDet = np.where(good, 1.0 / np.where(good, detE, 1.0), 0.0)
    a = (f1[:, 0] * e2[:, 1] - f2[:, 0] * e1[:, 1]) * invDet
    b = (f2[:, 0] * e1[:, 0] - f1[:, 0] * e2[:, 0]) * invDet
    c = (f1[:, 1] * e2[:, 1] - f2[:, 1] * e1[:, 1]) * invDet
    d = (f2[:, 1] * e1[:, 0] - f1[:, 1] * e2[:, 0]) * invDet
    tr = a * a + b * b + c * c + d * d
    det = a * d - b * c
    disc = np.sqrt(np.maximum(tr * tr - 4 * det * det, 0.0))
    s1 = np.sqrt((tr + disc) / 2.0)
    s2 = np.sqrt(np.maximum((tr - disc) / 2.0, 1e-10))
    ratio = np.maximum(s1 / s2, s2 / s1)
    ratio = np.where(det <= 0, 12.0, ratio)
    t = np.clip((ratio - 1.0) / 9.0, 0.0, 1.0)
    r = np.minimum(t * 2.0, 1.0)
    g = 1.0 - np.abs(t - 0.5) * 2.0
    bcol = 1.0 - t
    tri_col = np.stack([r, g, bcol], axis=1)   # (M,3)

    N = pos.shape[0]
    colors = np.zeros((N, 3))
    counts = np.zeros(N)
    for l in range(3):
        np.add.at(colors, F[:, l], tri_col)
        np.add.at(counts, F[:, l], 1.0)
    counts = np.where(counts == 0, 1.0, counts)
    colors /= counts[:, None]
    return colors.astype(np.float32)
