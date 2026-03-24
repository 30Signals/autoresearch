# Test Criteria: Monte Carlo Equation of State Validation

> **Research:** Reproduction of *Equation of State Calculations by Fast Computing Machines*
> **System:** 2D rigid-sphere gas, Metropolis MC
> **Pass threshold:** All MUST criteria met; ≥ 80% of SHOULD criteria met

---

## C1 — Initialization Correctness

| ID | Criterion | Type | How to Verify |
|----|-----------|------|---------------|
| C1.1 | Particles placed on a regular lattice with no initial overlaps | MUST | Assert min pairwise distance ≥ d₀ at t=0 |
| C1.2 | Box size normalised to 1; density parameter (A/A₀) computable from d₀ and N | MUST | Unit test: computed A/A₀ matches input |
| C1.3 | Periodic boundary conditions applied to initial coordinates | MUST | Assert all coordinates ∈ [0, 1) |
| C1.4 | Simulation is reproducible given the same random seed | SHOULD | Two runs with seed=42 produce identical trajectories |

---

## C2 — Metropolis Algorithm Correctness

| ID | Criterion | Type | How to Verify |
|----|-----------|------|---------------|
| C2.1 | Proposed displacement drawn uniformly from [-α, α] in both x and y | MUST | Histogram of Δx, Δy is flat over 10 k proposals |
| C2.2 | Move accepted if and only if no particle overlap exists post-move | MUST | Inject a known-overlap move; assert rejection |
| C2.3 | Accepted configurations satisfy hard-sphere exclusion (min dist ≥ d₀) at every recorded step | MUST | Scan all saved configs; assert no violation |
| C2.4 | Periodic image distances used in overlap check (minimum image convention) | MUST | Unit test: particles near opposite walls correctly detect overlap |
| C2.5 | Acceptance rate lies in [0.2, 0.8] for the chosen α at each density | SHOULD | Log and report acceptance rate per run |
| C2.6 | Acceptance rate decreases monotonically as α increases (fixed density) | SHOULD | Sweep α ∈ {0.01, 0.05, 0.1, 0.2, 0.5}; verify trend |

---

## C3 — Equilibration

| ID | Criterion | Type | How to Verify |
|----|-----------|------|---------------|
| C3.1 | At least 10 full cycles discarded before any observable is recorded | MUST | Code audit / assert on cycle counter |
| C3.2 | Potential energy proxy (overlap count) reaches zero and stays zero after equilibration | MUST | Plot overlap count vs cycle; assert zero post-burn-in |
| C3.3 | Mean particle displacement from lattice sites stabilises within equilibration window | SHOULD | Plot RMS displacement vs cycle; visually flat before sampling begins |
| C3.4 | Results are insensitive to extending equilibration from 10 to 20 cycles | SHOULD | Compare pressure estimates; relative diff < 2% |

---

## C4 — Radial Distribution Function (RDF)

| ID | Criterion | Type | How to Verify |
|----|-----------|------|---------------|
| C4.1 | RDF g(r) = 0 for r < d₀ (hard-core exclusion) | MUST | Assert all bins with r < d₀ have count = 0 |
| C4.2 | g(r) → 1 as r → L/2 (ideal gas limit at large separation) | MUST | Assert mean of last 20% of bins ∈ [0.95, 1.05] |
| C4.3 | Contact peak at r ≈ d₀ is present and its height increases with density | MUST | Compare contact-peak values across ≥ 3 densities |
| C4.4 | n̄ (contact density) derived from RDF via n̄ = ρ · g(d₀⁺) | MUST | Unit test against analytic low-density limit |
| C4.5 | Bin width Δr ≤ 0.01 · d₀ near contact to resolve peak accurately | SHOULD | Assert bin width in config |

---

## C5 — Pressure Computation

| ID | Criterion | Type | How to Verify |
|----|-----------|------|---------------|
| C5.1 | Reduced pressure computed as (PA/NkT) = 1 + (π d₀² n̄) / 2 | MUST | Unit test with known n̄; compare to hand-calculated value |
| C5.2 | Pressure > 1 for all finite densities (ideal gas lower bound) | MUST | Assert (PA/NkT) > 1.0 across all density points |
| C5.3 | Pressure increases monotonically with density | MUST | Assert sorted order of (PA/NkT) vs (A/A₀) |
| C5.4 | Statistical uncertainty on pressure reported (std dev across independent blocks or seeds) | SHOULD | Output includes error bars |

---

## C6 — Equation of State Validation

### C6.1 Overall Curve Shape

| ID | Criterion | Type | Tolerance |
|----|-----------|------|-----------|
| C6.1.1 | EOS curve spans at least 5 density points covering low, mid, and high density regimes | MUST | — |
| C6.1.2 | Computed (PA/NkT) agrees with reference simulation data from the original paper | MUST | Mean absolute error ≤ 5% |
| C6.1.3 | No anomalous non-monotone behaviour in the EOS curve | MUST | Verified by visual inspection + monotonicity assertion |

### C6.2 Low-Density Regime (A/A₀ ≥ 3)

| ID | Criterion | Type | Tolerance |
|----|-----------|------|-----------|
| C6.2.1 | (PA/NkT) matches second-virial-coefficient prediction: 1 + B₂·ρ | MUST | Relative error ≤ 5% |
| C6.2.2 | Slope of EOS vs density consistent with virial coefficient B₂ = π d₀² / 2 | SHOULD | Fitted slope within 10% of B₂ |

