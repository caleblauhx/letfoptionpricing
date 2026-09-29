"""
LETF option-pricing and realised-QV evaluation.

This module implements the mathematical hierarchy developed in derivation.md:

1. model-free risk-neutral QV from the QQQ option strip;
2. constant-QV / BSM LETF benchmark;
3. first-order pricing around mean QV;
4. second-order correction using Var_Q(QV);
5. finite higher-moment expansion;
6. realised-QV measurement and HAC forecast evaluation.
"""

from __future__ import annotations

import math
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.integrate import trapezoid
from scipy.special import ndtr


def bsm_forward_call(
    forward: float,
    strike: float,
    total_variance: float,
    rate: float,
    maturity: float,
) -> float:
    """
    Black-Scholes call written in forward/total-variance form.

    total_variance is w = sigma^2 T.
    """
    if forward <= 0 or strike <= 0 or total_variance < 0 or maturity <= 0:
        raise ValueError("Invalid BSM inputs.")

    discount = np.exp(-rate * maturity)

    if total_variance == 0:
        return float(discount * max(forward - strike, 0.0))

    root_w = np.sqrt(total_variance)
    d1 = np.log(forward / strike) / root_w + 0.5 * root_w
    d2 = d1 - root_w

    return float(discount * (
        forward * ndtr(d1) - strike * ndtr(d2)
    ))


def bsm_forward_put(
    forward: float,
    strike: float,
    total_variance: float,
    rate: float,
    maturity: float,
) -> float:
    """Black-Scholes put in forward/total-variance form."""
    call = bsm_forward_call(
        forward, strike, total_variance, rate, maturity
    )
    discount = np.exp(-rate * maturity)
    return float(call - discount * (forward - strike))


def model_free_qv(
    puts: pd.DataFrame,
    calls: pd.DataFrame,
    forward: float,
    rate: float,
    maturity: float,
) -> float:
    """
    Extract total risk-neutral QV from OTM QQQ option prices:

    QV^Q_T =
      2 exp(rT) [
        integral_0^F P(K)/K^2 dK
        + integral_F^infinity C(K)/K^2 dK
      ].

    The numerical integral is taken over the observed OTM strike range.
    """
    p = puts[["strike", "mid"]].dropna().copy()
    c = calls[["strike", "mid"]].dropna().copy()

    p["strike"] = pd.to_numeric(p["strike"], errors="coerce")
    c["strike"] = pd.to_numeric(c["strike"], errors="coerce")
    p["mid"] = pd.to_numeric(p["mid"], errors="coerce")
    c["mid"] = pd.to_numeric(c["mid"], errors="coerce")

    p = p[
        (p["strike"] > 0)
        & (p["strike"] < forward)
        & (p["mid"] >= 0)
    ].sort_values("strike")

    c = c[
        (c["strike"] >= forward)
        & (c["mid"] >= 0)
    ].sort_values("strike")

    if len(p) < 2 or len(c) < 2:
        raise ValueError("At least two OTM strikes are required on each side.")

    put_integral = trapezoid(
        p["mid"].to_numpy() / p["strike"].to_numpy() ** 2,
        p["strike"].to_numpy(),
    )
    call_integral = trapezoid(
        c["mid"].to_numpy() / c["strike"].to_numpy() ** 2,
        c["strike"].to_numpy(),
    )

    return float(
        2.0 * np.exp(rate * maturity)
        * (put_integral + call_integral)
    )


def realised_qv(
    prices: pd.Series,
) -> float:
    """Total realised QV from squared log returns."""
    s = pd.to_numeric(pd.Series(prices), errors="coerce").dropna()
    if len(s) < 2:
        raise ValueError("At least two prices are required.")

    log_returns = np.diff(np.log(s.to_numpy()))
    return float(np.sum(log_returns ** 2))


def annualised_qv(total_qv: float, maturity: float) -> float:
    """Convert total QV to annualised variance using the year fraction."""
    if maturity <= 0:
        raise ValueError("maturity must be positive.")
    return float(total_qv / maturity)


def letf_forward(
    L0: float,
    leverage: float,
    rate: float,
    maturity: float,
) -> float:
    """
    Risk-neutral LETF forward under dL/L = k dS/S.

    The forward is L0 exp(k r T); QV changes the distribution, not this
    risk-neutral forward.
    """
    if L0 <= 0 or maturity <= 0:
        raise ValueError("Invalid LETF inputs.")
    return float(L0 * np.exp(leverage * rate * maturity))


def letf_bsm_price(
    L0: float,
    strike: float,
    leverage: float,
    qv: float,
    rate: float,
    maturity: float,
) -> float:
    """
    Constant-QV LETF benchmark.

    Conditional total variance of the LETF log return is k^2 QV.
    """
    FL = letf_forward(L0, leverage, rate, maturity)
    return bsm_forward_call(
        FL,
        strike,
        leverage ** 2 * qv,
        rate,
        maturity,
    )


