"""2D Neural Lagrangian OT demo.

Example:
    python python/neural_ot/demo_2d.py --iters 1000 --plot
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

from neural_ot import (
    NeuralLagrangianOT,
    NeuralOTConfig,
    sample_gaussian,
    sample_gaussian_mixture,
    train_neural_ot,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a 2D Neural OT map.")
    parser.add_argument("--iters", type=int, default=1000)
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=32)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument("--layers", type=int, default=3)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--match", choices=["sinkhorn", "mmd"], default="sinkhorn")
    parser.add_argument("--potential", action="store_true")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--out", default="python/neural_ot/demo_2d.png")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    torch.manual_seed(7)

    config = NeuralOTConfig(
        dim=2,
        hidden_dim=args.hidden,
        num_layers=args.layers,
        num_steps=args.steps,
        integrator="rk4",
        match_loss=args.match,
        kinetic_weight=1.0,
        match_weight=10.0,
        sinkhorn_epsilon=0.05,
        sinkhorn_iters=60,
        mmd_sigma=0.25,
        time_smooth_weight=0.0,
        use_potential=args.potential,
    )
    model = NeuralLagrangianOT(config)

    def source_sampler(batch_size: int, device: torch.device) -> torch.Tensor:
        return sample_gaussian(batch_size, device, mean=(-0.65, -0.45), std=0.18)

    def target_sampler(batch_size: int, device: torch.device) -> torch.Tensor:
        return sample_gaussian_mixture(batch_size, device, std=0.12)

    train_neural_ot(
        model,
        source_sampler,
        target_sampler,
        batch_size=args.batch_size,
        num_iters=args.iters,
        lr=args.lr,
        device=args.device,
        log_every=max(1, args.iters // 10),
    )

    model.eval()
    device = torch.device(args.device)
    x0 = source_sampler(2048, device)
    y = target_sampler(2048, device)
    with torch.no_grad():
        x1 = model.map(x0)

    print("source mean:", x0.mean(dim=0).cpu().numpy())
    print("mapped mean:", x1.mean(dim=0).cpu().numpy())
    print("target mean:", y.mean(dim=0).cpu().numpy())

    if args.plot:
        save_plot(x0.cpu(), x1.cpu(), y.cpu(), Path(args.out))


def save_plot(source: torch.Tensor, mapped: torch.Tensor, target: torch.Tensor, out: Path) -> None:
    import matplotlib.pyplot as plt

    out.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharex=True, sharey=True)
    panels = [
        ("source", source),
        ("mapped", mapped),
        ("target", target),
    ]
    for ax, (title, pts) in zip(axes, panels):
        ax.scatter(pts[:, 0], pts[:, 1], s=3, alpha=0.35)
        ax.set_title(title)
        ax.set_aspect("equal")
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.grid(True, linewidth=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    print(f"saved plot to {out}")


if __name__ == "__main__":
    main()
