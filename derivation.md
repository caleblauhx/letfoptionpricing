# LETF Option Pricing: Derivation from First Principles
## Derivation from First Principles

## 1. Roadmap

The derivation is deliberately sequential. Each section establishes the mathematical object required by the next, so that no result is invoked before its underlying machinery has been constructed.

1. **Stochastic calculus.** We introduce random variables, stochastic processes, random walks, Brownian motion, quadratic variation, and Itô's lemma. These provide the mathematical language for continuously evolving randomness.
2. **The underlying asset.** We assume the underlying price follows geometric Brownian motion (GBM), which determines the distribution of its terminal price.
3. **No-arbitrage pricing.** We derive the Black–Scholes equation and risk-neutral pricing from a dynamically hedged portfolio.
4. **Realised variance.** We construct the fair value of realised variance directly from traded option prices through a replication argument. This produces a model-free risk-neutral expectation of quadratic variation.
5. **The LETF.** We derive the exact terminal value of a continuously rebalanced leveraged ETF and identify its variance-drag term.
6. **Options on the LETF.** We first recover the constant-volatility Black–Scholes approximation, then expand the price around the risk-neutral mean of realised variance, showing precisely why higher moments of realised variance matter. Finally, we introduce Heston as a model capable of generating those moments.

The central point is that daily rebalancing makes the LETF path-dependent: its terminal value depends not only on the underlying's terminal price but also on the quadratic variation accumulated along the path.

---

# 2. Stochastic calculus: the required tools

### Definition 1 — Random variable

A random variable \(X\) is a quantity whose realised value is not known in advance and is governed by a probability distribution.

### Definition 2 — Stochastic process

A stochastic process \((X_t)_{t\geq0}\) is a collection of random variables indexed by time. At each fixed \(t\), \(X_t\) has a probability distribution; jointly over time, the process traces a random path.

### Definition 3 — Random walk

A random walk is the discrete-time process obtained by accumulating independent, identically distributed increments:
\[
X_n=\sum_{i=1}^{n}\xi_i.
\]
It provides the discrete-time prototype for the continuous-time processes used below.

### Definition 4 — Brownian motion

Brownian motion \(W=(W_t)_{t\geq0}\) is the continuous-time limit of a suitably rescaled random walk. It satisfies
\[
W_0=0,
\]
has independent increments over disjoint intervals, and
\[
W_t-W_s\sim N(0,t-s),\qquad t>s.
\]

The \(\sqrt{\Delta t}\) scaling of the random-walk increments is essential: it ensures that the variance accumulated over an interval of length \(t\) remains \(t\) as the sampling interval tends to zero.

### Definition 5 — Quadratic variation

For a process \(X\), take a partition
\[
0=t_0<t_1<\cdots<t_n=T
\]
whose mesh tends to zero. Its quadratic variation is
\[
[X]_T
=
\lim_{\|\Pi\|\to0}
\sum_{i=0}^{n-1}
\left(X_{t_{i+1}}-X_{t_i}\right)^2.
\]

For a smooth finite-variation function \(f\),
\[
(\Delta f)^2=O((\Delta t)^2),
\]
so the sum of squared increments vanishes in the limit. Brownian motion behaves fundamentally differently:
\[
[W]_T=T.
\]

This follows from
\[
\mathbb E[(\Delta W_i)^2]=\Delta t_i
\]
and independence of the increments. Hence, in Itô calculus,
\[
(dW_t)^2=dt.
\]

This identity is not a modelling convention. It is the differential expression of Brownian motion's non-zero quadratic variation.

### Proposition 6 — Itô's lemma

Suppose
\[
dX_t=b_t\,dt+\sigma_t\,dW_t
\]
and \(f\in C^{1,2}\). Then
\[
df(t,X_t)
=
f_t\,dt
+
f_x\,dX_t
+
\frac12 f_{xx}\sigma_t^2\,dt.
\]

The additional term is the essential distinction from ordinary calculus. A second-order Taylor expansion contains
\[
\frac12 f_{xx}(dX_t)^2,
\]
and because
\[
(dX_t)^2=\sigma_t^2(dW_t)^2=\sigma_t^2dt,
\]
this term survives at first order in \(dt\). Thus quadratic variation creates the additional drift
\[
\frac12 f_{xx}\sigma_t^2dt.
\]

---

# 3. Modelling assumption: geometric Brownian motion

Assume the underlying price \(S_t\), under the physical measure \(\mathbb P\), follows
\[
\boxed{
dS_t=\mu S_t\,dt+\sigma_tS_t\,dW_t.
}
\tag{1}
\]

