"""
normals_meshlab.py — 调用本地 MeshLab 计算法线并导出 OBJ
用法: python scripts/normals_meshlab.py assets/Models assets/Models2 assets/Models3
"""
import sys, os, glob, subprocess

try:
    import pymeshlab
except ImportError:
    print("请先安装: pip install pymeshlab")
    sys.exit(1)


def process_obj(filepath):
    base = os.path.basename(filepath)
    print(f"  {base} ...", end=" ", flush=True)

    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(filepath)

    # 计算每顶点法线
    ms.compute_normal_for_point_clouds()
    ms.compute_normal_per_vertex()

    # 导出 OBJ（含法线 vn）
    ms.save_current_mesh(filepath, save_vertex_normal=True)

    m = ms.current_mesh()
    print(f"OK  v={m.vertex_number()}  f={m.face_number()}")


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/normals_meshlab.py <目录|文件.obj> ...")
        sys.exit(1)

    targets = []
    for arg in sys.argv[1:]:
        if os.path.isdir(arg):
            targets.extend(sorted(glob.glob(os.path.join(arg, "*.obj"))))
        elif arg.endswith(".obj"):
            targets.append(arg)

    print(f"处理 {len(targets)} 个文件...")
    for f in targets:
        try:
            process_obj(f)
        except Exception as e:
            print(f"ERR: {e}")
    print("全部完成!")


if __name__ == "__main__":
    main()
