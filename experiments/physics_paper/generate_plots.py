import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Ensure images directory exists
os.makedirs('images', exist_ok=True)

# Load pressure data (combine high and low density)
high = pd.read_csv('results/high_density_data.csv')
low = pd.read_csv('results/low_density_data.csv')
pressure_df = pd.concat([low, high], ignore_index=True)

# Plot pressure vs density
plt.figure(figsize=(8,6))
# Plot simulation points
plt.scatter(pressure_df['A/A0'], pressure_df['PA/NkT'], color='blue', label='Simulation')

# Theoretical curve: PA/NkT = 1 + (π d^2 n̄)/2
# We approximate n̄ as density = N/A; using d=1 and N=100, A = A/A0 * (π*(d/2)**2 * N)
# For simplicity, use a smooth range based on the data range
x_vals = np.linspace(pressure_df['A/A0'].min(), pressure_df['A/A0'].max(), 200)
# Assuming d=1, theoretical PA/NkT = 1 + (np.pi * 1**2 * (1/x_vals)) / 2 ???
# Actually n̄ = N / (A) ; A = A/A0 * (π*(d/2)**2 * N)
# So n̄ = N / (A/A0 * π*(d/2)**2 * N) = 1 / (A/A0 * π*(d/2)**2)
# With d=1, (d/2)**2 = 0.25, so denominator = A/A0 * π * 0.25 = (π/4) * (A/A0)
# Hence n̄ = 4/(π * (A/A0))
# Then PA/NkT = 1 + (π * d^2 * n̄)/2 = 1 + (π * 1 * 4/(π * (A/A0))) /2 = 1 + (4/(A/A0))/2 = 1 + 2/(A/A0)
theory_y = 1 + 2/ x_vals
plt.plot(x_vals, theory_y, 'r--', label='Theory')

# 95% confidence band using error_analysis (approximate std dev)
# Use absolute_error from error_analysis.csv as +/- error on PA/NkT
error_df = pd.read_csv('results/error_analysis.csv')
abs_err = error_df['absolute_error'].mean()
# Shade region
plt.fill_between(x_vals, theory_y-abs_err, theory_y+abs_err, color='gray', alpha=0.3, label='95% CI')

plt.xlabel('Area Ratio (A/A₀)')
plt.ylabel('PA/NkT')
plt.title('Pressure vs Density')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('images/pressure_vs_density.png')
plt.close()

# Radial distribution function plot
radial = pd.read_csv('results/radial_data.csv')
plt.figure(figsize=(8,6))
plt.plot(radial['bins'], radial['counts'], marker='o', linestyle='-', label='RDF')
plt.xlabel('Distance r')
plt.ylabel('Counts')
plt.title('Radial Distribution Function')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('images/radial_distribution.png')
plt.close()

print('Plots generated.')