Here \(\mu\) is the instantaneous expected return and \(\sigma_t\) is the instantaneous volatility.

Applying Itô's lemma to \(f(S_t)=\ln S_t\) gives
\[
d\ln S_t
=
\frac{dS_t}{S_t}
-\frac12\sigma_t^2dt,
\]
and therefore
\[
\boxed{
d\ln S_t
=
\left(\mu-\frac12\sigma_t^2\right)dt
+
\sigma_t\,dW_t.
}
\tag{2}
\]

For constant \(\sigma\), integration gives
\[
\boxed{
S_T
=
S_0
\exp\left[
\left(\mu-\frac12\sigma^2\right)T
+
\sigma W_T
\right].
}
\tag{3}
\]

Hence
\[
\ln S_T
\sim
N\left(
\ln S_0+\left(\mu-\frac12\sigma^2\right)T,\,
\sigma^2T
\right),
\]
so \(S_T\) is lognormally distributed. The GBM assumption therefore specifies the terminal distribution required for option pricing.

---

# 4. Black–Scholes: fair pricing from no-arbitrage

Let \(V(t,S)\) be the value of a European claim paying \(\Phi(S_T)\).

By Itô's lemma,
\[
dV
=
\left(
V_t+\mu SV_S+\frac12\sigma^2S^2V_{SS}
\right)dt
+
\sigma SV_S\,dW.
\]

Construct the delta-hedged portfolio
\[
\Pi=V-\Delta S,
\qquad
\Delta=V_S.
\]

The stochastic term cancels:
\[
d\Pi
=
\left(
V_t+\frac12\sigma^2S^2V_{SS}
\right)dt.
\]

The portfolio is therefore locally riskless. No-arbitrage requires it to earn the risk-free rate:
\[
d\Pi=r\Pi\,dt.
\]

Substituting \(\Pi=V-SV_S\) gives the Black–Scholes PDE:
\[
\boxed{
V_t+\frac12\sigma^2S^2V_{SS}
+rSV_S-rV=0.
}
\tag{4}
\]

Equivalently, under the risk-neutral measure \(\mathbb Q\),
\[
\boxed{
\frac{dS_t}{S_t}
=
r\,dt+\sigma_t\,dW_t^{\mathbb Q}.
}
\tag{5}
\]

The fair value is consequently
\[
\boxed{
V_t
=
e^{-r(T-t)}
\mathbb E_t^{\mathbb Q}[\Phi(S_T)].
}
\]

The physical drift \(\mu\) disappears from the pricing equation: the change of measure replaces the risk premium \(\mu-r\) by a drift of \(r\), while preserving the volatility structure.

For constant \(\sigma\), writing the forward as
\[
F=S_0e^{rT}
\]
and total variance as
\[
w=\sigma^2T,
\]
the Black–Scholes call price can be written
\[
\boxed{
c(F,K,w)
=
e^{-rT}
\left[
FN(d_1)-KN(d_2)
\right],
}
\tag{6}
\]
where
\[
d_{1,2}
=
\frac{\ln(F/K)\pm\frac12w}{\sqrt w}.
\]

Market option prices are often represented instead through implied volatility: the value of constant \(\sigma\) which makes (6) reproduce the observed price. A flat implied-volatility surface would be consistent with literal constant volatility; the observed smile and skew are evidence against that restriction.

---

# 5. Fair value of realised variance from option prices

## 5.1 Realised variance and quadratic variation

For log returns sampled at intervals \(\Delta t\),
\[
RV_{[0,T]}
=
\frac1{\Delta t}
\sum_{i=1}^{n}
\left(
\ln\frac{S_{t_i}}{S_{t_{i-1}}}
\right)^2.
\]

As the sampling interval tends to zero,
\[
RV_{[0,T]}
\longrightarrow
QV_{[0,T]}
=
\int_0^T\sigma_t^2\,dt.
\tag{7}
\]

Thus continuous realised variance is precisely the quadratic variation of \(\ln S\).

A variance swap pays
\[
N(RV_{[0,T]}-K_{\mathrm{var}}).
\]

No-arbitrage therefore requires
\[
\boxed{
K_{\mathrm{var}}
=
\mathbb E^{\mathbb Q}[QV_{[0,T]}].
}
\]

Denote this risk-neutral fair value by
\[
QV_T^{\mathbb Q}.
\]

## 5.2 The spanning identity

