import numpy as np

# Define the simulation parameters
N = 100  # Number of particles
L = 1.0   # Box size
d0 = 0.1  # Particle diameter
alpha = 0.1  # Step size
num_cycles = 1000  # Number of cycles

# Initialize the particle positions
positions = np.zeros((N, 2))
for i in range(N):
    positions[i] = [np.random.uniform(0, L), np.random.uniform(0, L)]

# Define the Metropolis algorithm
for cycle in range(num_cycles):
    for i in range(N):
        # Propose a random displacement
        dx = np.random.uniform(-alpha, alpha)
        dy = np.random.uniform(-alpha, alpha)
        new_position = [positions[i, 0] + dx, positions[i, 1] + dy]
        
        # Check for overlap with other particles
        overlap = False
        for j in range(N):
            if i != j:
                distance = np.sqrt((new_position[0] - positions[j, 0])**2 + (new_position[1] - positions[j, 1])**2)
                if distance < d0:
                    overlap = True
                    break
        
        # Accept or reject the move
        if not overlap:
            positions[i] = new_position

# Compute the pressure
pressure = 0
for i in range(N):
    for j in range(N):
        if i != j:
            distance = np.sqrt((positions[i, 0] - positions[j, 0])**2 + (positions[i, 1] - positions[j, 1])**2)
            if distance < d0:
                pressure += 1
pressure /= N

print(pressure)
