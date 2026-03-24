import numpy as np, matplotlib.pyplot as plt, pandas as pd

# Load data
low = pd.read_csv('results/low_density_data.csv')
high = pd.read_csv('results/high_density_data.csv')
error = pd.read_csv('results/error_analysis.csv')

# Combine for plotting
combined = pd.concat([low, high], ignore_index=True)

# Plot pressure vs density (A/A0)
A = combined['A/A0'].values
PA_NkT = combined['PA/NkT'].values
abs_error = error['absolute_error'].values

plt.figure(figsize=(6,4))
plt.errorbar(A, PA_NkT, yerr=abs_error[:, None], fmt='o', label='Simulation')
# Theoretical line (using simple hard-sphere EOS: PA/NkT = 1 + (np.pi * 1.0**2 * (1/ (combined['A/A0'] * np.pi * (1.0/2)**2))) / 2 )
# Derive density from A/A0: A/A0 = (L^2) / (N * pi*(d/2)^2) => N/(L^2) = 1/(A/A0 * pi*(d/2)^2)
# Using d=1.0
A_over_A0 = np.linspace(A.min(), A.max(), 200)
# density
rho = 1.0 / (A_over_A0 * np.pi * (1.0/2)**2)
theory = 1.0 + (np.pi * 1.0**2 * rho) / 2.0
plt.plot(A_over_A0, theory, '-', color='red', label='Theory')
# 95% confidence band (±2*std of absolute_error)
std_err = abs_error.std()
plt.fill_between(A_over_A0, theory-2*std_err, theory+2*std_err, color='red', alpha=0.2, label='95% CI')
plt.xlabel('A/A0')
plt.ylabel('PA/NkT')
plt.title('Pressure vs Density')
plt.legend()
os.makedirs('images', exist_ok=True)
plt.tight_layout()
plt.savefig('images/pressure_vs_density.png')
plt.close()

# Radial distribution function from a fresh MC run
from mc_simulation import positions, metropolis_step, L, d, N
# Run additional steps to equilibrate
pos = positions.copy()
for _ in range(2000):
    pos, _ = metropolis_step(pos, L, d, 1.0)
# Compute pair distances
pairs = []
for i in range(N):
    for j in range(i+1, N):
        rij = pos[j] - pos[i]
        rij = np.mod(rij + L/2, L) - L/2
        r = np.linalg.norm(rij)
        pairs.append(r)

pairs = np.array(pairs)
# Histogram
bins = np.linspace(0, L/2, 30)
hist, edges = np.histogram(pairs, bins=bins, density=True)
centers = 0.5*(edges[1:]+edges[:-1])

plt.figure(figsize=(6,4))
plt.plot(centers, hist, drawstyle='steps-mid')
plt.xlabel('r')
plt.ylabel('g(r)')
plt.title('Radial Distribution Function')
plt.tight_layout()
plt.savefig('images/radial_distribution.png')
plt.close()
print('Plots generated')