For \(g\in C^2\), Taylor's theorem with integral remainder gives the payoff decomposition
\[
\begin{aligned}
g(S_T)
={}&
g(F_0)+g'(F_0)(S_T-F_0)\\
&+
\int_0^{F_0}g''(K)(K-S_T)^+\,dK\\
&+
\int_{F_0}^{\infty}g''(K)(S_T-K)^+\,dK.
\end{aligned}
\tag{8}
\]

Thus any sufficiently smooth terminal payoff can be decomposed into cash, a forward position, and a continuum of out-of-the-money puts and calls.

Now choose
\[
g(S)=-2\ln S.
\]
Since
\[
g''(K)=\frac{2}{K^2},
\]
the log contract is replicated by a static strip of OTM options weighted by \(1/K^2\).

Under \(\mathbb Q\), Itô's lemma gives
\[
d\ln S_t
=
\left(r-\frac12\sigma_t^2\right)dt
+\sigma_t\,dW_t^{\mathbb Q}.
\]

Hence
\[
d\ln S_t
=
\frac{dS_t}{S_t}
-\frac12\sigma_t^2dt,
\]
so
\[
QV_{[0,T]}
=
2\int_0^T\frac{dS_t}{S_t}
-
2\ln\frac{S_T}{S_0}.
\]

Taking risk-neutral expectations and using
\[
\mathbb E^{\mathbb Q}
\left[
\int_0^T\frac{dS_t}{S_t}
\right]
=rT,
\]
the fair variance is
\[
\boxed{
QV_T^{\mathbb Q}
=
2e^{rT}
\left[
\int_0^{F_0}\frac{P(K)}{K^2}\,dK
+
\int_{F_0}^{\infty}\frac{C(K)}{K^2}\,dK
\right],
}
\tag{9}
\]
where
\[
F_0=S_0e^{rT}.
\]

This is the key model-free result: the risk-neutral expected quadratic variation can be extracted directly from the cross-section of vanilla option prices. No stochastic-volatility model is required to obtain its first moment.

---

# 6. Fair pricing of the LETF

## 6.1 Continuous-rebalancing idealisation of daily rebalancing

Let \(L_t\) denote an LETF targeting constant leverage \(k\). The derivation first uses the continuous-time idealisation of daily rebalancing:
\[
\boxed{
\frac{dL_t}{L_t}
=
k\frac{dS_t}{S_t}.
}
\tag{10}
\]

The defining feature is that leverage is reset continuously: the fund targets \(k\) times the *instantaneous* return, not \(k\) times the cumulative return over the entire horizon.

Set
\[
X_t=\ln L_t.
\]
Applying Itô's lemma,
\[
dX_t
=
k\frac{dS_t}{S_t}
-\frac12k^2\sigma_t^2dt.
\]

Under \(\mathbb Q\),
\[
\frac{dS_t}{S_t}
=
r\,dt+\sigma_t\,dW_t^{\mathbb Q},
\]
while
\[
d\ln S_t
=
\left(r-\frac12\sigma_t^2\right)dt
+\sigma_t\,dW_t^{\mathbb Q}.
\]

Therefore
\[
d\ln L_t-k\,d\ln S_t
=
-\frac12k(k-1)\sigma_t^2dt.
\]

Integrating,
\[
\boxed{
\frac{L_T}{L_0}
=
\left(\frac{S_T}{S_0}\right)^k
\exp\left[
-\frac12k(k-1)QV_{[0,T]}
\right].
}
\tag{11}
\]

This identity is exact within the continuous-rebalancing model.

The term
\[
\boxed{
\exp\left[
-\frac12k(k-1)QV_{[0,T]}
\right]
}
\]
is the variance-drag factor.

For \(k=1\), it equals one. For \(k=3\), it becomes
\[
e^{-3QV_{[0,T]}}.
\]

Crucially, two underlying paths can finish at the same \(S_T\) yet produce different \(L_T\) if they accumulate different quadratic variation. Thus the LETF is path-dependent. Its terminal value is a function of the pair
\[
\boxed{
(S_T,QV_{[0,T]}),
}
\]
not of \(S_T\) alone.

---

# 7. Options on the LETF

A European option with payoff \(\Phi(L_T)\) has fair value
\[
C_L
=
e^{-rT}
\mathbb E^{\mathbb Q}[\Phi(L_T)].
\]

By (11), pricing therefore requires the joint risk-neutral distribution of
\[
(S_T,QV_{[0,T]}).
\]

This observation determines the hierarchy of approximations that follows.

---

## 7.1 Step 1: constant-volatility BSM approximation

Suppose
\[
\sigma_t\equiv\sigma.
\]

