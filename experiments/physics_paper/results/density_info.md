# Density Parameter Calculation

For the simulation run in `mc_simulation.py` we used:
- Box size = 1.0 (area A = 1.0)
- Number of particles N = 100
- Particle diameter d0 = 0.1129 (approx)

The particle area is \(\pi (d_0/2)^2\). Therefore the total particle area \(A_0\) is:
```
A0 = N * pi * (d0/2)**2
```
Using the values above:
```
A0 = 100 * pi * (0.1129/2)**2 ≈ 0.9979
```
The density parameter \(A/A_0\) is:
```
A/A0 = 1.0 / 0.9979 ≈ 1.0021
```
Thus the system is at a density close to the target ratio of 1.0 (approximately unity).
