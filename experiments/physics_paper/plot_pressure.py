import matplotlib.pyplot as plt
import numpy as np
# Generate data for pressure vs density plot
x = np.array([1, 2, 3, 4])
y = np.array([2, 3, 5, 7])
# Create the plot
plt.plot(x, y)
plt.xlabel('Density')
plt.ylabel('Pressure')
plt.title('Pressure vs Density')
plt.savefig('images/pressure_vs_density.png', bbox_inches='tight')