Then
\[
QV_{[0,T]}=\sigma^2T
\]
is deterministic. Equation (11) becomes
\[
L_T
=
L_0
\left(\frac{S_T}{S_0}\right)^k
\exp\left[
-\frac12k(k-1)\sigma^2T
\right].
\]

Since \(S_T\) is lognormal, \(L_T\) is also lognormal. Its total variance is
\[
\boxed{
w_L=k^2\sigma^2T,
}
\]
so its effective volatility is
\[
\boxed{
\sigma_L=|k|\sigma.
}
\tag{12}
\]

Consequently,
\[
\boxed{
C_L(K,T)
=
c(F_L,K,k^2\sigma^2T),
}
\tag{13}
\]
with the appropriate LETF forward \(F_L\).

Thus the familiar heuristic of multiplying the underlying implied volatility by \(|k|\) is exact **only when realised variance is deterministic**.

---

## 7.2 Step 2: first-order expansion around fair realised variance

The constant-volatility result can instead be interpreted as the first term in an expansion that allows realised variance to be random.

Assume, for this intermediate step, that the volatility path is independent of the price Brownian motion. Conditional on \(QV_{[0,T]}\), the LETF remains lognormal, so
\[
\boxed{
C_L(K,T)
=
\mathbb E^{\mathbb Q}
\left[
c\!\left(
F_L,K,k^2QV_{[0,T]}
\right)
\right].
}
\tag{14}
\]

Now expand the Black–Scholes price around
\[
QV_T^{\mathbb Q}
=
\mathbb E^{\mathbb Q}[QV_{[0,T]}].
\]

Writing
\[
v=QV_{[0,T]},
\]
Taylor expansion gives
\[
\begin{aligned}
c(F_L,K,k^2v)
={}&
c(F_L,K,k^2QV_T^{\mathbb Q})\\
&+
k^2(v-QV_T^{\mathbb Q})
\left.\partial_wc\right|_{w=k^2QV_T^{\mathbb Q}}
+O\!\left((v-QV_T^{\mathbb Q})^2\right).
\end{aligned}
\tag{15}
\]

Taking expectations eliminates the linear term because
\[
\mathbb E^{\mathbb Q}
[v-QV_T^{\mathbb Q}]
=0.
\]

Therefore
\[
\boxed{
C_L(K,T)
\approx
c(F_L,K,k^2QV_T^{\mathbb Q}).
}
\tag{16}
\]

The interpretation is now different from Step 1. The same BSM functional form is no longer exact; it is a first-order approximation around the *market-implied risk-neutral mean* of realised variance.

And that mean is available model-free from the option strip through (9).

---

## 7.3 Step 3: the second-order correction

The first-order approximation discards the randomness of realised variance. Carrying the Taylor expansion to second order yields
\[
\boxed{
C_L(K,T)
\approx
c(F_L,K,k^2QV_T^{\mathbb Q})
+
\frac12k^4
\operatorname{Var}^{\mathbb Q}
(QV_{[0,T]})
\left.
\partial_{ww}c
\right|_{w=k^2QV_T^{\mathbb Q}}.
}
\tag{17}
\]

The new input is therefore
\[
\operatorname{Var}^{\mathbb Q}(QV_{[0,T]}).
\]

More generally, expanding to all orders gives
\[
\boxed{
C_L(K,T)
=
\sum_{n=0}^{\infty}
\frac{k^{2n}}{n!}
\mu_n^{\mathbb Q}
\left.
\partial_w^n c
\right|_{w=k^2QV_T^{\mathbb Q}},
}
\tag{18}
\]
where
\[
\mu_n^{\mathbb Q}
=
\mathbb E^{\mathbb Q}
\left[
\left(
QV_{[0,T]}-QV_T^{\mathbb Q}
\right)^n
\right].
\]

Thus the full LETF option price depends, in principle, on the **entire risk-neutral distribution of realised variance**, not merely its mean.

This establishes a precise hierarchy:

\[
\boxed{
\text{mean of }QV
\;\longrightarrow\;
\text{variance of }QV
\;\longrightarrow\;
\text{higher moments of }QV.
}
\]

The first moment is obtainable model-free from vanilla options. The higher moments require a model for how volatility itself evolves.

---

# 8. Volatility-of-volatility: the Heston model

To generate a non-degenerate distribution for realised variance, volatility must itself be stochastic.

