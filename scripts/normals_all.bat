@echo off
REM 调用本地 MeshLab 为所有模型计算法线并导出 OBJ
cd /d "%~dp0.."
python scripts/normals_meshlab.py assets\Models assets\Models2 assets\Models3
echo.
echo 完成！按任意键退出...
pause >nul
