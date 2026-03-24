# Research Goal: Monte Carlo Equation of State Validation

## Objective
Reproduce and validate the Monte Carlo method for computing the equation of state of a 2D rigid-sphere system, as introduced in *Equation of State Calculations by Fast Computing Machines*.

---

## Research Hypothesis
1. A Metropolis Monte Carlo process correctly samples configurations proportional to the Boltzmann distribution:
   - P ∝ exp(-E / kT)

2. This sampling enables accurate estimation of macroscopic thermodynamic quantities.

3. The computed equation of state:
   - (PA / NkT) = 1 + (π d₀² n̄) / 2

   should match:
   - Free volume theory at high density
   - Virial expansion at low density

---

## System Definition

### Physical Model
- 2D box with periodic boundary conditions
- N particles (100–500)
- Hard-sphere interaction:
  - No overlap allowed
  - Energy = 0 (valid), ∞ (overlap)

---

## Methodology

### Step 1: Initialization
- Initialize particles in a lattice configuration
- Define:
  - Box size = 1
  - Particle diameter d₀
  - Density parameter (A / A₀)

---

### Step 2: Monte Carlo Simulation (Metropolis Algorithm)

For each cycle:
- Iterate over all particles
- Propose random displacement within range [-α, α]

Acceptance rule:
- If no overlap → accept move
- If overlap → reject move

Note:
- For hard spheres, ΔE ∈ {0, ∞}, so acceptance reduces to overlap check

---

### Step 3: Equilibration
- Run 10–20 cycles without recording data
- Discard early configurations

---

### Step 4: Sampling
For each configuration after equilibration:
- Compute pairwise distances
- Build radial distribution function N(r)
- Bin distances into zones
- Estimate density near contact distance d₀

---

### Step 5: Pressure Computation
Compute:
- n̄ = density at contact

Then:
- (PA / NkT) = 1 + (π d₀² n̄) / 2

---

### Step 6: Parameter Sweep
Vary density by adjusting particle diameter or box scaling.

For each density:
- Run full simulation
- Compute pressure

---

## Experimental Variables

### Independent Variables
- Density (A / A₀)
- Number of particles N
- Step size α

### Dependent Variables
- Pressure (P)
- Radial distribution function N(r)
- Acceptance rate

---

## Validation Plan

### 1. Equation of State Curve
- Plot (PA / NkT) vs (A / A₀)
- Compare with:
  - Reference simulation results
  - Theoretical expectations

---

### 2. Regime Validation
- High density → match free volume theory
- Low density → match virial expansion

---

### 3. Error Analysis
- Compute % error vs reference values
- Target accuracy: ~3%

---

### 4. Convergence Checks
- Run multiple seeds
- Compare results across:
  - Different N
  - Different step sizes

---

## Failure Modes

### 1. Poor Mixing
- Step size too small → slow exploration
- Step size too large → high rejection rate

---

### 2. Lack of Equilibration
- Using early samples leads to biased results

---

### 3. Finite Size Effects
- Small N → noisy estimates

---

### 4. Boundary Errors
- Incorrect periodic boundary implementation

---

## Extensions

### Level 2
- Compare Metropolis vs naive Monte Carlo

### Level 3
- Replace hard-sphere with Lennard-Jones potential

### Level 4
- Extend to 3D systems
- Investigate phase transitions

---

## Output Format

### 1. Summary
- Key findings
- Whether results match theoretical expectations

### 2. Visualizations
- Pressure vs density
- Error vs density
- Radial distribution function

### 3. Diagnostics
- Acceptance rate
- Convergence plots

### 4. Conclusion
- Validation status: Confirmed / Partially Confirmed / Refuted

---

## Success Criteria
- Equation of state curve matches expected shape
- Agreement with theory in correct regimes
- Stable results across runs
- Error within acceptable bounds (~3–5%)

---

## Tooling

### Core Stack
- Python
- NumPy
- SciPy
- Matplotlib

### Optional
- Numba (for speed)
- JAX / PyTorch (for scaling experiments)

---
## REFERENCES
paper_summary.md : this file contains a summary of key claims of the paper
