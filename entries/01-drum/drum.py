# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "scipy", "matplotlib"]
# ///
"""Entry 01: what can you hear from a drum?

Compute the lowest few hundred eigenvalues of the Dirichlet Laplacian (a drum's frequencies, squared) for a few
shapes on a grid. Then "hear" each shape from its spectrum alone, using the heat trace

    Z(t) = sum_k exp(-lam_k t)  ~  A/(4 pi t)  -  P/(8 sqrt(pi t))  +  c        (t -> 0)

A = area, P = perimeter, c = a constant that depends on the corners (1/16 per right-angle corner, 1/6 for a
smooth boundary). Fitting Z(t) at small t recovers all three. The full shape still can't be recovered:
Gordon, Webb and Wolpert (1992) built two different drums with exactly the same spectrum.

    uv run drum.py            # prints a table and saves spectrum.png (about half a minute)
"""
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh

H = 0.0125         # grid spacing (smaller = more accurate, slower)
K = 400            # number of eigenvalues to compute


def laplacian(mask: np.ndarray, h: float) -> sp.csr_matrix:
    """5-point finite-difference -Laplacian on the cells where mask is True (zero outside = clamped drum edge)."""
    idx = -np.ones(mask.shape, dtype=int)
    pts = np.argwhere(mask)
    idx[mask] = np.arange(len(pts))
    rows, cols, vals = [], [], []
    for n, (i, j) in enumerate(pts):
        rows.append(n); cols.append(n); vals.append(4.0)
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = i + di, j + dj
            if 0 <= a < mask.shape[0] and 0 <= b < mask.shape[1] and idx[a, b] >= 0:
                rows.append(n); cols.append(idx[a, b]); vals.append(-1.0)
    return sp.csr_matrix((vals, (rows, cols)), shape=(len(pts), len(pts))) / h**2


def grid(w: float, h: float):
    xs = np.arange(-w, w + h / 2, h)
    return np.meshgrid(xs, xs, indexing="ij")


def shapes(h: float) -> dict:
    """name -> (mask, true area, true perimeter, theoretical corner constant c)."""
    X, Y = grid(1.2, h)
    reflex = (np.pi**2 - (1.5 * np.pi)**2) / (24 * np.pi * 1.5 * np.pi)   # one 270-degree corner
    return {
        "square 2x2": ((np.abs(X) < 1) & (np.abs(Y) < 1), 4.0, 8.0, 4 / 16),
        "disk r=1.1": (X**2 + Y**2 < 1.1**2, np.pi * 1.1**2, 2 * np.pi * 1.1, 1 / 6),
        "L-shape": (((np.abs(X) < 1) & (np.abs(Y) < 1)) & ~((X > 0) & (Y > 0)), 3.0, 8.0, 5 / 16 + reflex),
        "rectangle 2x1": ((np.abs(X) < 1) & (np.abs(Y) < 0.5), 2.0, 6.0, 4 / 16),
    }


def spectrum(mask: np.ndarray, h: float, k: int) -> np.ndarray:
    mu = np.sort(eigsh(laplacian(mask, h), k=k, sigma=0, which="LM", return_eigenvectors=False))
    # The grid makes high frequencies come out a bit low. Undo it with the 1-D dispersion relation
    # mu = (4/h^2) sin^2(k h / 2)  ->  k^2 = (2/h * arcsin(h sqrt(mu) / 2))^2
    return (2 / h * np.arcsin(np.minimum(1, h * np.sqrt(mu) / 2)))**2


def hear(lam: np.ndarray, t0: float = 0.015, t1: float = 0.05) -> tuple[float, float, float]:
    """Fit the heat trace at small t -> (area, perimeter, corner constant)."""
    ts = np.linspace(t0, t1, 40)
    Z = np.array([np.exp(-lam * t).sum() for t in ts])
    M = np.column_stack([1 / (4 * np.pi * ts), -1 / (8 * np.sqrt(np.pi * ts)), np.ones_like(ts)])
    (a, p, c), *_ = np.linalg.lstsq(M, Z, rcond=None)
    return a, p, c


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    print(f"{'shape':15} {'area':>13} {'perimeter':>13} {'corners c':>13}")
    print(f"{'':15} {'true  heard':>13} {'true  heard':>13} {'true  heard':>13}")
    fig, ax = plt.subplots(figsize=(7, 4))
    for name, (mask, area, perim, c_true) in shapes(H).items():
        lam = spectrum(mask, H, K)
        a, p, c = hear(lam)
        print(f"{name:15} {area:5.2f} {a:6.2f}  {perim:5.2f} {p:6.2f}  {c_true:5.3f} {c:6.3f}")
        ax.step(lam, np.arange(1, len(lam) + 1), where="post", label=name)
    ax.set_xlabel("eigenvalue λ (frequency²)")
    ax.set_ylabel("N(λ): how many below λ")
    ax.set_title("Bigger drums fill up faster: the slope is the area")
    ax.legend()
    fig.tight_layout()
    fig.savefig("spectrum.png", dpi=130)
    print("saved spectrum.png")


if __name__ == "__main__":
    main()
