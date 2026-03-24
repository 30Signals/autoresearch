### Physical Model

- 2D box with periodic boundary conditions

- N particles (100–500)

- Hard-sphere interaction:

  - No overlap allowed

  - Energy = 0 (valid), ∞ (overlap)

## Methodology

### Step 1: Initialization

- Initialize particles in a lattice configuration

- Define:

  - Box size = 1

  - Particle diameter d₀

  - Density parameter (A / A₀)

### Step 2: Monte Carlo Simulation (Metropolis Algorithm)

For each cycle:

- Iterate over all particles

- Propose random displacement within range [-α, α]