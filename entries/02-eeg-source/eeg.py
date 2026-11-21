# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "matplotlib"]
# ///
"""Entry 02: where does EEG come from?

When thousands of pyramidal neurons fire together, their synaptic currents add up to a small "current dipole": a
current p (A·m) flowing in one direction inside the cortex. In a uniform conductor the voltage it makes at a point r is

    V(r) = p · (r - r0) / (4 pi sigma |r - r0|^3)

This script puts one dipole a few centimetres under a spherical "scalp" and maps the voltage on the surface:
  - radial dipole (pointing out of the head, like a neuron on top of a gyrus) vs tangential (lying flat, like one in
    the wall of a sulcus),
  - at 1, 2 and 3 cm depth,
  - for a 10 nA·m dipole (a typical strength for evoked responses).

It ignores the skull, which conducts ~50-80x worse than brain and smears everything. That's entry 03.

    uv run eeg.py            # prints a table and saves topographies.png
"""
import numpy as np

SIGMA = 0.33          # S/m, roughly brain and scalp
R = 0.09              # m, head radius
P = 10e-9             # A·m, 10 nA·m
P_NEURON = 0.5e-12    # A·m per synchronously active pyramidal neuron (Murakami & Okada 2006 estimate ~0.2-0.9 pA·m)


def potential(points: np.ndarray, r0: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Volts at each point (N, 3) from a dipole p (3,) at r0 (3,), infinite homogeneous conductor."""
    d = points - r0
    dist = np.linalg.norm(d, axis=1)
    return (d @ p) / (4 * np.pi * SIGMA * dist**3)


def scalp(n: int = 181):
    """Upper hemisphere of the head, on a grid in the azimuthal-equidistant view (top of the head in the middle)."""
    u = np.linspace(-1, 1, n)
    X, Y = np.meshgrid(u, u)
    rho = np.hypot(X, Y)
    theta = rho * (np.pi / 2)            # 0 at the vertex, 90° at the ear line
    phi = np.arctan2(Y, X)
    pts = R * np.stack([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)], axis=-1)
    return X, Y, rho <= 1, pts.reshape(-1, 3)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    X, Y, inside, pts = scalp()
    depths = (0.01, 0.02, 0.03)
    kinds = {"radial": np.array([0, 0, 1.0]), "tangential": np.array([1.0, 0, 0])}
    fig, axes = plt.subplots(2, 3, figsize=(10, 6.6))
    print(f"{'dipole':11} {'depth':>6} {'peak-to-peak':>13} {'max at':>22}")
    for row, (name, direction) in enumerate(kinds.items()):
        for col, depth in enumerate(depths):
            r0 = np.array([0, 0, R - depth])
            v = potential(pts, r0, P * direction).reshape(X.shape) * 1e6   # µV
            v[~inside] = np.nan
            iy, ix = np.unravel_index(np.nanargmax(v), v.shape)
            away = np.degrees(np.hypot(X[iy, ix], Y[iy, ix]) * np.pi / 2)
            ptp = np.nanmax(v) - np.nanmin(v)
            print(f"{name:11} {depth * 100:4.0f}cm {ptp:10.2f} µV   {away:5.1f}° from the top")
            ax = axes[row, col]
            lim = np.nanmax(np.abs(v))
            ax.contourf(X, Y, v, levels=21, cmap="RdBu_r", vmin=-lim, vmax=lim)
            ax.contour(X, Y, v, levels=[0], colors="k", linewidths=0.6)
            ax.set_title(f"{name}, {depth * 100:.0f} cm deep\npeak-to-peak {ptp:.1f} µV", fontsize=9)
            ax.set_aspect("equal")
            ax.axis("off")
    fig.suptitle(f"One {P * 1e9:.0f} nA·m dipole under the scalp (no skull)", fontsize=11)
    fig.tight_layout()
    fig.savefig("topographies.png", dpi=130)
    print("saved topographies.png")
    print(f"\n{P * 1e9:.0f} nA·m / {P_NEURON * 1e12:.1f} pA·m per neuron ≈ {P / P_NEURON:,.0f} neurons firing together")


if __name__ == "__main__":
    main()
