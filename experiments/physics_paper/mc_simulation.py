import numpy as np
import os
import csv
import matplotlib.pyplot as plt
from collections import defaultdict


def initialize_positions(N, L, d, seed=None):
    """Place particles on a square lattice with small random displacements to avoid overlap."""
    rng = np.random.default_rng(seed)
    n_side = int(np.ceil(np.sqrt(N)))
    spacing = L / n_side
    positions = []
    for i in range(N):
        ix = i % n_side
        iy = i // n_side
        x = (ix + 0.5) * spacing + (rng.random() - 0.5) * 0.1 * spacing
        y = (iy + 0.5) * spacing + (rng.random() - 0.5) * 0.1 * spacing
        positions.append([x % L, y % L])
    return np.array(positions)


def minimum_image(rij, L):
    """Apply periodic boundary conditions (minimum image)."""
    rij -= L * np.rint(rij / L)
    return rij


def mc_step(positions, L, d, alpha, rng):
    N = len(positions)
    accepted = 0
    for i in range(N):
        # propose move
        disp = (rng.random(2) - 0.5) * 2 * alpha
        new_pos = (positions[i] + disp) % L
        # check overlaps
        # compute distances to all other particles
        delta = positions - new_pos
        delta = minimum_image(delta, L)
        dist2 = np.sum(delta**2, axis=1)
        # ignore self (i)
        dist2[i] = np.inf
        if np.all(dist2 >= d**2):
            positions[i] = new_pos
            accepted += 1
    return accepted / N


def compute_pressure(positions, L, d, dr=0.01):
    """Estimate pressure using contact value of radial distribution function.
    g(d) is approximated by counting pairs with distance in [d, d+dr].
    """
    N = len(positions)
    rho = N / L**2
    # pairwise distances
    diffs = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]
    diffs = minimum_image(diffs, L)
    dists = np.sqrt(np.sum(diffs**2, axis=-1))
    # exclude self
    np.fill_diagonal(dists, np.inf)
    shell = (dists >= d) & (dists < d + dr)
    count = np.sum(shell)
    # each pair counted twice
    g_contact = count / (N * rho * 2 * np.pi * d * dr)
    pressure = rho * (1 + np.pi * d**2 * g_contact / 2)
    return pressure, g_contact


def run_density_point(N, eta, steps=2000, equil=500, alpha=0.1, seed=None):
    """Run MC for a given packing fraction eta = N * pi * (d/2)^2 / L^2 (L=1).
    Returns pressure, acceptance_rate, g_contact.
    """
    L = 1.0
    # solve for d from eta
    d = np.sqrt(4 * eta / (np.pi * N))
    rng = np.random.default_rng(seed)
    pos = initialize_positions(N, L, d, seed=rng.integers(1e9))
    acc_rates = []
    for step in range(steps):
        acc = mc_step(pos, L, d, alpha, rng)
        acc_rates.append(acc)
        if step >= equil:
            # we could sample pressure periodically; here sample every step after equil
            pass
    acceptance_rate = np.mean(acc_rates)
    pressure, g_contact = compute_pressure(pos, L, d)
    return pressure, acceptance_rate, g_contact, d


def theoretical_pressure(eta):
    """Simple theoretical estimate: virial up to second order: 1 + 2*eta"""
    return 1 + 2 * eta


def generate_data():
    os.makedirs('results', exist_ok=True)
    os.makedirs('images', exist_ok=True)
    N = 200
    high_etas = [0.55, 0.60, 0.65, 0.70]
    low_etas = [0.10, 0.15, 0.20, 0.25]
    # run each density with 3 independent seeds
    def run_set(etas, filename):
        rows = []
        for eta in etas:
            pressures = []
            accs = []
            for s in range(3):
                p, acc, _, _ = run_density_point(N, eta, steps=1500, equil=300, alpha=0.1, seed=42 + s)
                pressures.append(p)
                accs.append(acc)
            mean_p = np.mean(pressures)
            std_p = np.std(pressures, ddof=1)
            rows.append([eta, mean_p, std_p])
        # write csv: eta, pressure_mean, pressure_std
        with open(f'results/{filename}', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['eta','pressure_mean','pressure_std'])
            writer.writerows(rows)
    run_set(high_etas, 'high_density_data.csv')
    run_set(low_etas, 'low_density_data.csv')
    # diagnostics (acceptance rates) using first seed only for brevity
    diagnostics = []
    for eta in high_etas + low_etas:
        _, acc, _, _ = run_density_point(N, eta, steps=1500, equil=300, alpha=0.1, seed=123)
        diagnostics.append([eta, acc])
    with open('results/diagnostics.csv','w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['eta','acceptance_rate'])
        w.writerows(diagnostics)
    # pressure vs density plot with 95% confidence band (mean +/- 1.96*std/ sqrt(n))
    import math
    def load_csv(path):
        data = np.loadtxt(path, delimiter=',', skiprows=1)
        return data
    high = load_csv('results/high_density_data.csv')
    low = load_csv('results/low_density_data.csv')
    all_data = np.vstack([low, high])
    plt.errorbar(all_data[:,0], all_data[:,1], yerr=1.96*all_data[:,2]/math.sqrt(3), fmt='o', label='Simulation')
    # theory curve
    etas = np.linspace(0.05,0.75,200)
    plt.plot(etas, theoretical_pressure(etas), 'r-', label='Theory (1+2η)')
    plt.xlabel('Packing fraction η')
    plt.ylabel('PA/(NkT)')
    plt.title('Pressure vs Packing Fraction')
    plt.legend()
    plt.savefig('images/pressure_vs_density.png')
    plt.close()
    # radial distribution for a medium density (eta=0.30)
    eta_mid = 0.30
    _, _, _, d_mid = run_density_point(N, eta_mid, steps=1500, equil=300, alpha=0.1, seed=999)
    # after run, positions are in last call; we need to compute g(r)
    # We'll reuse the function to get positions
    L=1.0
    pos = initialize_positions(N, L, d_mid, seed=999)
    # perform MC to equilibrate (discard) and get final positions
    rng = np.random.default_rng(999)
    for _ in range(800):
        mc_step(pos, L, d_mid, 0.1, rng)
    # compute g(r)
    dr = 0.01
    rmax = L/2
    bins = np.arange(0, rmax+dr, dr)
    g = np.zeros(len(bins)-1)
    diffs = pos[:,np.newaxis,:]-pos[np.newaxis,:,:]
    diffs = minimum_image(diffs, L)
    dists = np.sqrt(np.sum(diffs**2, axis=-1))
    np.fill_diagonal(dists, np.inf)
    hist, edges = np.histogram(dists[dists<rmax], bins=bins)
    rho = N / L**2
    shell_areas = np.pi * (edges[1:]**2 - edges[:-1]**2)
    ideal_counts = rho * shell_areas * N
    g = hist / ideal_counts
    plt.plot((edges[:-1]+edges[1:])/2, g, label=f'η={eta_mid}')
    plt.xlabel('r')
    plt.ylabel('g(r)')
    plt.title('Radial Distribution Function')
    plt.xlim(0, 0.5)
    plt.legend()
    plt.savefig('images/radial_distribution.png')
    plt.close()
    # error analysis compared to theory for all points
    with open('results/error_analysis.csv','w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['eta','abs_error','rel_error'])
        for row in all_data:
            eta=row[0]
            sim=row[1]
            theory=theoretical_pressure(eta)
            abs_err=abs(sim-theory)
            rel_err=abs_err/theory
            w.writerow([eta,abs_err,rel_err])

if __name__ == '__main__':
    generate_data()
