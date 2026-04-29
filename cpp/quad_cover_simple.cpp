#include <iostream>
#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <igl/readOBJ.h>
#include <igl/cotmatrix.h>
#include <igl/massmatrix.h>
#include <igl/grad.h>
//#include "divergence.hpp"
#include <igl/boundary_facets.h>
#include <igl/per_face_normals.h>
#include <igl/per_vertex_normals.h>

#include <igl/principal_curvature.h>
#include <igl/slice.h>
#include <igl/min_quad_with_fixed.h>
#include <corecrt_math_defines.h>
#include <igl/read_triangle_mesh.h>

#include <igl/opengl/glfw/Viewer.h>
using namespace std;
using namespace Eigen;

// 简化 QuadCover：无整数校正
int main(int argc, char* argv[]) {
    Eigen::MatrixXd V;
    Eigen::MatrixXi F;
    if (!igl::read_triangle_mesh((argc > 1) ? argv[1] : "D:/MyDocs/Models/input/small_bunny.obj", V, F))
    {
        std::cerr << "Failed to load mesh." << std::endl;
        return -1;
    }

    MatrixXd FN;
    igl::per_face_normals(V, F, FN);
    const double  nScale =  0.1;
    MatrixXd face_centers(F.rows(), 3);
    for (int i = 0; i < F.rows(); ++i) {
        face_centers.row(i) = (V.row(F(i, 0))+(V.row(F(i, 1))) + (V.row(F(i, 2))))/3.0;
    }
    
    



    
    // 3. 初始化 4-RoSy 方向场（使用主曲率方向）
    //    每个面存储一个角度 theta (in radians, modulo pi/2)
    VectorXd theta(F.rows());
    {
        MatrixXd PD1, PD2; // principal directions
        VectorXd PV1, PV2; // principal values
        igl::principal_curvature(V, F, PD1, PD2, PV1, PV2, 5);

        // 投影到切平面，取第一个主方向作为初始方向
        for (int i = 0; i < F.rows(); ++i) {
            // 构建局部坐标系
            Vector3d n = FN.row(i).normalized();
            Vector3d t1 = PD1.row(i).normalized();
            // 去除法向分量
            t1 = (t1 - n * n.dot(t1)).normalized();
            if (t1.norm() < 1e-6) {
                // fallback: use arbitrary tangent
                t1 = Vector3d(1,0,0);
                if (abs(n.dot(t1)) > 0.9) t1 = Vector3d(0,1,0);
                t1 = (t1 - n * n.dot(t1)).normalized();
            }
            // 角度（相对于局部 x 轴）
            double angle = atan2(t1(1), t1(0));
            // 对 4-RoSy，模 pi/2
            theta(i) = fmod(angle, M_PI / 2.0);
            if (theta(i) < 0) theta(i) += M_PI / 2.0;
        }
    }

    //// 4. 平滑方向场（最小二乘，忽略整数环绕）
    ////    构建系统: min sum_{e=(f1,f2)} w_e (theta_f1 - theta_f2)^2
    ////    这是一个 Laplacian 平滑
    //{
    //    // 构建面邻接图（通过边）
    //    vector<vector<int>> face_adj(n_faces);
    //    map<pair<int,int>, pair<int,int>> edge_to_faces;
    //    for (int i = 0; i < n_faces; ++i) {
    //        for (int j = 0; j < 3; ++j) {
    //            int v1 = F(i, j), v2 = F(i, (j+1)%3);
    //            if (v1 > v2) swap(v1, v2);
    //            auto key = make_pair(v1, v2);
    //            if (edge_to_faces.count(key)) {
    //                int f1 = edge_to_faces[key].first;
    //                face_adj[f1].push_back(i);
    //                face_adj[i].push_back(f1);
    //            } else {
    //                edge_to_faces[key] = make_pair(i, -1);
    //            }
    //        }
    //    }

    //    // 构建 Laplacian 矩阵 for faces
    //    vector<Triplet<double>> L_triplets;
    //    VectorXd b = VectorXd::Zero(n_faces);
    //    for (int i = 0; i < n_faces; ++i) {
    //        double degree = face_adj[i].size();
    //        L_triplets.emplace_back(i, i, degree);
    //        for (int j : face_adj[i]) {
    //            L_triplets.emplace_back(i, j, -1.0);
    //        }
    //    }
    //    SparseMatrix<double> L_face(n_faces, n_faces);
    //    L_face.setFromTriplets(L_triplets.begin(), L_triplets.end());

    //    // 固定部分面（防止零解），或直接求解 (L + I) theta = theta0
    //    SparseMatrix<double> A = L_face + SparseMatrix<double>(n_faces, n_faces).setIdentity();
    //    SimplicialLDLT<SparseMatrix<double>> solver(A);
    //    theta = solver.solve(theta);
    //}

    //// 5. 构建两个正交方向场 d1, d2（在每个面上）
    //MatrixXd d1(n_faces, 3), d2(n_faces, 3);
    //for (int i = 0; i < n_faces; ++i) {
    //    Vector3d n = FN.row(i);
    //    // 在切平面构建局部坐标系
    //    Vector3d x_axis(1, 0, 0);
    //    if (abs(n.dot(x_axis)) > 0.9) x_axis = Vector3d(0, 1, 0);
    //    Vector3d t1 = (x_axis - n * n.dot(x_axis)).normalized();
    //    Vector3d t2 = n.cross(t1).normalized();

    //    // 旋转 theta(i) 得到方向
    //    double c = cos(theta(i)), s = sin(theta(i));
    //    Vector3d dir1 = c * t1 + s * t2;
    //    Vector3d dir2 = -s * t1 + c * t2; // 旋转90度

    //    d1.row(i) = dir1;
    //    d2.row(i) = dir2;
    //}

    //// 6. 计算梯度约束：div(d1), div(d2)
    ////    libigl::divergence 需要向量场定义在顶点上，但我们有面场
    ////    简化：将面场插值到顶点（平均）
    //MatrixXd Vd1(n_verts, 3), Vd2(n_verts, 3);
    //Vd1.setZero(); Vd2.setZero();
    //VectorXi count(n_verts);
    //count.setZero();
    //for (int i = 0; i < n_faces; ++i) {
    //    for (int j = 0; j < 3; ++j) {
    //        int v = F(i, j);
    //        Vd1.row(v) += d1.row(i);
    //        Vd2.row(v) += d2.row(i);
    //        count(v)++;
    //    }
    //}
    //for (int i = 0; i < n_verts; ++i) {
    //    if (count(i) > 0) {
    //        Vd1.row(i) /= count(i);
    //        Vd2.row(i) /= count(i);
    //    }
    //}

    //// 7. 构建泊松系统: L u = div(Vd1), L v = div(Vd2)
    //SparseMatrix<double> L;
    //igl::cotmatrix(V, F, L);

    //VectorXd div1, div2;
    //::divergence(V, F, div1);
    //::divergence(V, F, div2);

    //// 8. 求解泊松方程（添加固定点防止零空间）
    //VectorXi bnd;
    //igl::boundary_facets(F, bnd);
    //if (bnd.size() == 0) {
    //    // 封闭网格：固定一个顶点
    //    bnd.resize(1); bnd(0) = 0;
    //}
    //VectorXd bc1 = VectorXd::Zero(bnd.size());
    //VectorXd bc2 = VectorXd::Zero(bnd.size());

    //MatrixXd U, V_param;
    //igl::min_quad_with_fixed(L, div1, bnd, bc1, {}, true, U);
    //igl::min_quad_with_fixed(L, div2, bnd, bc2, {}, true, V_param);

    //// 9. 输出参数坐标
    //MatrixXd UV(n_verts, 2);
    //UV.col(0) = U;
    //UV.col(1) = V_param;

    //// 10. （可选）保存 UV 到文件
    //ofstream uv_file("output_uv.txt");
    //uv_file << UV << endl;
    //uv_file.close();

    //cout << "Simplified QuadCover done. UV saved to output_uv.txt" << endl;

    //// 可视化建议：用 MATLAB / Python 画 scatter(UV(:,1), UV(:,2))
    return 0;
}