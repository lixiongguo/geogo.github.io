Reflector
====================
This program is designed to compute the shape of a reflector surface which transforms a given beam of light
into a specified output intensity.

Dependencies
============
+ MongeAmpere/PyMongeAmpere
+ numpy 1.9
+ matplotlib 1.4
+ pillow
+ mpi4py (optionnal)

Dependencies installation
-------------------------
numpy, matplotlib, pillow and mpi4py are available via the python package manager pip:
``` sh
sudo pip install numpy matplotlib pillow mpi4py
```
For MongeAmpere et PyMongeAmpere, follow the instructions [here](https://github.com/mrgt/PyMongeAmpere/wiki)

### PyMongeAmpere in this repo (WSL Ubuntu, recommended on Windows)

Upstream expects **mrgt/MongeAmpere** headers (with `cmake/`), not the smaller `cpp/MongeAmpere` tree used elsewhere in this project. Clones live under `cpp/ma_ot/`:

- `cpp/ma_ot/MongeAmpere` — https://github.com/mrgt/MongeAmpere
- `cpp/ma_ot/PyMongeAmpere` — https://github.com/mrgt/PyMongeAmpere

One-time system packages inside WSL (Ubuntu 22.04 example):

```sh
sudo apt-get update
sudo apt-get install -y build-essential cmake python3-dev python3-numpy \
  libeigen3-dev libcgal-dev libgmp-dev libmpfr-dev
```

`libx11-dev` is **optional**: this repo’s copy of PyMongeAmpere does not require X11 at CMake configure time. Install it only if the link step fails with unresolved `X*` symbols (still no X server needed for batch computation).

Build (from WSL; replace the path with your checkout):

```sh
cd /mnt/c/.../lixiongguo.github.io/cpp/ma_ot
bash build_wsl.sh
```

The extension module is installed under `cpp/ma_ot/PyMongeAmpere-build-wsl/`. The reflector scripts load it automatically via `lib/pymongeampere_path.py` (or set `PYMongeAmpere_BUILD` to your build directory). Run the full pipeline with **WSL Python** from `reflector-master`:

```sh
cd /mnt/c/.../lixiongguo.github.io/cpp/reflector-master
python3 reflecteur.py --help
```

Native Windows is still impractical for this stack (CGAL, pybind); use WSL. Headless runs do not need `DISPLAY`; avoid or replace `matplotlib` `plt.show()` if you do not want any GUI.

Run the program
===============
``` sh
python reflecteur.py [-h] [--f f]
```
optional arguments:
``` sh
-h, --help         show this help message and exit
--f f, --file f	   parameter file
```

Default source is a uniform square and
default target is a uniform triangle with 10000 diracs.

Warning
=======
The algorithm used to solve the semi-discrete Monge-Ampere equation only works
for a convex source density.

Parallel version
====================
reflecteurMPI.py is a parallelized version of reflecteur.py. The ray tracing is the only function parallelized, it is useless to run it if you are not concerned by the resimulation of the reflector. The command to run the program is:
``` sh
mpirun -n <nbofprocess> python reflecteurMPI.py [-h] [--f f]
```



