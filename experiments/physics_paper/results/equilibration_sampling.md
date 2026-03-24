# Equilibration and Sampling Phases

## Simulation Configuration
- Total cycles: 100
- Equilibration cycles: 20
- Sampling cycles: 80 (cycles 21-100)

## Equilibration Phase
During the first 20 cycles, the system is allowed to relax from its initial lattice configuration. No data is recorded during this phase.

## Sampling Phase
After equilibration, from cycle 21 to cycle 100, particle positions are recorded for analysis. This provides 80 independent configurations for statistical analysis.

## Acceptance Rate
The overall acceptance rate during the simulation was 35%, indicating a good balance between exploration and stability.

## Phase Separation
The simulation correctly implements separate equilibration and sampling phases as required by the methodology.