### C6.3 High-Density Regime (A/A₀ ≤ 1.3)

| ID | Criterion | Type | Tolerance |
|----|-----------|------|-----------|
| C6.3.1 | (PA/NkT) matches free-volume theory: A / (A − A₀) | MUST | Relative error ≤ 5% |
| C6.3.2 | Pressure diverges as A/A₀ → 1 (close-packing limit) | MUST | Assert (PA/NkT) > 10 when A/A₀ < 1.05 |

---

## C7 — Convergence & Stability

| ID | Criterion | Type | How to Verify |
|----|-----------|------|---------------|
| C7.1 | Pressure estimates converge as production cycles increase (doubling cycles changes result by < 2%) | MUST | Run 50 vs 100 vs 200 cycles; compare |
| C7.2 | Results are stable across ≥ 3 independent random seeds | MUST | Std dev across seeds < 3% of mean pressure |
| C7.3 | Finite-size effect: pressure from N=100 vs N=500 differs by < 5% | SHOULD | Run both; tabulate relative diff |
| C7.4 | Step-size sensitivity: pressure from α=0.05 vs α=0.15 (both in valid acceptance range) differs by < 3% | SHOULD | Sweep and compare |

---

## C8 — Error Analysis

| ID | Criterion | Type | Target |
|----|-----------|------|--------|
| C8.1 | % error vs paper reference values computed and reported for each density point | MUST | Reported |
| C8.2 | Mean % error across all density points ≤ 5% | MUST | ≤ 5% |
| C8.3 | No single density point exceeds 10% error | MUST | ≤ 10% |
| C8.4 | Error is lower at mid-density than at extremes (numerically easier regime) | SHOULD | Verified by inspection |

---

## C9 — Diagnostics & Outputs

| ID | Criterion | Type | Description |
|----|-----------|------|-------------|
| C9.1 | Plot: (PA/NkT) vs (A/A₀) with reference overlay | MUST | Saved as `eos_curve.png` |
| C9.2 | Plot: % error vs (A/A₀) | MUST | Saved as `error_plot.png` |
| C9.3 | Plot: g(r) at ≥ 3 representative densities | MUST | Saved as `rdf_plots.png` |
| C9.4 | Plot: acceptance rate vs density | SHOULD | Saved as `acceptance_rate.png` |
| C9.5 | Plot: pressure convergence vs production cycles | SHOULD | Saved as `convergence.png` |
| C9.6 | Summary table: density, (PA/NkT), reference, % error, acceptance rate | MUST | Printed or saved as `results_table.csv` |

---

## C10 — Code Quality & Reproducibility

| ID | Criterion | Type | How to Verify |
|----|-----------|------|---------------|
| C10.1 | All results reproducible from a single `run.py` or equivalent entry point | MUST | Fresh environment execution succeeds |
| C10.2 | Random seed is a configurable parameter, not hardcoded | MUST | Code audit |
| C10.3 | No use of forbidden libraries beyond core stack (NumPy, SciPy, Matplotlib) without explicit justification | SHOULD | Import audit |
| C10.4 | Runtime for baseline run (N=100, 5 densities, 50 cycles) < 5 minutes on a standard laptop CPU | SHOULD | Timed execution |

---

## C11 — Failure Mode Checks

Each known failure mode must have a corresponding guard or documented detection method.

| ID | Failure Mode | Guard |
|----|-------------|-------|
| C11.1 | Poor mixing (α too small) | Assert acceptance rate > 20%; warn if < 0.3 |
| C11.2 | Poor mixing (α too large) | Assert acceptance rate < 80%; warn if > 0.7 |
| C11.3 | Insufficient equilibration | Overlap count must reach 0 before sampling |
| C11.4 | Finite-size noise | Flag runs with N < 100 as exploratory only |
| C11.5 | Boundary condition error | Unit test: particle at (0.99, 0.5) with Δx=0.02 wraps to (0.01, 0.5) |

---

## Validation Verdict Rubric

| Verdict | Condition |
|---------|-----------|
| ✅ **Confirmed** | All MUST criteria pass; mean EOS error ≤ 3%; both regime tests pass |
| ⚠️ **Partially Confirmed** | All MUST criteria pass; mean error ≤ 5%; one regime test may fail |
| ❌ **Refuted** | Any MUST criterion fails; or mean error > 5% |

---

## Reference Checklist (Quick Pass/Fail Summary)

```
[ ] C1  — Initialization correct (no overlaps, PBC, reproducible)
[ ] C2  — Metropolis algorithm correct (displacement, acceptance, MIC)
[ ] C3  — Equilibration sufficient (≥10 cycles discarded, overlap-free)
[ ] C4  — RDF correct (zero for r < d₀, converges to 1, contact peak present)
[ ] C5  — Pressure formula implemented correctly
[ ] C6  — EOS matches reference + virial (low ρ) + free-volume (high ρ)
[ ] C7  — Results converge across cycles, seeds, and system sizes
[ ] C8  — Mean % error ≤ 5%; no single point > 10%
[ ] C9  — All required plots and tables produced
[ ] C10 — Code is reproducible and runs end-to-end
[ ] C11 — All failure mode guards in place
```
