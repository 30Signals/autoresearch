import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
N = 100  # number of particles
L = 10.0  # box length
d = 1.0  # particle diameter
kT = 1.0  # thermal energy
n_steps = 1000  # number of Monte Carlo steps

# Initialize positions on a lattice
positions = np.zeros((N, 2))
n_side = int(np.sqrt(N))
dx = L / n_side
for i in range(N):
    ix = i % n_side
    iy = i // n_side
    positions[i, 0] = (ix + 0.5) * dx
    positions[i, 1] = (iy + 0.5) * dx

# Monte Carlo simulation
def metropolis_step(positions, L, d, kT):
    """Perform one Metropolis Monte Carlo step"""
    N = len(positions)
    new_positions = positions.copy()
    
    # Randomly select a particle
    i = np.random.randint(N)
    
    # Propose a random displacement
    dr = np.random.uniform(-0.1, 0.1, 2)
    new_pos = positions[i] + dr
    
    # Apply periodic boundary conditions
    new_pos = np.mod(new_pos, L)
    
    # Check for overlaps
    overlap = False
    for j in range(N):
        if i != j:
            dist = np.linalg.norm(new_pos - positions[j])
            if dist < d:
                overlap = True
                break
    
    # Accept or reject the move
    if not overlap:
        new_positions[i] = new_pos
        return new_positions, True
    else:
        return positions, False

# Run simulation
acceptance_count = 0
for step in range(n_steps):
    positions, accepted = metropolis_step(positions, L, d, kT)
    if accepted:
        acceptance_count += 1

acceptance_rate = acceptance_count / n_steps
print(f"Acceptance rate: {acceptance_rate:.3f}")

# Calculate pressure using virial theorem
def calculate_pressure(positions, L, d, kT):
    """Calculate pressure using virial theorem"""
    N = len(positions)
    virial = 0.0
    
    for i in range(N):
        for j in range(i+1, N):
            rij = positions[j] - positions[i]
            rij = np.mod(rij + L/2, L) - L/2  # minimum image convention
            r = np.linalg.norm(rij)
            
            if r < d:
                virial += 1.0  # hard-sphere contact contribution
    
    # Pressure equation for 2D hard spheres
    area = L * L
    density = N / area
    PA_NkT = 1.0 + (np.pi * d**2 * density) / 2.0
    
    return PA_NkT

# Calculate and print pressure
PA_NkT = calculate_pressure(positions, L, d, kT)
print(f"PA/NkT = {PA_NkT:.4f}")

# Calculate density
A_A0 = (L * L) / (N * np.pi * (d/2)**2)
print(f"A/A0 = {A_A0:.4f}")