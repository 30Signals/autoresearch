## C1 — Initialization Correctness
- [ ] Particles placed on a regular lattice with no initial overlaps
- [ ] Box size normalised to 1; density parameter (A/A₀) computable from d₀ and N
- [ ] Periodic boundary conditions applied to initial coordinates
- [ ] Simulation is reproducible given the same random seed
## C2 — Metropolis Algorithm Correctness
- [ ] Proposed displacement drawn uniformly from [-α, α] in both x and y
- [ ] Move accepted if and only if no particle overlap exists post-move
- [ ] Accepted configurations satisfy hard-sphere exclusion (min dist ≥ d₀) at every recorded step
- [ ] Periodic image distances used in overlap check (minimum image convention)
- [ ] Acceptance rate lies in [0.2, 0.8] for the chosen α at each density
- [ ] Acceptance rate decreases monotonically as α increases (fixed density)
## C3 — Equilibration
- [ ] At least 10 full cycles discarded before any observable is recorded
- [ ] Potential energy proxy (overlap count) reaches zero and stays zero after equilibration
- [ ] Mean particle displacement from lattice sites stabilises within equilibration window
- [ ] Results are insensitive to extending equilibration from 10 to 20 cycles
## C4 — Radial Distribution Function (RDF)
- [ ] RDF g(r) = 0 for r < d₀ (hard-core exclusion)
- [ ] g(r) → 1 as r → L/2 (ideal gas limit at large separation)
- [ ] Contact peak at r ≈ d₀ is present and its height increases with density
- [ ] n̄ (contact density) derived from RDF via n̄ = ρ · g(d₀⁺)
- [ ] Bin width Δr ≤ 0.01 · d₀ near contact to resolve peak accurately
## C5 — Pressure Computation
- [ ] Reduced pressure computed as (PA/NkT) = 1 + (π d₀² n̄) / 2
- [ ] Pressure > 1 for all finite densities (ideal gas lower bound)
- [ ] Pressure increases monotonically with density
- [ ] Statistical uncertainty on pressure reported (std dev across independent blocks or seeds)
## C6 — Equation of State Validation
### Curve Shape
- [ ] EOS curve spans at least 5 density points covering low, mid, and high density regimes
- [ ] Computed (PA/NkT) agrees with reference simulation data from the original paper
- [ ] No anomalous non-monotone behaviour in the EOS curve
### Low-Density Regime (A/A₀ ≥ 3)
- [ ] (PA/NkT) matches second-virial-coefficient prediction: 1 + B₂·ρ
- [ ] Slope of EOS vs density consistent with virial coefficient B₂ = π d₀² / 2
### High-Density Regime (A/A₀ ≤ 1.3)
- [ ] (PA/NkT) matches free-volume theory: A / (A − A₀)
- [ ] Pressure diverges as A/A₀ → 1 (close-packing limit)
## C7 — Convergence & Stability
- [ ] Pressure estimates converge as production cycles increase (doubling cycles changes result by < 2%)
- [ ] Results are stable across ≥ 3 independent random seeds
- [ ] Finite-size effect: pressure from N=100 vs N=500 differs by < 5%
- [ ] Step-size sensitivity: pressure from α=0.05 vs α=0.15 (both in valid acceptance range) differs by < 3%
## C8 — Error Analysis
- [ ] % error vs paper reference values computed and reported for each density point
- [ ] Mean % error across all density points ≤ 5%
- [ ] No single density point exceeds 10% error
- [ ] Error is lower at mid-density than at extremes (numerically easier regime)
## C9 — Diagnostics & Outputs
- [ ] Plot: (PA/NkT) vs (A/A₀) with reference overlay (saved as `eos_curve.png`)
- [ ] Plot: % error vs (A/A₀) (saved as `error_plot.png`)
- [ ] Plot: g(r) at ≥ 3 representative densities (saved as `rdf_plots.png`)
- [ ] Plot: acceptance rate vs density (saved as `acceptance_rate.png`)
- [ ] Plot: pressure convergence vs production cycles (saved as `convergence.png`)
- [ ] Summary table: density, (PA/NkT), reference, % error, acceptance rate (saved as `results_table.csv`)
## C10 — Code Quality & Reproducibility
- [ ] All results reproducible from a single `run.py` or equivalent entry point
- [ ] Random seed is a configurable parameter, not hardcoded
- [ ] No use of forbidden libraries beyond core stack (NumPy, SciPy, Matplotlib) without explicit justification
- [ ] Runtime for baseline run (N=100, 5 densities, 50 cycles) < 5 minutes on a standard laptop CPU
## C11 — Failure Mode Checks
- [ ] All known failure modes have guards or documented detection methods
## Validation Verdict
- [ ] Confirmed (All MUST criteria pass; mean EOS error ≤ 3%; both regime tests pass)
- [ ] Partially Confirmed (All MUST criteria pass; mean error ≤ 5%; one regime test may fail)
- [ ] Refuted (Any MUST criterion fails; or mean error > 5%)