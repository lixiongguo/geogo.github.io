# Neural Lagrangian OT

PyTorch implementation of a small Neural Lagrangian Optimal Transport solver.

The learned map is a continuous-time particle flow:

```text
dx_t / dt = v_theta(x_t, t),   T(x_0) = x_1
```

The training loss combines:

- path kinetic energy, matching the Benamou-Brenier dynamic OT objective;
- terminal distribution matching with Sinkhorn divergence or MMD;
- optional velocity/time smoothness regularization.

## Files

- `neural_ot.py`: core PyTorch implementation.
- `demo_2d.py`: 2D Gaussian-to-mixture toy example.

## Install

```bash
pip install torch
pip install matplotlib  # optional, only for --plot
```

## Run

From the repository root:

```bash
python python/neural_ot/demo_2d.py --iters 1000 --batch-size 1024 --plot
```

Use potential parameterization, where `v = grad_x Phi`:

```bash
python python/neural_ot/demo_2d.py --potential --iters 1000
```

Use MMD instead of Sinkhorn:

```bash
python python/neural_ot/demo_2d.py --match mmd --iters 1000
```

## Minimal API

```python
import torch
from neural_ot import NeuralLagrangianOT, NeuralOTConfig

cfg = NeuralOTConfig(dim=2, match_loss="sinkhorn", num_steps=32)
model = NeuralLagrangianOT(cfg)

source = torch.randn(1024, 2)
target = torch.randn(1024, 2) + 1.0

loss, metrics = model.loss(source, target)
loss.backward()

mapped = model.map(source)
```

## Notes

This is a research/demo implementation, not a production OT library. For low-dimensional regular grids, the PDE/C++ solvers in `cpp/conformal-parameterization/OptimalTransports` are usually more accurate and deterministic. Neural OT is most useful when the distribution is sample-based or high-dimensional.
