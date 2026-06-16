"""Asset loaders: OBJ triangle meshes and BDHM polygon models."""

import json
import os
import numpy as np

try:
    from PIL import Image
    _HAVE_PIL = True
except Exception:  # pragma: no cover
    _HAVE_PIL = False


def load_obj(path):
    """Load a 2D OBJ (only x,y used). Returns (V (N,2), F (M,3))."""
    verts = []
    faces = []
    with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
        for line in fh:
            if not line:
                continue
            if line[0] == 'v' and line[1:2] in (' ', '\t'):
                parts = line.split()
                verts.append([float(parts[1]), float(parts[2])])
            elif line[0] == 'f' and line[1:2] in (' ', '\t'):
                parts = line.split()[1:]
                idx = []
                for p in parts:
                    tok = p.split('/')[0]
                    if tok == '':
                        continue
                    vi = int(tok)
                    if vi < 0:
                        vi = len(verts) + vi
                    else:
                        vi -= 1
                    idx.append(vi)
                # fan triangulation for polygons with >3 vertices
                for t in range(1, len(idx) - 1):
                    faces.append([idx[0], idx[t], idx[t + 1]])
    if not verts:
        raise ValueError('OBJ has no vertices: %s' % path)
    return (np.array(verts, dtype=np.float64),
            np.array(faces, dtype=np.int32))


def load_polygon(model_dir):
    """
    Load a BDHM polygon model directory containing data.json (+ optional
    image.png). Returns a dict with keys:
        outer       : (no,2) list outer ring
        holes       : list of (nh,2) rings
        src, dst    : control point source / target positions (lists)
        img_w,img_h : texture dimensions
        image       : np.ndarray RGBA (H,W,4) uint8 or None
    """
    with open(os.path.join(model_dir, 'data.json'), 'r', encoding='utf-8') as fh:
        data = json.load(fh)

    cages = data.get('allcages') or data.get('v') or []
    if not cages:
        raise ValueError('model has no boundary data: %s' % model_dir)
    outer = [[float(p[0]), float(p[1])] for p in cages[0]]
    holes_field = data.get('holes') or []
    n_holes = len(holes_field) if holes_field else (len(cages) - 1)
    holes = [[[float(p[0]), float(p[1])] for p in ring]
             for ring in cages[1:1 + n_holes]]

    src = data.get('P2Psrc') or []
    dst = data.get('P2Pdst') or []
    img_w = data.get('img_w', 1024)
    img_h = data.get('img_h', 1024)

    image = None
    img_path = os.path.join(model_dir, 'image.png')
    if _HAVE_PIL and os.path.exists(img_path):
        try:
            im = Image.open(img_path).convert('RGBA')
            # flip vertically so OpenGL texture v-axis matches world up
            im = im.transpose(Image.FLIP_TOP_BOTTOM)
            image = np.asarray(im, dtype=np.uint8)
            img_h, img_w = image.shape[0], image.shape[1]
        except Exception:
            image = None

    return dict(outer=outer, holes=holes, src=src, dst=dst,
                img_w=img_w, img_h=img_h, image=image)
