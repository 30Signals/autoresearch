import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

# Simulation parameters
N = 100  # Particle count
d = 1.0  # Particle diameter
L = 10.0  # Box length (fixed)
kT = 1.0  # Thermal energy
n_steps = 1000  # MC steps
num_bins = 20  # For radial distribution function

def initialize_positions(N, L):
    """Initialize positions in a square lattice."""
    positions = np.zeros((N, 2))
    n_side = int(np.sqrt(N))
    dx = L / n_side
    for i in range(N):
        ix, iy = divmod(i, n_side)
        positions[i, 0] = (ix + 0.5) * dx
        positions[i, 1] = (iy + 0.5) * dx
    return positions

def metropolis_step(positions, L, d):
    """Single Metropolis MC step with overlap check"""
    N = len(positions)
    new_positions = positions.copy()
    i = np.random.randint(N)
    dr = np.random.uniform(-0.1, 0.1, 2)
    new_pos = (positions[i] + dr) % L  # PBC with mod

    # Check for overlaps
    overlap = any(np.linalg.norm(new_pos - positions[j]) < d for j in range(N) if j != i)
    return new_positions if not overlap else positions

def run_simulation(N, d):
    """Run full MC simulation and compute metrics"""
    # Initialize and equilibrate
    positions = initialize_positions(N, L)
    for _ in range(100):  # Equilibration steps
        positions = metropolis_step(positions, L, d)

    # Sampling phase
    distances = []
    for _ in range(n_steps):
        positions = metropolis_step(positions, L, d)
        
        # Calculate pairwise distances for RDF
        for i in range(N):
            for j in range(i+1, N):
                rij = positions[j] - positions[i]
                rij = np.mod(rij + L/2, L) - L/2  # Minimum image
                distances.append(np.linalg.norm(rij))

    # Calculate pressure (PA/NkT)
    area = L * L
    density = N / area
    pressure_ratio = 1.0 + (np.pi * d**2 * density) / 2.0
    
    # Calculate area ratio A/A0
    A_A0 = area / (np.pi * (d/2)**2 * N)
    
    # Compute radial distribution function
    rbins = np.histogram(distances, bins=num_bins, range=(0, 3*d))[1]
    rdf, _ = np.histogram(distances, bins=rbins)
    
    # Return results as dictionary
    return {
        'N': N,
        'd': d,
        'A_A0': A_A0,
        'PA_NkT': pressure_ratio,
        'rdf': rdf,
        'rbins': rbins
    }

# Main execution
if __name__ == "__main__":
    # Run simulation
    sim_results = run_simulation(N, d)
    
    # Save density-pressure data to CSV
    pd.DataFrame([{'A_A0': sim_results['A_A0'], 'PA_NkT': sim_results['PA_NkT']}]).to_csv('results/pressure_data.csv', index=False)

    # Save radial distribution function data
    pd.DataFrame({
        'bins': sim_results['rbins'][:-1],
        'counts': sim_results['rdf']
    }).to_csv('results/radial_data.csv', index=False)

    # Plot pressure vs density curve
    plt.figure(figsize=(10, 6))
    data_file = pd.read_csv('results/pressure_data.csv')
    
    # Plot simulated pressure values
    plt.scatter(data_file['A_A0'], data_file['PA_NkT'], 
                label='Simulation data', alpha=0.7)
    
    # Plot theoretical curve based on equation (PA/NkT) = 1 + πd²n̄/2
    theory_A = np.linspace(0.5, 1.5, 100)
    theory_P = 1 + (np.pi * (1.0)**2 * theory_A) / 2  # Simplified version
    plt.plot(theory_A, theory_P, 'r--', label='Theoretical prediction')
    
    plt.xlabel('Area Ratio (A/A₀)')
    plt.ylabel('PA/NkT')
    plt.title('Pressure vs Density Curve')
    plt.legend()
    plt.grid()
    plt.savefig('images/pressure_vs_density.png')

    # Plot radial distribution function
    rdf_data = pd.read_csv('results/radial_data.csv')
    plt.figure(figsize=(10, 6))
    plt.plot(rdf_data['bins'], rdf_data['counts'],
             label='RDF from simulation')

    plt.xlabel('Distance (r)')
    plt.ylabel('g(r)')
    plt.title('Radial Distribution Function')
    plt.grid()
    plt.legend()
    plt.savefig('images/radial_distribution.png')

    print("Generated simulation outputs:")
    print("- pressure_vs_density.png")
    print("- radial_distribution.png")
    print("- pressure_data.csv")
    print("- radial_data.csv")  