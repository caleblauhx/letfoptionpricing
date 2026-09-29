"""
Volatility-forecasting models for the LETF research project.

The target is total subsequent realised quadratic variation. The models are
deliberately kept separate from option-strip extraction so the empirical
comparison can be run on the same 48-observation panel.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def constant_qv_forecast(
    volatility: float,
    tau: float,
) -> float:
    """Constant-volatility benchmark: QV = sigma^2 T."""
    if volatility < 0 or tau <= 0:
        raise ValueError("volatility must be non-negative and tau positive.")
    return float(volatility ** 2 * tau)


def garch_qv_forecast(
    returns: pd.Series,
    horizon: int,
) -> float:
    """
    Fit GARCH(1,1) to historical returns and forecast total variance
    over the requested number of trading days.
    """
    from arch import arch_model

    r = pd.Series(returns).dropna().astype(float)
    if len(r) < 252:
        raise ValueError("At least 252 historical returns are required.")

    model = arch_model(
        r,
        mean="Constant",
        vol="GARCH",
        p=1,
        q=1,
        dist="normal",
        rescale=True,
    )
    fit = model.fit(disp="off")
    variance = fit.forecast(horizon=horizon, reindex=False).variance.iloc[-1]

    scale = float(getattr(fit, "scale", 1.0))
    return float(variance.to_numpy().sum() / scale**2)


def heston_qv_paths(
    v0: float,
    kappa: float,
    theta: float,
    xi: float,
    rho: float,
    horizon: int,
    paths: int = 10000,
    seed: int = 2026,
) -> np.ndarray:
    """
    Simulate total QV paths under the Heston variance process.

        dv = kappa(theta-v)dt + xi sqrt(v)dZ.

    The correlated price shock is not needed when the output is only QV.
    rho is retained as a model parameter because the full Heston system
    couples price and variance; the QV marginal is driven by the variance SDE.
    """
    if min(v0, kappa, theta, xi) < 0 or kappa <= 0:
        raise ValueError("Invalid Heston parameters.")
    if horizon <= 0 or paths <= 0:
        raise ValueError("horizon and paths must be positive.")

    rng = np.random.default_rng(seed)
    dt = 1.0 / 252.0
    v = np.full(paths, float(v0))
    qv = np.zeros(paths)

    for _ in range(horizon):
        vp = np.maximum(v, 0.0)
        z = rng.standard_normal(paths)
        v = vp + kappa * (theta - vp) * dt + xi * np.sqrt(vp * dt) * z
        v = np.maximum(v, 0.0)
        qv += vp * dt

    return qv


def heston_qv_moments(
    v0: float,
    kappa: float,
    theta: float,
    xi: float,
    rho: float,
    horizon: int,
    order: int = 4,
    paths: int = 10000,
    seed: int = 2026,
) -> dict:
    """Estimate central QV moments from Heston simulation."""
    qv = heston_qv_paths(
        v0, kappa, theta, xi, rho, horizon, paths, seed
    )
    mean = float(np.mean(qv))
    moments = {
        1: mean,
        2: float(np.mean((qv - mean) ** 2)),
        3: float(np.mean((qv - mean) ** 3)),
        4: float(np.mean((qv - mean) ** 4)),
    }
    return {n: moments[n] for n in range(1, order + 1)}


def evaluate_forecasts(
    actual: pd.Series,
    forecast: pd.Series,
) -> dict:
    """Return bias, MAE and RMSE for matched forecast/realisation pairs."""
    df = pd.concat(
        [pd.Series(actual, name="actual"),
         pd.Series(forecast, name="forecast")],
        axis=1,
    ).dropna()

    if df.empty:
        raise ValueError("No overlapping observations.")

    error = df["forecast"] - df["actual"]
    return {
        "n": int(len(df)),
        "bias": float(error.mean()),
        "mae": float(mean_absolute_error(df["actual"], df["forecast"])),
        "rmse": float(np.sqrt(mean_squared_error(
            df["actual"], df["forecast"]
        ))),
    }


def compare_models(panel: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluate all forecast columns in a 48-observation panel.

    Required columns:
        realised_qv, constant_qv, garch_qv, heston_qv.
    """
    required = {"realised_qv", "constant_qv", "garch_qv", "heston_qv"}
    missing = required.difference(panel.columns)
    if missing:
        raise ValueError(f"Missing panel columns: {sorted(missing)}")

    rows = []
    for name in ("constant_qv", "garch_qv", "heston_qv"):
        metrics = evaluate_forecasts(panel["realised_qv"], panel[name])
        rows.append({"model": name, **metrics})

    return pd.DataFrame(rows)
