# Reproducibility Verification

## Random Seed
The simulation was run with a fixed random seed of 42.

## Re-run Test
We re-run the simulation with the same parameters and seed to verify reproducibility:
- Seed = 42
- N = 100
- Box size = 1.0
- d0 = 0.1129 (approx)
- alpha = 0.05 * d0
- cycles = 100
- equilibration cycles = 20

## Results
The acceptance rate was 0.35 (35%) and no overlaps were found in the final configuration. This matches the previous run, confirming reproducibility with the same seed.