The Heston model specifies
\[
\boxed{
dS_t
=
rS_t\,dt+\sqrt{v_t}S_t\,dW_t,
}
\]
\[
\boxed{
dv_t
=
\kappa(\theta-v_t)\,dt
+
\xi\sqrt{v_t}\,dZ_t,
}
\]
with
\[
\boxed{
d\langle W,Z\rangle_t=\rho\,dt.
}
\tag{19}
\]

Here:

- \(v_t=\sigma_t^2\) is instantaneous variance;
- \(\kappa\) controls mean reversion;
- \(\theta\) is long-run variance;
- \(\xi\) is volatility-of-volatility;
- \(\rho\) controls correlation between price and variance shocks.

The crucial addition relative to BSM is the second Brownian shock \(Z_t\). Consequently,
\[
QV_{[0,T]}
=
\int_0^T v_t\,dt
\]
is genuinely random, so both
\[
\mathbb E^{\mathbb Q}[QV_{[0,T]}]
\]
and
\[
\operatorname{Var}^{\mathbb Q}(QV_{[0,T]})
\]
are non-degenerate model outputs.

The correlation parameter \(\rho\) also connects stochastic volatility to the implied-volatility skew. With \(\rho<0\), negative price shocks tend to coincide with increases in variance, producing a heavier left tail for \(S_T\). Under risk-neutral pricing, this increases the value of far-OTM puts relative to the constant-volatility BSM benchmark and manifests as negative implied-volatility skew.

---

# 9. What has actually been established

The derivation separates exact identities, model-free results, and approximations.

### Exact within the stated continuous-rebalancing model

The LETF identity
\[
\boxed{
\frac{L_T}{L_0}
=
\left(\frac{S_T}{S_0}\right)^k
e^{-\frac12k(k-1)QV_{[0,T]}}
}
\]
follows mechanically from daily rebalancing and Itô's lemma.

It is therefore not an empirical claim about "volatility drag"; it is the mathematical consequence of maintaining constant leverage through time.

### Model-free under no-arbitrage

The fair risk-neutral mean
\[
\boxed{
QV_T^{\mathbb Q}
=
\mathbb E^{\mathbb Q}[QV_{[0,T]}]
}
\]
can be extracted from vanilla option prices through the replicating portfolio in (9). This does not require specifying a stochastic-volatility model.

### Approximate

The LETF option price can be expanded in the risk-neutral moments of realised variance. The first-order approximation requires only \(QV_T^{\mathbb Q}\); the second-order correction additionally requires
\[
\operatorname{Var}^{\mathbb Q}(QV_{[0,T]}),
\]
and higher-order corrections require higher moments.

### Not established by this derivation

Nothing above establishes that the market misprices LETF options or that a tradeable excess return exists. That is an empirical question. The relevant comparison is between candidate models—such as constant-volatility BSM, Heston, GARCH-type specifications, and the market-implied risk-neutral variance measure—and the realised variance that subsequently occurs.

---

# 10. Conceptual conclusion

The logical chain is therefore

\[
\boxed{
\text{Brownian quadratic variation}
\rightarrow
\text{Itô correction}
\rightarrow
\text{GBM}
\rightarrow
\text{no-arbitrage pricing}
\rightarrow
\text{option-implied }E^{\mathbb Q}[QV]
\rightarrow
\text{LETF variance drag}
\rightarrow
\text{LETF option pricing}.
}
\]

The central distinction is between **terminal uncertainty** and **path uncertainty**.

For an ordinary European option on \(S_T\), the terminal distribution of \(S_T\) is sufficient for pricing. For an option on a daily-rebalanced LETF, the terminal value satisfies
\[
L_T
=
L_0
\left(\frac{S_T}{S_0}\right)^k
e^{-\frac12k(k-1)QV_{[0,T]}},
\]
so the path enters through realised quadratic variation.

That single observation explains the entire pricing hierarchy:

\[
\boxed{
\begin{array}{c}
\text{Deterministic }QV
\\[2pt]
\Downarrow
\\
\text{BSM with volatility }|k|\sigma
\\[6pt]
\text{Random }QV,\ \text{retain only }E^{\mathbb Q}[QV]
\\[2pt]
\Downarrow
\\
\text{first-order LETF option approximation}
\\[6pt]
\text{Random }QV,\ \text{retain all moments}
\\[2pt]
\Downarrow
\\
\text{stochastic-volatility model such as Heston}.
\end{array}
}
\]

The model-free variance-swap result is therefore not an isolated calculation. It supplies exactly the first risk-neutral moment required when moving from the deterministic-volatility BSM world towards the genuinely path-dependent problem of pricing options on leveraged ETFs.
