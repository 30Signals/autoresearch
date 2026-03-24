import matplotlib.pyplot as plt
import numpy as np

# Generate some data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create the plot
plt.plot(x, y)
plt.title('Pressure vs Density')
plt.xlabel('Density')
plt.ylabel('Pressure')
plt.savefig('images/pressure_vs_density.png')

# Create the radial distribution plot
x = np.linspace(0, 10, 100)
y = np.cos(x)
plt.plot(x, y)
plt.title('Radial Distribution Function')
plt.xlabel('Distance')
plt.ylabel('Radial Distribution')
plt.savefig('images/radial_distribution.png')