def _derivative(
    function,
    x: float,
    order: int,
    step: float | None = None,
) -> float:
    """Central finite-difference derivative in total-QV space."""
    h = step if step is not None else max(1e-6, abs(x) * 1e-4)

    if order == 1:
        return float((function(x + h) - function(x - h)) / (2.0 * h))
    if order == 2:
        return float(
            (function(x + h) - 2.0 * function(x) + function(x - h))
            / h ** 2
        )
    raise ValueError("Only first and second derivatives are implemented.")


def letf_qv_pricing_hierarchy(
    L0: float,
    strike: float,
    leverage: float,
    mean_qv: float,
    qv_variance: float,
    higher_central_moments: dict[int, float] | None,
    rate: float,
    maturity: float,
) -> dict:
    """
    Return the LETF pricing hierarchy implied by the QV expansion.

    First order:
        c(F_L, K, k^2 E[QV])

    Second order:
        first order + 1/2 k^4 Var(QV) c_ww

    Higher orders:
        sum_{n=0}^N k^(2n)/n! mu_n c^(n)_w.

    The finite higher-order implementation uses numerical derivatives.
    """
    if mean_qv < 0 or qv_variance < 0:
        raise ValueError("QV moments must be non-negative.")

    FL = letf_forward(L0, leverage, rate, maturity)

    def price_from_qv(qv: float) -> float:
        return bsm_forward_call(
            FL,
            strike,
            leverage ** 2 * qv,
            rate,
            maturity,
        )

    base = price_from_qv(mean_qv)

    second_derivative = _derivative(
        price_from_qv,
        mean_qv,
        order=2,
    )

    second_order = base + 0.5 * leverage ** 4 * qv_variance * second_derivative

    result = {
        "constant_qv": float(base),
        "second_order": float(second_order),
        "mean_qv": float(mean_qv),
        "qv_variance": float(qv_variance),
    }

    if higher_central_moments:
        higher = 0.0
        for n, moment in sorted(higher_central_moments.items()):
            if n < 2:
                continue
            if n > 4:
                raise ValueError("Higher-order implementation currently supports n <= 4.")

            # Repeated central derivatives via finite differences are avoided
            # beyond the explicitly supported second-order correction.
            if n == 2:
                derivative = second_derivative
            else:
                derivative = _nth_derivative(price_from_qv, mean_qv, n)

            higher += (
                leverage ** (2 * n)
                / math.factorial(n)
                * moment
                * derivative
            )

        result["higher_moment_price"] = float(base + higher)

    return result


def _nth_derivative(function, x: float, n: int) -> float:
    """
    Finite-difference derivative for n=3,4.

    Used only for the finite QV-moment approximation; the analytical
    hierarchy itself is stated in derivation.md.
    """
    h = max(1e-5, abs(x) * 1e-3)

    if n == 3:
        return float(
            (
                function(x + 2*h)
                - 2*function(x + h)
                + 2*function(x - h)
                - function(x - 2*h)
            ) / (2*h**3)
        )

    if n == 4:
        return float(
            (
                function(x + 2*h)
                - 4*function(x + h)
                + 6*function(x)
                - 4*function(x - h)
                + function(x - 2*h)
            ) / h**4
        )

    raise ValueError("Only third and fourth derivatives are supported.")


def evaluate_qv_forecasts(
    realised: pd.Series,
    forecasts: dict[str, pd.Series],
) -> pd.DataFrame:
    """Return forecast bias, MAE and RMSE for each model."""
    rows = []

    for name, forecast in forecasts.items():
        df = pd.concat(
            [
                pd.Series(realised, name="realised"),
                pd.Series(forecast, name="forecast"),
            ],
            axis=1,
        ).dropna()

        if df.empty:
            continue

        error = df["forecast"] - df["realised"]
        rows.append({
            "model": name,
            "n": int(len(df)),
            "bias": float(error.mean()),
            "mae": float(np.mean(np.abs(error))),
            "rmse": float(np.sqrt(np.mean(error.to_numpy() ** 2))),
        })

    return pd.DataFrame(rows)


def hac_mean_error(
    realised: pd.Series,
    forecast: pd.Series,
) -> dict:
    """Test whether the mean forecast error differs from zero using HAC SEs."""
    error = (
        pd.Series(forecast)
        .subtract(pd.Series(realised))
        .dropna()
        .to_numpy()
    )

    if len(error) < 2:
        raise ValueError("At least two observations are required.")

    X = np.ones((len(error), 1))
    fit = sm.OLS(error, X).fit(
        cov_type="HAC",
        cov_kwds={"maxlags": max(1, min(5, len(error) - 1))},
    )

    return {
        "n": int(len(error)),
        "mean_error": float(fit.params[0]),
        "hac_t": float(fit.tvalues[0]),
        "p_value": float(fit.pvalues[0]),
    }


if __name__ == "__main__":
    print("Use the module functions with the prepared 48-observation QQQ/TQQQ panel.")
