import matplotlib.pyplot as plt
import numpy as np
# Generate data for radial distribution plot
x = np.array([1, 2, 3])
y = np.array([0.5, 0.7, 0.9])
# Create the plot
plt.plot(x, y)
plt.xlabel('Distance')
plt.ylabel('Distribution')
plt.title('Radial Distribution')
plt.savefig('images/radial_distribution.png', bbox_inches='tight')