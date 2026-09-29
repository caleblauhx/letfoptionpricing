# LETF Option Pricing & Volatility Forecasting

## Research Thesis

*Deriving LETF Option Pricing and Evaluating the Performance of Various Volatility Forecasting Models*

Leveraged exchange-traded funds are path-dependent because daily rebalancing makes the effect of volatility accumulate through quadratic variation. This project derives that relationship from first principles, links vanilla option prices to model-free risk-neutral quadratic variation, and evaluates volatility models for forecasting subsequent realised variance.

The research has three connected components:

1. **LETF dynamics.** Starting from Itô's lemma, derive the variance-drag identity for a continuously rebalanced leveraged ETF and show that terminal LETF value depends on both the underlying terminal price and path-integrated variance.
2. **Model-free QV and LETF option pricing.** Use log-contract replication to obtain the risk-neutral expectation of realised quadratic variation from the QQQ option surface. Conditional on quadratic variation, LETF options reduce to a Black–Scholes-type price; expanding that price around mean QV gives a hierarchy in the mean, variance, and higher central moments of QV.
3. **Volatility forecasting.** Compare a constant-volatility benchmark, GARCH(1,1), and Heston stochastic volatility in forecasting subsequent realised quadratic variation across a pre-specified 48-observation QQQ/TQQQ sample.

QQQ is used as the liquid options proxy for the NASDAQ-100 exposure underlying TQQQ. The LETF derivation idealises daily rebalancing as continuous rebalancing, as stated explicitly in `derivation.md`.

## Repository Structure

```text
TQQQ_LETF_Option_Pricing/
├── README.md
├── derivation.md
├── requirements.txt
├── data/
│   └── load_databento.py
└── src/
    ├── test_vol_models.py
    └── test_mispricing.py
```

## Data Design

The empirical design uses the first trading day of each month from January 2022 through December 2025:

- 48 anchor observations.
- For each anchor, select the common QQQ/TQQQ option expiry satisfying 35 ≤ DTE ≤ 60 and closest to 45 calendar days.
- Use 15:59 ET QQQ/TQQQ NBBO midpoints.
- Use 15:59 ET QQQ/TQQQ underlying prices.
- Use QQQ OTM puts and calls for model-free QV.
- Measure realised QV from the anchor date through the actual selected expiry.
- Use the corresponding short-term risk-free rate for discounting.

The exact anchor dates and expiry-selection rule are encoded in `data/load_databento.py`.

## Research Modules

### `derivation.md`

First-principles mathematical development covering:

- quadratic variation and Itô's lemma;
- risk-neutral pricing;
- log-contract replication;
- model-free risk-neutral QV;
- leveraged-ETF variance drag;
- the constant-QV/BSM benchmark;
- first- and second-order QV pricing approximations;
- the general QV-moment expansion;
- Heston stochastic volatility and volatility-of-volatility.

### `data/load_databento.py`

Data-preparation utilities for Databento equity and OPRA option data, including:

- the 48 monthly anchor schedule;
- common-expiry selection;
- 15:59 ET quote selection;
- NBBO cleaning;
- equity-price extraction;
- option-surface construction inputs.

### `src/test_mispricing.py`

Implements:

- BSM option pricing in total-variance form;
- model-free QV extraction from OTM QQQ options;
- the LETF deterministic-QV benchmark;
- the first-order mean-QV pricing approximation;
- the second-order QV-variance correction;
- the general finite-order central-moment expansion;
- realised-QV calculation;
- HAC inference and forecast-error evaluation.

### `src/test_vol_models.py`

Implements:

- constant-volatility QV forecasts;
- GARCH(1,1) variance forecasts;
- Heston stochastic-variance simulation;
- QV moment estimation from Heston paths;
- forecast-error metrics for the 48-observation panel.

## Data Conventions

Quadratic variation is treated as a **total** quantity:

\[
QV_{[0,T]}=\int_0^T \sigma_t^2\,dt.
\]

An annualised variance measure is obtained by dividing total QV by the year fraction when required. The model-free option-strip formula therefore returns total QV rather than an ATM implied-volatility square.

The risk-neutral QV extracted from options is not identified with physical realised QV. Their difference can contain a variance risk premium as well as forecast error.

The option-strip integral is evaluated over observed strikes. Tail coverage and any interpolation/extrapolation used in an empirical run should therefore be recorded with the results.

## Running

Install:

```bash
pip install -r requirements.txt
```

The modules expose functions for the full research workflow. They operate on supplied Databento-derived data rather than embedding fabricated market observations or research results.
