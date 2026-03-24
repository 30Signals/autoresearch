### Round 6

#### Objective
Reproduce and validate the Monte Carlo method for computing the equation of state of a 2D rigid-sphere system, as introduced in *Equation of State Calculations by Fast Computing Machines*.

#### Progress
Completed the diagnostic metrics for the simulation.

### Criteria Completed
- [x] mc_simulation.py implements Metropolis MC for 2D hard spheres
- [x] results/high_density_data.csv with PA/NkT vs A/A0 for 4 density points
- [x] results/low_density_data.csv with PA/NkT vs A/A0 for 4 density points
- [x] images/pressure_vs_density.png with theory curve and 95% confidence band
- [x] images/radial_distribution.png with 3 radial distance bins shown
- [x] results/error_analysis.csv with absolute_error µ 0.05, relative_error µ 0.05
- [x] results/diagnostics.csv with acceptance_rate between 0.2 and 0.5 for all runs

### Next Steps
Call done() to signal the end of the experiment and verify all criteria are met.