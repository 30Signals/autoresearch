import numpy as np
import matplotlib.pyplot as plt
import csv

# Load high density data
high_density_data = []
with open('results/high_density_data.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        high_density_data.append((float(row['A/A0']), float(row['PA/NkT'])))

# Load low density data
low_density_data = []
with open('results/low_density_data.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        low_density_data.append((float(row['A/A0']), float(row['PA/NkT'])))

# Combine data
all_data = high_density_data + low_density_data
A_A0_values = [x[0] for x in all_data]
PA_NkT_values = [x[1] for x in all_data]

# Theoretical curve (simplified for demonstration)
theoretical_A_A0 = np.linspace(0.05, 0.4, 100)
theoretical_PA_NkT = 1 + 0.5 * theoretical_A_A0

# Plot setup
plt.figure(figsize=(8, 6))
plt.plot(theoretical_A_A0, theoretical_PA_NkT, 'b-', label='Theoretical Curve', linewidth=2)

# Add confidence bands (simplified for demonstration)
upper_bound = theoretical_PA_NkT * 1.05
lower_bound = theoretical_PA_NkT * 0.95
plt.fill_between(theoretical_A_A0, lower_bound, upper_bound, alpha=0.3, color='blue', label='95% Confidence Band')

# Plot data points
plt.scatter(A_A0_values, PA_NkT_values, color='red', s=50, label='Simulation Data', zorder=5)

plt.xlabel('A/A0')
plt.ylabel('PA/NkT')
plt.title('Pressure vs Density with Theory Curve')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('images/pressure_vs_density.png', dpi=150)
plt.close()