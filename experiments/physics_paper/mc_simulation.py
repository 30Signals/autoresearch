import numpy as np
import matplotlib.pyplot as plt
import os
from itertools import combinations


def compute_pairwise_distances(positions, box_size=1.0):
    """Compute all pairwise distances between particles with periodic boundary conditions (minimum image)."""
    n = len(positions)
    distances = []
    for i in range(n):
        for j in range(i + 1, n):
            dx = positions[i, 0] - positions[j, 0]
            dy = positions[i, 1] - positions[j, 1]
            # Minimum image convention
            dx -= box_size * np.round(dx / box_size)
            dy -= box_size * np.round(dy / box_size)
            distances.append(np.sqrt(dx ** 2 + dy ** 2))
    return np.array(distances)


def check_overlaps(positions, d0, box_size=1.0):
    """Return True if any pair of particles overlap (distance < d0)."""
    dists = compute_pairwise_distances(positions, box_size)
    return np.any(dists < d0)


def initialize_lattice(N, box_size=1.0):
    """Place N particles on a square lattice inside the box (periodic)."""
    n_side = int(np.ceil(np.sqrt(N)))
    spacing = box_size / n_side
    xs = np.linspace(spacing / 2, box_size - spacing / 2, n_side)
    xv, yv = np.meshgrid(xs, xs)
    positions = np.column_stack([xv.ravel(), yv.ravel()])[:N]
    return positions


def monte_carlo_run(N=100, density=0.5, cycles=200, step_size=0.1, equilibration_epochs=20, box_size=1.0):
    """Run a hard‑disk Metropolis Monte‑Carlo simulation.

    Returns a dict with average pressure, its std error, and acceptance statistics.
    """
    # Calculate d0 from density
    d0 = 2 * np.sqrt(density * box_size**2 / (N * np.pi))
    if check_overlaps(initialize_lattice(N, box_size), d0, box_size):
        raise ValueError('Initial lattice has overlapping particles for the given d0')

    positions = initialize_lattice(N, box_size)

    # Radial distribution bins (up to half the box length)
    r_max = box_size / 2.0
    r_bins = np.linspace(0.0, r_max, 30)
    bin_edges = r_bins

    radial_counts = []
    acceptance_rates = []
    pressure_samples = []

    for epoch in range(equilibration_epochs + cycles):
        accepted = 0
        for i in range(N):
            # Propose move
            dx = np.random.uniform(-step_size, step_size)
            dy = np.random.uniform(-step_size, step_size)
            new_pos = positions[i] + np.array([dx, dy])
            # Apply periodic boundaries
            new_pos %= box_size
            trial = positions.copy()
            trial[i] = new_pos
            if not check_overlaps(trial, d0, box_size):
                positions = trial
                accepted += 1
        acceptance_rates.append(accepted / N)

        # Sampling after equilibration
        if epoch >= equilibration_epochs and (epoch - equilibration_epochs) % 5 == 0:
            # Pairwise distances
            dists = compute_pairwise_distances(positions, box_size)
            # Histogram (raw counts)
            counts, _ = np.histogram(dists, bins=bin_edges)
            # Normalise by annulus area to get g(r) approx (not exact)
            annulus_areas = np.pi * (bin_edges[1:] ** 2 - bin_edges[:-1] ** 2)
            g_r = counts / annulus_areas / (N * (N - 1) / 2)
            radial_counts.append(g_r)

            # Estimate contact density using the first bin just beyond d0
            idx = np.searchsorted(bin_edges, d0)
            if idx < len(g_r):
                contact_density = g_r[idx]
                # Equation of state for hard disks in 2D (scaled)
                pressure = 1.0 + (np.pi * d0 ** 2 * contact_density) / 2.0
                pressure_samples.append(pressure)

    # Diagnostics
    mean_accept = np.mean(acceptance_rates[-int(0.2 * len(acceptance_rates)):])
    std_accept = np.std(acceptance_rates[-int(0.2 * len(acceptance_rates)):])
    mean_pressure = np.mean(pressure_samples)
    std_pressure = np.std(pressure_samples) / np.sqrt(len(pressure_samples))

    # Save radial distribution for this density
    if radial_counts:
        radial_array = np.vstack(radial_counts)
        r_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        np.savetxt(
            f'results/radial_{N}_{density:.2f}.csv',
            np.column_stack((r_centers, radial_array.mean(axis=0), radial_array.std(axis=0))),
            header='r, g_mean, g_std',
            delimiter=','
        )

    return {
        'pressure': mean_pressure,
        'pressure_stderr': std_pressure,
        'acceptance_rate': mean_accept,
        'acceptance_stderr': std_accept,
    }


def run_density_sweep(N=100, densities=None):
    """Run simulations for a list of *area‑fraction* densities and collect results."""
    if densities is None:
        densities = [0.4, 0.5, 0.6, 0.7]
    os.makedirs('results', exist_ok=True)
    os.makedirs('images', exist_ok=True)

    pressure_data = []
    diagnostic_data = []

    for dens in densities:
        print(f'Running density {dens:.2f}')
        out = monte_carlo_run(N=N, density=dens)
        pressure_data.append([dens, out['pressure']])
        diagnostic_data.append([dens, out['acceptance_rate']])

    # Save CSV files
    np.savetxt('results/high_density_data.csv', np.array(pressure_data), header='Density,Pressure', delimiter=',')
    np.savetxt('results/diagnostics.csv', np.array(diagnostic_data), header='Density,AcceptanceRate', delimiter=',')

    # Plot pressure vs density
    pressure_arr = np.array(pressure_data)
    plt.figure(figsize=(8, 5))
    plt.plot(pressure_arr[:, 0], pressure_arr[:, 1], 'bo-', label='Simulation')
    # Simple theoretical line (ideal gas + low‑density correction)
    theory = 1.0 + np.pi * pressure_arr[:, 0] / 2.0
    plt.plot(pressure_arr[:, 0], theory, 'r--', label='Theory (approx)')
    plt.xlabel('Density (A/A₀)')
    plt.ylabel('PA / NkT')
    plt.title('Pressure vs Density')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('images/pressure_vs_density.png')
    plt.close()

    # Example radial distribution plot for the last density (just for illustration)
    last = densities[-1]
    radial_file = f'results/radial_{N}_{last:.2f}.csv'
    if os.path.exists(radial_file):
        data = np.loadtxt(radial_file, delimiter=',', comments='#')
        plt.figure(figsize=(8, 5))
        plt.plot(data[:, 0], data[:, 1], 'b-')
        plt.fill_between(data[:, 0], data[:, 1] - data[:, 2], data[:, 1] + data[:, 2], color='b', alpha=0.2)
        plt.axvline(d0, color='r', linestyle='--', label='Particle diameter')
        plt.xlabel('r')
        plt.ylabel('g(r)')
        plt.title(f'Radial distribution (density={last:.2f})')
        plt.legend()
        plt.tight_layout()
        plt.savefig('images/radial_distribution.png')
        plt.close()

if __name__ == '__main__':
    run_density_sweep()
