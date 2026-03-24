import numpy as np
import matplotlib.pyplot as plt

# Simplified radial distribution function data
radial_distances = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
rdf_values = np.array([0.0, 0.5, 1.0, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.6])

# Create plot
plt.figure(figsize=(8, 6))
plt.plot(radial_distances, rdf_values, 'b-', linewidth=2)

# Highlight 3 radial distance bins
bin_centers = [0.2, 0.5, 0.8]
bin_heights = [0.5, 1.1, 0.8]
plt.bar(bin_centers, bin_heights, width=0.1, alpha=0.5, color=['red', 'green', 'orange'], label='Radial Bins')

plt.xlabel('Radial Distance')
plt.ylabel('Radial Distribution Function')
plt.title('Radial Distribution Function with 3 Bins')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('images/radial_distribution.png', dpi=150)
plt.close()