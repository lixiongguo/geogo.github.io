"""Neural Lagrangian optimal transport in PyTorch.

This module implements a small, dependency-light Neural OT solver:

    dx_t / dt = v_theta(x_t, t)

The loss combines Benamou-Brenier kinetic energy with a terminal distribution
matching term, usually Sinkhorn divergence or MMD.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Literal, Optional, Tuple

import torch
from torch import Tensor, nn


Integrator = Literal["euler", "rk4"]
MatchLoss = Literal["sinkhorn", "mmd"]


@dataclass
class NeuralOTConfig:
    """Configuration for Neural Lagrangian OT training."""

    dim: int = 2
    hidden_dim: int = 128
    num_layers: int = 3
    num_steps: int = 32
    integrator: Integrator = "rk4"
    match_loss: MatchLoss = "sinkhorn"
    kinetic_weight: float = 1.0
    match_weight: float = 10.0
    time_smooth_weight: float = 0.0
    l2_velocity_weight: float = 0.0
    sinkhorn_epsilon: float = 0.05
    sinkhorn_iters: int = 80
    mmd_sigma: float = 0.2
    use_potential: bool = False


class MLP(nn.Module):
    """Simple MLP used by the velocity and potential models."""

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        hidden_dim: int = 128,
        num_layers: int = 3,
    ) -> None:
        super().__init__()
        if num_layers < 1:
            raise ValueError("num_layers must be at least 1")

        layers: List[nn.Module] = []
        last = in_dim
        for _ in range(num_layers):
            layers.append(nn.Linear(last, hidden_dim))
            layers.append(nn.SiLU())
            last = hidden_dim
        layers.append(nn.Linear(last, out_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x: Tensor) -> Tensor:
        return self.net(x)


class VelocityField(nn.Module):
    """Directly parameterized velocity v_theta(x, t)."""

    def __init__(self, dim: int, hidden_dim: int = 128, num_layers: int = 3) -> None:
        super().__init__()
        self.dim = dim
        self.mlp = MLP(dim + 1, dim, hidden_dim, num_layers)

    def forward(self, x: Tensor, t: Tensor | float) -> Tensor:
        t_col = _as_time_column(t, x)
        return self.mlp(torch.cat([x, t_col], dim=-1))


class PotentialVelocityField(nn.Module):
    """Velocity field represented as v_theta = grad_x Phi_theta(x, t)."""

    def __init__(self, dim: int, hidden_dim: int = 128, num_layers: int = 3) -> None:
        super().__init__()
        self.dim = dim
        self.potential = MLP(dim + 1, 1, hidden_dim, num_layers)

    def forward(self, x: Tensor, t: Tensor | float) -> Tensor:
        # The input coordinates must require gradients to build grad_x Phi.
        if not x.requires_grad:
            x = x.requires_grad_(True)
        t_col = _as_time_column(t, x)
        phi = self.potential(torch.cat([x, t_col], dim=-1)).sum()
        grad = torch.autograd.grad(phi, x, create_graph=True)[0]
        return grad


def _as_time_column(t: Tensor | float, x: Tensor) -> Tensor:
    if isinstance(t, Tensor):
        if t.ndim == 0:
            return torch.full((x.shape[0], 1), float(t.item()), device=x.device, dtype=x.dtype)
        if t.ndim == 1:
            return t[:, None].to(device=x.device, dtype=x.dtype)
        return t.to(device=x.device, dtype=x.dtype)
    return torch.full((x.shape[0], 1), float(t), device=x.device, dtype=x.dtype)


def pairwise_squared_distances(x: Tensor, y: Tensor) -> Tensor:
    """Squared Euclidean pairwise cost matrix."""

    return torch.cdist(x, y, p=2.0).pow(2)


def sinkhorn_cost(
    x: Tensor,
    y: Tensor,
    epsilon: float = 0.05,
    n_iters: int = 80,
) -> Tensor:
    """Entropic OT cost between two equally weighted point clouds.

    The implementation uses log-domain Sinkhorn iterations for stability.
    """

    if x.ndim != 2 or y.ndim != 2:
        raise ValueError("sinkhorn_cost expects 2D tensors")
    if x.shape[1] != y.shape[1]:
        raise ValueError("point clouds must have the same dimension")
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    n = x.shape[0]
    m = y.shape[0]
    cost = pairwise_squared_distances(x, y)
    log_a = torch.full((n,), -torch.log(torch.tensor(float(n), device=x.device, dtype=x.dtype)), device=x.device, dtype=x.dtype)
    log_b = torch.full((m,), -torch.log(torch.tensor(float(m), device=x.device, dtype=x.dtype)), device=x.device, dtype=x.dtype)
    log_k = -cost / epsilon

    u = torch.zeros_like(log_a)
    v = torch.zeros_like(log_b)
    for _ in range(n_iters):
        u = log_a - torch.logsumexp(log_k + v[None, :], dim=1)
        v = log_b - torch.logsumexp(log_k + u[:, None], dim=0)

    log_plan = log_k + u[:, None] + v[None, :]
    plan = torch.exp(log_plan)
    return torch.sum(plan * cost)


def sinkhorn_divergence(
    x: Tensor,
    y: Tensor,
    epsilon: float = 0.05,
    n_iters: int = 80,
) -> Tensor:
    """Debiased Sinkhorn divergence."""

    xy = sinkhorn_cost(x, y, epsilon, n_iters)
    xx = sinkhorn_cost(x, x, epsilon, n_iters)
    yy = sinkhorn_cost(y, y, epsilon, n_iters)
    return xy - 0.5 * xx - 0.5 * yy


def mmd_rbf(x: Tensor, y: Tensor, sigma: float = 0.2) -> Tensor:
    """RBF-kernel maximum mean discrepancy."""

    if sigma <= 0:
        raise ValueError("sigma must be positive")
    gamma = 1.0 / (2.0 * sigma * sigma)
    k_xx = torch.exp(-gamma * pairwise_squared_distances(x, x))
    k_yy = torch.exp(-gamma * pairwise_squared_distances(y, y))
    k_xy = torch.exp(-gamma * pairwise_squared_distances(x, y))
    return k_xx.mean() + k_yy.mean() - 2.0 * k_xy.mean()


class NeuralLagrangianOT(nn.Module):
    """Trainable Neural Lagrangian OT map X_1^theta."""

    def __init__(self, config: NeuralOTConfig) -> None:
        super().__init__()
        self.config = config
        field_cls = PotentialVelocityField if config.use_potential else VelocityField
        self.velocity = field_cls(config.dim, config.hidden_dim, config.num_layers)

    def integrate(self, x0: Tensor) -> Tuple[Tensor, Tensor, List[Tensor]]:
        """Integrate particles from t=0 to t=1.

        Returns:
            x1: final particles.
            kinetic: mean path kinetic energy.
            trajectory: list of states, including x0 and x1.
        """

        cfg = self.config
        dt = 1.0 / float(cfg.num_steps)
        x = x0
        trajectory: List[Tensor] = [x]
        kinetic = torch.zeros((), device=x0.device, dtype=x0.dtype)

        for k in range(cfg.num_steps):
            t = k * dt
            if cfg.integrator == "euler":
                v = self.velocity(x, t)
                kinetic = kinetic + 0.5 * v.pow(2).sum(dim=-1).mean() * dt
                x = x + dt * v
            elif cfg.integrator == "rk4":
                v1 = self.velocity(x, t)
                v2 = self.velocity(x + 0.5 * dt * v1, t + 0.5 * dt)
                v3 = self.velocity(x + 0.5 * dt * v2, t + 0.5 * dt)
                v4 = self.velocity(x + dt * v3, t + dt)
                v_avg = (v1 + 2.0 * v2 + 2.0 * v3 + v4) / 6.0
                kinetic = kinetic + 0.5 * v_avg.pow(2).sum(dim=-1).mean() * dt
                x = x + dt * v_avg
            else:
                raise ValueError(f"unknown integrator: {cfg.integrator}")
            trajectory.append(x)

        return x, kinetic, trajectory

    def terminal_loss(self, x1: Tensor, target: Tensor) -> Tensor:
        cfg = self.config
        if cfg.match_loss == "sinkhorn":
            return sinkhorn_divergence(
                x1,
                target,
                epsilon=cfg.sinkhorn_epsilon,
                n_iters=cfg.sinkhorn_iters,
            )
        if cfg.match_loss == "mmd":
            return mmd_rbf(x1, target, sigma=cfg.mmd_sigma)
        raise ValueError(f"unknown match_loss: {cfg.match_loss}")

    def regularization(self, trajectory: List[Tensor]) -> Tensor:
        cfg = self.config
        reg = torch.zeros((), device=trajectory[0].device, dtype=trajectory[0].dtype)

        if cfg.time_smooth_weight > 0.0 and len(trajectory) > 2:
            dt = 1.0 / float(cfg.num_steps)
            prev_v: Optional[Tensor] = None
            smooth = torch.zeros_like(reg)
            for k, x in enumerate(trajectory[:-1]):
                v = self.velocity(x, k * dt)
                if prev_v is not None:
                    smooth = smooth + (v - prev_v).pow(2).sum(dim=-1).mean()
                prev_v = v
            reg = reg + cfg.time_smooth_weight * smooth / max(1, len(trajectory) - 2)

        if cfg.l2_velocity_weight > 0.0:
            dt = 1.0 / float(cfg.num_steps)
            l2 = torch.zeros_like(reg)
            for k, x in enumerate(trajectory[:-1]):
                v = self.velocity(x, k * dt)
                l2 = l2 + v.pow(2).sum(dim=-1).mean()
            reg = reg + cfg.l2_velocity_weight * l2 / max(1, len(trajectory) - 1)

        return reg

    def loss(self, source: Tensor, target: Tensor) -> Tuple[Tensor, Dict[str, Tensor]]:
        x1, kinetic, trajectory = self.integrate(source)
        match = self.terminal_loss(x1, target)
        reg = self.regularization(trajectory)
        total = (
            self.config.kinetic_weight * kinetic
            + self.config.match_weight * match
            + reg
        )
        metrics = {
            "loss": total.detach(),
            "kinetic": kinetic.detach(),
            "match": match.detach(),
            "regularization": reg.detach(),
        }
        return total, metrics

    def map(self, x: Tensor) -> Tensor:
        """Evaluate the learned map T(x)=X_1^theta(x)."""

        was_training = self.training
        self.eval()
        # Potential parameterization needs autograd even at inference time,
        # because v_theta is defined as grad_x Phi_theta.
        with torch.enable_grad():
            x_eval = x.detach()
            if self.config.use_potential:
                x_eval = x_eval.requires_grad_(True)
            x1, _, _ = self.integrate(x_eval)
        if was_training:
            self.train()
        return x1.detach()


def train_neural_ot(
    model: NeuralLagrangianOT,
    source_sampler: Callable[[int, torch.device], Tensor],
    target_sampler: Callable[[int, torch.device], Tensor],
    *,
    batch_size: int = 1024,
    num_iters: int = 1000,
    lr: float = 1e-3,
    device: str | torch.device = "cpu",
    log_every: int = 100,
) -> List[Dict[str, float]]:
    """Train a NeuralLagrangianOT model from source/target samplers."""

    dev = torch.device(device)
    model.to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    history: List[Dict[str, float]] = []

    for it in range(1, num_iters + 1):
        source = source_sampler(batch_size, dev)
        target = target_sampler(batch_size, dev)

        opt.zero_grad(set_to_none=True)
        loss, metrics = model.loss(source, target)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=10.0)
        opt.step()

        if it == 1 or it % log_every == 0 or it == num_iters:
            row = {name: float(value.cpu()) for name, value in metrics.items()}
            row["iter"] = float(it)
            history.append(row)
            print(
                f"[{it:05d}] loss={row['loss']:.6f} "
                f"kinetic={row['kinetic']:.6f} match={row['match']:.6f} "
                f"reg={row['regularization']:.6f}"
            )

    return history


def sample_gaussian(
    batch_size: int,
    device: torch.device,
    *,
    mean: Tuple[float, float] = (0.0, 0.0),
    std: float = 0.2,
) -> Tensor:
    mean_t = torch.tensor(mean, device=device, dtype=torch.float32)
    return mean_t + std * torch.randn(batch_size, 2, device=device)


def sample_gaussian_mixture(
    batch_size: int,
    device: torch.device,
    *,
    means: Tuple[Tuple[float, float], ...] = ((-0.6, 0.5), (0.6, 0.5), (0.0, -0.5)),
    std: float = 0.12,
) -> Tensor:
    means_t = torch.tensor(means, device=device, dtype=torch.float32)
    ids = torch.randint(0, means_t.shape[0], (batch_size,), device=device)
    return means_t[ids] + std * torch.randn(batch_size, 2, device=device)

